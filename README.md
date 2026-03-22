# Weather Poet 🌦️📜

Weather Poet is a charming IoT project that transforms real-time weather data into atmospheric poetry, displayed on a beautiful 3-color e-Ink screen.

[Watch the video](https://www.youtube.com/watch?v=61_UXqVG5D0&list=PLIUz3-TvQRfU-pb-r6WZ-icGGzmVGv1Sr&index=4)

![Weather Poet Demo](pico/demo_ui/weather_poet.jpg)

## Features

- **Generative AI Poetry**: Uses Google Gemini 2.0 Flash (with Genkit) to write poems based on current temperature, wind, and sky conditions.
- **e-Ink Display**: Low-power, high-contrast 4.2" Waveshare display (Black/White/Red).
- **Multiple UI Styles**:
  - **Book**: Elegant quote-style layout with a bold red drop cap and decorative frames.
  - **Broadsheet**: A classic newspaper aesthetic focusing on location and date.
  - **Modern**: Sleek layout with weather stats and clean typography.
  - **Minimalist**: Focuses purely on the text.
- **Hardware Integration**: Trigger new poem fetches or cycle through UI styles using physical buttons.
- **Battery Efficient**: Uses MicroPython and deep sleep optimization for long-lasting performance.

## Hardware Requirements

- **Microcontroller**: Raspberry Pi Pico W
- **Display**: [Waveshare 4.2inch e-Paper Module (B)](https://www.waveshare.com/wiki/Pico-ePaper-4.2-B)
- **Buttons**: Two momentary push buttons (connected to GPIO 15 and 17)

## Project Structure

```text
├── firebase/               # Firebase Cloud Functions & Genkit setup
│   └── functions/          # Genkit poetry generation logic (TypeScript)
└── pico/                   # MicroPython code for Raspberry Pi Pico W
    ├── client.py           # Main application logic & API client
    ├── ui_styles.py        # UI rendering engine for different styles
    ├── epd4in2b_lib.py     # Waveshare e-Paper driver
    ├── writer.py           # Font rendering utility
    └── secrets.py.example  # Template for your credentials
```

## Setup Instructions

### 1. Firebase Backend
The backend uses **Firebase Genkit** to handle AI generation and weather API calls.

1. Navigate to `firebase/functions/`.
2. Install dependencies: `npm install`.
3. Set up your Firebase Secrets:
   - `firebase functions:secrets:set GOOGLE_GENAI_API_KEY`
   - `firebase functions:secrets:set WEATHER_API_KEY` (from [WeatherAPI](https://www.weatherapi.com/))
4. Deploy: `firebase deploy --only functions`.

### 2. Pico W Configuration
1. Flash your Pico W with the latest **MicroPython** firmware.
2. Copy all files from the `pico/` directory to your Pico.
3. Rename `secrets.py.example` to `secrets.py` and fill in your details:
   ```python
   WIFI_SSID = "Your_WiFi_Name"
   WIFI_PASSWORD = "Your_WiFi_Password"
   FIREBASE_URL = "https://your-cloud-function-url.run.app"
   FIREBASE_API_KEY = "Your_Firebase_Web_API_Key"
   POET_EMAIL = "user@example.com"
   POET_PASSWORD = "your_secure_password"
   ```

## Usage
- **Initial Boot**: On startup, the device connects to WiFi and fetches the current weather poem.
- **Button A**: Manually trigger a fresh weather update and poem generation.
- **Button B**: Instantly cycle through the available UI styles (Modern, Broadsheet, Minimalist, Book) using cached data.
