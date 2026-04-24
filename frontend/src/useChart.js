import { onBeforeUnmount, watch, nextTick } from 'vue'
import {
  Chart,
  BarController, BarElement,
  DoughnutController, ArcElement,
  LineController, LineElement, PointElement,
  CategoryScale, LinearScale,
  Tooltip, Legend, Filler,
} from 'chart.js'

Chart.register(
  BarController, BarElement,
  DoughnutController, ArcElement,
  LineController, LineElement, PointElement,
  CategoryScale, LinearScale,
  Tooltip, Legend, Filler
)

Chart.defaults.font.family = "'Inter', system-ui, sans-serif"
Chart.defaults.font.size   = 12
Chart.defaults.color       = '#888890'

export function useChart(canvasRef, configFn, deps = []) {
  let chart = null

  async function build() {
    await nextTick()
    if (!canvasRef.value) return
    if (chart) { chart.destroy(); chart = null }
    chart = new Chart(canvasRef.value, configFn())
  }

  // Watch the canvas ref itself — fires when v-if makes it appear
  watch(canvasRef, (el) => { if (el) build() }, { immediate: true })

  // Watch data deps — re-renders when data changes
  watch(deps, build, { deep: true })

  onBeforeUnmount(() => { if (chart) { chart.destroy(); chart = null } })
}