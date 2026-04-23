from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(title="Planner Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "planner.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            date TEXT,
            UNIQUE(habit_id, date),
            FOREIGN KEY(habit_id) REFERENCES habits(id)
        );
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL DEFAULT 'Прочие поступления',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL DEFAULT 'Кредиты',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS weekly_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            day_index INTEGER NOT NULL,
            week_start TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS weekly_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            week_start TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS day_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            note TEXT DEFAULT '',
            sleep_rating INTEGER DEFAULT 0,
            energy_rating INTEGER DEFAULT 0,
            mood_rating INTEGER DEFAULT 0,
            lesson TEXT DEFAULT '',
            gratitude TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS task_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            deadline TEXT DEFAULT NULL,
            priority TEXT DEFAULT '🟡 Средний',
            status TEXT DEFAULT '⚠️ Не начато',
            category TEXT DEFAULT 'Работа 💼',
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            percentage INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

init_db()

class HabitCreate(BaseModel):
    name: str

class ToggleDate(BaseModel):
    date: str

class IncomeCreate(BaseModel):
    name: str
    amount: float
    category: str = "Прочие поступления"

class ExpenseCreate(BaseModel):
    name: str
    amount: float
    category: str

class DebtCreate(BaseModel):
    name: str
    amount: float
    category: str = "Кредиты"

class WeeklyTaskCreate(BaseModel):
    text: str
    day_index: int
    week_start: str

class WeeklyTaskUpdate(BaseModel):
    done: bool

class WeeklyGoalCreate(BaseModel):
    text: str
    week_start: str

class WeeklyGoalUpdate(BaseModel):
    done: bool

class DayNoteUpsert(BaseModel):
    date: str
    note: str = ""
    sleep_rating: int = 0
    energy_rating: int = 0
    mood_rating: int = 0
    lesson: str = ""
    gratitude: str = ""

class TaskListCreate(BaseModel):
    text: str
    deadline: Optional[str] = None
    priority: str = "🟡 Средний"
    status: str = "⚠️ Не начато"
    category: str = "Работа 💼"
    note: str = ""

class TaskListUpdate(BaseModel):
    text: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    note: Optional[str] = None

class GoalCreate(BaseModel):
    name: str
    percentage: int = 0

class GoalUpdate(BaseModel):
    percentage: int

# Habits
@app.get("/habits")
def get_habits():
    conn = get_db()
    habits = conn.execute("SELECT * FROM habits ORDER BY id").fetchall()
    result = []
    for h in habits:
        logs = conn.execute("SELECT date FROM habit_logs WHERE habit_id=?", (h["id"],)).fetchall()
        result.append({"id": h["id"], "name": h["name"], "logs": [l["date"] for l in logs]})
    conn.close()
    return result

@app.post("/habits", status_code=201)
def create_habit(data: HabitCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO habits (name) VALUES (?)", (data.name,))
    conn.commit()
    hid = c.lastrowid
    conn.close()
    return {"id": hid, "name": data.name, "logs": []}

@app.delete("/habits/{hid}")
def delete_habit(hid: int):
    conn = get_db()
    conn.execute("DELETE FROM habit_logs WHERE habit_id=?", (hid,))
    conn.execute("DELETE FROM habits WHERE id=?", (hid,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/habits/{hid}/toggle")
def toggle_habit(hid: int, data: ToggleDate):
    conn = get_db()
    existing = conn.execute("SELECT id FROM habit_logs WHERE habit_id=? AND date=?", (hid, data.date)).fetchone()
    if existing:
        conn.execute("DELETE FROM habit_logs WHERE habit_id=? AND date=?", (hid, data.date))
        done = False
    else:
        conn.execute("INSERT INTO habit_logs (habit_id, date) VALUES (?,?)", (hid, data.date))
        done = True
    conn.commit()
    conn.close()
    return {"done": done}

# Incomes
@app.get("/incomes")
def get_incomes():
    conn = get_db()
    rows = conn.execute("SELECT * FROM incomes ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/incomes", status_code=201)
def create_income(data: IncomeCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO incomes (name, amount, category) VALUES (?,?,?)", (data.name, data.amount, data.category))
    conn.commit()
    iid = c.lastrowid
    conn.close()
    return {"id": iid, "name": data.name, "amount": data.amount, "category": data.category}

@app.delete("/incomes/{iid}")
def delete_income(iid: int):
    conn = get_db()
    conn.execute("DELETE FROM incomes WHERE id=?", (iid,))
    conn.commit()
    conn.close()
    return {"ok": True}

# Expenses
@app.get("/expenses")
def get_expenses():
    conn = get_db()
    rows = conn.execute("SELECT * FROM expenses ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/expenses", status_code=201)
def create_expense(data: ExpenseCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO expenses (name, amount, category) VALUES (?,?,?)", (data.name, data.amount, data.category))
    conn.commit()
    eid = c.lastrowid
    conn.close()
    return {"id": eid, "name": data.name, "amount": data.amount, "category": data.category}

@app.delete("/expenses/{eid}")
def delete_expense(eid: int):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return {"ok": True}

# Debts
@app.get("/debts")
def get_debts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM debts ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/debts", status_code=201)
def create_debt(data: DebtCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO debts (name, amount, category) VALUES (?,?,?)", (data.name, data.amount, data.category))
    conn.commit()
    did = c.lastrowid
    conn.close()
    return {"id": did, "name": data.name, "amount": data.amount, "category": data.category}

@app.delete("/debts/{did}")
def delete_debt(did: int):
    conn = get_db()
    conn.execute("DELETE FROM debts WHERE id=?", (did,))
    conn.commit()
    conn.close()
    return {"ok": True}

# Weekly Tasks
@app.get("/weekly-tasks")
def get_weekly_tasks(week_start: str):
    conn = get_db()
    rows = conn.execute("SELECT * FROM weekly_tasks WHERE week_start=? ORDER BY id", (week_start,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/weekly-tasks", status_code=201)
def create_weekly_task(data: WeeklyTaskCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO weekly_tasks (text, day_index, week_start) VALUES (?,?,?)", (data.text, data.day_index, data.week_start))
    conn.commit()
    tid = c.lastrowid
    conn.close()
    return {"id": tid, "text": data.text, "day_index": data.day_index, "week_start": data.week_start, "done": 0}

@app.patch("/weekly-tasks/{tid}")
def update_weekly_task(tid: int, data: WeeklyTaskUpdate):
    conn = get_db()
    conn.execute("UPDATE weekly_tasks SET done=? WHERE id=?", (int(data.done), tid))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/weekly-tasks/{tid}")
def delete_weekly_task(tid: int):
    conn = get_db()
    conn.execute("DELETE FROM weekly_tasks WHERE id=?", (tid,))
    conn.commit()
    conn.close()
    return {"ok": True}

# Weekly Goals
@app.get("/weekly-goals")
def get_weekly_goals(week_start: str):
    conn = get_db()
    rows = conn.execute("SELECT * FROM weekly_goals WHERE week_start=? ORDER BY id", (week_start,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/weekly-goals", status_code=201)
def create_weekly_goal(data: WeeklyGoalCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO weekly_goals (text, week_start) VALUES (?,?)", (data.text, data.week_start))
    conn.commit()
    gid = c.lastrowid
    conn.close()
    return {"id": gid, "text": data.text, "week_start": data.week_start, "done": 0}

@app.patch("/weekly-goals/{gid}")
def update_weekly_goal(gid: int, data: WeeklyGoalUpdate):
    conn = get_db()
    conn.execute("UPDATE weekly_goals SET done=? WHERE id=?", (int(data.done), gid))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/weekly-goals/{gid}")
def delete_weekly_goal(gid: int):
    conn = get_db()
    conn.execute("DELETE FROM weekly_goals WHERE id=?", (gid,))
    conn.commit()
    conn.close()
    return {"ok": True}

# Day Notes / Diary
@app.get("/day-notes")
def get_day_notes(week_start: str):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM day_notes WHERE date >= ? AND date <= date(?, '+6 days')",
        (week_start, week_start)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.put("/day-notes")
def upsert_day_note(data: DayNoteUpsert):
    conn = get_db()
    conn.execute("""
        INSERT INTO day_notes (date, note, sleep_rating, energy_rating, mood_rating, lesson, gratitude)
        VALUES (?,?,?,?,?,?,?)
        ON CONFLICT(date) DO UPDATE SET
          note=excluded.note, sleep_rating=excluded.sleep_rating,
          energy_rating=excluded.energy_rating, mood_rating=excluded.mood_rating,
          lesson=excluded.lesson, gratitude=excluded.gratitude
    """, (data.date, data.note, data.sleep_rating, data.energy_rating, data.mood_rating, data.lesson, data.gratitude))
    conn.commit()
    conn.close()
    return {"ok": True}

# Task List
@app.get("/task-list")
def get_task_list():
    conn = get_db()
    rows = conn.execute("SELECT * FROM task_list ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/task-list", status_code=201)
def create_task_list_item(data: TaskListCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO task_list (text, deadline, priority, status, category, note) VALUES (?,?,?,?,?,?)",
              (data.text, data.deadline, data.priority, data.status, data.category, data.note))
    conn.commit()
    tid = c.lastrowid
    conn.close()
    return {"id": tid, "text": data.text, "deadline": data.deadline, "priority": data.priority,
            "status": data.status, "category": data.category, "note": data.note}

@app.patch("/task-list/{tid}")
def update_task_list_item(tid: int, data: TaskListUpdate):
    conn = get_db()
    fields = {k: v for k, v in data.dict().items() if v is not None}
    if fields:
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE task_list SET {sets} WHERE id=?", list(fields.values()) + [tid])
        conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/task-list/{tid}")
def delete_task_list_item(tid: int):
    conn = get_db()
    conn.execute("DELETE FROM task_list WHERE id=?", (tid,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/task-list/stats")
def task_list_stats():
    from datetime import date
    today = date.today().isoformat()
    conn = get_db()
    total     = conn.execute("SELECT COUNT(*) FROM task_list").fetchone()[0]
    done      = conn.execute("SELECT COUNT(*) FROM task_list WHERE status='✅ Готово'").fetchone()[0]
    in_prog   = conn.execute("SELECT COUNT(*) FROM task_list WHERE status='✏️ В процессе'").fetchone()[0]
    overdue   = conn.execute(
        "SELECT COUNT(*) FROM task_list WHERE deadline < ? AND status NOT IN ('✅ Готово','❌ Отмена')", (today,)
    ).fetchone()[0]
    cancelled = conn.execute("SELECT COUNT(*) FROM task_list WHERE status='❌ Отмена'").fetchone()[0]
    conn.close()
    return {"total": total, "done": done, "in_progress": in_prog,
            "overdue": overdue, "cancelled": cancelled, "not_started": total - done - in_prog - cancelled}

# Annual Goals
@app.get("/goals")
def get_goals():
    conn = get_db()
    rows = conn.execute("SELECT * FROM goals ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/goals", status_code=201)
def create_goal(data: GoalCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO goals (name, percentage) VALUES (?,?)", (data.name, data.percentage))
    conn.commit()
    gid = c.lastrowid
    conn.close()
    return {"id": gid, "name": data.name, "percentage": data.percentage}

@app.patch("/goals/{gid}")
def update_goal(gid: int, data: GoalUpdate):
    conn = get_db()
    conn.execute("UPDATE goals SET percentage=? WHERE id=?", (data.percentage, gid))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/goals/{gid}")
def delete_goal(gid: int):
    conn = get_db()
    conn.execute("DELETE FROM goals WHERE id=?", (gid,))
    conn.commit()
    conn.close()
    return {"ok": True}
