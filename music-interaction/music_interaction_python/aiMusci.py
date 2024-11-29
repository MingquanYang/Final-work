import requests
import pyaudio
import wave
import json
import time

# Function to record 15 seconds of audio from the microphone
def record_audio(filename, duration=15):
    p = pyaudio.PyAudio()

    # Set up the audio stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)

    print(f"Recording {duration} seconds...")
    frames = []

    # Record audio for the given duration
    for _ in range(0, int(44100 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    # Stop the stream and close it
    print("Recording complete.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the audio to a file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))

# Function to upload audio and call the extend_audio API
def extend_audio(audio_file, continue_at=109.96):
    # Upload the audio to the API
    with open(audio_file, 'rb') as f:
        files = {'file': (audio_file, f, 'audio/wav')}
        response = requests.post("http://localhost:3000/api/extend_audio", files=files)
        
    if response.status_code == 200:
        print("Audio uploaded successfully.")
        response_data = response.json()

        # Get the audio_id from the response
        audio_id = response_data.get('audio_id')
        print(f"Audio ID: {audio_id}")
        
        # Call the extend API
        payload = {
            "audio_id": audio_id,
            "prompt": "",
            "continue_at": str(continue_at),
            "title": "",
            "tags": ""
        }

        headers = {'Content-Type': 'application/json'}
        extend_response = requests.post("http://localhost:3000/api/extend_audio", json=payload, headers=headers)
        
        if extend_response.status_code == 200:
            extended_audio = extend_response.json()
            mp3_url = extended_audio.get("url")
            print(f"Extended audio available at: {mp3_url}")
            return mp3_url
        else:
            print("Failed to extend the audio.")
            return None
    else:
        print("Failed to upload audio.")
        return None

# Main function to record, extend audio, and run every 3 minutes
def main():
    while True:
        audio_file = "recorded_audio.wav"
        record_audio(audio_file)  # Record 15 seconds of audio
        time.sleep(1)  # Wait for audio file to be ready
        mp3_url = extend_audio(audio_file)  # Call extend audio API

        if mp3_url:
            # Download the extended MP3 audio file
            mp3_response = requests.get(mp3_url)
            if mp3_response.status_code == 200:
                with open("extended_audio.mp3", 'wb') as f:
                    f.write(mp3_response.content)
                print("Extended audio saved as extended_audio.mp3")
            else:
                print("Failed to download extended audio.")
        else:
            print("Audio extension failed.")

        # Wait for 3 minutes before the next cycle
        print("Waiting for the next cycle...")
        time.sleep(180)  # 3 minutes (180 seconds)

if __name__ == "__main__":
    main()
