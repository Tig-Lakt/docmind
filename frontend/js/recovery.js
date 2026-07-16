const showAlert = (el, msg, type = 'error') => {
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
};

const hideAlert = (el) => { el.className = 'alert'; };

// ── Запрос сброса пароля ──
const recoveryForm = document.getElementById('recovery-form');
if (recoveryForm) {
  recoveryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const alert  = document.getElementById('alert');
    const btn    = document.getElementById('submit-btn');
    hideAlert(alert);

    const email = document.getElementById('email').value.trim();

    btn.disabled = true;
    btn.textContent = 'Отправляю...';

    try {
      const res = await fetch('/api/v1/recovery/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      // Всегда показываем одно сообщение — не раскрываем существует ли email
      showAlert(alert, 'Если email зарегистрирован — письмо отправлено. Проверьте почту.', 'success');
      recoveryForm.reset();

    } catch {
      showAlert(alert, 'Ошибка сети. Попробуйте позже.');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Отправить ссылку';
    }
  });
}

// ── Сброс пароля ──
const resetForm = document.getElementById('reset-form');
if (resetForm) {
  // Получаем токен из URL
  const token = new URLSearchParams(window.location.search).get('token');

  if (!token) {
    const alert = document.getElementById('alert');
    showAlert(alert, 'Недействительная ссылка. Запросите новую.');
    document.getElementById('submit-btn').disabled = true;
  }

  resetForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const alert   = document.getElementById('alert');
    const btn     = document.getElementById('submit-btn');
    hideAlert(alert);

    const password        = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('password-confirm').value;

    if (password !== passwordConfirm) {
      showAlert(alert, 'Пароли не совпадают');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Сохраняю...';

    try {
      const res  = await fetch('/api/v1/recovery/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(alert, data.detail || 'Ошибка сброса пароля');
        return;
      }

      showAlert(alert, 'Пароль успешно изменён! Перенаправляем...', 'success');
      setTimeout(() => { window.location.href = '/api/v1/auth/login'; }, 1500);

    } catch {
      showAlert(alert, 'Ошибка сети. Попробуйте позже.');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Сохранить пароль';
    }
  });
}