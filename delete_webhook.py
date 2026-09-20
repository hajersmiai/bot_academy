import requests
import os

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Supprimer le webhook
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
response = requests.get(url)
print(response.json())
