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

# Start the producer and consumer in separate threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()
