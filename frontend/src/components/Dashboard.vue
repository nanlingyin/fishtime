<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, DataAnalysis } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import html2canvas from 'html2canvas'

const { t, locale } = useI18n()

const currentApp = ref('Loading...')
const usageData = ref([])
const chartRef = ref(null)
const whitelistDialogVisible = ref(false)
const reportDialogVisible = ref(false)
const whitelist = ref([])
const newWhitelistItem = ref('')
const processList = ref([])
const icons = ref({})
const appLimits = ref({})
const aiConfig = ref({ api_key: '', base_url: '', model: '' })
const aiCritique = ref('')
const reportLoading = ref(false)
const reportPeriod = ref('today')
const reportRef = ref(null)

let chartInstance = null
let timer = null

const toggleLanguage = () => {
  locale.value = locale.value === 'en' ? 'zh' : 'en'
  updateChart() // Refresh chart title
}

const fetchStatus = async () => {
  try {
    const res = await axios.get('/api/status')
    currentApp.value = res.data.current_app || 'None'
  } catch (e) {
    console.error(e)
  }
}

const fetchIcons = async () => {
  const promises = usageData.value.map(async (item) => {
    if (!icons.value[item.name]) {
      try {
        const res = await axios.get(`/api/icon/${encodeURIComponent(item.name)}`)
        if (res.data.image) {
          icons.value[item.name] = 'image://' + res.data.image
        } else {
          icons.value[item.name] = 'none'
        }
      } catch (e) {
        console.error(e)
        icons.value[item.name] = 'none'
      }
    }
  })
  await Promise.all(promises)
}

const fetchData = async () => {
  try {
    const res = await axios.get('/api/today')
    usageData.value = res.data
    await fetchIcons()
    updateChart()
  } catch (e) {
    console.error(e)
  }
}

const fetchWhitelist = async () => {
  try {
    const res = await axios.get('/api/whitelist')
    whitelist.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchLimits = async () => {
  try {
    const res = await axios.get('/api/limits')
    appLimits.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchAiConfig = async () => {
  try {
    const res = await axios.get('/api/ai-config')
    aiConfig.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchProcesses = async () => {
  try {
    const res = await axios.get('/api/processes')
    processList.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const saveLimits = async () => {
  try {
    await axios.post('/api/limits', appLimits.value)
    ElMessage.success(t('success'))
  } catch (e) {
    ElMessage.error(t('fail'))
  }
}

const saveAiConfig = async () => {
  try {
    await axios.post('/api/ai-config', aiConfig.value)
    ElMessage.success(t('success'))
  } catch (e) {
    ElMessage.error(t('fail'))
  }
}

const generateReport = async () => {
  reportLoading.value = true
  aiCritique.value = ''
  try {
    const res = await axios.post('/api/report/ai', { period: reportPeriod.value })
    if (res.data.error) {
      ElMessage.error(res.data.error)
      aiCritique.value = "Error: " + res.data.error
    } else {
      aiCritique.value = res.data.content
    }
  } catch (e) {
    ElMessage.error(t('fail'))
    aiCritique.value = "Failed to generate report."
  } finally {
    reportLoading.value = false
  }
}

const downloadReportImage = async () => {
  if (!reportRef.value) return
  try {
    const canvas = await html2canvas(reportRef.value, {
      backgroundColor: '#ffffff',
      scale: 2
    })
    const link = document.createElement('a')
    link.download = `FishTime-Report-${new Date().toISOString().slice(0,10)}.png`
    link.href = canvas.toDataURL()
    link.click()
  } catch (e) {
    console.error(e)
    ElMessage.error(t('fail'))
  }
}

const addToWhitelist = async () => {
  if (!newWhitelistItem.value) return
  try {
    const res = await axios.post('/api/whitelist', { item: newWhitelistItem.value })
    whitelist.value = res.data
    newWhitelistItem.value = ''
    ElMessage.success(t('add') + ' ' + t('success'))
    fetchData() // Refresh data to hide whitelisted items
  } catch (e) {
    ElMessage.error(t('fail'))
  }
}

const removeFromWhitelist = async (item) => {
  try {
    const res = await axios.delete('/api/whitelist', { data: { item } })
    whitelist.value = res.data
    ElMessage.success(t('remove') + ' ' + t('success'))
  } catch (e) {
    ElMessage.error(t('fail'))
  }
}

const updateChart = () => {
  if (!chartInstance) return
  
  const data = usageData.value.map(item => {
    const icon = icons.value[item.name]
    const hasIcon = icon && icon !== 'none'
    return {
      value: item.duration,
      name: item.name,
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          formatter: hasIcon ? '{icon|}\n{name|{b}}' : '{name|{b}}',
          rich: {
            icon: {
              backgroundColor: {
                image: icon
              },
              height: 32,
              width: 32,
              align: 'center',
              marginBottom: 5
            },
            name: {
              fontSize: 20,
              fontWeight: 'bold',
              padding: [5, 0],
              color: '#333'
            }
          }
        }
      }
    }
  })

  const option = {
    title: {
      text: t('todayUsage'),
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}s ({d}%)'
    },
    series: [
      {
        name: 'Usage',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  }
  chartInstance.setOption(option)
}

const formatDuration = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h}h ${m}m ${s}s`
}

watch(whitelistDialogVisible, (newVal) => {
  if (newVal) {
    fetchProcesses()
    fetchLimits()
    fetchAiConfig()
  }
})

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  
  fetchStatus()
  fetchData()
  fetchWhitelist()

  timer = setInterval(() => {
    fetchStatus()
    fetchData()
  }, 1000)
  
  window.addEventListener('resize', () => {
    chartInstance && chartInstance.resize()
  })
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (chartInstance) chartInstance.dispose()
})
</script>

<template>
  <div class="container">
    <el-card class="header-card">
      <div class="header-content">
        <div class="title-section">
          <img src="/favicon.ico" alt="Logo" class="logo" />
          <h1>FishTime</h1>
        </div>
        <div class="status-section">
          <span class="label">{{ t('currentApp') }}:</span>
          <el-tag size="large" effect="dark">{{ currentApp }}</el-tag>
        </div>
        <div class="actions">
          <el-button @click="toggleLanguage">{{ locale === 'en' ? '中文' : 'English' }}</el-button>
          <el-button :icon="DataAnalysis" circle @click="reportDialogVisible = true" />
          <el-button :icon="Setting" circle @click="whitelistDialogVisible = true" />
        </div>
      </div>
    </el-card>

    <div class="content">
      <el-card class="chart-card">
        <div ref="chartRef" class="chart"></div>
      </el-card>
      
      <el-card class="list-card">
        <template #header>
          <div class="card-header">
            <span>{{ t('dashboard') }}</span>
          </div>
        </template>
        <el-table :data="usageData" style="width: 100%" height="400">
          <el-table-column prop="name" :label="t('currentApp')" />
          <el-table-column :label="t('todayUsage')" width="180">
            <template #default="scope">
              {{ formatDuration(scope.row.duration) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <el-dialog v-model="whitelistDialogVisible" :title="t('settings')" width="600px">
      <el-tabs>
        <el-tab-pane :label="t('whitelist')">
          <div class="whitelist-input">
            <el-select
              v-model="newWhitelistItem"
              filterable
              allow-create
              default-first-option
              :placeholder="t('selectProcess')"
              style="width: 100%"
            >
              <el-option
                v-for="item in processList"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
            <el-button type="primary" @click="addToWhitelist" style="margin-left: 10px">{{ t('add') }}</el-button>
          </div>
          <el-divider />
          <div class="whitelist-items">
            <el-tag
              v-for="item in whitelist"
              :key="item"
              class="whitelist-tag"
              closable
              @close="removeFromWhitelist(item)"
            >
              {{ item }}
            </el-tag>
          </div>
        </el-tab-pane>
        
        <el-tab-pane :label="t('limits')">
          <div class="limits-container">
            <div v-for="item in processList" :key="item" class="limit-item">
              <span>{{ item }}</span>
              <el-input-number 
                v-model="appLimits[item]" 
                :min="0" 
                :step="10" 
                :placeholder="t('setLimit')"
                style="width: 150px"
                @change="saveLimits"
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="t('aiConfig')">
          <el-form label-width="100px">
            <el-form-item :label="t('apiKey')">
              <el-input v-model="aiConfig.api_key" type="password" show-password />
            </el-form-item>
            <el-form-item :label="t('baseUrl')">
              <el-input v-model="aiConfig.base_url" />
            </el-form-item>
            <el-form-item :label="t('model')">
              <el-input v-model="aiConfig.model" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveAiConfig">{{ t('confirm') }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <el-dialog v-model="reportDialogVisible" :title="t('aiReport')" width="800px">
      <div class="report-controls">
        <el-radio-group v-model="reportPeriod">
          <el-radio-button label="today">{{ t('today') }}</el-radio-button>
          <el-radio-button label="week">{{ t('week') }}</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="generateReport" :loading="reportLoading">{{ t('generateReport') }}</el-button>
        <el-button type="success" @click="downloadReportImage" :disabled="!aiCritique">{{ t('downloadImage') }}</el-button>
      </div>
      
      <div class="report-preview" v-if="aiCritique" ref="reportRef">
        <div class="report-header">
          <h2>FishTime Report</h2>
          <p>{{ new Date().toLocaleDateString() }}</p>
        </div>
        <div class="report-body">
          <div class="report-chart">
             <!-- Simple bar chart for report -->
             <div v-for="(item, index) in usageData.slice(0, 5)" :key="index" class="report-bar-item">
                <span class="bar-name">{{ item.name }}</span>
                <div class="bar-bg">
                  <div class="bar-fill" :style="{ width: Math.min(item.duration / (usageData[0].duration || 1) * 100, 100) + '%' }"></div>
                </div>
                <span class="bar-time">{{ formatDuration(item.duration) }}</span>
             </div>
          </div>
          <div class="report-critique">
            <h3>{{ t('critique') }}</h3>
            <p>{{ aiCritique }}</p>
          </div>
        </div>
        <div class="report-footer">
          Generated by FishTime
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
  box-sizing: border-box;
}

.header-card {
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.9) !important;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title-section h1 {
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.5px;
  margin: 0;
  background: linear-gradient(135deg, #1d1d1f 0%, #434344 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo {
  width: 48px;
  height: 48px;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}

.status-section {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0,0,0,0.03);
  padding: 8px 16px;
  border-radius: 99px;
}

.label {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 14px;
}

.content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }
}

.chart-card, .list-card {
  height: 100%;
  min-height: 500px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart {
  height: 400px;
}

.whitelist-input {
  margin-bottom: 20px;
}

.whitelist-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  min-height: 100px;
}

.limits-container {
  max-height: 400px;
  overflow-y: auto;
}

.limit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.report-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
}

.report-preview {
  border: 1px solid #ddd;
  padding: 30px;
  border-radius: 8px;
  background: linear-gradient(to bottom right, #ffffff, #f9f9f9);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.report-header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 10px;
}

.report-header h2 {
  margin: 0;
  color: #303133;
  font-size: 28px;
}

.report-header p {
  margin: 5px 0 0;
  color: #909399;
}

.report-body {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.report-bar-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.bar-name {
  width: 120px;
  font-weight: bold;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-bg {
  flex: 1;
  height: 12px;
  background: #ebeef5;
  border-radius: 6px;
  margin: 0 15px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: #409EFF;
  border-radius: 6px;
}

.bar-time {
  width: 80px;
  text-align: right;
  color: #909399;
  font-size: 12px;
}

.report-critique {
  background: #fdf6ec;
  padding: 20px;
  border-radius: 8px;
  border-left: 5px solid #e6a23c;
}

.report-critique h3 {
  margin-top: 0;
  color: #e6a23c;
}

.report-critique p {
  line-height: 1.6;
  color: #606266;
  font-size: 16px;
}

.report-footer {
  margin-top: 30px;
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
}

.empty-text {
  color: #909399;
  width: 100%;
  text-align: center;
  padding: 20px 0;
}
</style>
