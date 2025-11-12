const recordBtn = document.getElementById('record');
const status = document.getElementById('status');
const reply = document.getElementById('reply');

let mediaRecorder;
let audioChunks = [];

async function init() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.addEventListener("dataavailable", event => {
    audioChunks.push(event.data);
  });

  mediaRecorder.addEventListener("stop", async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    audioChunks = [];
    status.textContent = "Uploading...";
    const fd = new FormData();
    fd.append("file", audioBlob, "speech.wav");
    // optional: send lang hint for Tamil 'ta' or 'en'
    const resp = await fetch("http://localhost:8000/transcribe", { method: "POST", body: fd });
    if (!resp.ok) {
      status.textContent = "Error from server";
      return;
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    reply.src = url;
    reply.play();
    status.textContent = "Done";
  });
}

recordBtn.addEventListener("mousedown", () => {
  if (!mediaRecorder) { status.textContent = "No mic"; return; }
  audioChunks = [];
  mediaRecorder.start();
  status.textContent = "Recording...";
});
recordBtn.addEventListener("mouseup", () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    status.textContent = "Processing...";
  }
});

// init on load
init().catch(e => { status.textContent = "Mic init failed: " + e; });
