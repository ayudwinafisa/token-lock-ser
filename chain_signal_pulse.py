import requests
import time
import statistics
import smtplib
from email.mime.text import MIMEText

ETHERSCAN_API_KEY = "YourApiKeyHere"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# Telegram настройки
TELEGRAM_BOT_TOKEN = "YourTelegramBotToken"
TELEGRAM_CHAT_ID = "YourChatID"

# Порог аномальной активности (изменяем по ситуации)
ANOMALY_THRESHOLD_MULTIPLIER = 3.5

def get_latest_blocks(n=20):
    latest_blocks = []
    for i in range(n):
        block_number = get_block_number() - i
        tx_count = get_tx_count(block_number)
        latest_blocks.append(tx_count)
        time.sleep(0.2)
    return list(reversed(latest_blocks))

def get_block_number():
    url = f"{ETHERSCAN_API_URL}?module=proxy&action=eth_blockNumber&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    return int(response['result'], 16)

def get_tx_count(block_number):
    url = f"{ETHERSCAN_API_URL}?module=proxy&action=eth_getBlockTransactionCountByNumber&tag={hex(block_number)}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    return int(response['result'], 16)

def detect_anomaly(data):
    if len(data) < 5:
        return False
    mean = statistics.mean(data[:-1])
    stdev = statistics.stdev(data[:-1])
    current = data[-1]
    return current > mean + ANOMALY_THRESHOLD_MULTIPLIER * stdev

def notify(message):
    print("[ALERT]:", message)
    send_telegram_message(message)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, data=payload)
        if not response.ok:
            print("⚠️ Telegram error:", response.text)
    except Exception as e:
        print("⚠️ Telegram exception:", str(e))

def main():
    print("🌀 Monitoring Ethereum blocks for unusual activity...")
    history = get_latest_blocks()
    while True:
        current_block = get_block_number()
        current_tx_count = get_tx_count(current_block)
        history.append(current_tx_count)
        if len(history) > 20:
            history.pop(0)

        if detect_anomaly(history):
            notify(f"🚨 Anomaly detected in block {current_block} with {current_tx_count} transactions")

        time.sleep(15)

if __name__ == "__main__":
    main()
