import requests
import json

webhook_url = 'http://localhost:5000/webhook'

data = {
    'alertname': 'Test Alert',
    'panel': 'Test Panel',
    'severity': 'critical',
}

r = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})