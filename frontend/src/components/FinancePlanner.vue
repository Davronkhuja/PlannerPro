<template>
  <div>
    <div class="section-title">Финансовый планер</div>
    <p class="section-sub">Доходы, расходы и долги — всё под контролем</p>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <div class="stat-grid">
      <div class="stat-card"><div class="stat-val teal">{{ fmt(totalInc) }}</div><div class="stat-lbl">Доходы</div></div>
      <div class="stat-card"><div class="stat-val coral">{{ fmt(totalExp) }}</div><div class="stat-lbl">Расходы</div></div>
      <div class="stat-card"><div class="stat-val" style="color:var(--lavender)">{{ fmt(totalDebt) }}</div><div class="stat-lbl">Долги</div></div>
      <div class="stat-card"><div :class="['stat-val',balance>=0?'teal':'coral']">{{ fmt(balance) }}</div><div class="stat-lbl">Баланс · {{ savRate }}%</div></div>
    </div>

    <!-- Balance bar -->
    <div v-if="totalInc>0" style="margin-bottom:20px">
      <div class="balance-bar"><div class="balance-fill" :style="{width:Math.min(100,Math.round((totalExp+totalDebt)/totalInc*100))+'%'}"></div></div>
      <div class="balance-labels">
        <span>{{ Math.min(100,Math.round((totalExp+totalDebt)/totalInc*100)) }}% потрачено</span>
        <span v-if="balance>0">{{ fmt(balance) }} свободно</span>
      </div>
    </div>

    <!-- Tabs -->
    <div class="fin-tabs">
      <button :class="['fin-tab',{active:finTab==='income'}]" @click="finTab='income'">Доходы</button>
      <button :class="['fin-tab',{active:finTab==='expense'}]" @click="finTab='expense'">Расходы</button>
      <button :class="['fin-tab',{active:finTab==='debt'}]" @click="finTab='debt'">Долги</button>
      <button :class="['fin-tab',{active:finTab==='chart'}]" @click="finTab='chart'">Графики</button>
    </div>

    <!-- ═══ INCOMES ═══ -->
    <div v-if="finTab==='income'" class="card">
      <div class="card-title">Добавить доход</div>
      <div class="form-row" style="margin-bottom:12px;flex-wrap:wrap">
        <input class="inp inp-sm" v-model="incName" placeholder="Описание..." @keyup.enter="addIncome" style="min-width:130px"/>
        <select class="inp inp-sm" v-model="incCat" style="min-width:160px"><option v-for="c in INC_CATS" :key="c">{{ c }}</option></select>
        <input class="inp inp-sm inp-num" v-model.number="incAmt" type="number" min="0" placeholder="Сумма" @keyup.enter="addIncome"/>
        <button class="btn btn-primary btn-sm" @click="addIncome">+ Добавить</button>
      </div>
      <div v-if="!incomes.length" class="empty">Нет записей</div>
      <div v-else class="item-list">
        <div class="item-row" v-for="item in incomes" :key="item.id">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-badge">{{ item.category }}</span>
          <span class="item-amount inc">+{{ fmt(item.amount) }}</span>
          <button class="btn-icon" @click="removeIncome(item.id)"><XIcon/></button>
        </div>
      </div>
    </div>

    <!-- ═══ EXPENSES ═══ -->
    <div v-if="finTab==='expense'" class="card">
      <div class="card-title">Добавить расход</div>
      <div class="form-row" style="margin-bottom:12px;flex-wrap:wrap">
        <input class="inp inp-sm" v-model="expName" placeholder="Описание..." @keyup.enter="addExpense" style="min-width:130px"/>
        <select class="inp inp-sm" v-model="expCat" style="min-width:160px"><option v-for="c in EXP_CATS" :key="c">{{ c }}</option></select>
        <input class="inp inp-sm inp-num" v-model.number="expAmt" type="number" min="0" placeholder="Сумма" @keyup.enter="addExpense"/>
        <button class="btn btn-primary btn-sm" @click="addExpense">+ Добавить</button>
      </div>
      <div v-if="!expenses.length" class="empty">Нет записей</div>
      <div v-else class="item-list">
        <div class="item-row" v-for="item in expenses" :key="item.id">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-badge">{{ item.category }}</span>
          <span class="item-amount exp">−{{ fmt(item.amount) }}</span>
          <button class="btn-icon" @click="removeExpense(item.id)"><XIcon/></button>
        </div>
      </div>
    </div>

    <!-- ═══ DEBTS ═══ -->
    <div v-if="finTab==='debt'" class="card">
      <div class="card-title">Долги и обязательства</div>
      <div class="form-row" style="margin-bottom:12px;flex-wrap:wrap">
        <input class="inp inp-sm" v-model="debtName" placeholder="Описание..." @keyup.enter="addDebt" style="min-width:130px"/>
        <select class="inp inp-sm" v-model="debtCat" style="min-width:160px"><option v-for="c in DEBT_CATS" :key="c">{{ c }}</option></select>
        <input class="inp inp-sm inp-num" v-model.number="debtAmt" type="number" min="0" placeholder="Сумма" @keyup.enter="addDebt"/>
        <button class="btn btn-primary btn-sm" @click="addDebt">+ Добавить</button>
      </div>
      <div v-if="!debts.length" class="empty">Нет долгов</div>
      <div v-else class="item-list">
        <div class="item-row" v-for="item in debts" :key="item.id">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-badge">{{ item.category }}</span>
          <span class="item-amount" style="color:var(--lavender)">{{ fmt(item.amount) }}</span>
          <button class="btn-icon" @click="removeDebt(item.id)"><XIcon/></button>
        </div>
      </div>
    </div>

    <!-- ═══ CHARTS ═══ -->
    <div v-if="finTab==='chart'">
      <!-- Income vs Expense bar -->
      <div class="card" style="margin-bottom:14px">
        <div class="card-title">Доходы vs Расходы vs Долги</div>
        <div class="chart-wrap" style="height:180px"><canvas ref="incExpChartRef"></canvas></div>
      </div>

      <!-- Two donuts side by side -->
      <div class="donut-row">
        <div class="card donut-card">
          <div class="card-title">Расходы по категориям</div>
          <div v-if="!expenses.length" class="empty">Нет данных</div>
          <div v-else class="chart-wrap" style="height:200px"><canvas ref="expDonutRef"></canvas></div>
          <div v-if="expenses.length" class="legend">
            <div class="leg-item" v-for="(c,i) in catBreakdownExp" :key="c.name">
              <span class="leg-dot" :style="{background:EXP_COLORS[i%EXP_COLORS.length]}"></span>
              <span class="leg-name">{{ c.name }}</span>
              <span class="leg-val">{{ fmt(c.total) }}</span>
            </div>
          </div>
        </div>

        <div class="card donut-card">
          <div class="card-title">Доходы по категориям</div>
          <div v-if="!incomes.length" class="empty">Нет данных</div>
          <div v-else class="chart-wrap" style="height:200px"><canvas ref="incDonutRef"></canvas></div>
          <div v-if="incomes.length" class="legend">
            <div class="leg-item" v-for="(c,i) in catBreakdownInc" :key="c.name">
              <span class="leg-dot" :style="{background:INC_COLORS[i%INC_COLORS.length]}"></span>
              <span class="leg-name">{{ c.name }}</span>
              <span class="leg-val">{{ fmt(c.total) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h } from 'vue'
import * as api from '../api.js'
import { useChart } from '../useChart.js'

const XIcon = defineComponent({ render: () => h('svg',{width:'13',height:'13',viewBox:'0 0 13 13',fill:'none',stroke:'currentColor','stroke-width':'1.5'},[h('path',{d:'M1.5 1.5l10 10M11.5 1.5l-10 10','stroke-linecap':'round'})]) })

const INC_CATS  = ['Зарплата','Премия','Фриланс','Бизнес / Дивиденды','Инвестиции & Вклады','Недвижимость','Перевод от семьи / друзей','Перевод от третьих лиц','Возврат долга','Продажа вещей','Стипендия / Грант','Социальные выплаты','Прочие поступления']
const EXP_CATS  = ['Аренда жилья','Мобильная связь','Интернет','Страхование','Абонементы','Подписки','Коммуналка','Семья','Домашние животные','Личное','Уход за собой','Благотворительность','Транспорт','Такси','Еда','Кафе & Рестораны','Автомобиль','Бензин','Путешествия','Отпуск','Развлечения','Алкоголь','Сигареты','Покупки','Одежда','Маркетплейсы','Образование','Хобби','Спорт','Медицина']
const DEBT_CATS = ['Кредиты','Долги','Кредитные карты','Ипотека','Задолженности']
const EXP_COLORS = ['#f05a5a','#e88a3b','#d4a04a','#4caf7d','#3bbcb4','#8896c8','#c77dd7','#6eb8e0','#e06ea0','#a0c878','#f0a05a','#5ab8f0']
const INC_COLORS = ['#3bbcb4','#4caf7d','#d4a04a','#8896c8','#3bbcb4','#e88a3b','#6eb8e0','#a0c878']

const incomes  = ref([])
const expenses = ref([])
const debts    = ref([])
const error    = ref('')
const finTab   = ref('income')

const incName=ref(''); const incAmt=ref(''); const incCat=ref(INC_CATS[0])
const expName=ref(''); const expAmt=ref(''); const expCat=ref(EXP_CATS[0])
const debtName=ref('');const debtAmt=ref('');const debtCat=ref(DEBT_CATS[0])

const incExpChartRef = ref(null)
const expDonutRef    = ref(null)
const incDonutRef    = ref(null)

const totalInc  = computed(()=>incomes.value.reduce((s,i)=>s+i.amount,0))
const totalExp  = computed(()=>expenses.value.reduce((s,i)=>s+i.amount,0))
const totalDebt = computed(()=>debts.value.reduce((s,i)=>s+i.amount,0))
const balance   = computed(()=>totalInc.value-totalExp.value-totalDebt.value)
const savRate   = computed(()=>totalInc.value>0?Math.max(0,Math.round(balance.value/totalInc.value*100)):0)

function makeCat(list,colorArr){
  const map={}; list.forEach(e=>{map[e.category]=(map[e.category]||0)+e.amount})
  return Object.entries(map).sort((a,b)=>b[1]-a[1]).map(([name,total],i)=>({name,total,color:colorArr[i%colorArr.length]}))
}
const catBreakdownExp = computed(()=>makeCat(expenses.value,EXP_COLORS))
const catBreakdownInc = computed(()=>makeCat(incomes.value,INC_COLORS))

function fmt(n){ return n.toLocaleString('ru-RU',{maximumFractionDigits:0}) }

const CHART_OPTS = { responsive:true, maintainAspectRatio:false }

// Income vs Expense vs Debt bar
useChart(incExpChartRef, ()=>({
  type:'bar',
  data:{
    labels:['Доходы','Расходы','Долги'],
    datasets:[{
      data:[totalInc.value, totalExp.value, totalDebt.value],
      backgroundColor:['#3bbcb4bb','#f05a5abb','#8896c8bb'],
      borderColor:['#3bbcb4','#f05a5a','#8896c8'],
      borderWidth:1.5, borderRadius:8,
    }],
  },
  options:{...CHART_OPTS,
    plugins:{legend:{display:false}, tooltip:{callbacks:{label:ctx=>' '+fmt(ctx.raw)}}},
    scales:{x:{grid:{display:false}}, y:{ticks:{callback:v=>fmt(v)}, grid:{color:'rgba(128,128,128,0.08)'}}},
  },
}),[incomes,expenses,debts])

// Expense donut
useChart(expDonutRef, ()=>({
  type:'doughnut',
  data:{
    labels: catBreakdownExp.value.map(c=>c.name),
    datasets:[{
      data: catBreakdownExp.value.map(c=>c.total),
      backgroundColor: catBreakdownExp.value.map(c=>c.color+'cc'),
      borderColor: catBreakdownExp.value.map(c=>c.color),
      borderWidth:1.5, hoverOffset:6,
    }],
  },
  options:{...CHART_OPTS, cutout:'68%',
    plugins:{legend:{display:false}, tooltip:{callbacks:{label:ctx=>` ${ctx.label}: ${fmt(ctx.raw)}`}}},
  },
}),[expenses])

// Income donut
useChart(incDonutRef, ()=>({
  type:'doughnut',
  data:{
    labels: catBreakdownInc.value.map(c=>c.name),
    datasets:[{
      data: catBreakdownInc.value.map(c=>c.total),
      backgroundColor: catBreakdownInc.value.map(c=>c.color+'cc'),
      borderColor: catBreakdownInc.value.map(c=>c.color),
      borderWidth:1.5, hoverOffset:6,
    }],
  },
  options:{...CHART_OPTS, cutout:'68%',
    plugins:{legend:{display:false}, tooltip:{callbacks:{label:ctx=>` ${ctx.label}: ${fmt(ctx.raw)}`}}},
  },
}),[incomes])

async function loadAll(){
  error.value=''
  try{ [incomes.value,expenses.value,debts.value]=await Promise.all([api.getIncomes(),api.getExpenses(),api.getDebts()]) }
  catch{ error.value='Не удалось загрузить данные. Запущен ли сервер?' }
}
async function addIncome(){ if(!incName.value.trim()||!incAmt.value)return; try{incomes.value.push(await api.createIncome(incName.value.trim(),Number(incAmt.value),incCat.value));incName.value='';incAmt.value=''}catch{error.value='Ошибка'} }
async function removeIncome(id){ try{await api.deleteIncome(id);incomes.value=incomes.value.filter(i=>i.id!==id)}catch{error.value='Ошибка'} }
async function addExpense(){ if(!expName.value.trim()||!expAmt.value)return; try{expenses.value.push(await api.createExpense(expName.value.trim(),Number(expAmt.value),expCat.value));expName.value='';expAmt.value=''}catch{error.value='Ошибка'} }
async function removeExpense(id){ try{await api.deleteExpense(id);expenses.value=expenses.value.filter(i=>i.id!==id)}catch{error.value='Ошибка'} }
async function addDebt(){ if(!debtName.value.trim()||!debtAmt.value)return; try{debts.value.push(await api.createDebt(debtName.value.trim(),Number(debtAmt.value),debtCat.value));debtName.value='';debtAmt.value=''}catch{error.value='Ошибка'} }
async function removeDebt(id){ try{await api.deleteDebt(id);debts.value=debts.value.filter(i=>i.id!==id)}catch{error.value='Ошибка'} }

onMounted(loadAll)
</script>

<style scoped>
.fin-tabs{display:flex;gap:2px;margin-bottom:14px;background:var(--bg2);padding:4px;border-radius:var(--r-lg)}
.fin-tab{flex:1;padding:8px 4px;border:none;background:transparent;font-family:var(--font);font-size:13px;color:var(--text2);border-radius:var(--r);cursor:pointer;transition:all .15s}
.fin-tab:hover{color:var(--text)}
.fin-tab.active{background:var(--bg);color:var(--text);font-weight:500;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.balance-bar{height:6px;background:var(--bg3);border-radius:3px;overflow:hidden;margin-bottom:5px}
.balance-fill{height:100%;background:var(--coral);border-radius:3px;transition:width .4s}
.balance-labels{display:flex;justify-content:space-between;font-size:11px;color:var(--text3)}
.chart-wrap{position:relative}
.donut-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:580px){.donut-row{grid-template-columns:1fr}}
.donut-card{}
.legend{display:flex;flex-direction:column;gap:4px;margin-top:10px;max-height:140px;overflow-y:auto}
.leg-item{display:flex;align-items:center;gap:7px;font-size:12px}
.leg-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.leg-name{flex:1;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.leg-val{font-family:var(--mono);font-size:11px;color:var(--text3)}
</style>