const showAlert = (el, msg, type = 'error') => {
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
};

const hideAlert = (el) => { el.className = 'alert'; };

// Получаем email из URL
const email = new URLSearchParams(window.location.search).get('email');

if (!email) {
  window.location.href = '/api/v1/auth/register';
}

// Показываем email на странице
const emailDisplay = document.getElementById('email-display');
if (emailDisplay) emailDisplay.textContent = email;

// ── Подтверждение кода ──
const confirmForm = document.getElementById('confirm-form');
if (confirmForm) {
  // Автофокус на поле кода
  document.getElementById('code').focus();

  confirmForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const alert = document.getElementById('alert');
    const btn   = document.getElementById('submit-btn');
    hideAlert(alert);

    const code = document.getElementById('code').value.trim();

    if (code.length !== 6) {
      showAlert(alert, 'Введите 6-значный код');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Проверяю...';

    try {
      const res = await fetch('/api/v1/auth/confirm-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(alert, data.detail || 'Неверный код');
        btn.disabled = false;
        btn.textContent = 'Подтвердить';
        return;
      }

      // Сохраняем токен и идём в личный кабинет
      localStorage.setItem('access_token', data.access_token);
      window.location.href = '/api/v1/service/dashboard';

    } catch {
      showAlert(alert, 'Ошибка сети. Попробуйте позже.');
      btn.disabled = false;
      btn.textContent = 'Подтвердить';
    }
  });
}

// ── Повторная отправка кода ──
const resendBtn = document.getElementById('resend-btn');
if (resendBtn) {
  let cooldown = false;

  resendBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    if (cooldown) return;

    const alert = document.getElementById('alert');
    hideAlert(alert);

    cooldown = true;
    resendBtn.style.opacity = '0.4';
    resendBtn.textContent = 'Отправляю...';

    try {
      const res = await fetch('/api/v1/auth/resend-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(alert, data.detail || 'Ошибка отправки');
        cooldown = false;
        resendBtn.style.opacity = '1';
        resendBtn.textContent = 'Отправить повторно';
        return;
      }

      showAlert(alert, 'Новый код отправлен на почту', 'success');

      // Кулдаун 60 секунд
      let seconds = 60;
      resendBtn.textContent = `Повторно через ${seconds}с`;

      const timer = setInterval(() => {
        seconds--;
        resendBtn.textContent = `Повторно через ${seconds}с`;
        if (seconds <= 0) {
          clearInterval(timer);
          cooldown = false;
          resendBtn.style.opacity = '1';
          resendBtn.textContent = 'Отправить повторно';
        }
      }, 1000);

    } catch {
      showAlert(alert, 'Ошибка сети. Попробуйте позже.');
      cooldown = false;
      resendBtn.style.opacity = '1';
      resendBtn.textContent = 'Отправить повторно';
    }
  });
}