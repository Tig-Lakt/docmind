const showAlert = (el, msg, type = 'error') => {
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
};

const hideAlert = (el) => { el.className = 'alert'; };

// ── Словарь ошибок ──
const VALIDATION_MESSAGES = {
  "value_error.email": "Введён некорректный email",
  "Пароль должен содержать хотя бы одну цифру": "В пароле должны быть цифры",
  "Пароль должен содержать хотя бы одну букву": "В пароле должны быть не только цифры",
  "Пароль должен быть не менее 8 символов": "Пароль слишком короткий — минимум 8 символов",
  "Email уже зарегистрирован": "Этот email уже зарегистрирован",
  "Неверный email или пароль": "Неверный email или пароль",
};

const parseError = (data) => {
  if (Array.isArray(data.detail)) {
    const err = data.detail[0];
    if (err.type === "value_error" && err.loc?.includes("email")) {
      return VALIDATION_MESSAGES["value_error.email"];
    }
    const msg = err.ctx?.error?.message || err.msg || "";
    for (const [key, val] of Object.entries(VALIDATION_MESSAGES)) {
      if (msg.includes(key)) return val;
    }
    return "Ошибка валидации";
  }
  if (typeof data.detail === "string") {
    return VALIDATION_MESSAGES[data.detail] || data.detail;
  }
  return "Неизвестная ошибка";
};

// ── Register ──
const registerForm = document.getElementById('register-form');
if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const alert = document.getElementById('alert');
    const btn   = document.getElementById('submit-btn');
    hideAlert(alert);

    const email    = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    btn.disabled = true;
    btn.textContent = 'Регистрация...';

    try {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(alert, parseError(data));
        btn.disabled = false;
        btn.textContent = 'Создать аккаунт';
        return;
      }

      // Редиректим на страницу ввода кода с email в параметре
      window.location.href = `/api/v1/auth/confirm-email?email=${encodeURIComponent(email)}`;

    } catch {
      showAlert(alert, 'Ошибка сети. Попробуйте позже.');
      btn.disabled = false;
      btn.textContent = 'Создать аккаунт';
    }
  });
}

// ── Login ──
const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const alert = document.getElementById('alert');
    const btn   = document.getElementById('submit-btn');
    hideAlert(alert);

    const email    = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    btn.disabled = true;
    btn.textContent = 'Вход...';

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(alert, parseError(data));
        btn.disabled = false;
        btn.textContent = 'Войти';
        return;
      }

      localStorage.setItem('access_token', data.access_token);
      window.location.href = '/api/v1/service/dashboard';

    } catch {
      showAlert(alert, 'Ошибка сети. Попробуйте позже.');
      btn.disabled = false;
      btn.textContent = 'Войти';
    }
  });
}