
import sounddevice as sd
import soundfile as sf
import os
import time

FOLDER = "voice_samples/fresh_test"
PHRASE = "My voice is my password."

os.makedirs(FOLDER, exist_ok=True)

SAMPLE_RATE = 16000
DURATION = 8


def record_speaker(speaker, number):

    filename = f"{speaker}_{number}.wav"
    filepath = os.path.join(FOLDER, filename)

    print("\nGet ready...")
    time.sleep(2)

    print(f"Recording {speaker} sample {number}!")
    print(f'Say: "{PHRASE}"')

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    sf.write(filepath, audio, SAMPLE_RATE)

    print(f"Saved: {filepath}")


print("VOICE RECORDING TEST")
print("--------------------")

speaker = input("Enter speaker name (jide or other): ").strip().lower()

if speaker not in ["jide", "other"]:
    print("Invalid name. Enter jide or other.")
    exit()

for number in range(1, 4):

    input(f"\nPress ENTER when ready for recording {number}...")

    record_speaker(speaker, number)

print("\nAll three recordings completed!")
