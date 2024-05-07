import numpy as np
import sounddevice as sd
from gpiozero import LED
import time
import tkinter as tk

# Constants
LED_PIN = 24        # GPIO pin connected to the LED
THRESHOLD = 0.05    # Adjust this to catch claps without catching background noise
SAMPLE_RATE = 44100 # Sample rate for microphone
BLOCK_SIZE = 1024   # Block size for stream callback

# Setup
led = LED(LED_PIN)
led_state = False
led_on_time_start = None
total_led_on_time = 0
program_start_time = time.time()

# Setup the GUI
root = tk.Tk()
root.title("LED Dashboard")

total_time_label = tk.Label(root, text="Total Running Time: 0.0 s")
total_time_label.pack()

led_on_time_label = tk.Label(root, text="Total LED ON Time: 0.0 s")
led_on_time_label.pack()

led_off_time_label = tk.Label(root, text="Total LED OFF Time: 0.0 s")
led_off_time_label.pack()

def update_gui():
    current_time = time.time()
    total_running_time = current_time - program_start_time
    total_time_label.config(text=f"Total Running Time: {total_running_time:.2f} s")
   
    led_off_time = total_running_time - total_led_on_time
    led_off_time_label.config(text=f"Total LED OFF Time: {led_off_time:.2f} s")
    led_on_time_label.config(text=f"Total LED ON Time: {total_led_on_time:.2f} s")
   
    root.update()

def audio_callback(indata, frames, time_info, status):
    global led_state, led_on_time_start, total_led_on_time
    current_time = time_info.inputBufferAdcTime
    rms = np.sqrt(np.mean(indata**2))

    if rms > THRESHOLD:
        led_state = not led_state
        led.value = led_state

        if led_state:
            led_on_time_start = time.time()
        else:
            if led_on_time_start is not None:
                total_led_on_time += time.time() - led_on_time_start
                led_on_time_start = None

def main():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE):
        while True:
            time.sleep(0.1)
            update_gui()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if led_state and led_on_time_start is not None:
            total_led_on_time += time.time() - led_on_time_start
        led.off()
        root.destroy()
