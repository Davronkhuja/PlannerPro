<template>
  <div>
    <div class="section-title">Трекер привычек</div>
    <p class="section-sub">Отслеживайте ежедневные привычки и стройте полезные ритуалы</p>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <!-- Summary stats -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-val">{{ habits.length }}</div>
        <div class="stat-lbl">Привычек</div>
      </div>
      <div class="stat-card">
        <div class="stat-val teal">{{ totalDone }}</div>
        <div class="stat-lbl">Выполнено</div>
      </div>
      <div class="stat-card">
        <div class="stat-val gold">{{ overallPct }}%</div>
        <div class="stat-lbl">Общий %</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{{ daysInMonth }}</div>
        <div class="stat-lbl">Дней</div>
      </div>
    </div>

    <!-- Month navigation -->
    <div class="month-nav">
      <button class="btn-icon nav-arrow" @click="changeMonth(-1)">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M10 3L5 8l5 5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <span class="month-label">{{ MONTHS[viewMonth] }} {{ viewYear }}</span>
      <button class="btn-icon nav-arrow" @click="changeMonth(1)">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M6 3l5 5-5 5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- Add habit -->
    <div class="form-row" style="margin-bottom:16px">
      <input
        class="inp"
        v-model="newHabitName"
        placeholder="Название новой привычки..."
        maxlength="40"
        @keyup.enter="addHabit"
      />
      <button class="btn btn-primary btn-sm" @click="addHabit" :disabled="loading">
        + Добавить
      </button>
    </div>

    <!-- Habit grid -->
    <div v-if="loading && !habits.length" class="state-wrap">
      <div class="spinner"></div>
      <span>Загрузка...</span>
    </div>

    <div v-else-if="habits.length === 0" class="empty">
      Добавьте первую привычку, чтобы начать отслеживание
    </div>

    <div v-else class="habit-grid-outer">
      <table class="habit-table">
        <thead>
          <tr>
            <th class="th-name">Привычка</th>
            <th
              v-for="d in daysInMonth"
              :key="d"
              :class="['th-day', { 'th-today': isToday(d), 'th-future': isFuture(d) }]"
            >{{ d }}</th>
            <th class="th-stat">%</th>
            <th class="th-stat">🔥</th>
            <th class="th-action"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(h, hi) in habits" :key="h.id">
            <td class="td-name">{{ h.name }}</td>
            <td
              v-for="d in daysInMonth"
              :key="d"
              class="td-cell"
            >
              <button
                :class="['cell-btn', {
                  done:   isDone(h, d),
                  today:  isToday(d),
                  future: isFuture(d)
                }]"
                :disabled="isFuture(d)"
                @click="toggleCell(h, d)"
              ></button>
            </td>
            <td class="td-stat">{{ habitPct(h) }}%</td>
            <td class="td-stat streak">{{ habitStreak(h) }}</td>
            <td class="td-action">
              <button class="btn-icon" @click="removeHabit(h.id)" title="Удалить">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M2 2l10 10M12 2L2 12" stroke-linecap="round"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as api from '../api.js'

const MONTHS = ['Январь','Февраль','Март','Апрель','Май','Июнь',
                'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']

const now = new Date()
const habits      = ref([])
const loading     = ref(false)
const error       = ref('')
const newHabitName= ref('')
const viewYear    = ref(now.getFullYear())
const viewMonth   = ref(now.getMonth())

const daysInMonth = computed(() =>
  new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
)
const isCurrentMonth = computed(() =>
  viewYear.value === now.getFullYear() && viewMonth.value === now.getMonth()
)

function dateKey(d) {
  const m = String(viewMonth.value + 1).padStart(2,'0')
  const dd= String(d).padStart(2,'0')
  return `${viewYear.value}-${m}-${dd}`
}

function isToday(d) {
  return isCurrentMonth.value && d === now.getDate()
}
function isFuture(d) {
  if (!isCurrentMonth.value) return false
  return d > now.getDate()
}
function isDone(h, d) {
  return h.logs.includes(dateKey(d))
}
function maxDay(h) {
  return isCurrentMonth.value ? now.getDate() : daysInMonth.value
}
function habitPct(h) {
  const done  = h.logs.filter(l => l.startsWith(`${viewYear.value}-${String(viewMonth.value+1).padStart(2,'0')}`)).length
  const total = maxDay(h)
  return total > 0 ? Math.round(done / total * 100) : 0
}
function habitStreak(h) {
  let streak = 0
  const max = isCurrentMonth.value ? now.getDate() : daysInMonth.value
  for (let d = max; d >= 1; d--) {
    if (h.logs.includes(dateKey(d))) streak++
    else break
  }
  return streak
}

const totalDone = computed(() => {
  const prefix = `${viewYear.value}-${String(viewMonth.value+1).padStart(2,'0')}`
  return habits.value.reduce((s, h) => s + h.logs.filter(l => l.startsWith(prefix)).length, 0)
})
const overallPct = computed(() => {
  const total = habits.value.reduce((s, h) => s + maxDay(h), 0)
  return total > 0 ? Math.round(totalDone.value / total * 100) : 0
})

function changeMonth(dir) {
  viewMonth.value += dir
  if (viewMonth.value > 11) { viewMonth.value = 0; viewYear.value++ }
  if (viewMonth.value < 0)  { viewMonth.value = 11; viewYear.value-- }
}

async function loadHabits() {
  loading.value = true; error.value = ''
  try { habits.value = await api.getHabits() }
  catch (e) { error.value = 'Не удалось загрузить привычки. Запущен ли сервер?' }
  finally { loading.value = false }
}

async function addHabit() {
  const name = newHabitName.value.trim()
  if (!name) return
  try {
    const h = await api.createHabit(name)
    habits.value.push(h)
    newHabitName.value = ''
  } catch { error.value = 'Ошибка при добавлении' }
}

async function removeHabit(id) {
  try {
    await api.deleteHabit(id)
    habits.value = habits.value.filter(h => h.id !== id)
  } catch { error.value = 'Ошибка при удалении' }
}

async function toggleCell(h, d) {
  if (isFuture(d)) return
  const date = dateKey(d)
  try {
    const { done } = await api.toggleHabit(h.id, date)
    if (done) h.logs.push(date)
    else h.logs = h.logs.filter(l => l !== date)
  } catch { error.value = 'Ошибка обновления' }
}

onMounted(loadHabits)
</script>

<style scoped>
.month-nav {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.month-label {
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
  min-width: 160px;
  text-align: center;
}
.nav-arrow { color: var(--text2); }
.nav-arrow:hover { color: var(--text); background: var(--bg2); }

.habit-grid-outer {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border: 0.5px solid var(--border2);
  border-radius: var(--r-lg);
}

.habit-table {
  border-collapse: collapse;
  font-size: 12px;
  min-width: 100%;
}

.habit-table th, .habit-table td {
  padding: 0;
  border-bottom: 0.5px solid var(--border);
}
.habit-table tr:last-child td { border-bottom: none; }

.th-name {
  position: sticky;
  left: 0;
  z-index: 2;
  background: var(--bg2);
  font-size: 11px;
  font-weight: 500;
  color: var(--text3);
  text-align: left;
  padding: 8px 10px;
  min-width: 120px;
  border-right: 0.5px solid var(--border);
}
.th-day {
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 400;
  color: var(--text3);
  text-align: center;
  padding: 8px 2px;
  min-width: 26px;
}
.th-day.th-today { color: var(--teal); font-weight: 600; }
.th-day.th-future { opacity: 0.35; }
.th-stat {
  font-size: 10px;
  color: var(--text3);
  font-weight: 400;
  text-align: center;
  padding: 8px 6px;
  min-width: 34px;
}
.th-action { min-width: 32px; }

.td-name {
  position: sticky;
  left: 0;
  z-index: 1;
  background: var(--bg);
  font-size: 13px;
  color: var(--text);
  padding: 6px 10px;
  border-right: 0.5px solid var(--border);
  white-space: nowrap;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.td-cell { text-align: center; padding: 5px 2px; }
.td-stat {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text2);
  text-align: center;
  padding: 6px;
}
.td-stat.streak { color: var(--gold); font-weight: 500; }
.td-action { text-align: center; padding: 4px; }

.cell-btn {
  width: 20px;
  height: 20px;
  border-radius: 5px;
  border: 0.5px solid var(--border2);
  background: var(--bg2);
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s, transform 0.1s;
  display: block;
  margin: auto;
  padding: 0;
}
.cell-btn:hover:not(:disabled) { background: var(--bg3); }
.cell-btn:active:not(:disabled) { transform: scale(0.88); }
.cell-btn.done {
  background: var(--teal);
  border-color: var(--teal);
}
.cell-btn.today { border-color: var(--gold); }
.cell-btn.future { opacity: 0.25; cursor: default; }
</style>
