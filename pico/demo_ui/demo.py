from epd4in2b_driver import EPD_4in2_B
from ui_styles import styles_list

content = "Hello, A whisper of snow, a frigid kiss,\nNorthwest winds in chilling bliss.\nSun obscured, a cloudy hold,\nFourteen Fahrenheit, a winter's scold.\n"

current_style_idx = 0

def updateScren(text):
    epd = EPD_4in2_B()

    epd.imageblack.fill(0xff)
    epd.imagered.fill(0xff)

    # Call current style
    styles_list[current_style_idx](epd, text)

    epd.EPD_4IN2B_Display(epd.buffer_black, epd.buffer_red)
    epd.Sleep()

from machine import Pin
import utime

# Define the GPIO pin for the button.
BUTTON_A_PIN = 15
BUTTON_B_PIN = 17
# A global variable to store the time of the last button event for debouncing
last_button_event_time = 0
DEBOUNCE_DELAY_MS = 300

# Interrupt flags for main-loop execution
needs_update_a = False
needs_update_b = False

def button_a_handler(pin):
    global last_button_event_time, needs_update_a
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_button_event_time) > DEBOUNCE_DELAY_MS:
        last_button_event_time = current_time
        print(f"Button A on pin {BUTTON_A_PIN} released!")
        needs_update_a = True

def button_b_handler(pin):
    global last_button_event_time, current_style_idx, needs_update_b
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_button_event_time) > DEBOUNCE_DELAY_MS:
        last_button_event_time = current_time
        print(f"Button B on pin {BUTTON_B_PIN} released!")
        current_style_idx = (current_style_idx + 1) % len(styles_list)
        needs_update_b = True

# Initialize the button pin with an internal pull-up resistor
# and configure an interrupt for the rising edge (release)
button_a = Pin(BUTTON_A_PIN, Pin.IN, Pin.PULL_UP)
button_a.irq(trigger=Pin.IRQ_RISING, handler=button_a_handler)

button_b = Pin(BUTTON_B_PIN, Pin.IN, Pin.PULL_UP)
button_b.irq(trigger=Pin.IRQ_RISING, handler=button_b_handler)

print("Button detection started. Press and release the button.")

# Main loop to keep the program running
while True:
    if needs_update_a:
        needs_update_a = False
        updateScren(content)
        
    if needs_update_b:
        needs_update_b = False
        updateScren(content)
        
    utime.sleep(0.1)
