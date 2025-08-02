import requests

bot_token = "8255069137:AAHPwP4dXQr3aOxAZiMKVWRhT0a4H_z_daM"  # Replace with your bot token

def get_chat_id(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    data = response.json()
    print(data)

    if data["ok"]:
        try:
            chat_id = data["result"][0]["message"]["chat"]["id"]
            return chat_id
        except (KeyError, IndexError):
            return None
    else:
        return None

chat_id = get_chat_id(bot_token)

if chat_id:
    print(f"Your chat ID is: {chat_id}")
else:
    print("Could not retrieve chat ID.")