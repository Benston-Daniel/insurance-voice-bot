const baseUrl = '/'; // change if backend is hosted elsewhere

const messagesDiv = document.getElementById('messages');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');

function appendMessage(who, text) {
  const el = document.createElement('div');
  el.innerHTML = `<b>${who}:</b> ${text}`;
  messagesDiv.appendChild(el);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

sendBtn.addEventListener('click', async () => {
  const message = textInput.value.trim();
  if (!message) return;
  appendMessage('You', message);
  textInput.value = '';

  try {
    const res = await fetch('/rasa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    if (data.status === 'ok' && Array.isArray(data.rasa)) {
      data.rasa.forEach(m => appendMessage('Bot', m.text || JSON.stringify(m)));
    } else if (data.status === 'error') {
      appendMessage('Bot', 'Error: ' + data.error);
    } else {
      appendMessage('Bot', JSON.stringify(data));
    }
  } catch (e) {
    appendMessage('Bot', 'Network error: ' + e.message);
  }
});
