from machine import Pin, I2C
import dht
import ssd1306
import time

# Task 1: Displaying Temperature & Humidity on OLED
# - We use a DHT11 sensor to measure temperature & humidity.
# - The data is displayed on an SSD1306 OLED screen.

# Initialize DHT sensor (DHT11)
dht_sensor = dht.DHT11(Pin(16))  # DHT sensor on GPIO16

# Initialize OLED display (128x64 pixels)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # I2C on GPIO22 (SCL), GPIO21 (SDA)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Task 4: Why Do We Use Interrupts?
# - Interrupts allow the processor to perform other tasks while waiting for an event.
# - Instead of constantly checking (polling) for button presses or sensor updates, 
#   the microcontroller can continue other work and respond only when needed.
# - This reduces CPU load and makes the system more efficient.

# Button with Interrupt (GPIO 14)
button = Pin(14, Pin.IN, Pin.PULL_UP)  # Pull-up resistor enabled

# Interrupt Handler Function
def button_pressed(pin):
    global interrupted
    interrupted = True

# Attach Interrupt to Button (Triggered on Press)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

interrupted = False  # Interrupt Flag

while True:
    try:
        if interrupted:
            print("Button Pressed! Interrupt Triggered!")
            interrupted = False  # Reset flag

        # Task 2: Running the Code Without Interrupt
        # - If we remove interrupts, the CPU has to keep checking the button state in a loop.
        # - This wastes processing power and slows down performance.
        # - Interrupts solve this by allowing the CPU to work on other tasks until the event occurs.

        # Read DHT sensor
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()

        # Display Temperature & Humidity on OLED
        oled.fill(0)  # Clear screen
        oled.text("Temp: {} C".format(temp), 10, 20)
        oled.text("Humidity: {}%".format(hum), 10, 40)
        oled.show()

        print("Temp:", temp, "C | Humidity:", hum, "%")  # Print to console
        time.sleep(2)  # Delay for next reading

    except OSError as e:
        print("Sensor Error:", e)

# Task 3: Understanding Debounce Issue
# - A debounce issue occurs when a mechanical button bounces, causing multiple unwanted signals.
# - Debounce can be problematic in embedded systems where a single press should register only once.
# - If a button press is detected multiple times quickly, it can lead to incorrect behavior.
# - Debounce can be solved in software using delays or debounce libraries.
