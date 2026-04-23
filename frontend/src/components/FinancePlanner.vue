<template>
  <div>
    <div class="section-title">Финансовый планер</div>
    <p class="section-sub">Доходы, расходы и долги — всё под контролем</p>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <!-- Summary cards -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-val teal">{{ fmt(totalInc) }}</div>
        <div class="stat-lbl">Доходы</div>
      </div>
      <div class="stat-card">
        <div class="stat-val coral">{{ fmt(totalExp) }}</div>
        <div class="stat-lbl">Расходы</div>
      </div>
      <div class="stat-card">
        <div class="stat-val coral" style="color:var(--lavender)">{{ fmt(totalDebt) }}</div>
        <div class="stat-lbl">Долги</div>
      </div>
      <div class="stat-card">
        <div :class="['stat-val', balance >= 0 ? 'teal' : 'coral']">{{ fmt(balance) }}</div>
        <div class="stat-lbl">Баланс · {{ savRate }}%</div>
      </div>
    </div>

    <!-- Balance bar -->
    <div v-if="totalInc > 0" style="margin-bottom:20px">
      <div class="balance-bar">
        <div class="balance-fill" :style="{ width: Math.min(100, Math.round((totalExp + totalDebt) / totalInc * 100)) + '%' }"></div>
      </div>
      <div class="balance-labels">
        <span>{{ Math.min(100, Math.round((totalExp + totalDebt) / totalInc * 100)) }}% потрачено + долги</span>
        <span v-if="balance > 0">{{ fmt(balance) }} свободно</span>
      </div>
    </div>

    <!-- Tab switcher -->
    <div class="fin-tabs">
      <button :class="['fin-tab', { active: finTab === 'income' }]" @click="finTab = 'income'">Доходы</button>
      <button :class="['fin-tab', { active: finTab === 'expense' }]" @click="finTab = 'expense'">Расходы</button>
      <button :class="['fin-tab', { active: finTab === 'debt' }]" @click="finTab = 'debt'">Долги</button>
      <button :class="['fin-tab', { active: finTab === 'chart' }]" @click="finTab = 'chart'">Аналитика</button>
    </div>

    <!-- Incomes -->
    <div v-if="finTab === 'income'" class="card">
      <div class="card-title">Добавить доход</div>
      <div class="form-row" style="margin-bottom:12px;flex-wrap:wrap">
        <input class="inp inp-sm" v-model="incName" placeholder="Описание..." @keyup.enter="addIncome" style="min-width:130px"/>
        <select class="inp inp-sm" v-model="incCat" style="min-width:160px">
          <option v-for="c in INC_CATS" :key="c">{{ c }}</option>
        </select>
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

    <!-- Expenses -->
    <div v-if="finTab === 'expense'" class="card">
      <div class="card-title">Добавить расход</div>
      <div class="form-row" style="margin-bottom:12px;flex-wrap:wrap">
        <input class="inp inp-sm" v-model="expName" placeholder="Описание..." @keyup.enter="addExpense" style="min-width:130px"/>
        <select class="inp inp-sm" v-model="expCat" style="min-width:160px">
          <option v-for="c in EXP_CATS" :key="c">{{ c }}</option>
        </select>
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

    <!-- Debts -->
    <div v-if="finTab === 'debt'" class="card">
      <div class="card-title">Добавить долг / обязательство</div>
      <div class="form-row" style="margin-bottom:12px;flex-wrap:wrap">
        <input class="inp inp-sm" v-model="debtName" placeholder="Описание..." @keyup.enter="addDebt" style="min-width:130px"/>
        <select class="inp inp-sm" v-model="debtCat" style="min-width:160px">
          <option v-for="c in DEBT_CATS" :key="c">{{ c }}</option>
        </select>
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

    <!-- Charts -->
    <div v-if="finTab === 'chart'">
      <div class="card" style="margin-bottom:14px" v-if="catBreakdownExp.length">
        <div class="card-title">Расходы по категориям</div>
        <div class="bar-chart">
          <div class="bar-row" v-for="(c, i) in catBreakdownExp" :key="c.name">
            <span class="bar-lbl">{{ c.name }}</span>
            <div class="bar-track"><div class="bar-fill" :style="{ width: c.pct + '%', background: COLORS[i % COLORS.length] }"></div></div>
            <span class="bar-val">{{ fmt(c.total) }}</span>
          </div>
        </div>
      </div>
      <div class="card" v-if="catBreakdownInc.length">
        <div class="card-title">Доходы по категориям</div>
        <div class="bar-chart">
          <div class="bar-row" v-for="(c, i) in catBreakdownInc" :key="c.name">
            <span class="bar-lbl">{{ c.name }}</span>
            <div class="bar-track"><div class="bar-fill" :style="{ width: c.pct + '%', background: COLORS_INC[i % COLORS_INC.length] }"></div></div>
            <span class="bar-val">{{ fmt(c.total) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h } from 'vue'
import * as api from '../api.js'

const XIcon = defineComponent({ render: () => h('svg',{width:'13',height:'13',viewBox:'0 0 13 13',fill:'none',stroke:'currentColor','stroke-width':'1.5'},[h('path',{d:'M1.5 1.5l10 10M11.5 1.5l-10 10','stroke-linecap':'round'})]) })

const INC_CATS = ['Зарплата','Премия','Фриланс','Бизнес / Дивиденды','Инвестиции & Вклады','Недвижимость','Перевод от семьи / друзей','Перевод от третьих лиц','Возврат долга','Продажа вещей','Стипендия / Грант','Социальные выплаты','Прочие поступления']
const EXP_CATS = ['Аренда жилья','Мобильная связь','Интернет','Страхование','Абонементы','Подписки','Коммуналка','Семья','Домашние животные','Личное','Уход за собой','Благотворительность','Транспорт','Такси','Еда','Кафе & Рестораны','Автомобиль','Бензин','Путешествия','Отпуск','Развлечения','Алкоголь','Сигареты','Покупки','Одежда','Маркетплейсы','Образование','Хобби','Спорт','Медицина']
const DEBT_CATS = ['Кредиты','Долги','Кредитные карты','Ипотека','Задолженности']
const COLORS = ['#f05a5a','#e88a3b','#d4a04a','#4caf7d','#3bbcb4','#8896c8','#c77dd7','#888']
const COLORS_INC = ['#3bbcb4','#4caf7d','#d4a04a','#8896c8','#3bbcb4','#e88a3b']

const incomes  = ref([])
const expenses = ref([])
const debts    = ref([])
const error    = ref('')
const finTab   = ref('income')

const incName = ref(''); const incAmt = ref(''); const incCat = ref(INC_CATS[0])
const expName = ref(''); const expAmt = ref(''); const expCat = ref(EXP_CATS[0])
const debtName= ref(''); const debtAmt= ref(''); const debtCat= ref(DEBT_CATS[0])

const totalInc  = computed(() => incomes.value.reduce((s,i) => s + i.amount, 0))
const totalExp  = computed(() => expenses.value.reduce((s,i) => s + i.amount, 0))
const totalDebt = computed(() => debts.value.reduce((s,i) => s + i.amount, 0))
const balance   = computed(() => totalInc.value - totalExp.value - totalDebt.value)
const savRate   = computed(() => totalInc.value > 0 ? Math.max(0, Math.round(balance.value / totalInc.value * 100)) : 0)

function makeCat(list) {
  const map = {}
  list.forEach(e => { map[e.category] = (map[e.category] || 0) + e.amount })
  const max = Math.max(...Object.values(map), 1)
  return Object.entries(map).sort((a,b)=>b[1]-a[1]).map(([name,total])=>({name,total,pct:Math.round(total/max*100)}))
}
const catBreakdownExp = computed(() => makeCat(expenses.value))
const catBreakdownInc = computed(() => makeCat(incomes.value))

function fmt(n) { return n.toLocaleString('ru-RU', { maximumFractionDigits: 0 }) }

async function loadAll() {
  error.value = ''
  try { [incomes.value, expenses.value, debts.value] = await Promise.all([api.getIncomes(), api.getExpenses(), api.getDebts()]) }
  catch { error.value = 'Не удалось загрузить данные. Запущен ли сервер?' }
}

async function addIncome() {
  if (!incName.value.trim() || !incAmt.value) return
  try { incomes.value.push(await api.createIncome(incName.value.trim(), Number(incAmt.value), incCat.value)); incName.value=''; incAmt.value='' }
  catch { error.value = 'Ошибка добавления' }
}
async function removeIncome(id) {
  try { await api.deleteIncome(id); incomes.value = incomes.value.filter(i=>i.id!==id) }
  catch { error.value = 'Ошибка удаления' }
}
async function addExpense() {
  if (!expName.value.trim() || !expAmt.value) return
  try { expenses.value.push(await api.createExpense(expName.value.trim(), Number(expAmt.value), expCat.value)); expName.value=''; expAmt.value='' }
  catch { error.value = 'Ошибка добавления' }
}
async function removeExpense(id) {
  try { await api.deleteExpense(id); expenses.value = expenses.value.filter(i=>i.id!==id) }
  catch { error.value = 'Ошибка удаления' }
}
async function addDebt() {
  if (!debtName.value.trim() || !debtAmt.value) return
  try { debts.value.push(await api.createDebt(debtName.value.trim(), Number(debtAmt.value), debtCat.value)); debtName.value=''; debtAmt.value='' }
  catch { error.value = 'Ошибка добавления' }
}
async function removeDebt(id) {
  try { await api.deleteDebt(id); debts.value = debts.value.filter(i=>i.id!==id) }
  catch { error.value = 'Ошибка удаления' }
}

onMounted(loadAll)
</script>

<style scoped>
.fin-tabs { display:flex; gap:2px; margin-bottom:14px; background:var(--bg2); padding:4px; border-radius:var(--r-lg); }
.fin-tab { flex:1; padding:8px 4px; border:none; background:transparent; font-family:var(--font); font-size:13px; color:var(--text2); border-radius:var(--r); cursor:pointer; transition:all 0.15s; }
.fin-tab:hover { color:var(--text); }
.fin-tab.active { background:var(--bg); color:var(--text); font-weight:500; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.balance-bar { height:6px; background:var(--bg3); border-radius:3px; overflow:hidden; margin-bottom:5px; }
.balance-fill { height:100%; background:var(--coral); border-radius:3px; transition:width 0.4s; }
.balance-labels { display:flex; justify-content:space-between; font-size:11px; color:var(--text3); }
</style>
