// Jarvis Voice Assistant - Web Interface

let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let audioContext;
let analyser;
let animationId;

const recordButton = document.getElementById('recordButton');
const statusDiv = document.getElementById('status');
const transcriptDiv = document.getElementById('transcript');
const responseDiv = document.getElementById('response');
const errorDiv = document.getElementById('error');
const audioPlayer = document.getElementById('audioPlayer');
const visualizer = document.getElementById('visualizer');
const canvas = document.getElementById('canvas');
const canvasCtx = canvas.getContext('2d');

// API endpoint
const API_URL = window.location.origin;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Jarvis Web Interface loaded');
    checkMicrophonePermission();
});

// Check microphone permission
async function checkMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop());
        console.log('Microphone permission granted');
    } catch (err) {
        showError('Erreur: Impossible d\'accéder au microphone. Veuillez autoriser l\'accès.');
        console.error('Microphone permission error:', err);
    }
}

// Record button events
recordButton.addEventListener('mousedown', startRecording);
recordButton.addEventListener('mouseup', stopRecording);
recordButton.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startRecording();
});
recordButton.addEventListener('touchend', (e) => {
    e.preventDefault();
    stopRecording();
});

// Prevent context menu on long press
recordButton.addEventListener('contextmenu', (e) => {
    e.preventDefault();
});

async function startRecording() {
    if (isRecording) return;

    try {
        audioChunks = [];

        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true,
            }
        });

        // Setup audio context for visualization
        audioContext = new AudioContext();
        const source = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);

        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm',
        });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());
            await processAudio();
        };

        mediaRecorder.start();
        isRecording = true;

        updateStatus('listening', '🔴 En écoute...');
        recordButton.classList.add('recording');
        visualizer.classList.add('active');

        visualize();

    } catch (err) {
        showError('Erreur lors du démarrage de l\'enregistrement: ' + err.message);
        console.error('Recording error:', err);
    }
}

function stopRecording() {
    if (!isRecording) return;

    mediaRecorder.stop();
    isRecording = false;

    recordButton.classList.remove('recording');
    visualizer.classList.remove('active');

    if (animationId) {
        cancelAnimationFrame(animationId);
    }

    updateStatus('processing', '⚙️ Traitement en cours...');
}

async function processAudio() {
    try {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        console.log('Audio blob size:', audioBlob.size, 'bytes');

        if (audioBlob.size < 1000) {
            showError('Enregistrement trop court. Réessayez.');
            updateStatus('idle', '🟢 Prêt - Appuyez pour parler');
            return;
        }

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        const response = await fetch(`${API_URL}/api/voice/process`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response:', data);

        // Display transcription
        transcriptDiv.textContent = data.transcription;
        transcriptDiv.classList.remove('empty');

        // Display response
        responseDiv.textContent = data.response;
        responseDiv.classList.remove('empty');

        // Play audio response if available
        if (data.audio_url) {
            updateStatus('speaking', '🔊 Jarvis parle...');
            audioPlayer.src = data.audio_url;
            audioPlayer.style.display = 'block';

            audioPlayer.onended = () => {
                updateStatus('idle', '🟢 Prêt - Appuyez pour parler');
            };

            await audioPlayer.play();
        } else {
            updateStatus('idle', '🟢 Prêt - Appuyez pour parler');
        }

    } catch (err) {
        showError('Erreur lors du traitement: ' + err.message);
        console.error('Processing error:', err);
        updateStatus('idle', '🟢 Prêt - Appuyez pour parler');
    }
}

function updateStatus(state, message) {
    statusDiv.className = 'status ' + state;
    statusDiv.textContent = message;
}

function showError(message) {
    errorDiv.textContent = '⚠️ ' + message;
    errorDiv.classList.add('show');

    setTimeout(() => {
        errorDiv.classList.remove('show');
    }, 5000);
}

function visualize() {
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const draw = () => {
        animationId = requestAnimationFrame(draw);

        analyser.getByteTimeDomainData(dataArray);

        canvasCtx.fillStyle = '#f5f5f5';
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = '#667eea';
        canvasCtx.beginPath();

        const sliceWidth = canvas.width / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = (v * canvas.height) / 2;

            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        canvasCtx.lineTo(canvas.width, canvas.height / 2);
        canvasCtx.stroke();
    };

    draw();
}
