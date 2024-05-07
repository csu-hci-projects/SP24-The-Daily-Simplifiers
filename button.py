# Libraries
import RPi.GPIO as GPIO
import tkinter as tk
from time import sleep, time

# Set warnings off (optional)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Set Button and LED pins
Button = 23
LED_PIN = 24

# Setup Button and LED
GPIO.setup(Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)
flag = 0

# GUI setup
root = tk.Tk()
root.title("Dashboard")

# Labels for displaying times
total_time_label = tk.Label(root, text="Total Time: 0s")
total_time_label.pack()

light_on_time_label = tk.Label(root, text="Light On Time: 0s")
light_on_time_label.pack()

light_off_time_label = tk.Label(root, text="Light Off Time: 0s")
light_off_time_label.pack()

start_time = time()
light_on_time = 0
light_off_time = 0
light_last_changed = start_time

def update_times():
    global light_on_time, light_off_time, light_last_changed, flag
    current_time = time()
    if flag == 1:  # Light is on
        light_on_time += current_time - light_last_changed
    else:  # Light is off
        light_off_time += current_time - light_last_changed
    light_last_changed = current_time
    
    total_time = current_time - start_time
    total_time_label.config(text=f"Total Time: {total_time:.1f}s")
    light_on_time_label.config(text=f"Light On Time: {light_on_time:.1f}s")
    light_off_time_label.config(text=f"Light Off Time: {light_off_time:.1f}s")
    root.after(1000, update_times)  # Update every second

def check_button():
    global flag, light_last_changed
    button_state = GPIO.input(Button)
    if button_state == False:
        sleep(0.2)  # Debounce delay
        flag = 1 - flag
        GPIO.output(LED_PIN, GPIO.HIGH if flag == 1 else GPIO.LOW)
        update_times()  # Update time splits on state change
    root.after(200, check_button)  # Check the button state every 200ms

# Initialize the time update and button check loops
root.after(1000, update_times)
root.after(200, check_button)

root.mainloop()