import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, jsonify

app = Flask(__name__)


def send_whatsapp_message(message):

    #username = os.getenv("USERNAME")
    #password = os.getenv("PASSWORD")
    #to = os.getenv("TO").split(',')
    username = request.form.get("username")
    password = request.form.get("password")
    to = request.form.get("to").split(',')
    
    asunto = "Alerta Grafana"

    # Crear el mensaje de correo
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = ', '.join(to)
    msg['Subject'] = asunto
    msg.attach(MIMEText(message, 'plain'))

    # Enviar el correo
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, to, msg.as_string())

    print('Email sent')


    return None

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.get_json()

        
        alert_name = data.get("alertname", "Sin nombre")
        panel = data.get("panel", "Desconocido")
        severity = data.get("severity", "Sin severidad")

        
        message = f"🔔 *Alerta Recibida*\n📌 *Panel:* {panel}\n⚠ *Severidad:* {severity}\n🔹 *Alerta:* {alert_name}"
        
        # Enviar mensaje de WhatsApp a todos los números
        #response = send_whatsapp_message(message, TO_PHONE_NUMBERS)

        return jsonify({"message": "Mensajes enviados", "response": response}), 200
    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
