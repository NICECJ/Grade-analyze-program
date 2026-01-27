import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import StudentImport from './components/StudentImport.vue'
import GradeImport from './components/GradeImport.vue'
import StandardTemplateImport from './components/StandardTemplateImport.vue'
import ManualGradeImport from './components/ManualGradeImport.vue'
import StudentAnalysis from './components/StudentAnalysis.vue'
import StudentManagement from './components/StudentManagement.vue'
import ExamList from './components/ExamList.vue'
import ExamAnalysis from './components/ExamAnalysis.vue'
import RankingAnalysis from './components/RankingAnalysis.vue'
import AdvancedRanking from './components/AdvancedRanking.vue'

const routes = [
  { path: '/', redirect: '/exam-list' },
  { path: '/student-import', component: StudentImport },
  { path: '/grade-import', component: GradeImport },
  { path: '/standard-template-import', component: StandardTemplateImport },
  { path: '/manual-grade-import', component: ManualGradeImport },
  { path: '/student-analysis', component: StudentAnalysis },
  { path: '/student-management', component: StudentManagement },
  { path: '/exam-list', component: ExamList },
  { path: '/exam-analysis', component: ExamAnalysis },
  { path: '/ranking', component: RankingAnalysis },
  { path: '/advanced-ranking', component: AdvancedRanking }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')