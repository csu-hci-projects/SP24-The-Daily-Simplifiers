import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
import tkinter as tk

# Initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# Allow the camera to warm up
time.sleep(0.1)

# GPIO setup
LED_PIN = 24
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)  # LED off initially

# Timer variables
led_on_time_start = 0
total_led_on_time = 0
program_start_time = time.time()

# GUI setup
root = tk.Tk()
root.title("LED Status Dashboard")

total_time_label = tk.Label(root, text="Total Time: 0s")
total_time_label.pack()

led_on_label = tk.Label(root, text="LED On Time: 0s")
led_on_label.pack()

led_off_label = tk.Label(root, text="LED Off Time: 0s")
led_off_label.pack()

def update_dashboard():
    current_time = time.time()
    total_time = current_time - program_start_time
    total_time_label.config(text=f"Total Time: {total_time:.2f}s")
    
    if led_on_time_start != 0:
        led_on_time = total_led_on_time + (current_time - led_on_time_start)
    else:
        led_on_time = total_led_on_time
    led_on_label.config(text=f"LED On Time: {led_on_time:.2f}s")
    
    led_off_time = total_time - led_on_time
    led_off_label.config(text=f"LED Off Time: {led_off_time:.2f}s")
    
    root.update()

# Function to detect hand by skin color in the frame
def detect_hand(frame):
    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Define skin color range in HSV
    lower_skin = np.array([0, 48, 80], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    # Threshold the HSV image to get only skin colors
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # Check if hand is detected
    if cv2.countNonZero(mask) > 10000:
        return True
    else:
        return False

# Variables to track the state of the LED and debounce timing
led_state = False
last_hand_detected = False
last_toggle_time = time.time()
debounce_delay = 1.0  # 1 second debounce delay

# Main loop with GUI update
try:
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array

        # Detect hand in the image
        hand_present = detect_hand(image)
        current_time = time.time()

        # Toggle LED state if hand is detected with debounce
        if hand_present != last_hand_detected and (current_time - last_toggle_time) > debounce_delay:
            last_toggle_time = current_time
            led_state = not led_state
            GPIO.output(LED_PIN, led_state)

            # Start or stop timing the LED on-time
            if led_state:
                led_on_time_start = current_time  # Start timing when LED is turned on
            elif led_on_time_start != 0:
                total_led_on_time += current_time - led_on_time_start  # Add the duration the LED was on
                led_on_time_start = 0

        last_hand_detected = hand_present

        # Update GUI
        update_dashboard()

        # Clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        # Break out of the loop by pressing 'q' on a connected keyboard (requires display and keyboard)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Clean up
    GPIO.cleanup()
    camera.close()
    root.destroy()

# Run the GUI
root.mainloop()