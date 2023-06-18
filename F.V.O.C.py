import RPi.GPIO as GPIO
import cv2
import numpy as np
import pyttsx3
import time
import subprocess
import speech_recognition as sr
import pyttsx3
import openai
import datetime
import psutil
import webbrowser
import tkinter as tk

# Set GPIO pin numbers
motor1_pin1 = 11
motor1_pin2 = 13
motor1_enable_pin = 15
motor2_pin1 = 16
motor2_pin2 = 18
motor2_enable_pin = 22

# Initialize GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor1_pin1, GPIO.OUT)
GPIO.setup(motor1_pin2, GPIO.OUT)
GPIO.setup(motor1_enable_pin, GPIO.OUT)
GPIO.setup(motor2_pin1, GPIO.OUT)
GPIO.setup(motor2_pin2, GPIO.OUT)
GPIO.setup(motor2_enable_pin, GPIO.OUT)

# Initialize camera and face detection
camera = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Initialize mapping variables
map_data = {}  # Dictionary to store room names and coordinates

# Initialize GUI
root = tk.Tk()
root.title("Personal Robot")

# Create a canvas for displaying the camera feed
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Create labels for battery life, time, and connectivity
battery_label = tk.Label(root, text="Battery: 100%", font=("Helvetica", 14))
battery_label.pack()

time_label = tk.Label(root, text="Time: ", font=("Helvetica", 14))
time_label.pack()

connectivity_label = tk.Label(root, text="Connectivity: Connected to Raspberry Pi", font=("Helvetica", 14))
connectivity_label.pack()

# Function to control the motors
def move_motors(direction):
    if direction == 'forward':
        GPIO.output(motor1_pin1, GPIO.HIGH)
        GPIO.output(motor1_pin2, GPIO.LOW)
        GPIO.output(motor1_enable_pin, GPIO.HIGH)
        GPIO.output(motor2_pin1, GPIO.HIGH)
        GPIO.output(motor2_pin2, GPIO.LOW)
        GPIO.output(motor2_enable_pin, GPIO.HIGH)
    elif direction == 'stop':
        GPIO.output(motor1_enable_pin, GPIO.LOW)
        GPIO.output(motor2_enable_pin, GPIO.LOW)
    # Add other motor movements as needed

# Function for person recognition
def recognize_person():
    while True:
        ret, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            # Face detected, start following
            move_motors('forward')
        else:
            # No face detected, stop
            move_motors('stop')

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Convert the OpenCV image to a Tkinter-compatible image
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)

        # Update the canvas with the new image
        canvas.create_image(0, 0, anchor=tk.NW, image=img)

        root.update()

        if cv2.waitKey(1) == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

# Function to process virtual assistant commands
def process_command(command):
    if 'follow' in command:
        engine.say("Starting person recognition.")
        engine.runAndWait()
        recognize_person()
    elif 'stop' in command:
        engine.say("Stopping person recognition.")
        engine.runAndWait()
        move_motors('stop')
    else:
        engine.say("Command not recognized.")
        engine.runAndWait()

# Function to recognize the house and memorize rooms
def recognize_house():
    # Implement house recognition using distance sensors or mapping cameras
    # Update the map_data dictionary with room names and coordinates as new rooms are detected
    pass

# Function to display the house map
def display_house_map():
    # Create a blank image
    map_image = np.zeros((500, 500, 3), np.uint8)

    # Draw room labels on the map
    for room, (x, y) in map_data.items():
        cv2.putText(map_image, room, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Display the map in a new window
    cv2.imshow("House Map", map_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Main function
def main():
    global engine

    engine = pyttsx3.init()

    # Start virtual assistant
    def start_assistant():
        while True:
            r = sr.Recognizer()
            with sr.Microphone(device_index=1) as source:  # Set the correct device index for the USB microphone
                print("Listening...")
                audio = r.listen(source)

            try:
                print("Recognizing...")
                command = r.recognize_google(audio)
                print(f"Command: {command}")
                process_command(command)
            except Exception as e:
                print("Sorry, I didn't understand that.")
                print(e)

    # Create buttons for recognizing the house and displaying the house map
    recognize_button = tk.Button(root, text="Recognize This House", command=recognize_house)
    recognize_button.pack()

    display_map_button = tk.Button(root, text="Display House Map", command=display_house_map)
    display_map_button.pack()

    start_assistant()

    root.mainloop()

if __name__ == "__main__":
    main()
