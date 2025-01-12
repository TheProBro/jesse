# import sys
# import queue
# import sounddevice as sd
# import vosk
# import json

# # Set the log level to -1 to suppress logs (optional)
# vosk.SetLogLevel(-1)

# # Specify the model path
# model_path = "model"

# # Initialize the Vosk model
# try:
#     model = vosk.Model(model_path)
# except Exception as e:
#     print("Could not initialize the model. Please ensure the model path is correct.")
#     sys.exit(1)

# # Create a queue to hold audio data
# audio_queue = queue.Queue()

# # Define the callback function for the audio stream
# def audio_callback(indata, frames, time, status):
#     if status:
#         print(f"Status: {status}", file=sys.stderr)
#     # Add audio data to the queue
#     audio_queue.put(bytes(indata))

# # Sampling rate should match the model's expected rate (16000 Hz for Vosk models)
# sample_rate = 16000

# # Initialize the recognizer
# recognizer = vosk.KaldiRecognizer(model, sample_rate)

# try:
#     # Start the audio stream
#     with sd.RawInputStream(samplerate=sample_rate, blocksize=8000, dtype='int16',
#                            channels=1, callback=audio_callback):
#         print("Listening... Press Ctrl+C to stop.")
#         while True:
#             # Get data from the audio queue
#             data = audio_queue.get()
#             if recognizer.AcceptWaveform(data):
#                 # Get the final result
#                 result = recognizer.Result()
#                 result_dict = json.loads(result)
#                 text = result_dict.get('text', '')
#                 if text:
#                     print(f"You said: {text}")
#             else:
#                 # Partial result (optional)
#                 # partial_result = recognizer.PartialResult()
#                 # print(partial_result)
#                 # If you want to display partial results, uncomment below
#                 # partial_dict = json.loads(partial_result)
#                 # partial_text = partial_dict.get('partial', '')
#                 # if partial_text:
#                 #     print(f"Partial: {partial_text}")
#                 pass
# except KeyboardInterrupt:
#     print("\nExiting...")
# except Exception as e:
#     print(f"An error occurred: {e}")

#!/usr/bin/env python3

# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`

import argparse
import queue
import sys
import sounddevice as sd
import re
from vosk import Model, KaldiRecognizer
import sys
sys.path.append('../')
import shared_queue1

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])
        
    if args.model is None:
        model = Model("model")
    else:
        model = Model(lang=args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = rec.Result()
                print(text)
                
                # Use regex to extract the value inside the quotes after "text" key
                match = re.search(r'"text" : "(.*?)"',text)

                # Check if a match was found
                if match:
                    real_text = match.group(1)
                    print(real_text)
                    shared_queue1.shared_queue.put(real_text)

                    # helo = shared_queue1.shared_queue.get()
                    # print(helo)

            else:
                # print(rec.PartialResult())
                pass
            if dump_fn is not None:
                dump_fn.write(data)

except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))