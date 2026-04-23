<template>
  <div>
    <div class="section-title">Трекер задач</div>
    <p class="section-sub">Все задачи с приоритетами, сроками и категориями</p>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <!-- Stats -->
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-val">{{ stats.total }}</div><div class="stat-lbl">Всего</div></div>
      <div class="stat-card"><div class="stat-val teal">{{ stats.done }}</div><div class="stat-lbl">Готово</div></div>
      <div class="stat-card"><div class="stat-val gold">{{ stats.in_progress }}</div><div class="stat-lbl">В процессе</div></div>
      <div class="stat-card"><div class="stat-val coral">{{ stats.overdue }}</div><div class="stat-lbl">Просрочено</div></div>
    </div>

    <!-- Add task -->
    <div class="card" style="margin-bottom:16px">
      <div class="card-title">Новая задача</div>
      <div class="form-row" style="margin-bottom:8px">
        <input class="inp inp-sm" v-model="newText" placeholder="Название задачи..." style="min-width:180px" @keyup.enter="addTask"/>
        <input class="inp inp-sm" v-model="newDeadline" type="date" style="min-width:130px"/>
      </div>
      <div class="form-row">
        <select class="inp inp-sm" v-model="newPriority" style="min-width:140px">
          <option v-for="p in PRIORITIES" :key="p">{{ p }}</option>
        </select>
        <select class="inp inp-sm" v-model="newStatus" style="min-width:140px">
          <option v-for="s in STATUSES" :key="s">{{ s }}</option>
        </select>
        <select class="inp inp-sm" v-model="newCategory" style="min-width:150px">
          <option v-for="c in CATEGORIES" :key="c">{{ c }}</option>
        </select>
        <button class="btn btn-primary btn-sm" @click="addTask" style="white-space:nowrap">+ Добавить</button>
      </div>
      <div style="margin-top:8px">
        <input class="inp inp-sm" v-model="newNote" placeholder="Примечание (необязательно)..." style="width:100%"/>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-row">
      <select class="inp inp-sm filter-sel" v-model="filterStatus">
        <option value="">Все статусы</option>
        <option v-for="s in STATUSES" :key="s">{{ s }}</option>
      </select>
      <select class="inp inp-sm filter-sel" v-model="filterPriority">
        <option value="">Все приоритеты</option>
        <option v-for="p in PRIORITIES" :key="p">{{ p }}</option>
      </select>
      <select class="inp inp-sm filter-sel" v-model="filterCategory">
        <option value="">Все категории</option>
        <option v-for="c in CATEGORIES" :key="c">{{ c }}</option>
      </select>
    </div>

    <!-- Task list -->
    <div v-if="loading && !tasks.length" class="state-wrap"><div class="spinner"></div><span>Загрузка...</span></div>
    <div v-else-if="!filteredTasks.length" class="empty">Нет задач</div>
    <div v-else class="tasks-list">
      <div v-for="t in filteredTasks" :key="t.id" class="task-card" :class="[priorityClass(t.priority), isOverdue(t)?'overdue':'']">
        <div class="tc-header">
          <div class="tc-title">{{ t.text }}</div>
          <button class="btn-icon" @click="deleteTask(t.id)"><XIcon/></button>
        </div>
        <div class="tc-meta">
          <span class="tc-badge pri" :style="priBadgeStyle(t.priority)">{{ t.priority }}</span>
          <span class="tc-badge cat">{{ t.category }}</span>
          <span class="tc-badge dl" v-if="t.deadline" :style="isOverdue(t)?'color:var(--coral)':''">
            📅 {{ formatDeadline(t.deadline) }}
          </span>
        </div>
        <div class="tc-status-row">
          <select class="inp inp-sm status-sel" :value="t.status" @change="changeStatus(t,$event)">
            <option v-for="s in STATUSES" :key="s">{{ s }}</option>
          </select>
          <span v-if="t.note" class="tc-note">{{ t.note }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h } from 'vue'
import * as api from '../api.js'

const XIcon = defineComponent({ render: () => h('svg',{width:'13',height:'13',viewBox:'0 0 13 13',fill:'none',stroke:'currentColor','stroke-width':'1.5'},[h('path',{d:'M1.5 1.5l10 10M11.5 1.5l-10 10','stroke-linecap':'round'})]) })

const PRIORITIES = ['🔴 Высокий','🟡 Средний','🔵 Низкий','⚪️ Необязательно']
const STATUSES   = ['⚠️ Не начато','✏️ В процессе','✅ Готово','❌ Отмена']
const CATEGORIES = ['Здоровье 💪🏻','Работа 💼','Деньги 💰','Семья 👨‍👩‍👧‍👦','Личностный рост 📚','Быт 🧹','Идеи 💡','Отдых 🎮','Духовность 🧘🏻']

const tasks    = ref([])
const stats    = ref({ total:0, done:0, in_progress:0, overdue:0, not_started:0, cancelled:0 })
const loading  = ref(false)
const error    = ref('')

const newText     = ref('')
const newDeadline = ref('')
const newPriority = ref(PRIORITIES[1])
const newStatus   = ref(STATUSES[0])
const newCategory = ref(CATEGORIES[1])
const newNote     = ref('')

const filterStatus   = ref('')
const filterPriority = ref('')
const filterCategory = ref('')

const filteredTasks = computed(() => tasks.value.filter(t =>
  (!filterStatus.value   || t.status   === filterStatus.value)   &&
  (!filterPriority.value || t.priority === filterPriority.value) &&
  (!filterCategory.value || t.category === filterCategory.value)
))

function isOverdue(t) {
  if (!t.deadline) return false
  if (['✅ Готово','❌ Отмена'].includes(t.status)) return false
  return t.deadline < new Date().toISOString().split('T')[0]
}

function formatDeadline(d) {
  if (!d) return ''
  const dt = new Date(d + 'T00:00:00')
  return `${dt.getDate()} ${['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек'][dt.getMonth()]} ${dt.getFullYear()}`
}

function priBadgeStyle(p) {
  if (p.includes('Высокий')) return 'background:rgba(240,90,90,0.12);color:var(--coral)'
  if (p.includes('Средний')) return 'background:rgba(212,160,74,0.15);color:var(--gold)'
  if (p.includes('Низкий'))  return 'background:rgba(59,188,180,0.12);color:var(--teal)'
  return 'background:var(--bg3);color:var(--text3)'
}
function priorityClass(p) {
  if (p.includes('Высокий')) return 'pri-high'
  if (p.includes('Средний')) return 'pri-mid'
  return ''
}

async function loadAll() {
  loading.value = true; error.value = ''
  try {
    [tasks.value, stats.value] = await Promise.all([api.getTaskList(), api.getTaskStats()])
  } catch { error.value = 'Не удалось загрузить задачи. Запущен ли сервер?' }
  finally { loading.value = false }
}

async function addTask() {
  if (!newText.value.trim()) return
  try {
    const t = await api.createTaskItem({
      text: newText.value.trim(),
      deadline: newDeadline.value || null,
      priority: newPriority.value,
      status: newStatus.value,
      category: newCategory.value,
      note: newNote.value.trim(),
    })
    tasks.value.push(t)
    stats.value.total++
    if (t.status === '⚠️ Не начато') stats.value.not_started++
    newText.value = ''; newDeadline.value = ''; newNote.value = ''
  } catch { error.value = 'Ошибка добавления' }
}

async function changeStatus(t, event) {
  const newStat = event.target.value
  const old = t.status
  t.status = newStat
  try {
    await api.updateTaskItem(t.id, { status: newStat })
    stats.value = await api.getTaskStats()
  } catch { t.status = old; error.value = 'Ошибка обновления' }
}

async function deleteTask(id) {
  try {
    await api.deleteTaskItem(id)
    tasks.value = tasks.value.filter(t => t.id !== id)
    stats.value = await api.getTaskStats()
  } catch { error.value = 'Ошибка удаления' }
}

onMounted(loadAll)
</script>

<style scoped>
.filters-row { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px; }
.filter-sel { min-width:120px; flex:1; }

.tasks-list { display:flex; flex-direction:column; gap:8px; }
.task-card {
  background:var(--bg);
  border:0.5px solid var(--border2);
  border-radius:var(--r-lg);
  padding:12px 14px;
  border-left:3px solid transparent;
  transition:border-color 0.15s;
}
.task-card.pri-high { border-left-color:var(--coral); }
.task-card.pri-mid  { border-left-color:var(--gold); }
.task-card.overdue  { background:rgba(240,90,90,0.03); }

.tc-header { display:flex; align-items:flex-start; gap:8px; margin-bottom:7px; }
.tc-title { flex:1; font-size:14px; font-weight:500; color:var(--text); line-height:1.4; }

.tc-meta { display:flex; flex-wrap:wrap; gap:5px; margin-bottom:8px; }
.tc-badge { font-size:11px; padding:3px 8px; border-radius:20px; background:var(--bg2); color:var(--text2); white-space:nowrap; }
.tc-badge.pri {}
.tc-badge.dl { color:var(--text3); }

.tc-status-row { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.status-sel { max-width:170px; font-size:12px; padding:5px 8px; }
.tc-note { font-size:12px; color:var(--text3); flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
</style>
