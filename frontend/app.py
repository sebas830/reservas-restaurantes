# /frontend/app.py

from flask import Flask, render_template, flash, request, redirect, url_for, jsonify, session
import os
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"  # Prefijo del gateway


def request_api(method: str, service: str, path: str, token: str = None, **kwargs):
    """Helper para consumir el API Gateway.

    method: GET/POST/PUT/DELETE/PATCH
    service: nombre del microservicio (auth, restaurantes, reservas, menu)
    path: path interno del servicio (ej: 'restaurantes/' o 'platos/?restaurante_id=1')
    token: access token opcional para Authorization
    kwargs: params, json, data, timeout, etc.
    """
    url = f"{API_GATEWAY_URL}{API_PREFIX}/{service}/{path}"
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.request(method, url, headers=headers, timeout=kwargs.pop("timeout", 6), **kwargs)
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return {}
    except requests.exceptions.HTTPError as e:
        # Propagar mensaje legible
        raise RuntimeError(f"Error HTTP {resp.status_code}: {resp.text}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Fallo de red al llamar {url}: {e}") from e


@app.route("/")
def index():
    return render_template("index.html", title="Inicio")


@app.route("/restaurantes")
def restaurantes():
    restaurantes = []
    try:
        restaurantes = request_api("GET", "restaurantes", "restaurantes/")
    except Exception as e:
        flash(f"No se pudieron cargar restaurantes: {e}", "error")

    # Para cada restaurante obtener su menú (platos filtrando por restaurante_id)
    for r in restaurantes:
        try:
            platos = request_api("GET", "menu", f"platos/?restaurante_id={r['id']}")
            r["menu"] = platos
        except Exception:
            r["menu"] = []

    return render_template("restaurantes.html", title="Restaurantes", restaurantes=restaurantes)


@app.route("/menu")
def menu():
    restaurantes = []
    try:
        restaurantes = request_api("GET", "restaurantes", "restaurantes/")
    except Exception as e:
        flash(f"No se pudieron cargar restaurantes: {e}", "error")
        return render_template("menu.html", title="Menú", restaurantes=[])

    for r in restaurantes:
        try:
            r["menu"] = request_api("GET", "menu", f"platos/?restaurante_id={r['id']}")
        except Exception:
            r["menu"] = []

    return render_template("menu.html", title="Menú", restaurantes=restaurantes)


@app.route("/reservas", methods=["GET", "POST"])
def reservas():
    # Preseleccionar restaurante si viene como query param
    restaurante_pre = request.args.get("restaurante_id")

    if request.method == "POST":
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")
        # Convertir a formato ISO para fecha_reserva
        fecha_reserva_iso = f"{fecha}T{hora}:00"  # Simple -> YYYY-MM-DDTHH:00
        try:
            # mapear campos al modelo del backend
            reserva_payload = {
                "cliente_nombre": request.form.get("cliente_nombre"),
                "cliente_email": request.form.get("cliente_email"),
                "cliente_telefono": request.form.get("cliente_telefono"),
                "restaurante_id": int(request.form.get("restaurante_id")),
                "fecha_reserva": fecha_reserva_iso,
                "numero_personas": int(request.form.get("numero_personas")),
                "notas": request.form.get("notas") or None
            }
        except (ValueError, TypeError):
            flash("Datos inválidos en el formulario.", "error")
            return redirect(url_for("reservas"))

        try:
            token = session.get("access_token")
            # Reservas actualmente no requieren auth, se deja token si existe
            request_api("POST", "reservas", "reservas/", json=reserva_payload, token=token)
            flash("¡Reserva creada con éxito!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error creando la reserva: {e}", "error")

    # GET
    try:
        restaurantes = request_api("GET", "restaurantes", "restaurantes/")
    except Exception as e:
        flash(f"Error cargando restaurantes: {e}", "error")
        restaurantes = []

    fecha_minima = datetime.now().strftime("%Y-%m-%d")
    fecha_maxima = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    horas_disponibles = [f"{h:02d}:00" for h in range(12, 23)]

    return render_template("reservas.html",
                           title="Reservas",
                           restaurantes=restaurantes,
                           fecha_minima=fecha_minima,
                           fecha_maxima=fecha_maxima,
                           horas_disponibles=horas_disponibles,
                           restaurante_pre=restaurante_pre)


# ------------------ AUTH ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            # OAuth2 password grant -> username field
            data = {"username": email, "password": password}
            tokens = request_api("POST", "auth", "login", data=data)
            session["access_token"] = tokens.get("access_token")
            session["refresh_token"] = tokens.get("refresh_token")
            session["user_email"] = email
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error de autenticación: {e}", "error")
    return render_template("login.html", title="Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        try:
            payload = {"email": email, "password": password, "full_name": full_name}
            request_api("POST", "auth", "register", json=payload)
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Error registrando usuario: {e}", "error")
    return render_template("register.html", title="Registro")


@app.route("/logout", methods=["POST"])
def logout():
    refresh = session.get("refresh_token")
    if refresh:
        try:
            request_api("POST", "auth", "logout", json={"refresh_token": refresh})
        except Exception:
            # Ignorar error de logout
            pass
    session.clear()
    flash("Sesión cerrada", "success")
    return redirect(url_for("index"))


# TODO: Implementar renovación silenciosa de access token usando refresh antes de expiración.

@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


@app.route("/profile")
def profile():
    """Página de perfil: consulta /me y lista reservas del email del usuario."""
    if not session.get("access_token"):
        flash("Debes iniciar sesión para ver tu perfil.", "error")
        return redirect(url_for("login"))

    token = session.get("access_token")
    try:
        user = request_api("GET", "auth", "me", token=token)
    except Exception as e:
        flash(f"No se pudo obtener datos de usuario: {e}", "error")
        return redirect(url_for("index"))

    # Obtener reservas por email
    reservas = []
    try:
        email = user.get("email")
        reservas = request_api("GET", "reservas", f"reservas/?cliente_email={email}")
    except Exception:
        reservas = []

    return render_template("profile.html", title="Mi Perfil", user=user, reservas=reservas)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
