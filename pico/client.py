import network
import requests
import json
import time
import gc
from machine import Pin
import utime

from epd4in2b_lib import EPD_4in2_B
import secrets
from ui_styles import styles_list

current_style_idx = 0
cached_poem_data = None

BUTTON_A_PIN = 15
BUTTON_B_PIN = 17
DEBOUNCE_DELAY_MS = 300
last_button_event_time = 0

needs_fetch_a = False
needs_style_b = False

def button_a_handler(pin):
    global last_button_event_time, needs_fetch_a
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_button_event_time) > DEBOUNCE_DELAY_MS:
        last_button_event_time = current_time
        print("Button A released! Requesting new fetch.")
        needs_fetch_a = True

def button_b_handler(pin):
    global last_button_event_time, current_style_idx, needs_style_b
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_button_event_time) > DEBOUNCE_DELAY_MS:
        last_button_event_time = current_time
        current_style_idx = (current_style_idx + 1) % len(styles_list)
        print(f"Button B released! Switching style to {current_style_idx}.")
        needs_style_b = True

def update_screen(data):
    if not data:
        print("No data to display")
        return

    epd = EPD_4in2_B()
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0xff)

    print(f"Using style index: {current_style_idx}")
    styles_list[current_style_idx](epd, data)

    epd.EPD_4IN2B_Display(epd.buffer_black, epd.buffer_red)
    epd.Sleep()


# --- Network Setup ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    
    print("Connecting to WiFi...", end="")
    max_wait = 15
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print(".", end="")
        time.sleep(1)
        
    print()
    if wlan.status() != 3:
        raise RuntimeError("Network connection failed")
    else:
        print("Connected! IP:", wlan.ifconfig()[0])

# --- API Calls ---
def get_auth_token(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={secrets.FIREBASE_API_KEY}"
    auth_data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = None
    try:
        response = requests.post(url, json=auth_data)
        auth_response_data = response.json()
        print("Auth Response status:", response.status_code)
        
        if 'idToken' in auth_response_data:
            return auth_response_data['idToken']
        else:
            print("Authentication failed:", auth_response_data)
            return None
    except Exception as e:
        print("Error during authentication:", e)
        return None
    finally:
        # CRITICAL in MicroPython: Always close the response to free sockets/memory!
        if response is not None:
            response.close()
        gc.collect()

def get_weather_poem(token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "data": {
            "location": "Waterloo,Canada",
            "tone": ""
        }
    }
    
    response = None
    try:
        response = requests.post(secrets.FIREBASE_URL, headers=headers, json=data)
        print("Poem API Status Code:", response.status_code)
        
        poem_data = response.json()
        print("JSON Response:", poem_data)
        return poem_data
    except Exception as e:
        print("Error fetching poem:", e)
        return None
    finally:
        if response is not None:
            response.close()
        gc.collect()

def fetch_and_display():
    global cached_poem_data
    print("Fetching new poem data...")
    token = get_auth_token(secrets.POET_EMAIL, secrets.POET_PASSWORD)
    if token:
        poem_response = get_weather_poem(token)
        if poem_response:
            result_data = poem_response.get("result", poem_response.get("data", poem_response))
            cached_poem_data = result_data
            update_screen(cached_poem_data)
        else:
            print("No poem response received.")
    else:
        print("Failed to get auth token.")

# --- Main Execution ---
if __name__ == "__main__":
    connect_wifi()
    
    button_a = Pin(BUTTON_A_PIN, Pin.IN, Pin.PULL_UP)
    button_a.irq(trigger=Pin.IRQ_RISING, handler=button_a_handler)

    button_b = Pin(BUTTON_B_PIN, Pin.IN, Pin.PULL_UP)
    button_b.irq(trigger=Pin.IRQ_RISING, handler=button_b_handler)
    
    # Initial fetch
    fetch_and_display()

    print("Main loop running. Press buttons to interact...")
    while True:
        if needs_fetch_a:
            needs_fetch_a = False
            fetch_and_display()
            
        if needs_style_b:
            needs_style_b = False
            if cached_poem_data is not None:
                print("Updating style with cached data...")
                update_screen(cached_poem_data)
            else:
                print("No cached data. Fetching new data before style update...")
                fetch_and_display()
                
        utime.sleep(0.1)


