
let mediaRecorder;
let audioChunks = [];

async function startVerification() {
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

            const audioURL = URL.createObjectURL(audioBlob);
            document.getElementById("audioPlayback").src = audioURL;

            const formData = new FormData();
            formData.append("audio", audioBlob, "verification.webm");

            const username = document.querySelector(
                'input[name="username"]'
            ).value;

            formData.append("username", username);

            document.getElementById("status").textContent =
                "Comparing voices...";

            try {
                const response = await fetch("/verify-voice", {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();

                let message = result.message;

                if (result.similarity !== undefined) {
                    message += " Similarity score: " + result.similarity;
                }

                document.getElementById("status").textContent = message;

                if (result.verified) {
                    document.getElementById("status").textContent =
                        "Voice verified! Redirecting to dashboard...";

                    setTimeout(() => {
                        window.location.href = "/dashboard";
                    }, 1500);
                }

            } catch (error) {
                document.getElementById("status").textContent =
                    "Verification failed: " + error.message;
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

function stopVerification() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();

        document.getElementById("status").textContent =
            "Processing recording...";

        document.getElementById("startBtn").disabled = false;
        document.getElementById("stopBtn").disabled = true;
    }
}
