<template>
  <div class="app">
    <header class="app-header">
      <div class="logo">
        <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
          <polygon points="11,2 20,8 17,19 5,19 2,8" fill="currentColor" opacity="0.15"/>
          <polygon points="11,2 20,8 17,19 5,19 2,8" fill="none" stroke="currentColor" stroke-width="1.5"/>
          <line x1="2" y1="8" x2="20" y2="8" stroke="currentColor" stroke-width="1" opacity="0.5"/>
          <line x1="11" y1="2" x2="5" y2="19" stroke="currentColor" stroke-width="1" opacity="0.3"/>
          <line x1="11" y1="2" x2="17" y2="19" stroke="currentColor" stroke-width="1" opacity="0.3"/>
        </svg>
        Planner Pro
      </div>
      <nav class="desktop-nav">
        <button v-for="tab in tabs" :key="tab.id"
          :class="['desktop-nav-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id">
          {{ tab.label }}
        </button>
      </nav>
    </header>

    <main class="app-main">
      <HabitTracker    v-if="activeTab === 'habits'"  />
      <FinancePlanner  v-if="activeTab === 'finance'" />
      <WeeklyPlanner   v-if="activeTab === 'weekly'"  />
      <TaskListView    v-if="activeTab === 'tasks'"   />
    </main>

    <nav class="mobile-nav">
      <button v-for="tab in tabs" :key="tab.id"
        :class="['mobile-nav-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id">
        <div class="nav-icon-wrap">
          <component :is="tab.icon" class="nav-icon" />
        </div>
        <span class="nav-label">{{ tab.short }}</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref, defineComponent, h } from 'vue'
import HabitTracker   from './components/HabitTracker.vue'
import FinancePlanner from './components/FinancePlanner.vue'
import WeeklyPlanner  from './components/WeeklyPlanner.vue'
import TaskListView   from './components/TaskListView.vue'

const activeTab = ref('habits')

const IconHabit = defineComponent({ render: () => h('svg', { viewBox:'0 0 18 18', fill:'none', stroke:'currentColor', 'stroke-width':'1.5'}, [h('rect',{x:'2',y:'2',width:'14',height:'14',rx:'3'}),h('path',{d:'M5.5 9l2.5 2.5 4-4','stroke-linecap':'round','stroke-linejoin':'round'})]) })
const IconFinance = defineComponent({ render: () => h('svg', { viewBox:'0 0 18 18', fill:'none', stroke:'currentColor', 'stroke-width':'1.5'}, [h('circle',{cx:'9',cy:'9',r:'7'}),h('path',{d:'M9 5v1.5m0 5V13m-2.5-4.5c0-1.1.9-2 2-2s2 .9 2 2-.9 2-2 2-2 .9-2 2 .9 2 2 2','stroke-linecap':'round'})]) })
const IconWeekly = defineComponent({ render: () => h('svg', { viewBox:'0 0 18 18', fill:'none', stroke:'currentColor', 'stroke-width':'1.5'}, [h('rect',{x:'2',y:'3',width:'14',height:'13',rx:'2'}),h('path',{d:'M6 2v2M12 2v2M2 7h14','stroke-linecap':'round'}),h('circle',{cx:'6',cy:'11',r:'1',fill:'currentColor',stroke:'none'}),h('circle',{cx:'9',cy:'11',r:'1',fill:'currentColor',stroke:'none'}),h('circle',{cx:'12',cy:'11',r:'1',fill:'currentColor',stroke:'none'})]) })
const IconTasks = defineComponent({ render: () => h('svg', { viewBox:'0 0 18 18', fill:'none', stroke:'currentColor', 'stroke-width':'1.5'}, [h('path',{d:'M3 4h12M3 9h9M3 14h6','stroke-linecap':'round'}),h('circle',{cx:'15',cy:'13',r:'2.5'}),h('path',{d:'M14 13l.7.7 1.3-1.4','stroke-linecap':'round','stroke-linejoin':'round','stroke-width':'1.2'})]) })

const tabs = [
  { id:'habits',  label:'Привычки', short:'Привычки', icon: IconHabit   },
  { id:'finance', label:'Финансы',  short:'Финансы',  icon: IconFinance },
  { id:'weekly',  label:'Неделя',   short:'Неделя',   icon: IconWeekly  },
  { id:'tasks',   label:'Задачи',   short:'Задачи',   icon: IconTasks   },
]
</script>
