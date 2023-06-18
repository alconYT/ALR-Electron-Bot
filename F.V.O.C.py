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

        cv2.imshow('Face Recognition', frame)

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
    elif 'recognize this house' in command:
        engine.say("Starting house recognition. Please guide me through the house.")
        engine.runAndWait()
        recognize_house()
    else:
        engine.say("Command not recognized.")
        engine.runAndWait()

# Mapping logic
def create_map():
    engine.say("Creating a map of the house.")
    engine.runAndWait()
    # Implement mapping logic here
    # Update the map_data dictionary with room names and coordinates

# Function for house recognition
def recognize_house():
    while True:
        ret, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Perform house recognition using distance sensors or mapping cameras
        # Update map_data dictionary with room names and coordinates as new rooms are detected
        cv2.imshow('House Recognition', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    create_map()

# Function to display the house map
def display_house_map():
    map_image = np.zeros((500, 500, 3), np.uint8)  # Create a blank image
    for room, (x, y) in map_data.items():
        cv2.putText(map_image, room, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("House Map", map_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Main function
def main():
    engine = pyttsx3.init()

    # Start virtual assistant
    def start_assistant():
        while True:
            r = sr.Recognizer()
            with sr.Microphone() as source:
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

    start_assistant()

if __name__ == "__main__":
    main()
