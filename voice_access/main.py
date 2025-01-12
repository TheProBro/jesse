import pyttsx3
import pyaudio
import wave
import os
import time
import pyautogui

def text_to_audio(text, output_file="output.wav"):
    """
    Convert text to speech and save it as a WAV file.
    """
    engine = pyttsx3.init()
    engine.save_to_file(text, output_file)
    engine.runAndWait()

def stream_audio_to_virtual_cable(wave_file, virtual_device_name="CABLE Input"):
    """
    Stream a WAV file to the VB-Audio Virtual Cable (virtual microphone).
    """
    # Open the WAV file
    wf = wave.open(wave_file, 'rb')

    # Set up PyAudio
    p = pyaudio.PyAudio()

    # Find the VB-Audio Virtual Cable device
    virtual_device_index = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if virtual_device_name in device_info['name']:
            virtual_device_index = i
            break

    if virtual_device_index is None:
        raise ValueError("VB-Audio Virtual Cable (CABLE Input) not found!")

    # Open the virtual microphone stream
    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
        output_device_index=virtual_device_index
    )

    # Stream audio to the virtual microphone
    chunk_size = 1024
    data = wf.readframes(chunk_size)
    while data:
        stream.write(data)
        data = wf.readframes(chunk_size)

    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()

def take_screenshot(filename="screenshot.png"):
    """
    Take a screenshot and save it as a PNG file.
    """
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")

def handle_text_command(command):
    """
    Handle a text command by converting it to speech, routing it to the virtual microphone,
    and taking a screenshot.
    """
    try:
        # Convert text command to audio
        text_to_audio(command)
        time.sleep(5)
        # Stream audio to VB-Audio Virtual Cable
        stream_audio_to_virtual_cable("output.wav")

        # Take and save a screenshot
        screenshot_filename = f"screenshot_{int(time.time())}.png"
        take_screenshot(screenshot_filename)

        print(f"Command '{command}' has been sent to the virtual microphone.")
    except Exception as e:
        print(f"Error: {e}")

# Main loop to accept user commands
if __name__ == "__main__":
    # Predefined sequence of commands
    commands = [
        "voice access wake up",
        "Open Spotify",  
        "Click on what do you want to play",
        "Little things give you away",  
        "click on play",
        "Increase volume",  
        "Decrease volume",
        "Exit"
    ]

    # Execute the sequence of commands
    print("Executing sequence of commands...")
    for command in commands:
        if command.lower() == "exit":
            break
        handle_text_command(command)
        

    # Cleanup temporary audio file
    if os.path.exists("output.wav"):
        os.remove("output.wav")
