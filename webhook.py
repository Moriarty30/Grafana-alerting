import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Variables de entorno
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",")

TO_PHONE_NUMBERS = ["573001234567", "573112345678", "573223456789"]
TO_GROUP_ID = "YOUR_GROUP_ID"

# --------------------- FUNCIÓN WHATSAPP ---------------------
def send_whatsapp_message(message, recipients):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
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

# --------------------- FUNCIÓN EMAIL ---------------------
def send_email_message(message):
    if not EMAIL_USER or not EMAIL_PASS or not EMAIL_RECIPIENTS:
        print("❌ Error: Faltan variables de entorno para el correo.")
        return {"status": "error", "message": "Missing email environment variables"}

    asunto = "🚨 Alerta en Grafana"
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = ', '.join(EMAIL_RECIPIENTS)
    msg['Subject'] = asunto
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_RECIPIENTS, msg.as_string())

        print('📧 Email enviado correctamente')
        return {"status": "success", "message": "Email sent"}
    
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
        return {"status": "error", "message": str(e)}

# --------------------- GENERAR MENSAJE ---------------------
def generate_message_template(data):
    template = "🚨 *Alerta en Grafana* 🚨\n\n📌 *Información recibida:*\n"
    for key, value in data.items():
        template += f"- *{key.capitalize().replace('_', ' ')}:* {value}\n"
    template += "\n⚠️ *Por favor, revisar la información correspondiente.*"
    return template

# --------------------- ENDPOINTS ---------------------
@app.route('/webhookWhatsApp', methods=['POST'])
def webhook_whatsapp():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        message = generate_message_template(data)
        response = send_whatsapp_message(message, TO_PHONE_NUMBERS)

        return jsonify({"message": "Mensajes enviados", "response": response}), 200

    return jsonify({"error": "Invalid request"}), 400

@app.route('/webhookCorreo', methods=['POST'])
def webhook_correo():
    print("EMAIL_USER:", EMAIL_USER)
    print("EMAIL_PASS:", EMAIL_PASS)
    print("EMAIL_RECIPIENTS:", EMAIL_RECIPIENTS)

    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        message = generate_message_template(data)
        response = send_email_message(message)

        return jsonify({"message": "Correo enviado", "response": response}), 200

    return jsonify({"error": "Invalid request","EMAIL_USER": EMAIL_USER, "EMAIL_PASS": EMAIL_PASS,"EMAIL_RECIPIENTS": EMAIL_RECIPIENTS}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8000)))
