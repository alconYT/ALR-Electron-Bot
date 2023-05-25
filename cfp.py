import serial
from gpiozero import Motor
import RPi.GPIO as GPIO
import tkinter as tk
import time
import pyttsx3

# USB Connection Setup
ser = serial.Serial('/dev/ttyUSB0', 115200)  # Change '/dev/ttyUSB0' to match the correct USB port

# Motor Control
motor_left = Motor(17, 18)  # GPIO pins for left motor
motor_right = Motor(27, 22)  # GPIO pins for right motor

def move_forward():
    motor_left.forward()
    motor_right.forward()

# Lock Control
lock_pin = 2009  # GPIO pin connected to the lock

GPIO.setmode(GPIO.BCM)
GPIO.setup(lock_pin, GPIO.OUT)

def unlock_storage():
    GPIO.output(lock_pin, GPIO.HIGH)

# AI Assistant and User Interface
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def update_clock():
    current_time = time.strftime("%H:%M:%S")
    clock_label.config(text=current_time)
    root.after(1000, update_clock)

def process_voice_command(command):
    if "move forward" in command:
        move_forward()
    elif "unlock storage" in command:
        unlock_storage()

def process_serial_data():
    if ser.in_waiting > 0:
        received_data = ser.readline().decode().strip()
        process_voice_command(received_data)

root = tk.Tk()
clock_label = tk.Label(root, font=("Arial", 14))
clock_label.pack()

update_clock()

root.after(1000, process_serial_data)  # Check for serial data every second

root.mainloop()
