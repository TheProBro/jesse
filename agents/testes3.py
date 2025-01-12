import threading
import queue
import sys
sys.path.append('../')
import shared_queue1

from LLMCompiler import chain
from langchain_core.messages import HumanMessage

import speech_recognition as sr
import pyaudio
import time

from gtts import gTTS
import pygame
import os


import face_recognition
import cv2
import numpy as np
import os
import json

# import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Path to save user profiles
USER_DATA_PATH = "user_profiles.json"

# Load user profiles from a JSON file
def load_user_profiles():
    if os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, "r") as f:
            return json.load(f)
    return {}

# Save user profiles to a JSON file
def save_user_profiles(profiles):
    with open(USER_DATA_PATH, "w") as f:
        json.dump(profiles, f, indent=4)

# Add a new user profile
def add_user_profile(name, encoding):
    profiles = load_user_profiles()
    profiles[name] = encoding.tolist()
    save_user_profiles(profiles)
    print(f"User {name} added successfully.")

# Authenticate a user based on face recognition
def authenticate_user(frame, known_face_encodings, known_face_names):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            return known_face_names[best_match_index]
    return None

# Capture a face and encode it for a new user
def capture_user_face(name):
    cap = cv2.VideoCapture(0)
    print("Capturing face. Please look at the camera.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):  # Press 'c' to capture
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            if len(face_locations) == 1:
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                add_user_profile(name, face_encoding)
                break
            else:
                print("No face or multiple faces detected. Try again.")
        elif key == ord("q"):  # Press 'q' to quit
            break
    cap.release()
    cv2.destroyAllWindows()



def speech_to_text(text):
    # Text you want to convert to speech
    # text = "Close chrome"

    # Create a gTTS object
    tts = gTTS(text=text, lang='en')

    # Save the generated speech to an audio file
    audio_file = "test_speech.mp3"
    tts.save(audio_file)

    # Initialize pygame mixer to play the audio
    pygame.mixer.init()

    # Load and play the audio file
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():  # Check if audio is still playing
        pygame.time.Clock().tick(10)

    # Optionally, remove the audio file after playback
    os.remove(audio_file)



def producer():
    recognizer = sr.Recognizer()
    print("Listening for audio (press Ctrl+C to stop)...")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        try:
            while True:
                print("Listening...")
                audio_data = recognizer.listen(source, timeout=None)  # Listen indefinitely
                try:
                    print("Recognizing...")
                    text = recognizer.recognize_google(audio_data)
                    print(f"Recognized: {text}")
                    shared_queue1.shared_queue.put(text)
                except sr.UnknownValueError:
                    print("Sorry, I could not understand the audio.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
        except KeyboardInterrupt:
            print("\nStopping listening.")
            return

# def text_to_speech():


def consumer():
    while True:
        try:
            # print("#"*50)
            # print(f"Queue size: {shared_queue1.shared_queue.qsize()}")
            

            recognized_text = shared_queue1.shared_queue.get(timeout=2)  # Get the recognized speech text
            # print("*"*50)
            print("recognized text is: "+recognized_text)

            # Process the text with your main chain code
            for step in chain.stream(
                {
                    "messages": [
                        HumanMessage(content=recognized_text)
                    ]
                }
            ):
                print(step)

            # Print the last part of the result
            speech_to_text(step["join"]["messages"][-1].content)

            print(recognized_text)
        except queue.Empty:
            # Queue is empty, print a message and wait a bit before checking again
            print("Queue is empty. Waiting for new items...")
            time.sleep(1)  # Adjust this to control the delay between retries

        except Exception as e:
            # Catch any other exceptions and log them
            print(f"Error occurred: {e}")
            time.sleep(1)


print("Loading user profiles...")
user_profiles = load_user_profiles()
known_face_names = list(user_profiles.keys())
known_face_encodings = [np.array(enc) for enc in user_profiles.values()]

print("Options:\n1. Add New User\n2. Authenticate User\n3. Exit")
choice = input("Enter your choice: ").strip()

if choice == "1":
    name = input("Enter the name of the new user: ").strip()
    capture_user_face(name)
elif choice == "2":
    print("Starting authentication. Press 'q' to quit.")
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break
        user = authenticate_user(frame, known_face_encodings, known_face_names)
        if user:
            print(f"Authentication Successful! Welcome, {user}.")
            break
        cv2.imshow("Authentication", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
elif choice == "3":
    print("Exiting system.")
else:
    print("Invalid choice. Please try again.")



# Start the producer and consumer in separate threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()
