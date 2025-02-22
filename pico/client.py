import network
import requests
import json

from epd4in2b_lib import EPD_4in2_B

def updateScren(text):
    epd = EPD_4in2_B()

    from writer import Writer

    import lbaskerv20 as font
    import esteban20 as font2

    epd.imageblack.fill(0xff)
    epd.imagered.fill(0xff)

    wri = Writer(epd.imageblack, font, True)
    Writer.set_textpos(epd.imageblack, 10, 0)  # verbose = False to suppress console output
    wri.printstring(text, True)

    wri2 = Writer(epd.imageblack, font2, True)
    Writer.set_textpos(epd.imageblack, 100, 0)  # verbose = False to suppress console output
    wri2.printstring("A whisper of snow, a frigid kiss,\nNorthwest winds in chilling bliss.\nSun obscured, a cloudy hold,\nFourteen Fahrenheit, a winter's scold.\n", True)

    epd.EPD_4IN2B_Display(epd.buffer_black, epd.buffer_red)
    epd.Sleep()

ssid = 'ssid'
password = 'password'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

url = "https://firebase-funcitons-url"

data = { "data": {
        "location": "Toronto,Canada",
        "tone": "",
}}

def getWeatherPoem(token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }    
    response = requests.post(url, headers=headers, json=data)
    print("Status Code", response.status_code)
    print("JSON Response ", response.json())

FIREBASE_API_KEY = 'API_KEY'

def get_auth_token(email, password):
    auth_data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    auth_response = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}", json=auth_data)
    auth_response_data = auth_response.json()
    print("Auth Response:", auth_response_data)  # Debugging line
    if 'idToken' in auth_response_data:
        return auth_response_data['idToken']
    else:
        print("Authentication failed:", auth_response_data)
        return None
    
token = get_auth_token("poet@gmail.com", "password")
getWeatherPoem(token)
