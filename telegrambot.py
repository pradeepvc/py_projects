import requests, sys, os
from subprocess import run as sprun
import xml.etree.ElementTree as ET

token = "8255069137:AAHPwP4dXQr3aOxAZiMKVWRhT0a4H_z_daM"
chat_id = "-4874857541"


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
    try:
        Blore_temp = requests.get("https://api.thingspeak.com/apps/thinghttp/send_request?api_key=A9J1L9Y3RUH067D7").text
        Blore_temp = ''.join(char for char in Blore_temp if char.isdigit())
        Blore_temp = int((int(Blore_temp) - 32) * 5/9)       #Fahrenheit to Celsius

        gold_price = ET.fromstring(requests.get("https://api.thingspeak.com/apps/thinghttp/send_request?api_key=N2KLBUQU2DPBNSUT").text).text
        pitemp = sprun(["vcgencmd","measure_temp"], capture_output=True, text=True)
        ipv6add = sprun(['bash', '-c', "ip -6 addr show wlan0 scope global | grep -oP 'inet6 \\K[^/]*'"], capture_output=True, text=True)
        message = f"{pitemp.stdout}pi5 address={ipv6add.stdout}Goldpricetoday={gold_price}\u20B9\nBangaloretemp={Blore_temp}"
        #print(message)
        send_telegram_message(token, chat_id, message)

    except Exception as e:
        send_telegram_message(token, chat_id, f"An error occurred: {e}")
