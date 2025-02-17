import network
import requests
import json

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
