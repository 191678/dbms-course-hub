/** 展示层语义化工具：把存储层的枚举值、标识与时间转换为用户可读文案。 */

export const studyTypeLabels: Record<string, string> = {
  self: '自主自习',
  class: '课堂学习',
  review: '复习巩固',
  exam: '考试测评',
  reading: '阅读学习',
  video: '视频学习',
  practice: '习题练习'
}

export const contentTypeLabels: Record<string, string> = {
  text: '图文资料',
  video: '视频课件',
  exercise: '练习材料',
  slide: '演示课件',
  diagram: '图表素材',
  rich_text: '富文本资料'
}

export const chartTypeLabels: Record<string, string> = {
  line: '趋势折线图',
  bar: '对比柱状图',
  pie: '占比饼图',
  radar: '能力雷达图',
  heatmap: '活跃热力图',
  scatter: '散点分布图',
  gauge: '仪表盘图',
  funnel: '漏斗分析图'
}

export const moduleTypeLabels: Record<string, string> = {
  knowledge_visualization: '知识可视化',
  knowledge_graph: '知识关联图谱',
  theory_content: '理论学习',
  key_points: '要点速览',
  diagram: '图表解析',
  agent_interaction: 'AI助教交互',
  search: '知识检索',
  node_click: '节点探索',
  session_start: '学习会话开始',
  study_session: '学习会话'
}

export const masteryLabels: Record<string, string> = {
  mastered: '已掌握',
  learning: '学习中',
  practicing: '巩固中',
  not_started: '未开始',
  unknown: '未开始'
}

export const roleLabels: Record<string, string> = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
}

export const contentStatusLabels: Record<string, string> = {
  draft: '草稿',
  published: '已发布',
  archived: '已归档'
}

export const permissionModuleLabels: Record<string, string> = {
  student: '学生管理',
  study_time: '学习时间',
  knowledge_point: '知识点',
  course_content: '课程内容',
  question: '题库',
  visualization: '可视化模板',
  system: '系统设置'
}

export const dataSourceLabels: Record<string, string> = {
  learning_records: '学习行为数据',
  study_records: '学习时长数据',
  student_knowledge_points: '知识点掌握数据',
  question_usages: '题目作答数据',
  agent_chat_history: '助教问答数据',
  chapters: '章节数据',
  knowledge_points: '知识点数据'
}

export const tagCategoryLabels: Record<string, string> = {
  custom: '自定义标签',
  difficulty: '难度标签',
  chapter: '章节标签',
  knowledge_point: '知识点标签'
}

export const tagTypeOf = (value: string) => value

export const labelOf = (map: Record<string, string>, value?: string | null, fallback = '未设置'): string => {
  if (!value) return fallback
  return map[value] || fallback
}

export const studyTypeLabel = (value?: string | null) => labelOf(studyTypeLabels, value)
export const contentTypeLabel = (value?: string | null) => labelOf(contentTypeLabels, value)
export const chartTypeLabel = (value?: string | null) => labelOf(chartTypeLabels, value, '其他图表')
export const moduleTypeLabel = (value?: string | null) => labelOf(moduleTypeLabels, value, '其他学习功能')
export const masteryLabel = (value?: string | null) => labelOf(masteryLabels, value, '未开始')
export const roleLabel = (value?: string | null) => labelOf(roleLabels, value, '学生')
export const contentStatusLabel = (value?: string | null) => labelOf(contentStatusLabels, value, '草稿')
export const permissionModuleLabel = (value?: string | null) => labelOf(permissionModuleLabels, value, '其他模块')
export const dataSourceLabel = (value?: string | null) => labelOf(dataSourceLabels, value, '平台统计数据')
export const tagCategoryLabel = (value?: string | null) => labelOf(tagCategoryLabels, value, '自定义标签')

/** 知识点理解难度：数值等级转为描述性文案 */
export const kpDifficultyLabel = (level?: number | null): string => {
  const value = Number(level || 0)
  if (value <= 1) return '入门'
  if (value <= 2) return '基础'
  if (value <= 3) return '进阶'
  if (value <= 4) return '较难'
  return '挑战'
}

/** 时长（分钟）转为“x 小时 y 分钟” */
export const formatMinutes = (minutes?: number | null): string => {
  const total = Math.max(0, Math.round(Number(minutes || 0)))
  if (total < 60) return `${total} 分钟`
  const hours = Math.floor(total / 60)
  const rest = total % 60
  return rest ? `${hours} 小时 ${rest} 分钟` : `${hours} 小时`
}

/** 学号脱敏：保留首尾，隐藏中间部分 */
export const maskStudentNo = (studentId?: string | null): string => {
  const value = (studentId || '').trim()
  if (!value) return '—'
  if (value.length <= 4) return value[0] + '*'.repeat(value.length - 1)
  return `${value.slice(0, 4)}${'*'.repeat(Math.max(value.length - 6, 2))}${value.slice(-2)}`
}

/** 相对时间：把时间点转换为“刚刚 / 3 分钟前 / 昨天”等文案 */
export const relativeTime = (value?: string | null): string => {
  if (!value) return '暂无记录'
  const time = new Date(value.replace(' ', 'T'))
  if (Number.isNaN(time.getTime())) return '暂无记录'
  const diff = Date.now() - time.getTime()
  if (diff < 60_000) return '刚刚'
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)} 分钟前`
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)} 小时前`
  const days = Math.floor(diff / 86_400_000)
  if (days === 1) return '昨天'
  if (days < 7) return `${days} 天前`
  return time.toLocaleDateString('zh-CN')
}
