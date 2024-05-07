import subprocess
import re
import math
import time
import tkinter as tk
import RPi.GPIO as GPIO

# Constants
RSSI_WINDOW_SIZE = 5
LED_PIN = 24  # Set to the GPIO pin connected to the LED

def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # BCM pin-numbering scheme
    GPIO.setup(LED_PIN, GPIO.OUT)  # Set pin as an output pin

def get_rssi(address):
    cmd = ["hcitool", "rssi", address]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        rssi = int(re.search(r'RSSI return value: (-?\d+)', output.decode('utf-8')).group(1))
        return rssi
    except subprocess.CalledProcessError as e:
        print(f"Failed to read RSSI: {e.output.decode('utf-8')}")
        return None

def moving_average(rssi_list):
    if len(rssi_list) >= RSSI_WINDOW_SIZE:
        return sum(rssi_list[-RSSI_WINDOW_SIZE:]) / RSSI_WINDOW_SIZE
    return None

def estimate_distance(rssi, rssi_at_1m=-0.5, env_factor=2.0):
    if rssi is None:
        return None
    distance = math.pow(10, (rssi_at_1m - rssi) / (10 * env_factor))
    return distance

def control_led(distance):
    if distance is not None:
        if distance > 2:
            GPIO.output(LED_PIN, GPIO.LOW)  # Turn LED off
        elif distance < 1:
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
    else:
        print("Distance is None, check RSSI readings.")

def update_gui(start_time, led_on_time, led_off_time, root, led_on_label, led_off_label, total_time_label):
    now = time.time()
    elapsed = now - start_time
    led_on_label.config(text=f"LED On Time: {led_on_time:.2f} seconds")
    led_off_label.config(text=f"LED Off Time: {led_off_time:.2f} seconds")
    total_time_label.config(text=f"Total Running Time: {elapsed:.2f} seconds")
    root.update()

def main():
    global led_on_label, led_off_label, total_time_label, root
    device_address = '90:81:58:1B:6D:7E'
    #90:81:58:1B:6D:7E if using Ben's
    rssi_list = []
    setup_gpio()
    start_time = time.time()
    last_update_time = start_time
    led_on_time = 0
    led_off_time = 0

    # Set up the GUI
    root = tk.Tk()
    root.title("LED Control Dashboard")
    led_on_label = tk.Label(root, text="")
    led_off_label = tk.Label(root, text="")
    total_time_label = tk.Label(root, text="")
    led_on_label.pack()
    led_off_label.pack()
    total_time_label.pack()

    try:
        while True:
            rssi = get_rssi(device_address)
            if rssi is not None:
                rssi_list.append(rssi)
                smoothed_rssi = moving_average(rssi_list)
                if smoothed_rssi is not None:
                    distance = estimate_distance(smoothed_rssi)
                    control_led(distance)
                    print(f"Distance: {distance:.2f} meters, LED {'on' if GPIO.input(LED_PIN) else 'off'}")

            now = time.time()
            led_state = GPIO.input(LED_PIN)
            if led_state:
                led_on_time += now - last_update_time
            else:
                led_off_time += now - last_update_time
            last_update_time = now

            update_gui(start_time, led_on_time, led_off_time, root, led_on_label, led_off_label, total_time_label)
            time.sleep(1)
    finally:
        GPIO.cleanup()  # Clean up GPIO on normal exit

if __name__ == "__main__":
    main()
