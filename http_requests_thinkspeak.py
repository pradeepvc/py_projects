import requests
import xml.etree.ElementTree as ET

temp = requests.get("https://api.thingspeak.com/apps/thinghttp/send_request?api_key=A9J1L9Y3RUH067D7")

print(temp.text)
exit()
url = "https://api.thingspeak.com/apps/thinghttp/send_request?api_key=N2KLBUQU2DPBNSUT"

response = requests.get(url)

root = ET.fromstring(response.text)
# Extract temperature and weather condition from the XML
temperature = root.find(".//temp_f").text + "°"
condition = root.find(".//condition").text
print(temperature, "and", condition)
# Example: print all elements and their text
#for elem in root.iter():
#    print(elem.tag, elem.text)


