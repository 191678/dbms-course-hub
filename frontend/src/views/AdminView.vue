<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  ElCard, ElTable, ElForm, ElFormItem, ElDialog, ElSelect, ElOption,
  ElInput, ElButton, ElTag, ElStatistic, ElDescriptions, ElDescriptionsItem,
  ElMenu, ElMenuItem, ElBreadcrumb, ElBreadcrumbItem,
  ElDatePicker, ElPagination, ElProgress, ElEmpty, ElTooltip,
  ElRow, ElCol, ElSpace, ElInputNumber, ElSwitch
} from "element-plus"
import {
  DataAnalysis, User, Clock, Reading, Document, QuestionFilled, PieChart,
  Lock, Plus, Edit, Delete, Search, Download, Refresh, Warning, View, Setting, ArrowLeft,
  TrendCharts
} from "@element-plus/icons-vue"
import { adminApi } from "@/api"
import SvgChart from '@/components/SvgChart.vue'
import { useRealtime } from '@/utils/useRealtime'
import {
  studyTypeLabel, contentTypeLabel, chartTypeLabel, dataSourceLabel, masteryLabel,
  kpDifficultyLabel, roleLabel, contentStatusLabel, permissionModuleLabel, tagCategoryLabel,
  formatMinutes, relativeTime, maskStudentNo
} from '@/utils/labels'

const router = useRouter()
const activeMenu = ref('dashboard')
const menuLoading = ref(false)

const navItems = [
  { key: 'dashboard', label: '仪表盘', icon: DataAnalysis },
  { key: 'usage', label: '学生软件使用', icon: TrendCharts },
  { key: 'students', label: '学生管理', icon: User },
  { key: 'study-time', label: '学习时间管理', icon: Clock },
  { key: 'knowledge', label: '疑难知识点', icon: Reading },
  { key: 'course', label: '课程内容管理', icon: Document },
  { key: 'questions', label: '题库管理', icon: QuestionFilled },
  { key: 'viz', label: '可视化模板', icon: PieChart },
  { key: 'rbac', label: '权限管理', icon: Lock },
]

const currentTitle = computed(() => navItems.find(n => n.key === activeMenu.value)?.label || '管理后台')

type TagType = 'primary' | 'success' | 'info' | 'warning' | 'danger'

const getDifficultyTag = (d: string): { text: string; type: TagType } => {
  const map: Record<string, { text: string; type: TagType }> = {
    easy: { text: '简单', type: 'success' },
    medium: { text: '中等', type: 'warning' },
    hard: { text: '困难', type: 'danger' },
  }
  return map[d] || { text: '未标注', type: 'info' }
}

const getStatusTag = (s: string): { text: string; type: TagType } => {
  const map: Record<string, TagType> = {
    draft: 'info',
    published: 'success',
    archived: 'warning',
  }
  return { text: contentStatusLabel(s), type: map[s] || 'info' }
}

const dashboardLoading = ref(false)
const dashboardStats = ref<any>(null)

const emptyCharts = () => ({
  mastery_pie: [] as Array<{ name: string; value: number }>,
  study_trend: { dates: [] as string[], minutes: [] as number[] },
  chapter_bar: { labels: [] as string[], values: [] as number[] },
  resource_radar: { indicators: [] as Array<{ name: string; max: number }>, values: [] as number[] },
  activity_heatmap: { xLabels: [] as string[], yLabels: [] as string[], values: [] as number[][] },
})
const dashboardCharts = computed<any>(() => dashboardStats.value?.charts || emptyCharts())

const loadDashboard = async () => {
  dashboardLoading.value = true
  try {
    dashboardStats.value = await adminApi.getDashboard()
  } catch (e: any) {
    ElMessage.error('加载仪表盘失败: ' + (e?.message || '未知错误'))
  } finally {
    dashboardLoading.value = false
  }
}

const usageLoading = ref(false)
const usageDays = ref(10)
const usageOverview = ref<any>(null)

const loadUsage = async () => {
  usageLoading.value = true
  try {
    usageOverview.value = await adminApi.getUsageOverview(usageDays.value)
  } catch (e: any) {
    ElMessage.error('加载使用情况失败：' + (e?.message || '请稍后重试'))
  } finally {
    usageLoading.value = false
  }
}

// 「近期使用动态」：近 10 天窗口指标、同期对比、异常节点与知识点重灾区
const usageRecent = computed(() => usageOverview.value?.recent || {})
const usageMetrics = computed(() => usageRecent.value.metrics || {})
const usageCompareItems = computed<any[]>(() => usageRecent.value.comparison?.items || [])
const usageAnomalies = computed<any[]>(() => usageRecent.value.daily?.anomalies || [])
const usageWeakKPs = computed<any[]>(() => usageRecent.value.weak_knowledge_points || [])

const compareOf = (key: string) => usageCompareItems.value.find((item: any) => item.key === key)

const deltaText = (item: any) => {
  if (!item) return '暂无可比数据'
  const prefix = item.delta > 0 ? '+' : ''
  if (item.key === 'completion_rate') {
    return `${prefix}${item.delta} ${item.unit}`
  }
  if (item.change_percent === null || item.change_percent === undefined) {
    return `${prefix}${item.delta} ${item.unit}`
  }
  return `${prefix}${item.delta} ${item.unit}（${prefix}${item.change_percent}%）`
}

const deltaClass = (item: any) => {
  if (!item || item.trend === 'flat') return 'delta-flat'
  return item.trend === 'up' ? 'delta-up' : 'delta-down'
}

const metricValue = (key: string) => {
  const metrics = usageMetrics.value
  if (key === 'completion_rate') return `${metrics.completion_rate ?? 0}%`
  if (key === 'daily_avg_minutes') return `${metrics.daily_avg_minutes ?? 0} 分钟`
  if (key === 'feature_count') return `${metrics.feature_count ?? 0} 次`
  return `${metrics.active_students ?? 0} 人`
}

const compareValue = (item: any) => {
  if (item.key === 'completion_rate') return `${item.current}%`
  return `${item.current} ${item.unit}`
}

const comparePrevious = (item: any) => {
  if (item.key === 'completion_rate') return `${item.previous}%`
  return `${item.previous} ${item.unit}`
}

const attentionTag = (value: string): TagType => {
  if (value === '重点关注') return 'danger'
  if (value === '持续跟进') return 'warning'
  return 'success'
}

const usageFeatureData = computed(() => ({
  items: (usageOverview.value?.feature_usage || []).map((item: any) => ({ name: item.name, value: item.value }))
}))

const usageTrendData = computed(() => ({
  labels: usageOverview.value?.daily_trend?.dates || [],
  values: usageOverview.value?.daily_trend?.study_minutes || [],
  average: usageOverview.value?.daily_trend?.average_study_minutes ?? 0,
  anomalies: usageAnomalies.value,
  simulated: usageOverview.value?.daily_trend?.simulated_flags || [],
  unit: '分钟'
}))

const usageActiveStudentData = computed(() => ({
  labels: usageOverview.value?.daily_trend?.dates || [],
  values: usageOverview.value?.daily_trend?.active_students || [],
  simulated: usageOverview.value?.daily_trend?.simulated_flags || []
}))

const usageHourData = computed(() => ({
  labels: usageOverview.value?.hour_distribution?.labels || [],
  values: usageOverview.value?.hour_distribution?.values || []
}))

const usageStatusTag = (status: string): TagType => {
  const map: Record<string, TagType> = {
    '今日活跃': 'success',
    '近期活跃': 'primary',
    '活跃度一般': 'warning',
    '较久未使用': 'info',
    '尚未使用': 'info',
  }
  return map[status] || 'info'
}

const studentsLoading = ref(false)
const students = ref<any[]>([])
const studentSearch = ref('')
const studentPage = ref(1)
const studentPageSize = ref(10)
const studentTotal = ref(0)
const studentDialogVisible = ref(false)
const studentDialogMode = ref<'create' | 'edit'>('create')
const studentForm = reactive({ id: null as number | null, student_id: '', username: '', name: '', role: 'student', password: '' })

const loadStudents = async () => {
  studentsLoading.value = true
  try {
    const res: any = await adminApi.listStudents({ page: studentPage.value, page_size: studentPageSize.value, search: studentSearch.value || undefined })
    students.value = res?.items || res || []
    studentTotal.value = res?.total || students.value.length
  } catch (e: any) {
    ElMessage.error('加载学生列表失败: ' + (e?.message || '未知错误'))
  } finally {
    studentsLoading.value = false
  }
}

const openStudentDialog = (mode: 'create' | 'edit', item?: any) => {
  studentDialogMode.value = mode
  if (mode === 'edit' && item) {
    Object.assign(studentForm, { id: item.id, student_id: item.student_id || '', username: item.username || '', name: item.name || '', role: item.role || 'student', password: '' })
  } else {
    Object.assign(studentForm, { id: null, student_id: '', username: '', name: '', role: 'student', password: '' })
  }
  studentDialogVisible.value = true
}

const saveStudent = async () => {
  try {
    if (studentDialogMode.value === 'create') {
      await adminApi.createStudent(studentForm as any)
      ElMessage.success('创建学生成功')
    } else if (studentForm.id) {
      await adminApi.updateStudent(studentForm.id, studentForm as any)
      ElMessage.success('更新学生成功')
    }
    studentDialogVisible.value = false
    loadStudents()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
  }
}

const deleteStudent = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该学生吗？', '提示', { type: 'warning' })
    await adminApi.deactivateStudent(id)
    ElMessage.success('删除成功')
    loadStudents()
  } catch { /* cancelled */ }
}

const studyLoading = ref(false)
const studyRecords = ref<any[]>([])
const studyPage = ref(1)
const studyPageSize = ref(10)
const studyTotal = ref(0)
const studyDateRange = ref<string[]>([])
const studyAbnormalFilter = ref<boolean | ''>('')
const studyTypeFilter = ref('')
const studyDialogVisible = ref(false)
const studyDialogMode = ref<'create' | 'edit'>('create')
const studyForm = reactive<any>({ id: null, student_id: '', study_date: '', duration_minutes: 0, study_type: 'reading', notes: '' })

const loadStudyRecords = async () => {
  studyLoading.value = true
  try {
    const params: any = { page: studyPage.value, page_size: studyPageSize.value }
    if (studyDateRange.value?.length === 2) {
      params.start_date = studyDateRange.value[0]
      params.end_date = studyDateRange.value[1]
    }
    if (studyAbnormalFilter.value !== '') params.is_abnormal = studyAbnormalFilter.value
    if (studyTypeFilter.value) params.study_type = studyTypeFilter.value
    const res: any = await adminApi.listStudyRecords(params)
    studyRecords.value = res?.items || res || []
    studyTotal.value = res?.total || studyRecords.value.length
  } catch (e: any) {
    ElMessage.error('加载学习记录失败: ' + (e?.message || '未知错误'))
  } finally {
    studyLoading.value = false
  }
}

const openStudyDialog = (mode: 'create' | 'edit', item?: any) => {
  studyDialogMode.value = mode
  if (mode === 'edit' && item) {
    Object.assign(studyForm, { id: item.id, student_id: item.student_id, study_date: item.study_date, duration_minutes: item.duration_minutes, study_type: item.study_type, notes: item.notes || '' })
  } else {
    Object.assign(studyForm, { id: null, student_id: '', study_date: '', duration_minutes: 0, study_type: 'reading', notes: '' })
  }
  studyDialogVisible.value = true
}

const saveStudyRecord = async () => {
  try {
    if (studyDialogMode.value === 'create') {
      await adminApi.createStudyRecord(studyForm)
      ElMessage.success('创建记录成功')
    } else if (studyForm.id) {
      await adminApi.updateStudyRecord(studyForm.id, studyForm)
      ElMessage.success('更新记录成功')
    }
    studyDialogVisible.value = false
    loadStudyRecords()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
  }
}

const deleteStudyRecord = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该记录？', '提示', { type: 'warning' })
    await adminApi.deleteStudyRecord(id)
    ElMessage.success('删除成功')
    loadStudyRecords()
  } catch { /* cancelled */ }
}

const detectAnomalies = async () => {
  try {
    const res = await adminApi.detectAnomalies()
    ElMessage.success('检测完成，发现 ' + (res?.abnormal_count || 0) + ' 条异常记录')
    loadStudyRecords()
  } catch (e: any) {
    ElMessage.error('异常检测失败: ' + (e?.message || '未知错误'))
  }
}

const exportStudyRecords = async () => {
  try {
    const params: any = {}
    if (studyDateRange.value?.length === 2) {
      params.start_date = studyDateRange.value[0]
      params.end_date = studyDateRange.value[1]
    }
    const blob: any = await adminApi.exportStudyRecords(params)
    const url = window.URL.createObjectURL(new Blob([blob as any]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'study-records-' + Date.now() + '.csv'
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e: any) {
    ElMessage.error('导出失败: ' + (e?.message || '未知错误'))
  }
}

const kpTagsLoading = ref(false)
const kpTags = ref<any[]>([])
const kpStudentLoading = ref(false)
const studentKPs = ref<any[]>([])
const kpStatsLoading = ref(false)
const kpStats = ref<any>(null)
const kpTagDialogVisible = ref(false)
const kpTagForm = reactive({ id: null as number | null, name: '', category: '', color: '', description: '' })

const loadKPTags = async () => {
  kpTagsLoading.value = true
  try {
    kpTags.value = await adminApi.listKPTags()
  } catch (e: any) {
    ElMessage.error('加载标签失败: ' + (e?.message || '未知错误'))
  } finally {
    kpTagsLoading.value = false
  }
}

const openKPTagDialog = (item?: any) => {
  if (item) {
    Object.assign(kpTagForm, { id: item.id, name: item.name, category: item.category || '', color: item.color || '', description: item.description || '' })
  } else {
    Object.assign(kpTagForm, { id: null, name: '', category: '', color: '', description: '' })
  }
  kpTagDialogVisible.value = true
}

const saveKPTag = async () => {
  try {
    if (kpTagForm.id) {
      await adminApi.updateKPTag(kpTagForm.id, kpTagForm)
      ElMessage.success('更新标签成功')
    } else {
      await adminApi.createKPTag(kpTagForm)
      ElMessage.success('创建标签成功')
    }
    kpTagDialogVisible.value = false
    loadKPTags()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
  }
}

const deleteKPTag = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该标签？', '提示', { type: 'warning' })
    await adminApi.deleteKPTag(id)
    ElMessage.success('删除成功')
    loadKPTags()
  } catch { /* cancelled */ }
}

const loadStudentKPs = async () => {
  kpStudentLoading.value = true
  try {
    studentKPs.value = await adminApi.listStudentKPs()
  } catch (e: any) {
    ElMessage.error('加载学生知识点失败: ' + (e?.message || '未知错误'))
  } finally {
    kpStudentLoading.value = false
  }
}

const loadKPStats = async () => {
  kpStatsLoading.value = true
  try {
    kpStats.value = await adminApi.getStudentKPStats()
  } catch (e: any) {
    ElMessage.error('加载统计失败: ' + (e?.message || '未知错误'))
  } finally {
    kpStatsLoading.value = false
  }
}

const courseLoading = ref(false)
const courseContents = ref<any[]>([])
const coursePage = ref(1)
const coursePageSize = ref(10)
const courseTotal = ref(0)
const courseStatusFilter = ref('')
const courseSearch = ref('')
const courseDialogVisible = ref(false)
const courseDialogMode = ref<'create' | 'edit'>('create')
const courseForm = reactive<any>({ id: null, content_type: 'text', title: '', content: '', status: 'draft', chapter_id: null, knowledge_point_id: null })
const courseVersions = ref<any[]>([])
const versionDialogVisible = ref(false)

const loadCourseContents = async () => {
  courseLoading.value = true
  try {
    const params: any = { page: coursePage.value, page_size: coursePageSize.value }
    if (courseStatusFilter.value) params.status = courseStatusFilter.value
    if (courseSearch.value) params.search = courseSearch.value
    const res: any = await adminApi.listCourseContents(params)
    courseContents.value = res?.items || res || []
    courseTotal.value = res?.total || courseContents.value.length
  } catch (e: any) {
    ElMessage.error('加载课程内容失败: ' + (e?.message || '未知错误'))
  } finally {
    courseLoading.value = false
  }
}

const openCourseDialog = (mode: 'create' | 'edit', item?: any) => {
  courseDialogMode.value = mode
  if (mode === 'edit' && item) {
    Object.assign(courseForm, { id: item.id, content_type: item.content_type || 'text', title: item.title, content: item.content || '', status: item.status || 'draft', chapter_id: item.chapter_id || null, knowledge_point_id: item.knowledge_point_id || null })
  } else {
    Object.assign(courseForm, { id: null, content_type: 'text', title: '', content: '', status: 'draft', chapter_id: null, knowledge_point_id: null })
  }
  courseDialogVisible.value = true
}

const saveCourseContent = async () => {
  try {
    if (courseDialogMode.value === 'create') {
      await adminApi.createCourseContent(courseForm)
      ElMessage.success('创建成功')
    } else if (courseForm.id) {
      await adminApi.updateCourseContent(courseForm.id, courseForm)
      ElMessage.success('更新成功')
    }
    courseDialogVisible.value = false
    loadCourseContents()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
  }
}

const deleteCourseContent = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该课程内容？', '提示', { type: 'warning' })
    await adminApi.deleteCourseContent(id)
    ElMessage.success('删除成功')
    loadCourseContents()
  } catch { /* cancelled */ }
}

const publishCourseContent = async (id: number) => {
  try {
    await adminApi.publishCourseContent(id)
    ElMessage.success('发布成功')
    loadCourseContents()
  } catch (e: any) {
    ElMessage.error('发布失败: ' + (e?.message || '未知错误'))
  }
}

const archiveCourseContent = async (id: number) => {
  try {
    await adminApi.archiveCourseContent(id)
    ElMessage.success('已归档')
    loadCourseContents()
  } catch (e: any) {
    ElMessage.error('归档失败: ' + (e?.message || '未知错误'))
  }
}

const viewVersions = async (id: number) => {
  try {
    courseVersions.value = await adminApi.listContentVersions(id)
    versionDialogVisible.value = true
  } catch (e: any) {
    ElMessage.error('加载版本历史失败: ' + (e?.message || '未知错误'))
  }
}

const questionsLoading = ref(false)
const questions = ref<any[]>([])
const questionPage = ref(1)
const questionPageSize = ref(10)
const questionTotal = ref(0)
const questionTypeFilter = ref('')
const questionDifficultyFilter = ref('')
const questionDialogVisible = ref(false)
const questionDialogMode = ref<'create' | 'edit'>('create')
const questionForm = reactive<any>({ id: null, knowledge_point_id: null, type: '单选', difficulty: 'medium', stem: '', options: [] as string[], answer: '', analysis: '' })
const questionUsage = ref<any>(null)
const usageDialogVisible = ref(false)

const loadQuestions = async () => {
  questionsLoading.value = true
  try {
    const params: any = { page: questionPage.value, page_size: questionPageSize.value }
    if (questionTypeFilter.value) params.type = questionTypeFilter.value
    if (questionDifficultyFilter.value) params.difficulty = questionDifficultyFilter.value
    const res: any = await adminApi.listQuestionsAdmin(params)
    questions.value = res?.items || res || []
    questionTotal.value = res?.total || questions.value.length
  } catch (e: any) {
    ElMessage.error('加载题库失败: ' + (e?.message || '未知错误'))
  } finally {
    questionsLoading.value = false
  }
}

const openQuestionDialog = (mode: 'create' | 'edit', item?: any) => {
  questionDialogMode.value = mode
  if (mode === 'edit' && item) {
    Object.assign(questionForm, { id: item.id, knowledge_point_id: item.knowledge_point_id, type: item.type, difficulty: item.difficulty || 'medium', stem: item.stem, options: item.options || [], answer: item.answer, analysis: item.analysis || '' })
  } else {
    Object.assign(questionForm, { id: null, knowledge_point_id: null, type: '单选', difficulty: 'medium', stem: '', options: [], answer: '', analysis: '' })
  }
  questionDialogVisible.value = true
}

const saveQuestion = async () => {
  try {
    if (questionDialogMode.value === 'create') {
      await adminApi.createQuestionAdmin(questionForm)
      ElMessage.success('创建题目成功')
    } else if (questionForm.id) {
      await adminApi.updateQuestionAdmin(questionForm.id, questionForm)
      ElMessage.success('更新题目成功')
    }
    questionDialogVisible.value = false
    loadQuestions()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
  }
}

const deleteQuestion = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该题目？', '提示', { type: 'warning' })
    await adminApi.deleteQuestionAdmin(id)
    ElMessage.success('删除成功')
    loadQuestions()
  } catch { /* cancelled */ }
}

const viewQuestionUsage = async (id: number) => {
  try {
    questionUsage.value = await adminApi.getQuestionUsage(id)
    usageDialogVisible.value = true
  } catch (e: any) {
    ElMessage.error('加载使用统计失败: ' + (e?.message || '未知错误'))
  }
}

const vizLoading = ref(false)
const vizTemplates = ref<any[]>([])
const vizChartTypes = ref<any[]>([])
const vizDialogVisible = ref(false)
const vizDialogMode = ref<'create' | 'edit'>('create')
const vizForm = reactive<any>({ id: null, name: '', chart_type: '', config: {} as Record<string, unknown>, data_source: '', is_public: true, knowledge_point_id: null })

const vizPreviewVisible = ref(false)
const vizPreviewTemplate = ref<any>(null)
const openVizPreview = (item: any) => {
  vizPreviewTemplate.value = item
  vizPreviewVisible.value = true
}

// 模板预览数据：优先采用模板 config 中声明的维度标签，配合示意数值渲染
const vizPreviewData = (t: any) => {
  const cfg = (t?.config || {}) as Record<string, any>
  switch (t?.chart_type) {
    case 'pie': {
      const names: string[] = Array.isArray(cfg.series) && cfg.series.length ? cfg.series : ['掌握', '学习中', '未开始']
      const base = [42, 33, 25, 18, 12]
      return { items: names.map((n: string, i: number) => ({ name: n, value: base[i % base.length] })), colors: cfg.colors || [] }
    }
    case 'line':
      return { dates: ['1日', '5日', '10日', '15日', '20日', '25日', '30日'], values: [28, 46, 38, 62, 54, 78, 66] }
    case 'bar':
      return { labels: ['第1章', '第2章', '第3章', '第4章', '第5章', '第6章', '第7章', '第8章'], values: [12, 20, 15, 26, 18, 30, 22, 28] }
    case 'radar': {
      const inds: string[] = Array.isArray(cfg.indicators) && cfg.indicators.length ? cfg.indicators : ['基础', '进阶', '应用', '分析', '评价']
      const base = [82, 68, 74, 60, 88]
      return { indicators: inds.map((n: string) => ({ name: n, max: 100 })), values: inds.map((_: string, i: number) => base[i % base.length]) }
    }
    case 'heatmap':
      return {
        xLabels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        yLabels: ['基础', '进阶', '应用', '综合'],
        values: [[8, 12, 9, 15, 11, 6, 4], [5, 9, 7, 12, 10, 5, 3], [3, 6, 8, 10, 7, 4, 2], [2, 4, 5, 7, 6, 3, 1]],
      }
    default:
      return {}
  }
}

const loadVizTemplates = async () => {
  vizLoading.value = true
  try {
    const res: any = await adminApi.listVizTemplates()
    vizTemplates.value = res?.items || res || []
  } catch (e: any) {
    ElMessage.error('加载可视化模板失败: ' + (e?.message || '未知错误'))
  } finally {
    vizLoading.value = false
  }
}

const loadVizChartTypes = async () => {
  try {
    const res: any = await adminApi.listVizChartTypes()
    vizChartTypes.value = res?.chart_types || res || []
  } catch { /* ignore */ }
}

const openVizDialog = (mode: 'create' | 'edit', item?: any) => {
  vizDialogMode.value = mode
  if (mode === 'edit' && item) {
    Object.assign(vizForm, { id: item.id, name: item.name, chart_type: item.chart_type, config: item.config || {}, data_source: item.data_source || '', is_public: item.is_public ?? true, knowledge_point_id: item.knowledge_point_id || null })
  } else {
    Object.assign(vizForm, { id: null, name: '', chart_type: '', config: {}, data_source: '', is_public: true, knowledge_point_id: null })
  }
  vizDialogVisible.value = true
}

const saveVizTemplate = async () => {
  try {
    if (vizDialogMode.value === 'create') {
      await adminApi.createVizTemplate(vizForm)
      ElMessage.success('创建模板成功')
    } else if (vizForm.id) {
      await adminApi.updateVizTemplate(vizForm.id, vizForm)
      ElMessage.success('更新模板成功')
    }
    vizDialogVisible.value = false
    loadVizTemplates()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
  }
}

const deleteVizTemplate = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该模板？', '提示', { type: 'warning' })
    await adminApi.deleteVizTemplate(id)
    ElMessage.success('删除成功')
    loadVizTemplates()
  } catch { /* cancelled */ }
}

const rbacLoading = ref(false)
const roles = ref<any[]>([])
const permissions = ref<any[]>([])
const selectedRole = ref<any>(null)
const rbacDialogVisible = ref(false)
const rbacForm = reactive({ id: null as number | null, name: '', description: '' })
const assignPermDialogVisible = ref(false)
const assignedPermissionIds = ref<number[]>([])

const loadRoles = async () => {
  rbacLoading.value = true
  try {
    roles.value = await adminApi.listRoles()
  } catch (e: any) {
    ElMessage.error('加载角色失败: ' + (e?.message || '未知错误'))
  } finally {
    rbacLoading.value = false
  }
}

const loadPermissions = async () => {
  try {
    permissions.value = await adminApi.listPermissions()
  } catch (e: any) {
    ElMessage.error('加载权限失败: ' + (e?.message || '未知错误'))
  }
}

const openRoleDialog = (item?: any) => {
  if (item) {
    Object.assign(rbacForm, { id: item.id, name: item.name, description: item.description || '' })
  } else {
    Object.assign(rbacForm, { id: null, name: '', description: '' })
  }
  rbacDialogVisible.value = true
}

const saveRole = async () => {
  try {
    if (rbacForm.id) {
      await adminApi.updateRole(rbacForm.id, rbacForm)
      ElMessage.success('更新角色成功')
    } else {
      await adminApi.createRole(rbacForm)
      ElMessage.success('创建角色成功')
    }
    rbacDialogVisible.value = false
    loadRoles()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
  }
}

const deleteRole = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除该角色？', '提示', { type: 'warning' })
    await adminApi.deleteRole(id)
    ElMessage.success('删除成功')
    if (selectedRole.value?.id === id) selectedRole.value = null
    loadRoles()
  } catch { /* cancelled */ }
}

const openAssignPermDialog = async (role: any) => {
  selectedRole.value = role
  assignedPermissionIds.value = role.permissions?.map((p: any) => p.id) || []
  assignPermDialogVisible.value = true
}

const assignPermissions = async () => {
  try {
    if (selectedRole.value) {
      await adminApi.assignRolePermissions(selectedRole.value.id, assignedPermissionIds.value)
      ElMessage.success('权限分配成功')
      assignPermDialogVisible.value = false
      loadRoles()
    }
  } catch (e: any) {
    ElMessage.error('权限分配失败: ' + (e?.message || '未知错误'))
  }
}

const initRbac = async () => {
  try {
    await adminApi.initRbac()
    ElMessage.success('RBAC 初始化成功')
    loadRoles()
    loadPermissions()
  } catch (e: any) {
    ElMessage.error('初始化失败: ' + (e?.message || '未知错误'))
  }
}

const refreshCurrentView = () => {
  switch (activeMenu.value) {
    case 'dashboard': loadDashboard(); break
    case 'usage': loadUsage(); break
    case 'students': loadStudents(); break
    case 'study-time': loadStudyRecords(); break
    case 'knowledge': loadKPTags(); loadStudentKPs(); loadKPStats(); break
    case 'course': loadCourseContents(); break
    case 'questions': loadQuestions(); break
    case 'viz': loadVizTemplates(); loadVizChartTypes(); break
    case 'rbac': loadRoles(); loadPermissions(); break
  }
}

const handleMenuSelect = (key: string) => {
  activeMenu.value = key
  menuLoading.value = true
  setTimeout(() => {
    refreshCurrentView()
    menuLoading.value = false
  }, 50)
}

onMounted(() => {
  refreshCurrentView()
})

// 数据变化后自动刷新当前模块（1 秒内完成，无需手动刷新）
const { connected: rtConnected, channel: rtChannel, lastSyncAt: rtLastSyncAt } = useRealtime(() => {
  if (document.hidden) return
  if (studentDialogVisible.value || studyDialogVisible.value || courseDialogVisible.value
      || questionDialogVisible.value || vizDialogVisible.value || rbacDialogVisible.value
      || kpTagDialogVisible.value) {
    return
  }
  refreshCurrentView()
})

const rtStatusText = computed(() => {
  if (!rtConnected.value) return '连接中断，自动重连中…'
  if (rtChannel.value === 'websocket') return '实时同步 · WebSocket'
  if (rtChannel.value === 'sse') return '实时同步 · SSE'
  return '实时同步 · 轮询'
})
</script>

<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <DataAnalysis class="logo-icon" />
        <span>管理后台</span>
      </div>
      <ElMenu :default-active="activeMenu" class="sidebar-menu"
        background-color="#001529" text-color="#b7bdc6"
        active-text-color="#409EFF" @select="handleMenuSelect">
        <ElMenuItem v-for="item in navItems" :key="item.key" :index="item.key">
          <component :is="item.icon" class="menu-icon" />
          <span>{{ item.label }}</span>
        </ElMenuItem>
      </ElMenu>
      <div class="sidebar-footer">
        <ElButton link @click="router.back()"><ArrowLeft style="margin-right:4px"/> 返回前台</ElButton>
      </div>
    </aside>
    <main class="admin-main">
      <header class="admin-header">
        <ElBreadcrumb separator="/">
          <ElBreadcrumbItem>首页</ElBreadcrumbItem>
          <ElBreadcrumbItem>{{ currentTitle }}</ElBreadcrumbItem>
        </ElBreadcrumb>
        <div class="header-actions">
          <div class="rt-status" :class="{ offline: !rtConnected }" :title="rtLastSyncAt ? `最近同步 ${rtLastSyncAt}` : ''">
            <span class="rt-dot"></span>
            {{ rtStatusText }}
          </div>
          <ElTooltip content="刷新">
            <ElButton circle @click="refreshCurrentView"><Refresh /></ElButton>
          </ElTooltip>
        </div>
      </header>
      <div class="admin-content" v-loading="menuLoading">
        <!-- ======== Dashboard ======== -->
        <div v-if="activeMenu === 'dashboard'">
          <ElRow :gutter="16" class="stat-cards">
            <ElCol :xs="24" :sm="12" :md="6">
              <ElCard shadow="hover" class="stat-card">
                <ElStatistic title="学生总数" :value="dashboardStats?.student_count || 0" :loading="dashboardLoading">
                  <template #prefix><User class="stat-icon" style="color:#409EFF" /></template>
                </ElStatistic>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :sm="12" :md="6">
              <ElCard shadow="hover" class="stat-card">
                <ElStatistic title="今日学习时长(分钟)" :value="dashboardStats?.today_study_minutes || 0" :loading="dashboardLoading">
                  <template #prefix><Clock class="stat-icon" style="color:#67c23a" /></template>
                </ElStatistic>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :sm="12" :md="6">
              <ElCard shadow="hover" class="stat-card">
                <ElStatistic title="异常记录" :value="dashboardStats?.abnormal_records_count || 0" :loading="dashboardLoading">
                  <template #prefix><Warning class="stat-icon" style="color:#e6a23c" /></template>
                </ElStatistic>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :sm="12" :md="6">
              <ElCard shadow="hover" class="stat-card">
                <ElStatistic title="已掌握知识点" :value="dashboardStats?.mastered_knowledge_points_count || 0" :loading="dashboardLoading">
                  <template #prefix><Reading class="stat-icon" style="color:#f56c6c" /></template>
                </ElStatistic>
              </ElCard>
            </ElCol>
          </ElRow>
          <ElRow :gutter="16" style="margin-top: 16px">
            <ElCol :xs="24" :md="12">
              <ElCard shadow="hover">
                <template #header><span>平台概览</span></template>
                <ElDescriptions :column="2" border v-loading="dashboardLoading">
                  <ElDescriptionsItem label="章节总数">{{ dashboardStats?.chapters_count || 0 }}</ElDescriptionsItem>
                  <ElDescriptionsItem label="知识点总数">{{ dashboardStats?.knowledge_points_count || 0 }}</ElDescriptionsItem>
                  <ElDescriptionsItem label="题库总数">{{ dashboardStats?.questions_count || 0 }}</ElDescriptionsItem>
                  <ElDescriptionsItem label="课程内容">{{ dashboardStats?.course_contents_count || 0 }}</ElDescriptionsItem>
                  <ElDescriptionsItem label="学习记录">{{ dashboardStats?.study_records_count || 0 }}</ElDescriptionsItem>
                  <ElDescriptionsItem label="管理员数">{{ dashboardStats?.admin_count || 0 }}</ElDescriptionsItem>
                </ElDescriptions>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :md="12">
              <ElCard shadow="hover">
                <template #header><span>学生学习功能使用情况</span></template>
                <div v-if="dashboardStats?.module_usage?.length">
                  <div v-for="item in dashboardStats.module_usage" :key="item.name" class="module-activity">
                    <span class="module-name">{{ item.name }}</span>
                    <ElProgress :percentage="item.percentage" :stroke-width="14" :text-inside="true" />
                  </div>
                </div>
                <ElEmpty v-else description="暂无功能使用数据" />
              </ElCard>
            </ElCol>
          </ElRow>

          <ElRow :gutter="16" style="margin-top: 16px">
            <ElCol :xs="24" :md="8">
              <ElCard shadow="hover" v-loading="dashboardLoading">
                <template #header><span>知识点掌握度分布</span></template>
                <SvgChart type="pie" :data="dashboardCharts.mastery_pie" :height="240" />
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :md="16">
              <ElCard shadow="hover" v-loading="dashboardLoading">
                <template #header><span>近 7 日学习时长趋势（分钟）</span></template>
                <SvgChart type="line" :data="{ labels: dashboardCharts.study_trend.dates, values: dashboardCharts.study_trend.minutes }" :height="240" />
              </ElCard>
            </ElCol>
          </ElRow>
          <ElRow :gutter="16" style="margin-top: 16px">
            <ElCol :xs="24" :md="12">
              <ElCard shadow="hover" v-loading="dashboardLoading">
                <template #header><span>各章学习记录数</span></template>
                <SvgChart type="bar" :data="dashboardCharts.chapter_bar" :height="240" />
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :md="12">
              <ElCard shadow="hover" v-loading="dashboardLoading">
                <template #header><span>平台资源分布</span></template>
                <SvgChart type="radar" :data="dashboardCharts.resource_radar" :height="240" />
              </ElCard>
            </ElCol>
          </ElRow>
          <ElRow :gutter="16" style="margin-top: 16px">
            <ElCol :span="24">
              <ElCard shadow="hover" v-loading="dashboardLoading">
                <template #header><span>学习活跃热力图（星期 × 学习类型）</span></template>
                <SvgChart type="heatmap" :data="dashboardCharts.activity_heatmap" :height="220" />
              </ElCard>
            </ElCol>
          </ElRow>
        </div>
        <!-- ======== Usage ======== -->
        <div v-else-if="activeMenu === 'usage'">
          <ElRow :gutter="16" class="stat-cards">
            <ElCol :xs="24" :sm="12" :md="6">
              <ElCard shadow="hover" class="stat-card">
                <ElStatistic title="今日活跃学生" :value="usageOverview?.summary?.today_active_students || 0" :loading="usageLoading">
                  <template #prefix><User class="stat-icon" style="color:#409EFF" /></template>
                </ElStatistic>
                <div class="stat-hint">累计活跃 {{ usageOverview?.summary?.active_students || 0 }} 人</div>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :sm="12" :md="6">
              <ElCard shadow="hover" class="stat-card">
                <ElStatistic title="累计学习时长" :value="formatMinutes(usageOverview?.summary?.total_study_minutes || 0)" :loading="usageLoading">
                  <template #prefix><Clock class="stat-icon" style="color:#67c23a" /></template>
                </ElStatistic>
                <div class="stat-hint">按学习记录累计统计</div>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :sm="12" :md="6">
              <ElCard shadow="hover" class="stat-card">
                <ElStatistic title="人均学习时长" :value="formatMinutes(usageOverview?.summary?.avg_minutes_per_student || 0)" :loading="usageLoading">
                  <template #prefix><Reading class="stat-icon" style="color:#e6a23c" /></template>
                </ElStatistic>
                <div class="stat-hint">仅统计有使用行为的学生</div>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :sm="12" :md="6">
              <ElCard shadow="hover" class="stat-card">
                <ElStatistic title="功能交互次数" :value="usageOverview?.summary?.interaction_count || 0" :loading="usageLoading">
                  <template #prefix><TrendCharts class="stat-icon" style="color:#f56c6c" /></template>
                </ElStatistic>
                <div class="stat-hint">近 {{ usageDays }} 天覆盖 {{ usageOverview?.summary?.feature_count || 0 }} 个学习功能</div>
              </ElCard>
            </ElCol>
          </ElRow>

          <ElCard shadow="never" class="recent-section" style="margin-top: 16px" v-loading="usageLoading">
            <template #header>
              <div class="card-header">
                <span>近期使用动态</span>
                <span class="section-range">
                  {{ usageRecent?.range?.label || '近 10 天（含今日）' }}
                  {{ usageRecent?.range?.start_date || '' }} 至 {{ usageRecent?.range?.end_date || '' }}
                  · 同期对比 {{ usageRecent?.range?.previous_start_date || '' }} 至 {{ usageRecent?.range?.previous_end_date || '' }}
                </span>
              </div>
            </template>

            <ElRow :gutter="16">
              <ElCol :xs="24" :sm="12" :md="6">
                <div class="recent-metric">
                  <div class="recent-metric-label">活跃学生数</div>
                  <div class="recent-metric-value">{{ metricValue('active_students') }}</div>
                  <div class="recent-metric-delta" :class="deltaClass(compareOf('active_students'))">
                    环比 {{ deltaText(compareOf('active_students')) }}
                  </div>
                </div>
              </ElCol>
              <ElCol :xs="24" :sm="12" :md="6">
                <div class="recent-metric">
                  <div class="recent-metric-label">功能模块使用频次</div>
                  <div class="recent-metric-value">{{ metricValue('feature_count') }}</div>
                  <div class="recent-metric-delta" :class="deltaClass(compareOf('feature_count'))">
                    环比 {{ deltaText(compareOf('feature_count')) }}
                  </div>
                </div>
              </ElCol>
              <ElCol :xs="24" :sm="12" :md="6">
                <div class="recent-metric">
                  <div class="recent-metric-label">日均使用时长</div>
                  <div class="recent-metric-value">{{ metricValue('daily_avg_minutes') }}</div>
                  <div class="recent-metric-delta" :class="deltaClass(compareOf('daily_avg_minutes'))">
                    环比 {{ deltaText(compareOf('daily_avg_minutes')) }}
                  </div>
                </div>
              </ElCol>
              <ElCol :xs="24" :sm="12" :md="6">
                <div class="recent-metric">
                  <div class="recent-metric-label">关键操作完成率</div>
                  <div class="recent-metric-value">{{ metricValue('completion_rate') }}</div>
                  <div class="recent-metric-delta" :class="deltaClass(compareOf('completion_rate'))">
                    环比 {{ deltaText(compareOf('completion_rate')) }}
                  </div>
                </div>
              </ElCol>
            </ElRow>

            <ElRow :gutter="16" style="margin-top: 18px">
              <ElCol :xs="24" :lg="14">
                <div class="chart-title">
                  每日学习时长趋势（分钟）
                  <span class="chart-sub">虚线为整体日均值 {{ usageRecent?.daily?.average_study_minutes ?? 0 }} 分钟，红色节点为异常波动</span>
                </div>
                <SvgChart type="line" :data="usageTrendData" :height="280" />
                <div v-if="usageRecent?.daily?.has_simulated" class="sim-legend">
                  <span class="sim-dot"></span>
                  橙色空心点为模拟填充数据（{{ usageRecent?.daily?.simulated_days ?? 0 }} 个无真实记录的日期），仅用于保持时间轴连续，不计入统计指标
                </div>
                <div class="anomaly-list">
                  <span class="anomaly-title">异常波动节点：</span>
                  <template v-if="usageAnomalies.length">
                    <ElTag
                      v-for="item in usageAnomalies"
                      :key="item.index"
                      size="small"
                      :type="item.direction === 'up' ? 'danger' : 'info'"
                    >
                      {{ item.date }}（{{ item.weekday }}）{{ item.value }} 分钟，{{ item.direction === 'up' ? '高于' : '低于' }}均值 {{ Math.abs(item.deviation) }} 分钟
                    </ElTag>
                  </template>
                  <span v-else class="anomaly-none">近 10 天无显著异常波动</span>
                </div>
              </ElCol>
              <ElCol :xs="24" :lg="10">
                <div class="chart-title">近 10 天与同期对比</div>
                <ElTable :data="usageCompareItems" size="small" stripe class="compare-table">
                  <ElTableColumn prop="label" label="指标" min-width="120" />
                  <ElTableColumn label="近 10 天" width="100" align="right">
                    <template #default="{ row }">{{ compareValue(row) }}</template>
                  </ElTableColumn>
                  <ElTableColumn label="前 10 天" width="100" align="right">
                    <template #default="{ row }">{{ comparePrevious(row) }}</template>
                  </ElTableColumn>
                  <ElTableColumn label="变化" min-width="150">
                    <template #default="{ row }">
                      <span :class="deltaClass(row)">{{ deltaText(row) }}</span>
                    </template>
                  </ElTableColumn>
                </ElTable>
              </ElCol>
            </ElRow>

            <div class="recent-basis">
              统计依据：近 10 天学习行为记录 {{ usageRecent?.basis?.learning_records ?? 0 }} 条、学习时长记录
              {{ usageRecent?.basis?.study_records ?? 0 }} 条、助教问答记录 {{ usageRecent?.basis?.chat_records ?? 0 }} 条；
              前 10 天对应 {{ usageRecent?.basis?.previous_learning_records ?? 0 }} /
              {{ usageRecent?.basis?.previous_study_records ?? 0 }} /
              {{ usageRecent?.basis?.previous_chat_records ?? 0 }} 条。
              关键操作完成率 = 产生实际学习时长的学习行为记录占比；
              图表中无真实记录的日期以模拟值填充（空心点/浅色柱），仅用于保持时间轴连续，不计入统计指标。
            </div>
          </ElCard>

          <ElRow :gutter="16" style="margin-top: 16px">
            <ElCol :xs="24" :lg="10">
              <ElCard shadow="hover" v-loading="usageLoading">
                <template #header><span>近 10 天功能模块使用频次</span></template>
                <SvgChart type="pie" :data="usageFeatureData" :height="280" />
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :lg="14">
              <ElCard shadow="hover" v-loading="usageLoading">
                <template #header>
                  <span>每日活跃学生数（近 10 天）</span>
                  <span v-if="usageRecent?.daily?.has_simulated" class="chart-sub">浅色虚线框柱为模拟填充数据</span>
                </template>
                <SvgChart type="bar" :data="usageActiveStudentData" :height="280" />
              </ElCard>
            </ElCol>
          </ElRow>

          <ElRow :gutter="16" style="margin-top: 16px">
            <ElCol :xs="24" :md="12">
              <ElCard shadow="hover" v-loading="usageLoading">
                <template #header><span>使用时段分布（近 10 天）</span></template>
                <SvgChart type="bar" :data="usageHourData" :height="240" />
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :md="12">
              <ElCard shadow="hover" v-loading="usageLoading">
                <template #header><span>学生知识点重灾区</span></template>
                <ElTable :data="usageWeakKPs" size="small" stripe max-height="240">
                  <ElTableColumn prop="content" label="知识点" min-width="150" show-overflow-tooltip />
                  <ElTableColumn prop="chapter_title" label="所属章节" width="110" show-overflow-tooltip />
                  <ElTableColumn label="掌握率" width="110">
                    <template #default="{ row }">
                      <ElProgress :percentage="row.mastery_rate" :stroke-width="10" :show-text="false"
                        :color="row.mastery_rate < 25 ? '#F56C6C' : row.mastery_rate < 50 ? '#E6A23C' : '#67C23A'" />
                      <span class="weak-rate">{{ row.mastery_rate }}%</span>
                    </template>
                  </ElTableColumn>
                  <ElTableColumn prop="not_mastered_count" label="未掌握" width="80" align="center" />
                  <ElTableColumn label="关注等级" width="100">
                    <template #default="{ row }">
                      <ElTag size="small" :type="attentionTag(row.attention)">{{ row.attention }}</ElTag>
                    </template>
                  </ElTableColumn>
                </ElTable>
              </ElCard>
            </ElCol>
          </ElRow>

          <ElCard shadow="never" style="margin-top: 16px">
            <template #header>
              <div class="card-header">
                <span>学生使用明细</span>
                <ElTag type="info" size="small">累计口径</ElTag>
              </div>
            </template>
            <ElTable :data="usageOverview?.student_usage || []" v-loading="usageLoading" stripe max-height="480">
              <ElTableColumn label="学生" min-width="180">
                <template #default="{ row }">
                  <div class="usage-student">
                    <span class="usage-name">{{ row.name }}</span>
                    <span class="usage-no">{{ row.student_no }}</span>
                  </div>
                </template>
              </ElTableColumn>
              <ElTableColumn label="累计学习" width="130">
                <template #default="{ row }">{{ formatMinutes(row.study_minutes) }}</template>
              </ElTableColumn>
              <ElTableColumn prop="active_days" label="活跃天数" width="100" align="center" />
              <ElTableColumn label="常用功能" width="150">
                <template #default="{ row }"><ElTag size="small" type="info">{{ row.favorite_feature }}</ElTag></template>
              </ElTableColumn>
              <ElTableColumn label="最近使用" width="130">
                <template #default="{ row }">{{ relativeTime(row.last_active_at) }}</template>
              </ElTableColumn>
              <ElTableColumn label="活跃状态" width="120">
                <template #default="{ row }">
                  <ElTag size="small" :type="usageStatusTag(row.status)">{{ row.status }}</ElTag>
                </template>
              </ElTableColumn>
            </ElTable>
            <div class="usage-footnote">
              数据更新时间：{{ usageOverview?.generated_at?.replace('T', ' ') || '—' }} · 数据变化后页面自动同步，无需手动刷新
            </div>
          </ElCard>
        </div>
        <!-- ======== Students ======== -->
        <div v-else-if="activeMenu === 'students'">
          <ElCard shadow="never">
            <template #header>
              <div class="card-header">
                <span>学生管理</span>
                <ElSpace>
                  <ElInput v-model="studentSearch" placeholder="搜索学生ID/姓名" style="width: 220px" clearable @keyup.enter="loadStudents">
                    <template #prefix><Search /></template>
                  </ElInput>
                  <ElButton type="primary" @click="openStudentDialog('create')"><Plus /> 新增学生</ElButton>
                </ElSpace>
              </div>
            </template>
            <ElTable :data="students" v-loading="studentsLoading" stripe>
              <ElTableColumn label="学号" width="130">
                <template #default="{ row }">{{ maskStudentNo(row.student_id) }}</template>
              </ElTableColumn>
              <ElTableColumn prop="username" label="用户名" width="130" />
              <ElTableColumn prop="name" label="姓名" width="120" />
              <ElTableColumn prop="role" label="角色" width="100">
                <template #default="{ row }">
                  <ElTag :type="row.role === 'admin' ? 'danger' : row.role === 'teacher' ? 'warning' : 'info'" size="small">
                    {{ roleLabel(row.role) }}
                  </ElTag>
                </template>
              </ElTableColumn>
              <ElTableColumn prop="is_active" label="状态" width="90">
                <template #default="{ row }">
                  <ElTag :type="row.is_active ? 'success' : 'info'" size="small">
                    {{ row.is_active ? '启用' : '停用' }}
                  </ElTag>
                </template>
              </ElTableColumn>
              <ElTableColumn prop="created_at" label="创建时间" min-width="170" />
              <ElTableColumn label="操作" width="160" fixed="right">
                <template #default="{ row }">
                  <ElButton link type="primary" size="small" @click="openStudentDialog('edit', row)"><Edit /> 编辑</ElButton>
                  <ElButton link type="danger" size="small" @click="deleteStudent(row.id)"><Delete /> 删除</ElButton>
                </template>
              </ElTableColumn>
            </ElTable>
            <div class="pagination-wrap">
              <ElPagination v-model:current-page="studentPage" v-model:page-size="studentPageSize"
                :page-sizes="[10, 20, 50]" :total="studentTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="loadStudents" @current-change="loadStudents" />
            </div>
          </ElCard>
        </div>
        <!-- ======== Study Time ======== -->
        <div v-else-if="activeMenu === 'study-time'">
          <ElCard shadow="never">
            <template #header>
              <div class="card-header">
                <span>学习时间管理</span>
                <ElSpace>
                  <ElDatePicker v-model="studyDateRange" type="daterange" range-separator="至"
                    start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 240px" />
                  <ElSelect v-model="studyAbnormalFilter" placeholder="异常筛选" style="width: 130px" clearable>
                    <ElOption :value="''" label="全部" />
                    <ElOption :value="true" label="异常" />
                    <ElOption :value="false" label="正常" />
                  </ElSelect>
                  <ElSelect v-model="studyTypeFilter" placeholder="学习类型" style="width: 140px" clearable>
                    <ElOption value="reading" label="阅读" />
                    <ElOption value="video" label="视频" />
                    <ElOption value="practice" label="练习" />
                    <ElOption value="exam" label="考试" />
                  </ElSelect>
                  <ElButton type="primary" @click="loadStudyRecords"><Search /> 查询</ElButton>
                </ElSpace>
              </div>
            </template>
            <ElSpace style="margin-bottom: 12px">
              <ElButton type="success" @click="detectAnomalies"><Warning /> 异常检测</ElButton>
              <ElButton @click="exportStudyRecords"><Download /> 导出记录</ElButton>
              <ElButton type="primary" plain @click="openStudyDialog('create')"><Plus /> 新增记录</ElButton>
            </ElSpace>
            <ElTable :data="studyRecords" v-loading="studyLoading" stripe>
              <ElTableColumn label="学号" width="120">
                <template #default="{ row }">{{ maskStudentNo(row.student_id) }}</template>
              </ElTableColumn>
              <ElTableColumn prop="course_name" label="课程" width="140" show-overflow-tooltip />
              <ElTableColumn prop="chapter_name" label="章节" width="140" show-overflow-tooltip />
              <ElTableColumn prop="knowledge_point_content" label="知识点" width="180" show-overflow-tooltip />
              <ElTableColumn prop="study_date" label="学习日期" width="120" />
              <ElTableColumn prop="duration_minutes" label="时长(分钟)" width="100" align="right" />
              <ElTableColumn prop="study_type" label="类型" width="90">
                <template #default="{ row }"><ElTag size="small">{{ studyTypeLabel(row.study_type) }}</ElTag></template>
              </ElTableColumn>
              <ElTableColumn prop="is_abnormal" label="异常" width="80">
                <template #default="{ row }">
                  <ElTag v-if="row.is_abnormal" type="danger" size="small">异常</ElTag>
                  <span v-else style="color:#67c23c">正常</span>
                </template>
              </ElTableColumn>
              <ElTableColumn label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <ElButton link type="primary" size="small" @click="openStudyDialog('edit', row)"><Edit /> 编辑</ElButton>
                  <ElButton link type="danger" size="small" @click="deleteStudyRecord(row.id)"><Delete /> 删除</ElButton>
                </template>
              </ElTableColumn>
            </ElTable>
            <div class="pagination-wrap">
              <ElPagination v-model:current-page="studyPage" v-model:page-size="studyPageSize"
                :page-sizes="[10, 20, 50]" :total="studyTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="loadStudyRecords" @current-change="loadStudyRecords" />
            </div>
          </ElCard>
        </div>
        <!-- ======== Knowledge Points ======== -->
        <div v-else-if="activeMenu === 'knowledge'">
          <ElRow :gutter="16">
            <ElCol :xs="24" :lg="12">
              <ElCard shadow="never">
                <template #header>
                  <div class="card-header">
                    <span>知识点标签管理</span>
                    <ElButton type="primary" size="small" @click="openKPTagDialog()"><Plus /> 新增标签</ElButton>
                  </div>
                </template>
                <ElTable :data="kpTags" v-loading="kpTagsLoading" stripe size="small">
                  <ElTableColumn prop="name" label="标签名" width="120" />
                  <ElTableColumn prop="category" label="分类" width="120">
                    <template #default="{ row }"><ElTag size="small">{{ tagCategoryLabel(row.category) }}</ElTag></template>
                  </ElTableColumn>
                  <ElTableColumn prop="color" label="颜色" width="80">
                    <template #default="{ row }">
                      <span :style="{ display: 'inline-block', width: 16, height: 16, background: row.color || '#ccc', borderRadius: 3 }" />
                    </template>
                  </ElTableColumn>
                  <ElTableColumn prop="description" label="描述" show-overflow-tooltip />
                  <ElTableColumn label="操作" width="120" fixed="right">
                    <template #default="{ row }">
                      <ElButton link type="primary" size="small" @click="openKPTagDialog(row)"><Edit /></ElButton>
                      <ElButton link type="danger" size="small" @click="deleteKPTag(row.id)"><Delete /></ElButton>
                    </template>
                  </ElTableColumn>
                </ElTable>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :lg="12">
              <ElCard shadow="never">
                <template #header><span>知识点掌握统计</span></template>
                <div v-loading="kpStatsLoading">
                  <ElDescriptions :column="1" border v-if="kpStats">
                    <ElDescriptionsItem label="总知识点数">{{ kpStats.total_kps || 0 }}</ElDescriptionsItem>
                    <ElDescriptionsItem label="已掌握">{{ kpStats.mastered || 0 }}</ElDescriptionsItem>
                    <ElDescriptionsItem label="学习中">{{ kpStats.learning || 0 }}</ElDescriptionsItem>
                    <ElDescriptionsItem label="未学习">{{ kpStats.not_started || 0 }}</ElDescriptionsItem>
                  </ElDescriptions>
                  <ElEmpty v-else description="暂无统计数据" />
                </div>
              </ElCard>
            </ElCol>
          </ElRow>
          <ElCard shadow="never" style="margin-top: 16px">
            <template #header><span>学生知识点掌握详情</span></template>
            <ElTable :data="studentKPs" v-loading="kpStudentLoading" stripe max-height="400">
              <ElTableColumn label="学号" width="120">
                <template #default="{ row }">{{ maskStudentNo(row.student_id) }}</template>
              </ElTableColumn>
              <ElTableColumn prop="kp_content" label="知识点" min-width="200" show-overflow-tooltip />
              <ElTableColumn prop="mastery_level" label="掌握程度" width="110">
                <template #default="{ row }">
                  <ElTag :type="row.mastery_level === 'mastered' ? 'success' : row.mastery_level === 'learning' ? 'warning' : 'info'" size="small">
                    {{ masteryLabel(row.mastery_level) }}
                  </ElTag>
                </template>
              </ElTableColumn>
              <ElTableColumn label="难度" width="90" align="center">
                <template #default="{ row }">{{ kpDifficultyLabel(row.difficulty_level) }}</template>
              </ElTableColumn>
              <ElTableColumn prop="study_count" label="学习次数" width="90" align="right" />
              <ElTableColumn prop="total_study_minutes" label="总时长(分)" width="110" align="right" />
              <ElTableColumn prop="last_study_date" label="最近学习" width="120" />
              <ElTableColumn label="标签" min-width="120">
                <template #default="{ row }">
                  <ElTag v-for="tag in (row.tags || [])" :key="tag.id" size="small" style="margin-right: 4px">{{ tag.name }}</ElTag>
                </template>
              </ElTableColumn>
            </ElTable>
          </ElCard>
        </div>
        <!-- ======== Course Content ======== -->
        <div v-else-if="activeMenu === 'course'">
          <ElCard shadow="never">
            <template #header>
              <div class="card-header">
                <span>课程内容管理</span>
                <ElSpace>
                  <ElInput v-model="courseSearch" placeholder="搜索标题" style="width: 180px" clearable @keyup.enter="loadCourseContents">
                    <template #prefix><Search /></template>
                  </ElInput>
                  <ElSelect v-model="courseStatusFilter" placeholder="状态" style="width: 120px" clearable>
                    <ElOption value="" label="全部" />
                    <ElOption value="draft" label="草稿" />
                    <ElOption value="published" label="已发布" />
                    <ElOption value="archived" label="已归档" />
                  </ElSelect>
                  <ElButton type="primary" @click="openCourseDialog('create')"><Plus /> 新增内容</ElButton>
                </ElSpace>
              </div>
            </template>
            <ElTable :data="courseContents" v-loading="courseLoading" stripe>
              <ElTableColumn prop="title" label="标题" min-width="180" show-overflow-tooltip />
              <ElTableColumn prop="content_type" label="类型" width="110">
                <template #default="{ row }"><ElTag size="small">{{ contentTypeLabel(row.content_type) }}</ElTag></template>
              </ElTableColumn>
              <ElTableColumn prop="status" label="状态" width="90">
                <template #default="{ row }">
                  <ElTag :type="getStatusTag(row.status).type" size="small">{{ getStatusTag(row.status).text }}</ElTag>
                </template>
              </ElTableColumn>
              <ElTableColumn label="所属章节" width="140" show-overflow-tooltip>
                <template #default="{ row }">{{ row.chapter_title || '未关联章节' }}</template>
              </ElTableColumn>
              <ElTableColumn label="关联知识点" width="160" show-overflow-tooltip>
                <template #default="{ row }">{{ row.knowledge_point_content || '未关联知识点' }}</template>
              </ElTableColumn>
              <ElTableColumn prop="published_at" label="发布时间" width="170" />
              <ElTableColumn label="操作" width="240" fixed="right">
                <template #default="{ row }">
                  <ElButton link type="primary" size="small" @click="openCourseDialog('edit', row)"><Edit /> 编辑</ElButton>
                  <ElButton link type="success" size="small" @click="viewVersions(row.id)"><View /> 版本</ElButton>
                  <ElButton v-if="row.status === 'draft'" link type="warning" size="small" @click="publishCourseContent(row.id)">发布</ElButton>
                  <ElButton v-if="row.status === 'published'" link type="info" size="small" @click="archiveCourseContent(row.id)">归档</ElButton>
                  <ElButton link type="danger" size="small" @click="deleteCourseContent(row.id)"><Delete /> 删除</ElButton>
                </template>
              </ElTableColumn>
            </ElTable>
            <div class="pagination-wrap">
              <ElPagination v-model:current-page="coursePage" v-model:page-size="coursePageSize"
                :page-sizes="[10, 20, 50]" :total="courseTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="loadCourseContents" @current-change="loadCourseContents" />
            </div>
          </ElCard>
        </div>
        <!-- ======== Questions ======== -->
        <div v-else-if="activeMenu === 'questions'">
          <ElCard shadow="never">
            <template #header>
              <div class="card-header">
                <span>题库管理</span>
                <ElSpace>
                  <ElSelect v-model="questionTypeFilter" placeholder="题型" style="width: 120px" clearable>
                    <ElOption value="" label="全部" />
                    <ElOption value="单选" label="单选题" />
                    <ElOption value="多选" label="多选题" />
                    <ElOption value="判断" label="判断题" />
                    <ElOption value="填空" label="填空题" />
                    <ElOption value="SQL编程" label="SQL编程题" />
                  </ElSelect>
                  <ElSelect v-model="questionDifficultyFilter" placeholder="难度" style="width: 110px" clearable>
                    <ElOption value="" label="全部" />
                    <ElOption value="easy" label="简单" />
                    <ElOption value="medium" label="中等" />
                    <ElOption value="hard" label="困难" />
                  </ElSelect>
                  <ElButton type="primary" @click="loadQuestions"><Search /> 查询</ElButton>
                  <ElButton type="primary" plain @click="openQuestionDialog('create')"><Plus /> 新增题目</ElButton>
                </ElSpace>
              </div>
            </template>
            <ElTable :data="questions" v-loading="questionsLoading" stripe>
              <ElTableColumn prop="type" label="题型" width="100">
                <template #default="{ row }"><ElTag size="small">{{ row.type }}</ElTag></template>
              </ElTableColumn>
              <ElTableColumn prop="difficulty" label="难度" width="90">
                <template #default="{ row }">
                  <ElTag :type="getDifficultyTag(row.difficulty).type" size="small">{{ getDifficultyTag(row.difficulty).text }}</ElTag>
                </template>
              </ElTableColumn>
              <ElTableColumn prop="stem" label="题干" min-width="280" show-overflow-tooltip />
              <ElTableColumn label="所属知识点" width="160" show-overflow-tooltip>
                <template #default="{ row }">{{ row.kp_content || '未关联知识点' }}</template>
              </ElTableColumn>
              <ElTableColumn label="操作" width="180" fixed="right">
                <template #default="{ row }">
                  <ElButton link type="primary" size="small" @click="openQuestionDialog('edit', row)"><Edit /> 编辑</ElButton>
                  <ElButton link type="success" size="small" @click="viewQuestionUsage(row.id)"><View /> 统计</ElButton>
                  <ElButton link type="danger" size="small" @click="deleteQuestion(row.id)"><Delete /> 删除</ElButton>
                </template>
              </ElTableColumn>
            </ElTable>
            <div class="pagination-wrap">
              <ElPagination v-model:current-page="questionPage" v-model:page-size="questionPageSize"
                :page-sizes="[10, 20, 50]" :total="questionTotal"
                layout="total, sizes, prev, pager, next"
                @size-change="loadQuestions" @current-change="loadQuestions" />
            </div>
          </ElCard>
        </div>
        <!-- ======== Viz Templates ======== -->
        <div v-else-if="activeMenu === 'viz'">
          <ElCard shadow="never">
            <template #header>
              <div class="card-header">
                <span>可视化模板管理</span>
                <ElButton type="primary" @click="openVizDialog('create')"><Plus /> 新增模板</ElButton>
              </div>
            </template>
            <ElTable :data="vizTemplates" v-loading="vizLoading" stripe>
              <ElTableColumn prop="name" label="模板名称" width="160" />
              <ElTableColumn prop="chart_type" label="图表类型" width="130">
                <template #default="{ row }"><ElTag size="small">{{ chartTypeLabel(row.chart_type) }}</ElTag></template>
              </ElTableColumn>
              <ElTableColumn label="图表预览" width="150">
                <template #default="{ row }">
                  <div class="viz-mini" @click="openVizPreview(row)">
                    <SvgChart :type="row.chart_type" :data="vizPreviewData(row)" :height="300" compact />
                  </div>
                </template>
              </ElTableColumn>
              <ElTableColumn label="数据来源" width="150">
                <template #default="{ row }">{{ dataSourceLabel(row.data_source) }}</template>
              </ElTableColumn>
              <ElTableColumn prop="is_public" label="公开" width="80" align="center">
                <template #default="{ row }">
                  <ElTag :type="row.is_public ? 'success' : 'info'" size="small">{{ row.is_public ? '是' : '否' }}</ElTag>
                </template>
              </ElTableColumn>
              <ElTableColumn label="关联知识点" width="150" show-overflow-tooltip>
                <template #default="{ row }">{{ row.knowledge_point_content || '未关联知识点' }}</template>
              </ElTableColumn>
              <ElTableColumn prop="updated_at" label="更新时间" width="170" />
              <ElTableColumn label="操作" width="230" fixed="right">
                <template #default="{ row }">
                  <ElButton link type="primary" size="small" @click="openVizPreview(row)"><View /> 预览</ElButton>
                  <ElButton link type="primary" size="small" @click="openVizDialog('edit', row)"><Edit /> 编辑</ElButton>
                  <ElButton link type="danger" size="small" @click="deleteVizTemplate(row.id)"><Delete /> 删除</ElButton>
                </template>
              </ElTableColumn>
            </ElTable>
          </ElCard>
        </div>
        <!-- ======== RBAC ======== -->
        <div v-else-if="activeMenu === 'rbac'">
          <ElRow :gutter="16">
            <ElCol :xs="24" :lg="14">
              <ElCard shadow="never">
                <template #header>
                  <div class="card-header">
                    <span>角色管理</span>
                    <ElSpace>
                      <ElButton size="small" @click="initRbac"><Setting /> 初始化权限数据</ElButton>
                      <ElButton type="primary" size="small" @click="openRoleDialog()"><Plus /> 新增角色</ElButton>
                    </ElSpace>
                  </div>
                </template>
                <ElTable :data="roles" v-loading="rbacLoading" stripe>
                  <ElTableColumn prop="name" label="角色名" width="150" />
                  <ElTableColumn prop="description" label="描述" min-width="180" show-overflow-tooltip />
                  <ElTableColumn label="操作" width="220" fixed="right">
                    <template #default="{ row }">
                      <ElButton link type="primary" size="small" @click="openRoleDialog(row)"><Edit /> 编辑</ElButton>
                      <ElButton link type="warning" size="small" @click="openAssignPermDialog(row)"><Lock /> 分配权限</ElButton>
                      <ElButton link type="danger" size="small" @click="deleteRole(row.id)"><Delete /> 删除</ElButton>
                    </template>
                  </ElTableColumn>
                </ElTable>
              </ElCard>
            </ElCol>
            <ElCol :xs="24" :lg="10">
              <ElCard shadow="never">
                <template #header><span>权限列表</span></template>
                <ElTable :data="permissions" v-loading="rbacLoading" stripe size="small" max-height="500">
                  <ElTableColumn prop="name" label="权限名" width="150" />
                  <ElTableColumn prop="module" label="所属模块" width="120">
                    <template #default="{ row }"><ElTag size="small">{{ permissionModuleLabel(row.module) }}</ElTag></template>
                  </ElTableColumn>
                  <ElTableColumn prop="description" label="描述" show-overflow-tooltip />
                </ElTable>
              </ElCard>
            </ElCol>
          </ElRow>
        </div>

      </div>
    </main>
  </div>
    <!-- Student Dialog -->
    <ElDialog v-model="studentDialogVisible" :title="studentDialogMode === 'create' ? '新增学生' : '编辑学生'" width="480px">
      <ElForm :model="studentForm" label-width="90px">
        <ElFormItem label="学号"><ElInput v-model="studentForm.student_id" /></ElFormItem>
        <ElFormItem label="用户名"><ElInput v-model="studentForm.username" /></ElFormItem>
        <ElFormItem label="姓名"><ElInput v-model="studentForm.name" /></ElFormItem>
        <ElFormItem label="角色">
          <ElSelect v-model="studentForm.role" style="width: 100%">
            <ElOption value="student" label="学生" />
            <ElOption value="teacher" label="教师" />
            <ElOption value="admin" label="管理员" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem v-if="studentDialogMode === 'create'" label="密码">
          <ElInput v-model="studentForm.password" type="password" show-password />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="studentDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="saveStudent">保存</ElButton>
      </template>
    </ElDialog>

    <!-- Study Dialog -->
    <ElDialog v-model="studyDialogVisible" :title="studyDialogMode === 'create' ? '新增学习记录' : '编辑学习记录'" width="500px">
      <ElForm :model="studyForm" label-width="110px">
        <ElFormItem label="学号"><ElInput v-model="studyForm.student_id" /></ElFormItem>
        <ElFormItem label="学习日期">
          <ElDatePicker v-model="studyForm.study_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="时长(分钟)">
          <ElInputNumber v-model="studyForm.duration_minutes" :min="0" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="学习类型">
          <ElSelect v-model="studyForm.study_type" style="width: 100%">
            <ElOption value="reading" label="阅读" />
            <ElOption value="video" label="视频" />
            <ElOption value="practice" label="练习" />
            <ElOption value="exam" label="考试" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="备注"><ElInput v-model="studyForm.notes" type="textarea" :rows="3" /></ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="studyDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="saveStudyRecord">保存</ElButton>
      </template>
    </ElDialog>
    <!-- KP Tag Dialog -->
    <ElDialog v-model="kpTagDialogVisible" :title="kpTagForm.id ? '编辑标签' : '新增标签'" width="440px">
      <ElForm :model="kpTagForm" label-width="80px">
        <ElFormItem label="名称"><ElInput v-model="kpTagForm.name" /></ElFormItem>
        <ElFormItem label="分类"><ElInput v-model="kpTagForm.category" /></ElFormItem>
        <ElFormItem label="颜色"><ElInput v-model="kpTagForm.color" placeholder="#409EFF" /></ElFormItem>
        <ElFormItem label="描述"><ElInput v-model="kpTagForm.description" type="textarea" :rows="2" /></ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="kpTagDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="saveKPTag">保存</ElButton>
      </template>
    </ElDialog>

    <!-- Course Dialog -->
    <ElDialog v-model="courseDialogVisible" :title="courseDialogMode === 'create' ? '新增课程内容' : '编辑课程内容'" width="580px">
      <ElForm :model="courseForm" label-width="110px">
        <ElFormItem label="标题"><ElInput v-model="courseForm.title" /></ElFormItem>
        <ElFormItem label="内容类型">
          <ElSelect v-model="courseForm.content_type" style="width: 100%">
            <ElOption value="text" label="文本" />
            <ElOption value="video" label="视频" />
            <ElOption value="slides" label="幻灯片" />
            <ElOption value="interactive" label="交互式" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="状态">
          <ElSelect v-model="courseForm.status" style="width: 100%">
            <ElOption value="draft" label="草稿" />
            <ElOption value="published" label="已发布" />
            <ElOption value="archived" label="已归档" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="章节ID">
          <ElInputNumber v-model="courseForm.chapter_id" :min="null" placeholder="选填" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="知识点ID">
          <ElInputNumber v-model="courseForm.knowledge_point_id" :min="null" placeholder="选填" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="内容正文"><ElInput v-model="courseForm.content" type="textarea" :rows="5" /></ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="courseDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="saveCourseContent">保存</ElButton>
      </template>
    </ElDialog>

    <!-- Version Dialog -->
    <ElDialog v-model="versionDialogVisible" title="版本历史" width="600px">
      <ElTable :data="courseVersions" stripe v-if="courseVersions.length > 0">
        <ElTableColumn prop="version" label="版本号" width="100" />
        <ElTableColumn prop="title" label="标题" show-overflow-tooltip />
        <ElTableColumn prop="created_at" label="创建时间" width="170" />
      </ElTable>
      <ElEmpty v-else description="暂无版本历史" />
    </ElDialog>
    <!-- Question Dialog -->
    <ElDialog v-model="questionDialogVisible" :title="questionDialogMode === 'create' ? '新增题目' : '编辑题目'" width="600px">
      <ElForm :model="questionForm" label-width="100px">
        <ElFormItem label="知识点ID">
          <ElInputNumber v-model="questionForm.knowledge_point_id" :min="1" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="题型">
          <ElSelect v-model="questionForm.type" style="width: 100%">
            <ElOption value="单选" label="单选题" />
            <ElOption value="多选" label="多选题" />
            <ElOption value="判断" label="判断题" />
            <ElOption value="填空" label="填空题" />
            <ElOption value="SQL编程" label="SQL编程题" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="难度">
          <ElSelect v-model="questionForm.difficulty" style="width: 100%">
            <ElOption value="easy" label="简单" />
            <ElOption value="medium" label="中等" />
            <ElOption value="hard" label="困难" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="题干"><ElInput v-model="questionForm.stem" type="textarea" :rows="3" /></ElFormItem>
        <ElFormItem label="选项" v-if="questionForm.type === '单选' || questionForm.type === '多选'">
          <div style="width: 100%">
            <div v-for="(_, idx) in questionForm.options" :key="idx" style="margin-bottom: 6px">
              <ElInput v-model="questionForm.options[idx]" :placeholder="'选项 ' + String.fromCharCode(65 + idx)" />
            </div>
            <ElButton link type="primary" size="small" @click="questionForm.options.push('')">+ 添加选项</ElButton>
            <ElButton link type="danger" size="small" @click="questionForm.options.pop()" style="margin-left: 8px">- 移除</ElButton>
          </div>
        </ElFormItem>
        <ElFormItem label="答案"><ElInput v-model="questionForm.answer" type="textarea" :rows="2" /></ElFormItem>
        <ElFormItem label="解析"><ElInput v-model="questionForm.analysis" type="textarea" :rows="3" /></ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="questionDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="saveQuestion">保存</ElButton>
      </template>
    </ElDialog>

    <!-- Usage Dialog -->
    <ElDialog v-model="usageDialogVisible" title="题目使用统计" width="500px">
      <ElDescriptions :column="1" border v-if="questionUsage">
        <ElDescriptionsItem label="使用次数">{{ questionUsage.usage_count || 0 }}</ElDescriptionsItem>
        <ElDescriptionsItem label="正确次数">{{ questionUsage.correct_count || 0 }}</ElDescriptionsItem>
        <ElDescriptionsItem label="正确率">{{ questionUsage.usage_count ? Math.round(questionUsage.correct_count / questionUsage.usage_count * 100) : 0 }}%</ElDescriptionsItem>
        <ElDescriptionsItem label="平均耗时">{{ questionUsage.average_time_seconds || 0 }} 秒</ElDescriptionsItem>
        <ElDescriptionsItem label="难度评分">{{ questionUsage.difficulty_rating || '-' }}</ElDescriptionsItem>
        <ElDescriptionsItem label="最近使用">{{ questionUsage.last_used_at || '-' }}</ElDescriptionsItem>
      </ElDescriptions>
      <ElEmpty v-else description="暂无使用数据" />
    </ElDialog>
    <!-- Viz Template Dialog -->
    <ElDialog v-model="vizDialogVisible" :title="vizDialogMode === 'create' ? '新增可视化模板' : '编辑可视化模板'" width="520px">
      <ElForm :model="vizForm" label-width="110px">
        <ElFormItem label="模板名称"><ElInput v-model="vizForm.name" /></ElFormItem>
        <ElFormItem label="图表类型">
          <ElSelect v-model="vizForm.chart_type" style="width: 100%" placeholder="选择图表类型">
            <ElOption v-for="t in vizChartTypes" :key="t.value || t" :value="t.value || t" :label="t.label || t" />
            <ElOption value="bar" label="柱状图" />
            <ElOption value="line" label="折线图" />
            <ElOption value="pie" label="饼图" />
            <ElOption value="scatter" label="散点图" />
            <ElOption value="heatmap" label="热力图" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="数据来源"><ElInput v-model="vizForm.data_source" placeholder="如：学习行为数据" /></ElFormItem>
        <ElFormItem label="公开">
          <ElSwitch v-model="vizForm.is_public" />
        </ElFormItem>
        <ElFormItem label="关联知识点">
          <ElInputNumber v-model="vizForm.knowledge_point_id" :min="null" placeholder="选填" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="配置JSON"><ElInput v-model="vizForm.config" type="textarea" :rows="4" placeholder="JSON配置" /></ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="vizDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="saveVizTemplate">保存</ElButton>
      </template>
    </ElDialog>

    <!-- Viz Template Preview Dialog -->
    <ElDialog v-model="vizPreviewVisible" :title="vizPreviewTemplate?.name || '图表预览'" width="640px">
      <div v-if="vizPreviewTemplate" class="viz-preview">
        <div class="viz-preview-meta">
          <span>图表类型：</span>
          <ElTag size="small">{{ chartTypeLabel(vizPreviewTemplate.chart_type) }}</ElTag>
          <span v-if="vizPreviewTemplate.data_source" style="margin-left: 12px">数据来源：{{ dataSourceLabel(vizPreviewTemplate.data_source) }}</span>
        </div>
        <SvgChart :type="vizPreviewTemplate.chart_type" :data="vizPreviewData(vizPreviewTemplate)" :height="320" />
      </div>
    </ElDialog>

    <!-- Role Dialog -->
    <ElDialog v-model="rbacDialogVisible" :title="rbacForm.id ? '编辑角色' : '新增角色'" width="450px">
      <ElForm :model="rbacForm" label-width="80px">
        <ElFormItem label="角色名"><ElInput v-model="rbacForm.name" /></ElFormItem>
        <ElFormItem label="描述"><ElInput v-model="rbacForm.description" type="textarea" :rows="3" /></ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="rbacDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="saveRole">保存</ElButton>
      </template>
    </ElDialog>

    <!-- Assign Permission Dialog -->
    <ElDialog v-model="assignPermDialogVisible" title="分配权限" width="550px">
      <div v-if="selectedRole" style="margin-bottom: 12px; color: #606266">
        为角色 <strong>{{ selectedRole.name }}</strong> 分配权限：
      </div>
      <ElTable :data="permissions" size="small" max-height="400" @selection-change="(sel: any[]) => assignedPermissionIds = sel.map((p: any) => p.id)">
        <ElTableColumn type="selection" width="50" />
        <ElTableColumn prop="name" label="权限名" width="150" />
        <ElTableColumn prop="module" label="模块" width="120">
          <template #default="{ row }"><ElTag size="small">{{ row.module }}</ElTag></template>
        </ElTableColumn>
        <ElTableColumn prop="description" label="描述" show-overflow-tooltip />
      </ElTable>
      <template #footer>
        <ElButton @click="assignPermDialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="assignPermissions">保存</ElButton>
      </template>
    </ElDialog>

</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f5f7fa;
}
.admin-sidebar {
  background: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: fixed;
  width: 220px;
  left: 0;
  top: 0;
  z-index: 100;
  overflow: hidden;
}
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 20px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  border-bottom: 1px solid #1f2d3d;
  flex-shrink: 0;
}
.logo-icon { font-size: 22px; color: #409EFF; }
.sidebar-menu { border-right: none; flex: 1; width: 100%; overflow-y: auto; }
.sidebar-menu .menu-icon { font-size: 18px; margin-right: 10px; flex-shrink: 0; }
.sidebar-menu :deep(.el-menu) {
  background-color: transparent !important;
  border-right: none !important;
}
.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: 6px;
  color: #b7bdc6 !important;
  transition: all 0.2s ease;
}
.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(64, 158, 255, 0.15) !important;
  color: #fff !important;
}
.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%) !important;
  color: #fff !important;
}
.sidebar-menu :deep(.el-menu-item span) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sidebar-footer { padding: 12px; border-top: 1px solid #1f2d3d; flex-shrink: 0; }
.sidebar-footer .el-button { color: #b7bdc6 !important; }
.admin-main {
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f5f7fa;
}
.admin-header {
  background: #fff; padding: 14px 24px; display: flex; align-items: center;
  justify-content: space-between; border-bottom: 1px solid #e4e7ed;
}
.header-actions { display: flex; gap: 12px; }
.admin-content { flex: 1; padding: 20px; }
.stat-card { border-radius: 8px; }
.stat-card .stat-icon { font-size: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
.module-activity { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.module-name { width: 96px; flex-shrink: 0; font-size: 13px; color: #606266; }
.stat-card .stat-hint { margin-top: 6px; font-size: 12px; color: #909399; }
.section-range { font-size: 12px; color: #909399; font-weight: 400; }
.recent-section .card-header { align-items: baseline; flex-wrap: wrap; gap: 8px; }
.recent-metric { padding: 14px 16px; border-radius: 8px; background: #f7f9fc; border: 1px solid #ebeef5; }
.recent-metric-label { font-size: 13px; color: #606266; }
.recent-metric-value { margin-top: 6px; font-size: 26px; font-weight: 600; color: #303133; line-height: 1.2; }
.recent-metric-delta { margin-top: 6px; font-size: 12px; }
.delta-up { color: #67C23A; }
.delta-down { color: #F56C6C; }
.delta-flat { color: #909399; }
.chart-title { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.chart-sub { margin-left: 8px; font-size: 12px; font-weight: 400; color: #909399; }
.anomaly-list { margin-top: 10px; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 12px; }
.anomaly-title { color: #606266; }
.anomaly-none { color: #909399; }
.sim-legend { margin-top: 6px; display: flex; align-items: center; gap: 6px; font-size: 12px; color: #909399; }
.sim-dot { width: 9px; height: 9px; border-radius: 50%; background: #ffffff; border: 2px solid #E6A23C; box-sizing: border-box; flex-shrink: 0; }
.rt-status { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #67C23A; margin-right: 12px; }
.rt-status.offline { color: #F56C6C; }
.rt-dot { width: 8px; height: 8px; border-radius: 50%; background: #67C23A; flex-shrink: 0; }
.rt-status.offline .rt-dot { background: #F56C6C; animation: rt-blink 1s infinite; }
@keyframes rt-blink { 50% { opacity: 0.25; } }
.recent-basis { margin-top: 14px; padding-top: 10px; border-top: 1px dashed #ebeef5; font-size: 12px; color: #909399; line-height: 1.7; }
.compare-table { margin-top: 4px; }
.weak-rate { margin-left: 8px; font-size: 12px; color: #606266; }
.usage-student { display: flex; flex-direction: column; line-height: 1.4; }
.usage-name { font-weight: 600; color: #303133; }
.usage-no { font-size: 12px; color: #909399; }
.usage-footnote { margin-top: 10px; font-size: 12px; color: #909399; text-align: right; }
.viz-mini { cursor: pointer; padding: 2px 0; transition: opacity 0.2s; }
.viz-mini:hover { opacity: 0.75; }
.viz-preview { display: flex; flex-direction: column; gap: 10px; }
.viz-preview-meta { font-size: 13px; color: #606266; display: flex; align-items: center; }

@media (max-width: 768px) {
  .admin-sidebar { width: 64px; }
  .sidebar-header span,
  .sidebar-menu :deep(.el-menu-item span),
  .sidebar-footer .el-button span { display: none; }
  .admin-main { margin-left: 64px; }
}
</style>


