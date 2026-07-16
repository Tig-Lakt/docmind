// ── Проверка токена ──
const token = localStorage.getItem('access_token');
if (!token) { window.location.href = '/api/v1/auth/login'; }

const authHeaders = { 'Authorization': `Bearer ${token}` };

// ── Утилиты ──
const showAlert = (el, msg, type = 'error') => {
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
  setTimeout(() => { el.className = 'alert'; }, 6000);
};

const formatDate = (iso) => new Date(iso).toLocaleDateString('ru-RU', {
  day: '2-digit', month: '2-digit', year: 'numeric',
});

const fileTypeLabel = (type) => ({ pdf: 'PDF', docx: 'DOC', xlsx: 'XLS', url: 'URL' }[type] || type.toUpperCase());

// ── Состояние ──
let selectedDocId   = null;
let selectedDocName = null;
let isAsking        = false;

// ── Список документов ──
const docsList  = document.getElementById('docs-list');
const docsCount = document.getElementById('docs-count');

const selectDoc = (docId, docName) => {
  selectedDocId   = docId;
  selectedDocName = docName;

  // Подсвечиваем выбранный документ
  document.querySelectorAll('.doc-item').forEach(el => el.classList.remove('selected'));
  document.querySelector(`.doc-item[data-id="${docId}"]`)?.classList.add('selected');

  // Активируем чат
  const chatInput   = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const chatDocName = document.getElementById('chat-doc-name');

  chatInput.disabled   = false;
  chatSendBtn.disabled = false;
  chatDocName.textContent = docName;
  chatDocName.classList.add('active');
  chatInput.focus();
};

const renderDocs = (docs) => {
  const n = docs.length;
  docsCount.textContent = `${n} ${n === 1 ? 'документ' : n < 5 ? 'документа' : 'документов'}`;

  if (n === 0) {
    docsList.innerHTML = '<div class="docs-empty">Загрузите первый документ</div>';
    return;
  }

  docsList.innerHTML = docs.map(doc => `
    <div class="doc-item${doc.doc_id === selectedDocId ? ' selected' : ''}"
         data-id="${doc.doc_id}"
         data-name="${doc.filename}"
         style="cursor:pointer">
      <div class="doc-icon">${fileTypeLabel(doc.file_type)}</div>
      <div class="doc-info">
        <div class="doc-name">${doc.filename}</div>
        <div class="doc-meta">Добавлен ${formatDate(doc.created_at)}</div>
      </div>
    </div>
  `).join('');

  // Клик по документу — выбираем его для чата
  docsList.querySelectorAll('.doc-item').forEach(el => {
    el.addEventListener('click', () => selectDoc(
      parseInt(el.dataset.id),
      el.dataset.name,
    ));
  });
};

const loadDocs = async () => {
  try {
    const res = await fetch('/api/v1/documents/my', { headers: authHeaders });
    if (res.status === 401) { window.location.href = '/api/v1/auth/login'; return; }
    const docs = await res.json();
    renderDocs(docs);
  } catch {
    docsList.innerHTML = '<div class="docs-empty">Не удалось загрузить документы</div>';
  }
};

// ── Загрузка файла ──
const fileInput   = document.getElementById('file-input');
const fileName    = document.getElementById('file-name');
const uploadBtn   = document.getElementById('upload-btn');
const uploadAlert = document.getElementById('upload-alert');
const dropZone    = document.getElementById('drop-zone');

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file) { fileName.textContent = file.name; uploadBtn.disabled = false; }
});

dropZone.addEventListener('dragover',  (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', ()  => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) { fileInput.files = e.dataTransfer.files; fileName.textContent = file.name; uploadBtn.disabled = false; }
});

uploadBtn.addEventListener('click', async () => {
  const file = fileInput.files[0];
  if (!file) return;

    // Проверка размера на фронте
  if (file.size > 50 * 1024 * 1024) {
    showAlert(uploadAlert, 'Файл слишком большой. Максимум — 50 МБ');
    return;
  }

  uploadBtn.disabled = true;
  uploadBtn.innerHTML = '<span class="spinner"></span>Загружаю...';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res  = await fetch('/api/v1/documents/upload', { method: 'POST', headers: authHeaders, body: formData });
    const data = await res.json();
    if (!res.ok) { showAlert(uploadAlert, data.detail || 'Ошибка загрузки'); return; }
    showAlert(uploadAlert, `Файл «${data.filename}» загружен`, 'success');
    fileInput.value = ''; fileName.textContent = '';
    await loadDocs();
  } catch {
    showAlert(uploadAlert, 'Ошибка сети. Попробуйте позже.');
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Загрузить';
  }
});

// ── Загрузка ссылки ──
const urlInput = document.getElementById('url-input');
const urlBtn   = document.getElementById('url-btn');
const urlAlert = document.getElementById('url-alert');

if (urlBtn) {
      urlBtn.addEventListener('click', async () => {
    urlBtn.addEventListener('click', async () => {
      const url = urlInput.value.trim();
      if (!url) { showAlert(urlAlert, 'Введите ссылку'); return; }

      urlBtn.disabled = true;
      urlBtn.innerHTML = '<span class="spinner"></span>Обрабатываю...';

      const formData = new FormData();
      formData.append('url', url);

      try {
        const res  = await fetch('/api/v1/documents/upload-url', { method: 'POST', headers: authHeaders, body: formData });
        const data = await res.json();
        if (!res.ok) { showAlert(urlAlert, data.detail || 'Ошибка обработки ссылки'); return; }
        showAlert(urlAlert, 'Ссылка добавлена', 'success');
        urlInput.value = '';
        await loadDocs();
      } catch {
        showAlert(urlAlert, 'Ошибка сети. Попробуйте позже.');
      } finally {
        urlBtn.disabled = false;
        urlBtn.textContent = 'Добавить';
      }
    });

});
}

// ── Чат ──
const chatMessages = document.getElementById('chat-messages');
const chatInput    = document.getElementById('chat-input');
const chatSendBtn  = document.getElementById('chat-send-btn');

const addMessage = (text, role) => {
  // Убираем плейсхолдер при первом сообщении
  const placeholder = chatMessages.querySelector('.chat-placeholder');
  if (placeholder) placeholder.remove();

  const time = new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  const div  = document.createElement('div');
  div.className = `chat-msg ${role}`;
  div.innerHTML = `
    <div class="chat-msg-bubble">${text}</div>
    <div class="chat-msg-meta">${time}</div>
  `;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
};

const addLoadingMessage = () => {
  const placeholder = chatMessages.querySelector('.chat-placeholder');
  if (placeholder) placeholder.remove();

  const div = document.createElement('div');
  div.className = 'chat-msg bot loading';
  div.innerHTML = `
    <div class="chat-msg-bubble">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>
  `;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
};

const sendQuestion = async () => {
  const question = chatInput.value.trim();
  if (!question || !selectedDocId || isAsking) return;

  isAsking = true;
  chatInput.disabled  = true;
  chatSendBtn.disabled = true;
  chatInput.value = '';

  addMessage(question, 'user');
  const loadingEl = addLoadingMessage();

  try {
    const res = await fetch('/chat/ask', {
      method: 'POST',
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify({ doc_id: selectedDocId, question }),
    });

    const data = await res.json();
    loadingEl.remove();

    if (!res.ok) {
      addMessage(data.detail || 'Произошла ошибка', 'bot');
      return;
    }

    addMessage(data.answer, 'bot');

  } catch {
    loadingEl.remove();
    addMessage('Ошибка сети. Попробуйте позже.', 'bot');
  } finally {
    isAsking = false;
    chatInput.disabled   = false;
    chatSendBtn.disabled = false;
    chatInput.focus();
  }
};

chatSendBtn.addEventListener('click', sendQuestion);
chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendQuestion(); }
});

// ── Выход ──
document.getElementById('logout-btn').addEventListener('click', (e) => {
  e.preventDefault();
  localStorage.removeItem('access_token');
  window.location.href = '/api/v1/auth/login';
});

// ── Инициализация ──
loadDocs();