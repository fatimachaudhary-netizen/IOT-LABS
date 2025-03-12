import network
import socket
import dht
import machine
import ssd1306
from neopixel import NeoPixel

# WiFi Configuration
SSID = "StormFiber-4cd8"
PASSWORD = "03326552418"

# Initialize WiFi in Station Mode
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

# Add timeout to Wi-Fi connection to avoid infinite loop
import time
timeout = 10
while not wifi.isconnected() and timeout > 0:
    print("Connecting to WiFi...")
    time.sleep(1)
    timeout -= 1

if wifi.isconnected():
    print("Connected! IP Address:", wifi.ifconfig()[0])
else:
    print("Failed to connect to WiFi")

# Initialize DHT11 Sensor
dht_pin = machine.Pin(4)  # GPIO4
dht_sensor = dht.DHT11(dht_pin)

# Initialize OLED Display (SSD1306)
try:
    i2c = machine.SoftI2C(scl=machine.Pin(9), sda=machine.Pin(8))  # Correct I2C pins for ESP32
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
except OSError as e:
    print("I2C Error:", e)

# Initialize RGB LED (Built-in NeoPixel)
rgb_pin = machine.Pin(48, machine.Pin.OUT)
rgb_led = NeoPixel(rgb_pin, 1)  # Only 1 LED on ESP32

# Function to Set RGB Color
def set_rgb_color(r, g, b):
    rgb_led[0] = (r, g, b)
    rgb_led.write()

# Function to Read Temperature & Humidity
def get_sensor_data():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        return temp, hum
    except OSError as e:
        print("DHT11 Sensor Error:", e)
        return "N/A", "N/A"

# Function to Update OLED Display
def update_oled(temp, hum, r, g, b):
    try:
        oled.fill(0)
        oled.text("Temp: {} C".format(temp), 0, 0)
        oled.text("Humidity: {}%".format(hum), 0, 10)
        oled.text("RGB: R{} G{} B{}".format(r, g, b), 0, 30)
        oled.show()
    except Exception as e:
        print("OLED Display Error:", e)

# HTML Web Page
def generate_webpage(temp, hum):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Web Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; background: #2a5298; color: white; }}
            .card {{ background: rgba(255, 255, 255, 0.2); padding: 20px; border-radius: 15px; }}
            h1 {{ font-size: 28px; }}
            input {{ padding: 12px; width: 80px; margin: 5px; }}
            button {{ padding: 12px 20px; background: #ff9800; color: white; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>ESP32 RGB LED & Sensor Web Server</h1>
        <div class="card">
            <h2>Temperature: {temp}°C</h2>
            <h2>Humidity: {hum}%</h2>
        </div>
        <div class="card">
            <h3>Set RGB Color</h3>
            <form action="/" method="GET">
                <input type="number" name="r" placeholder="Red (0-255)" min="0" max="255">
                <input type="number" name="g" placeholder="Green (0-255)" min="0" max="255">
                <input type="number" name="b" placeholder="Blue (0-255)" min="0" max="255">
                <br><br>
                <button type="submit">Set Color</button>
            </form>
        </div>
    </body>
    </html>
    """

# Start Web Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 80))
server.listen(5)

print("Web Server Started! Access it via browser.")

while True:
    conn, addr = server.accept()
    print("Client connected from", addr)
    
    request = conn.recv(1024).decode()

    # Parse RGB Values
    r, g, b = 0, 0, 0
    if "GET /?" in request:
        try:
            params = request.split(" ")[1].split("?")[1].split("&")
            r = int(params[0].split("=")[1])
            g = int(params[1].split("=")[1])
            b = int(params[2].split("=")[1])
            set_rgb_color(r, g, b)
        except:
            pass

    # Get Sensor Data
    temp, hum = get_sensor_data()

    # Update OLED Display
    update_oled(temp, hum, r, g, b)

    # Send Webpage Response
    response = generate_webpage(temp, hum)
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response)
    conn.close()
