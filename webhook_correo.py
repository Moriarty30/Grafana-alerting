import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",")


def send_email_message(message):
    """
    Envía un correo con el mensaje recibido.
    """
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


def generate_email_template(data):
    """
    Genera una plantilla de mensaje con los datos recibidos de forma dinámica.
    """
    template = "🚨 *Alerta en Grafana* 🚨\n\n📌 *Información recibida:*\n"

    for key, value in data.items():
        template += f"- *{key.capitalize().replace('_', ' ')}:* {value}\n"

    template += "\n⚠️ *Por favor, revisar la información correspondiente.*"
    return template


@app.route('/webhookCorreo', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400

        message = generate_email_template(data)

        response = send_email_message(message)

        return jsonify({"message": "Correo enviado", "response": response}), 200

    return jsonify({"error": "Invalid request"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
