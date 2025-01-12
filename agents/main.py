import threading
import queue
import sys
sys.path.append('../')
from shared_queue import shared_queue 
from LLMCompiler import chain
from langchain_core.messages import HumanMessage

import speech_recognition as sr
import pyaudio
import time


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
                    shared_queue.put(text)
                except sr.UnknownValueError:
                    print("Sorry, I could not understand the audio.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
        except KeyboardInterrupt:
            print("\nStopping listening.")
            return


def consumer():
    while True:
        try:
            # print("#"*50)
            # print(f"Queue size: {shared_queue.qsize()}")
            

            recognized_text = shared_queue.get(timeout=5)  # Get the recognized speech text
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
            print(step["join"]["messages"][-1].content)

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
