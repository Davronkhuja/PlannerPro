<template>
  <div>
    <div class="section-title">Недельный планер</div>
    <p class="section-sub">Задачи, цели, привычки и дневник на неделю</p>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <!-- Stats -->
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-val">{{ totalTasks }}</div><div class="stat-lbl">Задач</div></div>
      <div class="stat-card"><div class="stat-val teal">{{ doneTasks }}</div><div class="stat-lbl">Выполнено</div></div>
      <div class="stat-card"><div class="stat-val gold">{{ weekPct }}%</div><div class="stat-lbl">КПД</div></div>
      <div class="stat-card"><div class="stat-val" style="color:var(--lavender)">{{ doneGoals }}/{{ weekGoals.length }}</div><div class="stat-lbl">Целей</div></div>
    </div>

    <!-- Week nav -->
    <div class="week-nav">
      <button class="btn-icon" @click="changeWeek(-1)"><ChevronL/></button>
      <span class="week-label">{{ weekLabel }}</span>
      <button class="btn-icon" @click="changeWeek(1)"><ChevronR/></button>
    </div>

    <!-- Inner tabs -->
    <div class="fin-tabs">
      <button :class="['fin-tab',{active:wTab==='tasks'}]" @click="wTab='tasks'">Задачи</button>
      <button :class="['fin-tab',{active:wTab==='goals'}]" @click="wTab='goals'">Цели</button>
      <button :class="['fin-tab',{active:wTab==='diary'}]" @click="wTab='diary'">Дневник</button>
      <button :class="['fin-tab',{active:wTab==='annual'}]" @click="wTab='annual'">Год. цели</button>
    </div>

    <!-- TASKS TAB -->
    <div v-if="wTab==='tasks'">
      <div v-if="loading" class="state-wrap"><div class="spinner"></div><span>Загрузка...</span></div>
      <div v-else class="days-list">
        <div v-for="(date,di) in weekDates" :key="di" :class="['day-card',{today:isToday(date)}]">
          <div class="day-header">
            <div class="day-info">
              <span class="day-name" :style="isToday(date)?'color:var(--teal)':''">{{ DAYS[di] }}</span>
              <span class="day-date">{{ formatDate(date) }}</span>
            </div>
            <span class="day-count">{{ dayTasks(di).filter(t=>t.done).length }}/{{ dayTasks(di).length }}</span>
          </div>
          <div class="task-list">
            <div v-for="t in dayTasks(di)" :key="t.id" :class="['task-row',{done:t.done}]">
              <button :class="['task-check',{checked:t.done}]" @click="toggleTask(t)">
                <svg v-if="t.done" width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="2"><path d="M1.5 5l2.5 2.5 4.5-4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
              <span class="task-text">{{ t.text }}</span>
              <button class="btn-icon task-del" @click="removeTask(t)"><XIcon/></button>
            </div>
          </div>
          <div class="add-task-row">
            <input class="inp inp-sm" v-model="newTaskText[di]" placeholder="Добавить задачу..." @keyup.enter="addTask(di)"/>
            <button class="btn btn-primary btn-sm" @click="addTask(di)">+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- GOALS TAB -->
    <div v-if="wTab==='goals'">
      <div class="card" style="margin-bottom:12px">
        <div class="card-title">Цели недели</div>
        <div v-if="!weekGoals.length" class="empty">Добавьте цели на эту неделю</div>
        <div class="item-list" style="margin-bottom:12px">
          <div v-for="g in weekGoals" :key="g.id" :class="['item-row',{done:g.done}]">
            <button :class="['task-check',{checked:g.done}]" @click="toggleGoal(g)">
              <svg v-if="g.done" width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="2"><path d="M1.5 5l2.5 2.5 4.5-4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
            <span class="item-name" :style="g.done?'text-decoration:line-through;opacity:0.5':''">{{ g.text }}</span>
            <button class="btn-icon" @click="removeWeekGoal(g.id)"><XIcon/></button>
          </div>
        </div>
        <div class="form-row">
          <input class="inp inp-sm" v-model="newGoalText" placeholder="Новая цель на неделю..." @keyup.enter="addWeekGoal"/>
          <button class="btn btn-primary btn-sm" @click="addWeekGoal">+ Добавить</button>
        </div>
      </div>
    </div>

    <!-- DIARY TAB -->
    <div v-if="wTab==='diary'">
      <div class="days-list">
        <div v-for="(date, di) in weekDates" :key="di" :class="['day-card',{today:isToday(date)}]">
          <div class="day-header">
            <div class="day-info">
              <span class="day-name" :style="isToday(date)?'color:var(--teal)':''">{{ DAYS[di] }}</span>
              <span class="day-date">{{ formatDate(date) }}</span>
            </div>
          </div>
          <div class="diary-grid">
            <div class="diary-rating-row">
              <span class="diary-lbl">Сон</span>
              <div class="stars">
                <button v-for="s in 5" :key="s" :class="['star',{filled: getDiaryField(date,'sleep_rating') >= s}]" @click="setDiary(date,'sleep_rating',s)">★</button>
              </div>
            </div>
            <div class="diary-rating-row">
              <span class="diary-lbl">Энергия</span>
              <div class="stars">
                <button v-for="s in 5" :key="s" :class="['star',{filled: getDiaryField(date,'energy_rating') >= s}]" @click="setDiary(date,'energy_rating',s)">★</button>
              </div>
            </div>
            <div class="diary-rating-row">
              <span class="diary-lbl">Настроение</span>
              <div class="stars">
                <button v-for="s in 5" :key="s" :class="['star',{filled: getDiaryField(date,'mood_rating') >= s}]" @click="setDiary(date,'mood_rating',s)">★</button>
              </div>
            </div>
          </div>
          <textarea class="inp diary-inp" :value="getDiaryField(date,'lesson')" @blur="setDiaryText(date,'lesson',$event)" placeholder="Урок дня..." rows="2"></textarea>
          <textarea class="inp diary-inp" :value="getDiaryField(date,'gratitude')" @blur="setDiaryText(date,'gratitude',$event)" placeholder="Благодарность..." rows="2" style="margin-top:6px"></textarea>
          <textarea class="inp diary-inp" :value="getDiaryField(date,'note')" @blur="setDiaryText(date,'note',$event)" placeholder="Заметки дня..." rows="2" style="margin-top:6px"></textarea>
        </div>
      </div>
    </div>

    <!-- ANNUAL GOALS TAB -->
    <div v-if="wTab==='annual'" class="card">
      <div class="card-title">Годовые цели</div>
      <div v-if="!annualGoals.length" class="empty">Добавьте первую годовую цель</div>
      <div class="goals-list">
        <div class="goal-item" v-for="(g,gi) in annualGoals" :key="g.id">
          <div class="goal-row">
            <span class="goal-name">{{ g.name }}</span>
            <span class="goal-pct">{{ g.percentage }}%</span>
            <button class="btn-icon" @click="removeAnnualGoal(g.id)"><XIcon/></button>
          </div>
          <div class="progress-track" style="margin:5px 0 4px">
            <div class="progress-fill" :style="{ width: g.percentage + '%', background: COLORS[gi % COLORS.length] }"></div>
          </div>
          <input type="range" min="0" max="100" :value="g.percentage" class="goal-slider" @input="g.percentage=parseInt($event.target.value)" @change="saveAnnualGoal(g)"/>
        </div>
      </div>
      <div class="divider"></div>
      <div class="form-row">
        <input class="inp inp-sm" v-model="newAnnualName" placeholder="Название цели..." @keyup.enter="addAnnualGoal"/>
        <input class="inp inp-sm inp-num" v-model.number="newAnnualPct" type="number" min="0" max="100" placeholder="%"/>
        <button class="btn btn-primary btn-sm" @click="addAnnualGoal">+</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, defineComponent, h } from 'vue'
import * as api from '../api.js'

const XIcon    = defineComponent({ render: () => h('svg',{width:'13',height:'13',viewBox:'0 0 13 13',fill:'none',stroke:'currentColor','stroke-width':'1.5'},[h('path',{d:'M1.5 1.5l10 10M11.5 1.5l-10 10','stroke-linecap':'round'})]) })
const ChevronL = defineComponent({ render: () => h('svg',{width:'16',height:'16',viewBox:'0 0 16 16',fill:'none',stroke:'currentColor','stroke-width':'1.8'},[h('path',{d:'M10 3L5 8l5 5','stroke-linecap':'round','stroke-linejoin':'round'})]) })
const ChevronR = defineComponent({ render: () => h('svg',{width:'16',height:'16',viewBox:'0 0 16 16',fill:'none',stroke:'currentColor','stroke-width':'1.8'},[h('path',{d:'M6 3l5 5-5 5','stroke-linecap':'round','stroke-linejoin':'round'})]) })

const DAYS   = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']
const MONTHS = ['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек']
const COLORS = ['#3bbcb4','#d4a04a','#8896c8','#f05a5a','#4caf7d','#e88a3b']

const tasks       = ref([])
const weekGoals   = ref([])
const dayNotes    = ref([])
const annualGoals = ref([])
const loading     = ref(false)
const error       = ref('')
const weekOffset  = ref(0)
const wTab        = ref('tasks')

const newTaskText  = ref(Array(7).fill(''))
const newGoalText  = ref('')
const newAnnualName= ref('')
const newAnnualPct = ref(0)

function getMonday(off=0) {
  const d = new Date(); const day = d.getDay()
  const mon = new Date(d)
  mon.setDate(d.getDate() - ((day+6)%7) + off*7)
  mon.setHours(0,0,0,0)
  return mon
}

const weekStart  = computed(() => getMonday(weekOffset.value))
const weekDates  = computed(() => Array.from({length:7},(_,i)=>{ const d=new Date(weekStart.value); d.setDate(weekStart.value.getDate()+i); return d }))
const weekKey    = computed(() => { const d=weekStart.value; return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}` })
const weekLabel  = computed(() => { const s=weekDates.value[0],e=weekDates.value[6]; return `${s.getDate()} ${MONTHS[s.getMonth()]} – ${e.getDate()} ${MONTHS[e.getMonth()]} ${e.getFullYear()}` })

function isToday(d) { return d.toDateString() === new Date().toDateString() }
function formatDate(d) { return `${d.getDate()} ${MONTHS[d.getMonth()]}` }
function dateStr(d) { return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}` }
function dayTasks(di) { return tasks.value.filter(t=>t.day_index===di) }

const totalTasks = computed(()=>tasks.value.length)
const doneTasks  = computed(()=>tasks.value.filter(t=>t.done).length)
const weekPct    = computed(()=>totalTasks.value>0?Math.round(doneTasks.value/totalTasks.value*100):0)
const doneGoals  = computed(()=>weekGoals.value.filter(g=>g.done).length)

function changeWeek(d){ weekOffset.value+=d }
watch(weekKey, loadWeek)

async function loadWeek() {
  loading.value = true
  try {
    const [t, g, n] = await Promise.all([
      api.getWeeklyTasks(weekKey.value),
      api.getWeeklyGoals(weekKey.value),
      api.getDayNotes(weekKey.value),
    ])
    tasks.value     = t.map(x=>({...x,done:!!x.done}))
    weekGoals.value = g.map(x=>({...x,done:!!x.done}))
    dayNotes.value  = n
  } catch { error.value = 'Ошибка загрузки' }
  finally { loading.value = false }
}

async function loadAnnual() {
  try { annualGoals.value = await api.getGoals() } catch {}
}

// Diary helpers
function getDiaryField(date, field) {
  const ds = dateStr(date)
  const note = dayNotes.value.find(n=>n.date===ds)
  return note ? note[field] : (field.endsWith('rating') ? 0 : '')
}
function setDiary(date, field, val) {
  const ds = dateStr(date)
  let note = dayNotes.value.find(n=>n.date===ds)
  if (!note) { note={date:ds,note:'',sleep_rating:0,energy_rating:0,mood_rating:0,lesson:'',gratitude:''}; dayNotes.value.push(note) }
  note[field] = val
  saveDiary(note)
}
function setDiaryText(date, field, event) {
  setDiary(date, field, event.target.value)
}
let diaryTimers = {}
function saveDiary(note) {
  clearTimeout(diaryTimers[note.date])
  diaryTimers[note.date] = setTimeout(()=>api.upsertDayNote(note).catch(()=>{}), 500)
}

// Tasks
async function addTask(di) {
  const text = newTaskText.value[di]?.trim(); if(!text) return
  try { const t=await api.createWeeklyTask(text,di,weekKey.value); tasks.value.push({...t,done:false}); newTaskText.value[di]='' }
  catch { error.value='Ошибка' }
}
async function toggleTask(t) {
  t.done=!t.done
  try { await api.updateWeeklyTask(t.id,t.done) }
  catch { t.done=!t.done }
}
async function removeTask(t) {
  try { await api.deleteWeeklyTask(t.id); tasks.value=tasks.value.filter(x=>x.id!==t.id) }
  catch { error.value='Ошибка' }
}

// Weekly goals
async function addWeekGoal() {
  if(!newGoalText.value.trim()) return
  try { const g=await api.createWeeklyGoal(newGoalText.value.trim(),weekKey.value); weekGoals.value.push({...g,done:false}); newGoalText.value='' }
  catch { error.value='Ошибка' }
}
async function toggleGoal(g) {
  g.done=!g.done
  try { await api.updateWeeklyGoal(g.id,g.done) }
  catch { g.done=!g.done }
}
async function removeWeekGoal(id) {
  try { await api.deleteWeeklyGoal(id); weekGoals.value=weekGoals.value.filter(g=>g.id!==id) }
  catch {}
}

// Annual goals
async function addAnnualGoal() {
  if(!newAnnualName.value.trim()) return
  try { annualGoals.value.push(await api.createGoal(newAnnualName.value.trim(),Math.min(100,Math.max(0,newAnnualPct.value||0)))); newAnnualName.value=''; newAnnualPct.value=0 }
  catch {}
}
let annTimers = {}
function saveAnnualGoal(g) {
  clearTimeout(annTimers[g.id])
  annTimers[g.id]=setTimeout(()=>api.updateGoal(g.id,g.percentage).catch(()=>{}),300)
}
async function removeAnnualGoal(id) {
  try { await api.deleteGoal(id); annualGoals.value=annualGoals.value.filter(g=>g.id!==id) }
  catch {}
}

onMounted(()=>{ loadWeek(); loadAnnual() })
</script>

<style scoped>
.week-nav { display:flex; align-items:center; gap:10px; margin-bottom:14px; }
.week-label { font-size:14px; font-weight:500; flex:1; text-align:center; color:var(--text); }
.fin-tabs { display:flex; gap:2px; margin-bottom:14px; background:var(--bg2); padding:4px; border-radius:var(--r-lg); }
.fin-tab { flex:1; padding:8px 4px; border:none; background:transparent; font-family:var(--font); font-size:13px; color:var(--text2); border-radius:var(--r); cursor:pointer; transition:all 0.15s; }
.fin-tab:hover { color:var(--text); }
.fin-tab.active { background:var(--bg); color:var(--text); font-weight:500; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.days-list { display:flex; flex-direction:column; gap:8px; }
.day-card { background:var(--bg); border:0.5px solid var(--border2); border-radius:var(--r-lg); padding:12px 14px; }
.today { border-color:var(--teal); }
.day-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
.day-info { display:flex; align-items:center; gap:8px; }
.day-name { font-size:13px; font-weight:600; color:var(--text); }
.day-date { font-size:12px; color:var(--text3); }
.day-count { font-family:var(--mono); font-size:11px; color:var(--text3); background:var(--bg2); padding:2px 7px; border-radius:20px; }
.task-list { display:flex; flex-direction:column; gap:3px; margin-bottom:8px; }
.task-row { display:flex; align-items:center; gap:8px; padding:5px 6px; border-radius:7px; }
.task-row:hover { background:var(--bg2); }
.task-row.done { opacity:0.5; }
.task-check { width:16px; height:16px; border-radius:4px; border:0.5px solid var(--border2); background:var(--bg2); flex-shrink:0; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all 0.12s; padding:0; color:white; }
.task-check.checked { background:var(--teal); border-color:var(--teal); }
.task-text { flex:1; font-size:13px; color:var(--text); }
.task-row.done .task-text { text-decoration:line-through; }
.task-del { opacity:0; transition:opacity 0.12s; }
.task-row:hover .task-del { opacity:1; }
.add-task-row { display:flex; gap:6px; }
.diary-grid { display:grid; grid-template-columns:1fr; gap:6px; margin-bottom:8px; }
.diary-rating-row { display:flex; align-items:center; gap:10px; }
.diary-lbl { font-size:12px; color:var(--text2); min-width:80px; }
.stars { display:flex; gap:3px; }
.star { background:none; border:none; cursor:pointer; font-size:18px; color:var(--bg3); transition:color 0.1s; padding:0; line-height:1; }
.star.filled { color:var(--gold); }
.diary-inp { display:block; width:100%; resize:none; font-size:13px; }
.goals-list { display:flex; flex-direction:column; gap:14px; margin-bottom:4px; }
.goal-item {}
.goal-row { display:flex; align-items:center; gap:6px; margin-bottom:2px; }
.goal-name { flex:1; font-size:13px; color:var(--text); }
.goal-pct { font-family:var(--mono); font-size:12px; color:var(--text2); min-width:32px; text-align:right; }
.goal-slider { width:100%; cursor:pointer; accent-color:var(--teal); height:4px; }
</style>
