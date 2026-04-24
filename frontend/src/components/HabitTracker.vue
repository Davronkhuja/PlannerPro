<template>
  <div>
    <div class="section-title">Трекер привычек</div>
    <p class="section-sub">Ежедневные привычки и статистика за год</p>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <div class="stat-grid">
      <div class="stat-card"><div class="stat-val">{{ habits.length }}</div><div class="stat-lbl">Привычек</div></div>
      <div class="stat-card"><div class="stat-val teal">{{ totalDone }}</div><div class="stat-lbl">Выполнено</div></div>
      <div class="stat-card"><div class="stat-val gold">{{ overallPct }}%</div><div class="stat-lbl">Прогресс</div></div>
      <div class="stat-card"><div class="stat-val">{{ daysInMonth }}</div><div class="stat-lbl">Дней</div></div>
    </div>

    <div class="fin-tabs">
      <button :class="['fin-tab',{active:hTab==='tracker'}]" @click="hTab='tracker'">Трекер</button>
      <button :class="['fin-tab',{active:hTab==='stats'}]" @click="switchStats">Статистика за год</button>
    </div>

    <!-- ═══ TRACKER ═══ -->
    <div v-if="hTab==='tracker'">
      <div class="month-nav">
        <button class="btn-icon" @click="changeMonth(-1)"><ChevL/></button>
        <span class="month-label">{{ MONTHS[viewMonth] }} {{ viewYear }}</span>
        <button class="btn-icon" @click="changeMonth(1)"><ChevR/></button>
      </div>

      <div class="form-row" style="margin-bottom:16px">
        <input class="inp" v-model="newHabitName" placeholder="Название новой привычки..." maxlength="40" @keyup.enter="addHabit"/>
        <button class="btn btn-primary btn-sm" @click="addHabit">+ Добавить</button>
      </div>

      <div v-if="loading && !habits.length" class="state-wrap"><div class="spinner"></div><span>Загрузка...</span></div>
      <div v-else-if="!habits.length" class="empty">Добавьте первую привычку</div>

      <div v-else>
        <!-- Grid -->
        <div class="habit-grid-outer">
          <table class="habit-table">
            <thead>
              <tr>
                <th class="th-name">Привычка</th>
                <th v-for="d in daysInMonth" :key="d" :class="['th-day',{today:isToday(d),future:isFuture(d)}]">{{ d }}</th>
                <th class="th-stat">%</th>
                <th class="th-stat">🔥</th>
                <th class="th-action"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="h in habits" :key="h.id">
                <td class="td-name">{{ h.name }}</td>
                <td v-for="d in daysInMonth" :key="d" class="td-cell">
                  <button :class="['cell-btn',{done:isDone(h,d),today:isToday(d),future:isFuture(d)}]"
                          :disabled="isFuture(d)" @click="toggleCell(h,d)"></button>
                </td>
                <td class="td-stat">{{ habitPct(h) }}%</td>
                <td class="td-stat streak">{{ habitStreak(h) }}</td>
                <td class="td-action">
                  <button class="btn-icon" @click="removeHabit(h.id)"><XIcon/></button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Monthly bar chart -->
        <div class="card" style="margin-top:16px">
          <div class="card-title">Прогресс за {{ MONTHS[viewMonth] }}</div>
          <div class="chart-wrap" style="height:200px">
            <canvas ref="monthChartRef"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ STATS ═══ -->
    <div v-if="hTab==='stats'">
      <div class="year-nav">
        <button class="btn-icon" @click="statsYear--; loadYearlyStats()"><ChevL/></button>
        <span class="month-label">{{ statsYear }} год</span>
        <button class="btn-icon" @click="statsYear++; loadYearlyStats()"><ChevR/></button>
      </div>

      <div v-if="statsLoading" class="state-wrap"><div class="spinner"></div></div>
      <div v-else>
        <!-- Yearly bar chart -->
        <div class="card" style="margin-bottom:16px">
          <div class="card-title">Прогресс по месяцам ({{ statsYear }})</div>
          <div class="chart-wrap" style="height:220px">
            <canvas ref="yearChartRef"></canvas>
          </div>
        </div>

        <!-- Monthly mini-cards -->
        <div class="months-grid">
          <div v-for="(s,i) in yearlyStats" :key="i" class="month-stat-card">
            <div class="ms-name">{{ MONTHS_SHORT[i] }}</div>
            <div class="ms-pct" :style="{color: barColor(s.pct)}">{{ s.pct }}%</div>
            <div class="progress-track" style="margin:5px 0 3px">
              <div class="progress-fill" :style="{width: s.pct+'%', background: barColor(s.pct)}"></div>
            </div>
            <div class="ms-sub">{{ s.done }}/{{ s.total }}</div>
          </div>
        </div>

        <div class="stat-grid" style="margin-top:16px">
          <div class="stat-card"><div class="stat-val teal">{{ bestMonth.pct }}%</div><div class="stat-lbl">Лучший — {{ MONTHS_SHORT[bestMonth.idx] }}</div></div>
          <div class="stat-card"><div class="stat-val gold">{{ avgYearPct }}%</div><div class="stat-lbl">Средний за год</div></div>
          <div class="stat-card"><div class="stat-val">{{ totalYearDone }}</div><div class="stat-lbl">Выполнено всего</div></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, defineComponent, h } from 'vue'
import * as api from '../api.js'
import { useChart } from '../useChart.js'

const ChevL = defineComponent({ render: () => h('svg',{width:'16',height:'16',viewBox:'0 0 16 16',fill:'none',stroke:'currentColor','stroke-width':'1.8'},[h('path',{d:'M10 3L5 8l5 5','stroke-linecap':'round','stroke-linejoin':'round'})]) })
const ChevR = defineComponent({ render: () => h('svg',{width:'16',height:'16',viewBox:'0 0 16 16',fill:'none',stroke:'currentColor','stroke-width':'1.8'},[h('path',{d:'M6 3l5 5-5 5','stroke-linecap':'round','stroke-linejoin':'round'})]) })
const XIcon = defineComponent({ render: () => h('svg',{width:'14',height:'14',viewBox:'0 0 14 14',fill:'none',stroke:'currentColor','stroke-width':'1.5'},[h('path',{d:'M2 2l10 10M12 2L2 12','stroke-linecap':'round'})]) })

const MONTHS       = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
const MONTHS_SHORT = ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек']
const PALETTE = ['#3bbcb4','#d4a04a','#8896c8','#f05a5a','#4caf7d','#e88a3b','#c77dd7','#6eb8e0','#e06ea0','#a0c878']

const now = new Date()
const habits      = ref([])
const loading     = ref(false)
const error       = ref('')
const newHabitName= ref('')
const viewYear    = ref(now.getFullYear())
const viewMonth   = ref(now.getMonth())
const hTab        = ref('tracker')
const statsYear   = ref(now.getFullYear())
const yearlyStats = ref([])
const statsLoading= ref(false)

const monthChartRef = ref(null)
const yearChartRef  = ref(null)

const daysInMonth    = computed(() => new Date(viewYear.value, viewMonth.value+1, 0).getDate())
const isCurrentMonth = computed(() => viewYear.value===now.getFullYear() && viewMonth.value===now.getMonth())
const maxDay         = computed(() => isCurrentMonth.value ? now.getDate() : daysInMonth.value)
const monthPrefix    = computed(() => `${viewYear.value}-${String(viewMonth.value+1).padStart(2,'0')}`)

function dateKey(d) { return `${viewYear.value}-${String(viewMonth.value+1).padStart(2,'0')}-${String(d).padStart(2,'0')}` }
function isToday(d) { return isCurrentMonth.value && d===now.getDate() }
function isFuture(d){ return isCurrentMonth.value && d>now.getDate() }
function isDone(h,d){ return h.logs.includes(dateKey(d)) }
function habitDone(h){ return h.logs.filter(l=>l.startsWith(monthPrefix.value)).length }
function habitPct(h) { return maxDay.value>0 ? Math.round(habitDone(h)/maxDay.value*100) : 0 }
function habitStreak(h){ let s=0; for(let d=maxDay.value;d>=1;d--){ if(h.logs.includes(dateKey(d)))s++; else break }; return s }

const totalDone  = computed(()=>habits.value.reduce((s,h)=>s+habitDone(h),0))
const overallPct = computed(()=>{ const t=habits.value.length*maxDay.value; return t>0?Math.round(totalDone.value/t*100):0 })

function barColor(pct){ return pct>=80?'#4caf7d':pct>=50?'#d4a04a':pct>0?'#f05a5a':'var(--bg3)' }

const bestMonth    = computed(()=>{ let b={pct:-1,idx:0}; yearlyStats.value.forEach((s,i)=>{if(s.pct>b.pct)b={pct:s.pct,idx:i}}); return b })
const avgYearPct   = computed(()=>{ const m=yearlyStats.value.filter(s=>s.total>0); return m.length?Math.round(m.reduce((s,x)=>s+x.pct,0)/m.length):0 })
const totalYearDone= computed(()=>yearlyStats.value.reduce((s,m)=>s+m.done,0))

// ── Monthly bar chart (per habit)
useChart(monthChartRef, () => ({
  type: 'bar',
  data: {
    labels: habits.value.map(h=>h.name),
    datasets: [{
      label: 'Выполнено %',
      data: habits.value.map(h=>habitPct(h)),
      backgroundColor: habits.value.map((_,i)=>PALETTE[i%PALETTE.length]+'cc'),
      borderColor:     habits.value.map((_,i)=>PALETTE[i%PALETTE.length]),
      borderWidth: 1.5,
      borderRadius: 6,
    }],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend:{display:false}, tooltip:{ callbacks:{ label: ctx=>' '+ctx.raw+'%' } } },
    scales: {
      x: { grid:{display:false}, ticks:{font:{size:11}, maxRotation:30} },
      y: { min:0, max:100, ticks:{callback:v=>v+'%', font:{size:11}}, grid:{color:'rgba(128,128,128,0.08)'} },
    },
  },
}), [habits, viewMonth, viewYear])

// ── Yearly bar chart
useChart(yearChartRef, () => ({
  type: 'bar',
  data: {
    labels: MONTHS_SHORT,
    datasets: [{
      label: 'Прогресс %',
      data: yearlyStats.value.map(s=>s.pct),
      backgroundColor: yearlyStats.value.map(s=>barColor(s.pct)+'bb'),
      borderColor:     yearlyStats.value.map(s=>barColor(s.pct)),
      borderWidth: 1.5,
      borderRadius: 6,
    }],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend:{display:false}, tooltip:{ callbacks:{ label: ctx=>' '+ctx.raw+'%' } } },
    scales: {
      x: { grid:{display:false} },
      y: { min:0, max:100, ticks:{callback:v=>v+'%', font:{size:11}}, grid:{color:'rgba(128,128,128,0.08)'} },
    },
  },
}), [yearlyStats])

function changeMonth(dir){
  viewMonth.value+=dir
  if(viewMonth.value>11){viewMonth.value=0;viewYear.value++}
  if(viewMonth.value<0) {viewMonth.value=11;viewYear.value--}
}

async function loadHabits(){
  loading.value=true; error.value=''
  try{ habits.value=await api.getHabits() }
  catch{ error.value='Не удалось загрузить привычки. Запущен ли сервер?' }
  finally{ loading.value=false }
}
async function loadYearlyStats(){
  statsLoading.value=true
  try{ yearlyStats.value=await api.getHabitsYearlyStats(statsYear.value) }
  catch{ error.value='Ошибка загрузки статистики' }
  finally{ statsLoading.value=false }
}
async function switchStats(){ hTab.value='stats'; await loadYearlyStats() }

async function addHabit(){
  const name=newHabitName.value.trim(); if(!name) return
  try{ habits.value.push(await api.createHabit(name)); newHabitName.value='' }
  catch{ error.value='Ошибка' }
}
async function removeHabit(id){
  try{ await api.deleteHabit(id); habits.value=habits.value.filter(h=>h.id!==id) }
  catch{ error.value='Ошибка' }
}
async function toggleCell(h,d){
  if(isFuture(d)) return
  const date=dateKey(d)
  try{
    const {done}=await api.toggleHabit(h.id,date)
    if(done) h.logs.push(date); else h.logs=h.logs.filter(l=>l!==date)
  }catch{ error.value='Ошибка' }
}

onMounted(loadHabits)
</script>

<style scoped>
.fin-tabs{display:flex;gap:2px;margin-bottom:14px;background:var(--bg2);padding:4px;border-radius:var(--r-lg)}
.fin-tab{flex:1;padding:8px 4px;border:none;background:transparent;font-family:var(--font);font-size:13px;color:var(--text2);border-radius:var(--r);cursor:pointer;transition:all .15s}
.fin-tab:hover{color:var(--text)}
.fin-tab.active{background:var(--bg);color:var(--text);font-weight:500;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.month-nav,.year-nav{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.month-label{font-size:15px;font-weight:500;color:var(--text);min-width:160px;text-align:center}
.chart-wrap{position:relative}

.habit-grid-outer{overflow-x:auto;-webkit-overflow-scrolling:touch;border:0.5px solid var(--border2);border-radius:var(--r-lg)}
.habit-table{border-collapse:collapse;font-size:12px;min-width:100%}
.habit-table th,.habit-table td{padding:0;border-bottom:0.5px solid var(--border)}
.habit-table tr:last-child td{border-bottom:none}
.th-name{position:sticky;left:0;z-index:2;background:var(--bg2);font-size:11px;font-weight:500;color:var(--text3);text-align:left;padding:8px 10px;min-width:120px;border-right:0.5px solid var(--border)}
.th-day{font-family:var(--mono);font-size:10px;color:var(--text3);text-align:center;padding:8px 2px;min-width:26px}
.th-day.today{color:var(--teal);font-weight:600}
.th-day.future{opacity:.35}
.th-stat{font-size:10px;color:var(--text3);text-align:center;padding:8px 6px;min-width:34px}
.th-action{min-width:32px}
.td-name{position:sticky;left:0;z-index:1;background:var(--bg);font-size:13px;color:var(--text);padding:6px 10px;border-right:0.5px solid var(--border);white-space:nowrap;max-width:160px;overflow:hidden;text-overflow:ellipsis}
.td-cell{text-align:center;padding:5px 2px}
.td-stat{font-family:var(--mono);font-size:11px;color:var(--text2);text-align:center;padding:6px}
.td-stat.streak{color:var(--gold);font-weight:500}
.td-action{text-align:center;padding:4px}
.cell-btn{width:20px;height:20px;border-radius:5px;border:0.5px solid var(--border2);background:var(--bg2);cursor:pointer;transition:all .12s;display:block;margin:auto;padding:0}
.cell-btn:hover:not(:disabled){background:var(--bg3)}
.cell-btn:active:not(:disabled){transform:scale(.88)}
.cell-btn.done{background:var(--teal);border-color:var(--teal)}
.cell-btn.today{border-color:var(--gold)}
.cell-btn.future{opacity:.25;cursor:default}

.months-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:8px}
.month-stat-card{background:var(--bg2);border-radius:var(--r);padding:10px;text-align:center}
.ms-name{font-size:11px;color:var(--text3);margin-bottom:2px}
.ms-pct{font-size:18px;font-weight:500;font-family:var(--mono);line-height:1.2}
.ms-sub{font-size:10px;color:var(--text3);font-family:var(--mono);margin-top:2px}
</style>