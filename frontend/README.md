## Frontend (Vite + React + axios)

**Структура**

- `src` — основной код фронтенда
  - `assets` — стили и статические ресурсы
  - `components` — (пока пусто) общие компоненты
  - `hooks` — кастомные хуки (например, `useApi`)
  - `routes` — страницы и маршруты (`App`, `HomePage`, `AboutPage`)

**Основные команды**

- `npm install` — установка зависимостей
- `npm run dev` — локальная разработка (Vite dev server на `http://localhost:5173`)
- `npm run build` — сборка продакшн-бандла в `dist/`

**Переменные окружения**

- `VITE_API_URL` — базовый URL вашего бекенда для axios (по умолчанию `http://localhost:8000`).
  - В Docker для продакшна в `docker-compose.yml` передаётся `https://api.${DOMAIN}`.
  - В `docker-compose.override.yml` для локалки используется `http://localhost:8000`.

**Docker**

- Сборка образа: `docker build -t traefick-frontend ./frontend`
- В продакшене фронтенд сервится nginx из `frontend/Dockerfile` и `frontend/nginx.conf`.


