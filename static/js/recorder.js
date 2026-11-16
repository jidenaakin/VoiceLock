
let mediaRecorder;
let audioChunks = [];

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        audioChunks = [];

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {

            const audioBlob = new Blob(audioChunks, {
                type: mediaRecorder.mimeType
            });

            // Play the recorded voice
            const audioURL = URL.createObjectURL(audioBlob);

            document.getElementById("audioPlayback").src = audioURL;

            // Prepare audio for upload
            const formData = new FormData();

            formData.append("audio", audioBlob, "voice.webm");
formData.append("username", document.querySelector('input[name="username"]').value);

            document.getElementById("status").textContent =
                "Uploading voice...";

            try {
                const response = await fetch("/save-voice", {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.message);
                }

                document.getElementById("status").textContent =
                    result.message;

            } catch (error) {
                document.getElementById("status").textContent =
                    "Upload failed: " + error.message;
            }

            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();

        document.getElementById("status").textContent =
            "Recording... Speak now!";

        document.getElementById("startBtn").disabled = true;
        document.getElementById("stopBtn").disabled = false;

    } catch (error) {
        alert("Could not access microphone.");
        console.error(error);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {

        mediaRecorder.stop();

        document.getElementById("status").textContent =
            "Processing recording...";

        document.getElementById("startBtn").disabled = false;
        document.getElementById("stopBtn").disabled = true;
    }
}
