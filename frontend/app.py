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
    """Helper para consumir el API Gateway con reintento automático usando refresh token.

    - Si la respuesta es 401 y existe refresh_token en sesión, intenta un /auth/refresh
      y reintenta la solicitud original una única vez.
    - Si el refresh falla, limpia la sesión y lanza error.
    - Retorna JSON (dict/list) o {} si no hay contenido.
    """
    url = f"{API_GATEWAY_URL}{API_PREFIX}/{service}/{path}"
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    timeout = kwargs.pop("timeout", 6)

    def _do_request(current_token):
        local_headers = dict(headers)
        if current_token:
            local_headers["Authorization"] = f"Bearer {current_token}"
        return requests.request(method, url, headers=local_headers, timeout=timeout, **kwargs)

    try:
        resp = _do_request(token)
        if resp.status_code == 401 and token and session.get("refresh_token") and service != "auth":
            # Intentar refresh
            try:
                refresh_payload = {"refresh_token": session.get("refresh_token")}
                r_refresh = requests.post(f"{API_GATEWAY_URL}{API_PREFIX}/auth/refresh", json=refresh_payload, timeout=timeout)
                if r_refresh.status_code == 200:
                    data_refresh = r_refresh.json()
                    # Actualizar sesión
                    session["access_token"] = data_refresh.get("access_token")
                    # Nuevo refresh token (rotación)
                    if data_refresh.get("refresh_token"):
                        session["refresh_token"] = data_refresh.get("refresh_token")
                    # Reintentar una vez con nuevo access token
                    resp = _do_request(session.get("access_token"))
                else:
                    # Falló el refresh -> limpiar sesión y dejar error
                    session.clear()
                    raise RuntimeError("Sesión expirada. Inicia sesión nuevamente.")
            except requests.exceptions.RequestException:
                session.clear()
                raise RuntimeError("No se pudo refrescar la sesión. Conéctate e inicia sesión otra vez.")

        # Manejo final de status
        if resp.status_code >= 400:
            raise RuntimeError(f"Error HTTP {resp.status_code}: {resp.text}")
        if resp.content:
            # Intentar parseo json, fallback a cadena
            try:
                return resp.json()
            except ValueError:
                return {"raw": resp.text}
        return {}
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Fallo de red al llamar {url}: {e}") from e


@app.route("/")
def index():
    reservas = []
    # Si el usuario está autenticado, obtener sus reservas y mostrarlas en el panel
    if session.get("access_token"):
        token = session.get("access_token")
        try:
            user = request_api("GET", "auth", "me", token=token)
            email = user.get("email")
            reservas = request_api("GET", "reservas", f"reservas/?cliente_email={email}")
        except Exception as e:
            # No bloquear la página principal si falla la obtención de reservas
            flash(f"No se pudieron cargar tus reservas: {e}", "error")

    return render_template("index.html", title="Inicio", reservas=reservas)


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
            session.modified = True  # Asegurar que Flask guarde la sesión
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


@app.route("/owner/dashboard")
def owner_dashboard():
    """Panel para propietarios/restaurantes: muestra quiénes han hecho reservas en sus restaurantes."""
    if not session.get("access_token"):
        flash("Debes iniciar sesión para ver el panel de restaurante.", "error")
        return redirect(url_for("login"))

    token = session.get("access_token")
    try:
        user = request_api("GET", "auth", "me", token=token)
    except Exception as e:
        flash(f"No se pudo obtener datos de usuario: {e}", "error")
        return redirect(url_for("index"))

    owner_email = user.get("email")

    # Obtener todos los restaurantes
    restaurantes = []
    try:
        restaurantes = request_api("GET", "restaurantes", "restaurantes/")
    except Exception as e:
        flash(f"No se pudieron cargar restaurantes: {e}", "error")
        restaurantes = []

    # Filtrar restaurantes que pertenezcan al owner
    my_restaurants = [r for r in restaurantes if r.get("owner_email") == owner_email]

    # Para cada restaurante obtener sus reservas (mostrar todas: pendientes, confirmadas, completadas, canceladas)
    all_reservas = []
    for r in my_restaurants:
        try:
            reservas = request_api("GET", "reservas", f"reservas/?restaurante_id={r['id']}")
            # Mostrar todas las reservas independientemente del estado
            for res in reservas:
                res["restaurante_nombre"] = r.get("nombre")
                res["restaurante_id"] = r.get("id")
            all_reservas.extend(reservas)
        except Exception:
            pass

    # Ordenar por fecha descendente (más recientes primero)
    all_reservas.sort(key=lambda x: x.get("fecha_reserva", ""), reverse=True)

    return render_template("restaurant_panel.html", title="Panel Restaurante", reservas=all_reservas, user=user)


@app.route("/mis-reservas")
def mis_reservas():
    """Página dedicada a mostrar las reservas del usuario autenticado."""
    if not session.get("access_token"):
        flash("Debes iniciar sesión para ver tus reservas.", "error")
        return redirect(url_for("login"))

    token = session.get("access_token")
    try:
        user = request_api("GET", "auth", "me", token=token)
    except Exception as e:
        flash(f"No se pudo obtener datos de usuario: {e}", "error")
        return redirect(url_for("login"))

    reservas = []
    try:
        email = user.get("email")
        reservas = request_api("GET", "reservas", f"reservas/?cliente_email={email}")
    except Exception as e:
        flash(f"No se pudieron cargar tus reservas: {e}", "error")
        reservas = []

    return render_template("mis_reservas.html", title="Mis Reservas", reservas=reservas)


@app.route('/consultar-reserva')
def consultar_reserva():
    """Página para que un usuario autenticado vea sus reservas (sin buscar por ID ni email).
    Redirige a login si no está autenticado.
    """
    if not session.get("access_token"):
        flash("Debes iniciar sesión para consultar tus reservas.", "error")
        return redirect(url_for("login"))

    token = session.get("access_token")
    try:
        # Obtener email del usuario autenticado
        user = request_api("GET", "auth", "me", token=token)
        email = user.get("email")
    except Exception as e:
        flash(f"No se pudo obtener los datos del usuario: {e}", "error")
        return redirect(url_for("index"))

    resultados = []
    try:
        resultados = request_api('GET', 'reservas', f"reservas/?cliente_email={email}")
    except Exception as e:
        flash(f"No se pudieron cargar las reservas: {e}", "error")
        resultados = []

    return render_template('consultar_reserva.html', title='Mis Reservas', resultados=resultados)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
