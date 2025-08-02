import requests
import sys
import os

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}", file=sys.stderr)
        return False
    return True

if __name__ == "__main__":
    token = "8255069137:AAHPwP4dXQr3aOxAZiMKVWRhT0a4H_z_daM"
    chat_id = "YOUR_TELEGRAM_CHAT_ID"

    if len(sys.argv) != 2:
        print("Usage: python telegrambot.py <MESSAGE>", file=sys.stderr)
        sys.exit(1)

    message = sys.argv[1]

    success = send_telegram_message(token, chat_id, message)
    if success:
        print("Message sent successfully.")
    else:
        print("Failed to send message.", file=sys.stderr)
