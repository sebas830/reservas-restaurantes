# /frontend/app.py

from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
import os
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

# Obtén la URL del API Gateway desde las variables de entorno.
# Esta variable debe estar configurada en el docker-compose.yml.
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

@app.route("/")
def index():
    """Ruta de la página de inicio."""
    return render_template("index.html", title="Sistema de Reservas de Restaurantes")

@app.route("/restaurantes")
def restaurantes():
    """Página de listado de restaurantes con sus mesas y menús."""
    try:
        # Obtener restaurantes
        response = requests.get(f"{API_GATEWAY_URL}/restaurantes/")
        response.raise_for_status()
        restaurantes = response.json()

        # Para cada restaurante, obtener sus mesas y menú
        for restaurante in restaurantes:
            # Obtener mesas
            try:
                mesas_response = requests.get(f"{API_GATEWAY_URL}/mesas/restaurante/{restaurante['id']}")
                mesas_response.raise_for_status()
                restaurante['mesas'] = mesas_response.json()
            except requests.exceptions.RequestException:
                restaurante['mesas'] = []

            # Obtener menú
            try:
                menu_response = requests.get(f"{API_GATEWAY_URL}/menu/restaurante/{restaurante['id']}")
                menu_response.raise_for_status()
                restaurante['menu'] = menu_response.json()
            except requests.exceptions.RequestException:
                restaurante['menu'] = []

        return render_template("restaurantes.html", 
                            title="Nuestros Restaurantes",
                            restaurantes=restaurantes)
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los restaurantes: {e}")
        flash("Error al cargar los restaurantes. Por favor, intente más tarde.", "error")
        return render_template("restaurantes.html", 
                            title="Nuestros Restaurantes",
                            restaurantes=[])

@app.route("/menu")
def menu():
    """Página de menús de los restaurantes."""
    try:
        # Obtener lista de restaurantes
        response = requests.get(f"{API_GATEWAY_URL}/restaurantes/")
        response.raise_for_status()
        restaurantes = response.json()
        
        # Para cada restaurante, obtener su menú
        for restaurante in restaurantes:
            try:
                menu_response = requests.get(f"{API_GATEWAY_URL}/menu/restaurante/{restaurante['id']}")
                menu_response.raise_for_status()
                restaurante['menu'] = menu_response.json()
            except requests.exceptions.RequestException:
                restaurante['menu'] = []
        
        return render_template("menu.html", 
                            title="Menús",
                            restaurantes=restaurantes)
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los menús: {str(e)}", "error")
        return render_template("menu.html", 
                            title="Menús",
                            restaurantes=[])

@app.route("/reservas", methods=["GET", "POST"])
def reservas():
    """Página de reservas."""
    if request.method == "POST":
        # Recoger datos del formulario
        reserva_data = {
            "restaurante_id": request.form.get("restaurante_id"),
            "fecha": request.form.get("fecha"),
            "hora": request.form.get("hora"),
            "num_personas": request.form.get("num_personas"),
            "nombre_cliente": request.form.get("nombre_cliente"),
            "telefono": request.form.get("telefono"),
            "email": request.form.get("email"),
            "notas": request.form.get("notas", "")
        }
        
        try:
            # Crear la reserva
            response = requests.post(f"{API_GATEWAY_URL}/reservas/", json=reserva_data)
            response.raise_for_status()
            flash("¡Reserva realizada con éxito!", "success")
            return redirect(url_for("index"))
        except requests.exceptions.RequestException as e:
            flash(f"Error al realizar la reserva: {str(e)}", "error")
    
    try:
        # Obtener lista de restaurantes para el formulario
        response = requests.get(f"{API_GATEWAY_URL}/restaurantes/")
        response.raise_for_status()
        restaurantes = response.json()
        
        # Configurar fechas disponibles (desde hoy hasta 30 días después)
        fecha_minima = datetime.now().strftime("%Y-%m-%d")
        fecha_maxima = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Horarios predeterminados (se actualizarán via AJAX según el restaurante)
        horas_disponibles = [f"{h:02d}:00" for h in range(12, 23)]
        
        return render_template("reservas.html",
                            title="Realizar Reserva",
                            restaurantes=restaurantes,
                            fecha_minima=fecha_minima,
                            fecha_maxima=fecha_maxima,
                            horas_disponibles=horas_disponibles)
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los datos: {str(e)}", "error")
        return render_template("reservas.html",
                            title="Realizar Reserva",
                            restaurantes=[],
                            fecha_minima=datetime.now().strftime("%Y-%m-%d"),
                            fecha_maxima=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                            horas_disponibles=[])

@app.route("/api/horas-disponibles/<int:restaurante_id>")
def horas_disponibles(restaurante_id):
    """API endpoint para obtener horas disponibles de un restaurante."""
    try:
        response = requests.get(f"{API_GATEWAY_URL}/restaurantes/{restaurante_id}/horario")
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException:
        return jsonify({"horas": [f"{h:02d}:00" for h in range(12, 23)]})

@app.route("/api/horas-disponibles/<int:restaurante_id>/<fecha>")
def horas_disponibles_fecha(restaurante_id, fecha):
    """API endpoint para obtener horas disponibles de un restaurante en una fecha específica."""
    try:
        response = requests.get(f"{API_GATEWAY_URL}/restaurantes/{restaurante_id}/horario/{fecha}")
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException:
        return jsonify({"horas": [f"{h:02d}:00" for h in range(12, 23)]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
