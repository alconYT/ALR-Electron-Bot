import speech_recognition as sr
import pyttsx3
import openai
import datetime
import psutil
import webbrowser
import tkinter as tk
import subprocess
import RPi.GPIO as GPIO
import cv2
import numpy as np
import time

# Configure OpenAI Chat GPT
openai.api_key = 'YOUR_OPENAI_API_KEY'
assistant_model = 'gpt-3.5-turbo'

# Set up speech recognition with Adafruit Silicon MEMS microphone
r = sr.Recognizer()
mic = sr.Microphone(device_index=0)  # Replace 0 with the correct device index for your microphone

# Set up text-to-speech
engine = pyttsx3.init()

# Set up tkinter GUI
root = tk.Tk()
root.geometry("400x300")
root.title("Electron Assistant")

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
    else:
        engine.say("Sorry, I couldn't understand that command.")
        engine.runAndWait()

# Function to get internal temperature of the Raspberry Pi
def get_temperature():
    result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temperature = result.stdout.decode().split('=')[1].split("'")[0]
    return temperature

# Function to get battery level of the Raspberry Pi
def get_battery_level():
    result = subprocess.run(['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0'], capture_output=True)
    output = result.stdout.decode()
    percentage = None
    for line in output.split('\n'):
        if 'percentage' in line:
            percentage = line.split(':')[1].strip()
            break
    return percentage

# Function to display the information on the Samsung Galaxy Tab S2
def display_info():
    # Update the time
    current_time = time.strftime('%H:%M:%S')
    subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.TIME_SET', '--es', 'time', current_time])

    # Update the internal temperature
    temperature = get_temperature()
    subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'com.example.robot.SET_TEMPERATURE', '--es', 'temperature', temperature])

    # Update the battery level
    battery_level = get_battery_level()
    subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'com.example.robot.SET_BATTERY_LEVEL', '--es', 'battery_level', battery_level])

    # Display the voice assistant options
    voice_assistant_options = ['Google Assistant', 'Amazon Alexa', 'Microsoft Cortana']
    for index, option in enumerate(voice_assistant_options):
        subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'com.example.robot.SET_VOICE_OPTION', '--ei', 'option_index', str(index), '--es', 'option_name', option])

    # Sleep for a while to allow the Samsung Galaxy Tab S2 to process the updates
    time.sleep(2)

# Function to set the background image of the Samsung Galaxy Tab S2
def set_background_image(image_path):
    subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'com.example.robot.SET_BACKGROUND_IMAGE', '--es', 'image_path', image_path])

# Start the voice assistant
def start_assistant():
    command = get_voice_command()
    if 'electron' in command:
        if 'follow me' in command:
            speak("Starting follow me functionality.")
            subprocess.Popen(['python', 'follow_me_code.py'])  # Replace 'follow_me_code.py' with your actual code file
        else:
            speak("How can I assist you?")
            while True:
                user_input = get_voice_command()
                if 'stop' in user_input:
                    break
                
                if 'wifi' in user_input:
                    # Check internet connectivity
                    has_internet = True  # Replace with your internet connectivity check logic
                    
                    if has_internet:
                        # Pass user input to OpenAI Chat GPT
                        prompt = f"User: {user_input}\nAssistant:"
                        response = generate_chat_response(prompt)
                        
                        # Output the response
                        print(response)
                        show_popup(response)
                        speak(response)
                    else:
                        if 'time' in user_input:
                            current_time = get_current_time()
                            print(f"The current time is {current_time}")
                            show_popup(f"The current time is {current_time}")
                            speak(f"The current time is {current_time}")
                        elif 'date' in user_input:
                            current_date = get_current_date()
                            print(f"The current date is {current_date}")
                            show_popup(f"The current date is {current_date}")
                            speak(f"The current date is {current_date}")
                        elif 'battery' in user_input:
                            battery_life = get_battery_life()
                            print(f"The current battery life is {battery_life}%")
                            show_popup(f"The current battery life is {battery_life}%")
                            speak(f"The current battery life is {battery_life}%")
                        else:
                            query = user_input
                            search_on_browser(query)
                            show_popup(f"Performing a search for '{query}'")
                else:
                    show_popup("I'm sorry, I can only provide limited functionality without an internet connection.")
                    speak("I'm sorry, I can only provide limited functionality without an internet connection.")

# Continuously update and display the information
while True:
    set_background_image('/path/to/your/image.jpg')  # Set the path to your desired background image
    display_info()
    start_assistant()
    time.sleep(1)

root.mainloop()
"
