
from speakeronnx import SpeakerEmbedder, cosine
import os
from statistics import mean

FOLDER = "voice_samples/fresh_test"

print("Loading speaker recognition model...")
model = SpeakerEmbedder(model="wespeaker-resnet34")

embeddings = {}

for speaker in ["jide", "other"]:
    for number in range(1, 4):
        filename = f"{speaker}_{number}.wav"
        filepath = os.path.join(FOLDER, filename)

        print(f"Processing {filename}...")
        embeddings[filename] = model.embed(filepath)


same_scores = []
different_scores = []

# Compare recordings from the same speaker
for speaker in ["jide", "other"]:
    for i in range(1, 4):
        for j in range(i + 1, 4):
            score = cosine(
                embeddings[f"{speaker}_{i}.wav"],
                embeddings[f"{speaker}_{j}.wav"]
            )
            same_scores.append(score)

# Compare recordings from different speakers
for i in range(1, 4):
    for j in range(1, 4):
        score = cosine(
            embeddings[f"jide_{i}.wav"],
            embeddings[f"other_{j}.wav"]
        )
        different_scores.append(score)


print("\n========== FINAL RESULTS ==========")

print(f"Same-speaker average: {mean(same_scores):.4f}")
print(f"Different-speaker average: {mean(different_scores):.4f}")

print("\nComparison completed!")
