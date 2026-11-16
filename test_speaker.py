
import os
import subprocess
import tempfile

import imageio_ffmpeg
from speakeronnx import SpeakerEmbedder, cosine


# Load the AI speaker-recognition model
print("Loading AI speaker-recognition model...")

model = SpeakerEmbedder(model="wespeaker-resnet34")

print("Model loaded successfully!")


def convert_to_wav(webm_path):

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp_file:
        wav_path = temp_file.name

    try:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i", webm_path,
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                wav_path
            ],
            check=True,
            capture_output=True
        )

        return wav_path

    except Exception:
        if os.path.exists(wav_path):
            os.remove(wav_path)
        raise


# Recording file paths
my_voice = "voice_samples/f3ee0083-998a-43ef-8886-354ec7f1a37e.webm"

other_voice = "voice_samples/7588b062-7258-4e93-9a32-b34edd63505a.webm"

my_test_voice = "voice_samples/test_voice.webm"


converted_files = []

try:
    print("\nConverting recordings to WAV...")

    my_wav = convert_to_wav(my_voice)
    converted_files.append(my_wav)

    other_wav = convert_to_wav(other_voice)
    converted_files.append(other_wav)

    test_wav = convert_to_wav(my_test_voice)
    converted_files.append(test_wav)

    print("Conversion completed!")

    print("\nGenerating voice embeddings...")

    my_embedding = model.embed(my_wav)
    other_embedding = model.embed(other_wav)
    test_embedding = model.embed(test_wav)

    print("Embeddings generated successfully!")

    print("\nVOICE COMPARISON RESULTS")

    print(
        "Your voice vs your test voice:",
        cosine(my_embedding, test_embedding)
    )

    print(
        "Your voice vs other person's voice:",
        cosine(my_embedding, other_embedding)
    )

finally:
    for file_path in converted_files:
        if os.path.exists(file_path):
            os.remove(file_path)
