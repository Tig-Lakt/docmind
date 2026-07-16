# DocMind

Проект доступен по адресу https://docmind.site

RAG-агент для работы с документами. Загружайте PDF, DOCX и XLSX — и задавайте вопросы на естественном языке. DocMind найдёт нужное за секунды.

---

## Возможности

- Регистрация и авторизация с верификацией email
- Восстановление пароля через email
- Загрузка документов: PDF, DOCX, XLSX (до 50 МБ)
- Индексация документов в векторной базе данных Qdrant
- RAG-чат: задавайте вопросы по загруженным документам
- Агент отвечает строго по содержимому документа

---

## Стек

| Слой | Технологии |
|---|---|
| Backend | FastAPI, SQLModel, SQLAlchemy async |
| База данных | PostgreSQL |
| Векторная БД | Qdrant |
| AI | OpenAI (gpt-4o-mini, text-embedding-3-small) |
| Email | Resend |
| Frontend | HTML, CSS, JavaScript |
| Инфраструктура | Docker, Docker Compose, Nginx |

---

## Структура проекта

```
docmind/
├── backend/
│   ├── api/
│   │   ├── deps.py                 ← зависимости FastAPI
│   │   └── v1/
│   │       └── endpoints/          ← роутеры
│   ├── core/
│   │   ├── config.py               ← настройки из .env
│   │   ├── security.py             ← JWT, bcrypt
│   │   └── prompts.py              ← системный промпт LLM
│   ├── db/
│   │   └── database.py             ← подключение к БД
│   ├── models/                     ← SQLModel модели
│   ├── repositories/               ← слой доступа к данным
│   ├── schemas/                    ← Pydantic схемы
│   ├── services/                   ← бизнес-логика
│   └── main.py                     ← точка входа
├── frontend/
│   ├── css/
│   ├── js/
│   └── templates/                  ← HTML шаблоны
├── uploads/                        ← загруженные файлы
├── nginx/
│   └── nginx.conf
├── .env
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Архитектура

```
router → service → repository → PostgreSQL
               ↘ Qdrant (векторный поиск)
               ↘ OpenAI (эмбеддинги, LLM)
               ↘ Resend (email)
```

---

## Быстрый старт

### Требования

- Docker
- Docker Compose v2+
- OpenAI API ключ
- Resend API ключ

### Установка

**1. Клонируй репозиторий:**

```bash
git clone https://github.com/Tig-Lakt/docmind.git
cd docmind
```

**2. Создай `.env` на основе `.env.example`:**

```bash
cp .env.example .env
```

**3. Заполни `.env`:**

```env
POSTGRES_USER=docmind
POSTGRES_PASSWORD=docmindpassword
POSTGRES_DB=docminddb
DATABASE_URL=postgresql+asyncpg://docmind:docmindpassword@db:5432/docminddb

SECRET_KEY=твой-секретный-ключ
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

QDRANT_URL=http://qdrant:6333
OPENAI_API_KEY=sk-...

RESEND_API_KEY=re_...
```

**4. Запусти:**

```bash
docker-compose up --build -d
```

**5. Открой в браузере:**

```
http://localhost:8001
```

---

## Переменные окружения

| Переменная | Описание |
|---|---|
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `POSTGRES_DB` | Название базы данных |
| `DATABASE_URL` | Строка подключения к БД |
| `SECRET_KEY` | Секретный ключ для JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена в минутах |
| `ALGORITHM` | Алгоритм JWT (HS256) |
| `QDRANT_URL` | URL Qdrant |
| `OPENAI_API_KEY` | API ключ OpenAI |
| `RESEND_API_KEY` | API ключ Resend для отправки email |

---

## API

Документация доступна после запуска:

```
http://localhost:8001/docs
```

### Основные эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/confirm-email` | Подтверждение email |
| POST | `/api/v1/auth/resend-code` | Повторная отправка кода |
| POST | `/api/v1/auth/login` | Вход |
| POST | `/api/v1/auth/forgot-password` | Запрос сброса пароля |
| POST | `/api/v1/auth/reset-password` | Сброс пароля |
| POST | `/api/v1/documents/upload` | Загрузка файла |
| GET | `/api/v1/documents/my` | Список документов |
| POST | `/chat/ask` | Вопрос по документу |

---

## Git flow

```
main        ← стабильные релизы
develop     ← интеграционная ветка
feature/*   ← новые функции
refactor/*  ← рефакторинг
fix/*       ← исправления
```

---

