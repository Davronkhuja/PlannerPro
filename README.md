# Planner Pro

Профессиональное приложение-планировщик с 4 разделами.

**Стек:** Vue 3 + FastAPI + SQLite | Адаптивный (mobile-first)

---

## Быстрый старт

### Backend (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API: http://localhost:8000 | Docs: http://localhost:8000/docs

### Frontend (Vue)
```bash
cd frontend
npm install
npm run dev
```
Приложение: http://localhost:3000

---

## Модули

| Модуль | Описание |
|--------|----------|
| **Привычки** | Ежемесячный трекер с streak, % выполнения |
| **Финансы** | Доходы (13 категорий), расходы (30 категорий), долги + аналитика |
| **Неделя** | Задачи по дням, цели недели, дневник (сон/энергия/настроение) + годовые цели |
| **Задачи** | Task list с приоритетом, статусом, дедлайном, категорией, фильтрами |

---

## Структура

```
planner-pro/
├── backend/
│   ├── main.py          # FastAPI + SQLite
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.vue
    │   ├── api.js
    │   ├── assets/main.css
    │   └── components/
    │       ├── HabitTracker.vue
    │       ├── FinancePlanner.vue
    │       ├── WeeklyPlanner.vue
    │       └── TaskListView.vue
    ├── index.html
    ├── package.json
    └── vite.config.js
```
