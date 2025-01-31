import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración de la API de WhatsApp
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


TO_PHONE_NUMBERS = ["573001234567", "573112345678", "573223456789"] 

TO_GROUP_ID = "YOUR_GROUP_ID"

def send_whatsapp_message(message, recipients):
    """ Envía un mensaje de WhatsApp a múltiples destinatarios """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data2 = {
        "messaging_product": "whatsapp",
        "to": TO_GROUP_ID,
        "type": "text",
        "text": {"body": message}
    }
    
    responses = []
    for phone in recipients:
        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }
        response = requests.post(WHATSAPP_API_URL, json=data, headers=headers)
        responses.append(response.json())

    return responses

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.get_json()

        
        alert_name = data.get("alertname", "Sin nombre")
        panel = data.get("panel", "Desconocido")
        severity = data.get("severity", "Sin severidad")

        
        message = f"🔔 *Alerta Recibida*\n📌 *Panel:* {panel}\n⚠ *Severidad:* {severity}\n🔹 *Alerta:* {alert_name}"
        
        # Enviar mensaje de WhatsApp a todos los números
        response = send_whatsapp_message(message, TO_PHONE_NUMBERS)

        return jsonify({"message": "Mensajes enviados", "response": response}), 200
    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
