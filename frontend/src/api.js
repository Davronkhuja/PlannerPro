const BASE = '/api'

async function req(method, path, body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body !== null) opts.body = JSON.stringify(body)
  const res = await fetch(BASE + path, opts)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

// Habits
export const getHabits     = ()           => req('GET',    '/habits')
export const createHabit   = (name)       => req('POST',   '/habits', { name })
export const deleteHabit   = (id)         => req('DELETE', `/habits/${id}`)
export const toggleHabit   = (id, date)   => req('POST',   `/habits/${id}/toggle`, { date })

// Finance
export const getIncomes    = ()           => req('GET',    '/incomes')
export const createIncome  = (n, a, cat)  => req('POST',   '/incomes', { name: n, amount: a, category: cat })
export const deleteIncome  = (id)         => req('DELETE', `/incomes/${id}`)

export const getExpenses   = ()           => req('GET',    '/expenses')
export const createExpense = (n, a, cat)  => req('POST',   '/expenses', { name: n, amount: a, category: cat })
export const deleteExpense = (id)         => req('DELETE', `/expenses/${id}`)

export const getDebts      = ()           => req('GET',    '/debts')
export const createDebt    = (n, a, cat)  => req('POST',   '/debts', { name: n, amount: a, category: cat })
export const deleteDebt    = (id)         => req('DELETE', `/debts/${id}`)

// Weekly planner
export const getWeeklyTasks   = (ws)           => req('GET',    `/weekly-tasks?week_start=${ws}`)
export const createWeeklyTask = (text, di, ws) => req('POST',   '/weekly-tasks', { text, day_index: di, week_start: ws })
export const updateWeeklyTask = (id, done)     => req('PATCH',  `/weekly-tasks/${id}`, { done })
export const deleteWeeklyTask = (id)           => req('DELETE', `/weekly-tasks/${id}`)

export const getWeeklyGoals   = (ws)   => req('GET',    `/weekly-goals?week_start=${ws}`)
export const createWeeklyGoal = (text, ws) => req('POST',   '/weekly-goals', { text, week_start: ws })
export const updateWeeklyGoal = (id, done) => req('PATCH',  `/weekly-goals/${id}`, { done })
export const deleteWeeklyGoal = (id)       => req('DELETE', `/weekly-goals/${id}`)

export const getDayNotes  = (ws)   => req('GET', `/day-notes?week_start=${ws}`)
export const upsertDayNote = (data) => req('PUT', '/day-notes', data)

// Task list
export const getTaskList     = ()        => req('GET',    '/task-list')
export const createTaskItem  = (data)    => req('POST',   '/task-list', data)
export const updateTaskItem  = (id, data)=> req('PATCH',  `/task-list/${id}`, data)
export const deleteTaskItem  = (id)      => req('DELETE', `/task-list/${id}`)
export const getTaskStats    = ()        => req('GET',    '/task-list/stats')

// Annual goals
export const getGoals    = ()          => req('GET',    '/goals')
export const createGoal  = (name, pct) => req('POST',   '/goals', { name, percentage: pct })
export const updateGoal  = (id, pct)   => req('PATCH',  `/goals/${id}`, { percentage: pct })
export const deleteGoal  = (id)        => req('DELETE', `/goals/${id}`)
