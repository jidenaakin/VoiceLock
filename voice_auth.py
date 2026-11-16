
import os
import subprocess
import tempfile

import imageio_ffmpeg
from speakeronnx import SpeakerEmbedder, cosine


# Load the AI speaker recognition model
print("Loading speaker recognition model...")

model = SpeakerEmbedder(model="wespeaker-resnet34")

print("Speaker recognition model loaded!")


def convert_to_wav(audio_path):

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
                "-i", audio_path,
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


def compare_voices(reference_path, test_path):

    reference_wav = None
    test_wav = None

    try:
        # Convert both recordings to WAV
        reference_wav = convert_to_wav(reference_path)
        test_wav = convert_to_wav(test_path)

        # Generate speaker embeddings
        reference_embedding = model.embed(reference_wav)
        test_embedding = model.embed(test_wav)

        # Calculate voice similarity
        similarity = cosine(
            reference_embedding,
            test_embedding
        )

        return float(similarity)

    finally:

        if reference_wav and os.path.exists(reference_wav):
            os.remove(reference_wav)

        if test_wav and os.path.exists(test_wav):
            os.remove(test_wav)
