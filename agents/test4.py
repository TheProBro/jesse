import threading
import queue

from LLMCompiler2 import chain
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI  # Or any other LLM you are using (e.g., HuggingFace, GPT-3)

import speech_recognition as sr
import pyaudio
import time

from gtts import gTTS
import pygame
import os

import cv2
import dlib
import json
import numpy as np
import os

# File to store user profiles
PROFILE_FILE = 'user_profiles.json'

def answer_question_based_on_history(user, question):
    profiles = load_profiles()

    if user in profiles:
        history = profiles[user]["conversation_history"]

        # Prepare conversation history as context
        history_context = "\n".join(history)

        # Use a template to generate the answer from the model
        prompt_template = """
        You are an AI assistant. You have access to the conversation history below

        Conversation History:
        {history}

        Question: {question}
        Provide a concise and accurate answer based on the above conversation history
        """

        prompt = PromptTemplate(
            input_variables=["history", "question"],
            template=prompt_template
        )

        # Create the LLM chain using the prompt and language model
        chain = LLMChain(llm=llm, prompt=prompt)

        # Generate the answer from the LLM chain
        response = chain.run({"history": history_context, "question": question})

        return response
    else:
        return "I don't have any history for you."


# Load user profiles from the JSON file, if it exists
def load_profiles():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}

# Save user profiles to the JSON file
def save_profiles(profiles):
    with open(PROFILE_FILE, 'w') as file:
        json.dump(profiles, file, indent=4)

# Initialize dlib's face detector and face landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("C:/Users/Alank/Desktop/jesse/agents/shape_predictor_68_face_landmarks.dat")
face_encoder = dlib.face_recognition_model_v1("C:/Users/Alank/Desktop/jesse/agents/dlib_face_recognition_resnet_model_v1.dat")

# Capture and encode face
def capture_and_encode_face():
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = detector(gray)

        if len(faces) > 0:
            for face in faces:
                landmarks = predictor(gray, face)
                encoding = np.array(face_encoder.compute_face_descriptor(frame, landmarks))
                video_capture.release()
                cv2.destroyAllWindows()
                return encoding

        # Display the video feed
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    video_capture.release()
    cv2.destroyAllWindows()

    return None

# Save a new user profile
def save_profile(name, face_encoding):
    profiles = load_profiles()

    # Convert the face encoding into a list (JSON doesn't support numpy arrays directly)
    face_encoding_list = face_encoding.tolist()

    # Add the new user profile
    profiles[name] = {
        "name": name,
        "encoding": face_encoding_list,
        "conversation_history": []
    }

    save_profiles(profiles)
    print(f"User {name} registered successfully!")

# Authenticate a user by comparing face encodings
def authenticate_user():
    profiles = load_profiles()

    # Start capturing video again
    video_capture = cv2.VideoCapture(0)
    while True:
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = detector(gray)

        if len(faces) > 0:
            for face in faces:
                landmarks = predictor(gray, face)

                # Check if landmarks are detected properly
                if landmarks:
                    # Compute face descriptor (encoding)
                    encoding = np.array(face_encoder.compute_face_descriptor(frame, landmarks))

                    # Compare captured face encoding to all stored face encodings
                    matches = []
                    for profile in profiles.values():
                        stored_encoding = np.array(profile['encoding'])
                        # Compute the Euclidean distance between the encodings
                        dist = np.linalg.norm(stored_encoding - encoding)
                        matches.append(dist)

                    name = "Unknown"
                    if matches and min(matches) < 0.6:  # Threshold for similarity
                        min_index = matches.index(min(matches))
                        name = list(profiles.keys())[min_index]

                    print(f"Authenticated as: {name}")
                    return name
                else:
                    print("No landmarks detected. Skipping this face.")

        # Display the video feed
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    video_capture.release()
    cv2.destroyAllWindows()



def speech_to_text(text, user):
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
    try:
        # Optionally, remove the audio file after playback
        os.remove(audio_file)
    except Exception as e:
        print(f"Error occurred: {e}")
        # Save the recognized text (note) into the user's conversation history

    profiles = load_profiles()
    if user in profiles:
        profiles[user]["conversation_history"].append(text)
        save_profiles(profiles)  # Save updated profile with conversation history
        print("Conversation history updated successfully!")

def main():

    print("Face Recognition Authentication System")
    user = ""
    while True:
        print("1. Register New User")
        print("2. Authenticate User")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter your name: ")
            face_encoding = capture_and_encode_face()
            if face_encoding is not None:
                save_profile(name, face_encoding)

        elif choice == '2':
            user = authenticate_user()
            if user:
                break

        elif choice == '3':
            break

        else:
            print("Invalid choice, try again.")

    init_rec = sr.Recognizer()
    print(f"Let's speak {user}!")
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        init_rec.adjust_for_ambient_noise(source)  # Adjust for ambient noise levels
        print("Listening for your speech...")

        # Listen for speech until silence is detected
        audio_data = init_rec.listen(source)

        print("Recognizing your speech...")

        try:
            # Recognize the speech using Google Web Speech API
            text = init_rec.recognize_google(audio_data)
            print("You said: " + text)

        except sr.UnknownValueError:
            print("Sorry, I could not understand your speech.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    try:
        answer = answer_question_based_on_history(user, text)
        print(answer)
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(1)

    try:
        # Process the text with your main chain code
        for step in chain.stream(
            {
                "messages": [
                    HumanMessage(content=text)
                ]
            }
        ):
            print(step)

        if step["join"]["messages"][-1].content:
            # Print the last part of the result
            speech_to_text(step["join"]["messages"][-1].content, user)
        else:
            speech_to_text(f"Thank you for using jesse {user}!", user)

        print(text)
    except queue.Empty:
        # Queue is empty, print a message and wait a bit before checking again
        print("Queue is empty. Waiting for new items...")
        time.sleep(1)  # Adjust this to control the delay between retries

    except Exception as e:
        # Catch any other exceptions and log them
        print(f"Error occurred: {e}")
        time.sleep(1)


if __name__ == '__main__':
    main()
