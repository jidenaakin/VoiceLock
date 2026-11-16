
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

            document.getElementById("audioPlayback").src =
                URL.createObjectURL(audioBlob);

            const username = document.querySelector(
                'input[name="username"]'
            ).value.trim();

            const formData = new FormData();

            formData.append("audio", audioBlob, "recovery.webm");
            formData.append("username", username);

            document.getElementById("status").textContent =
                "Verifying your voice...";

            try {
                const response = await fetch("/recover-verify", {
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
                        "Voice verified! Opening password reset...";

                    setTimeout(() => {
                        window.location.href = "/reset-password";
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
            "Recording... Say your registered phrase.";

        document.getElementById("startBtn").disabled = true;
        document.getElementById("stopBtn").disabled = false;

    } catch (error) {
        alert("Could not access microphone. Please allow microphone access.");
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
