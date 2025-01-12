import threading
import queue
import sys
sys.path.append('../')
import shared_queue1

import argparse
import sounddevice as sd
import re
from vosk import Model, KaldiRecognizer
import time

from LLMCompiler import chain
from langchain_core.messages import HumanMessage



def producer():
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
            model = Model("../real_time_translation/model")
        else:
            model = Model(lang=args.model)

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None

        with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
                dtype="int16", channels=1, callback=callback):
            # print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            # print("#" * 80)

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

def consumer():
    while True:
        try:
            # print("#"*50)
            print(f"Queue size: {shared_queue1.shared_queue.qsize()}")
            

            recognized_text = shared_queue1.shared_queue.get(timeout=2)  # Get the recognized speech text
            print("*"*50)

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
