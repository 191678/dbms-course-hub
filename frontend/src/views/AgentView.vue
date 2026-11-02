<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElCard, ElInput, ElButton, ElScrollbar, ElTag, ElProgress, ElImage } from 'element-plus'
import { Message, VideoPlay, VideoPause, RefreshLeft, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { agentApi } from '@/api'
import { getUser } from '@/utils/auth'
import MermaidChart from '@/components/MermaidChart.vue'
import mermaid from 'mermaid'

interface MessageData {
  role: 'user' | 'assistant'
  content: string
  tool_used?: string
  media_data?: {
    media_type: string
    format: string
    content?: string
    title?: string
    steps?: Array<{ frame: number; speech: string; highlight_element: string }>
    slides?: Array<{ slide_number: number; title: string; content: string; speech: string; duration: number }>
    full_speech?: string
    duration?: string
    duration_seconds?: number
    slides_count?: number
  }
  questions?: Array<{ id: number; type: string; stem: string; options?: string[]; answer: string; analysis: string }>
}

const inputMessage = ref('')
const messages = ref<MessageData[]>([])
const isLoading = ref(false)

const playingIndex = ref<number | null>(null)
const isPlaying = ref(false)
const currentStep = ref(0)
const audioProgress = ref(0)
// 存储每条 PPT 视频消息对应的 TTS 音频 URL 列表
const slideAudioUrls = ref<Record<number, string[]>>({})
// 是否正在等待 TTS 合成
const audioLoading = ref(false)

const audio = ref<HTMLAudioElement | null>(null)
const mermaidReady = ref(false)
const previewImage = ref<string | undefined>('')
const showPreview = ref(false)

// 当前账户最近提问（最多 5 条，账户之间互不互通）
const recentQuestions = ref<string[]>([])

const currentStudentId = (): string => getUser()?.student_id || ''

const loadHistory = async () => {
  const studentId = currentStudentId()
  if (!studentId) {
    recentQuestions.value = []
    return
  }
  try {
    const result = await agentApi.getHistory(studentId)
    recentQuestions.value = (result.questions || []).map((item) => item.question)
  } catch (e) {
    console.error('加载提问历史失败:', e)
  }
}

const askHistoryQuestion = (question: string) => {
  inputMessage.value = question
}

onMounted(() => {
  audio.value = new Audio()
  loadHistory()
  
  try {
    if (!mermaid) {
      console.warn('Mermaid not loaded')
      mermaidReady.value = true
      return
    }
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      themeVariables: {
        primaryColor: '#409EFF',
        primaryTextColor: '#303133',
        primaryBorderColor: '#409EFF',
        lineColor: '#606266',
        secondaryColor: '#67c23a',
        tertiaryColor: '#e6a23c',
        fontSize: '36px',
        fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
        mainBkg: '#ffffff',
        edgeLabelBackground: '#f5f7fa',
        textColor: '#303133',
        nodeTextColor: '#303133',
        nodeBorder: '#409EFF',
        clusterBorder: '#409EFF',
        clusterBkg: '#f0f5ff',
        actorBorder: '#409EFF',
        actorBackground: '#f0f5ff',
        signalColor: '#606266',
        labelColor: '#303133'
      },
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis',
        nodeSpacing: 150,
        rankSpacing: 180
      },
      gantt: {
        useMaxWidth: true
      },
      pie: {
        useMaxWidth: true
      },
      sequenceDiagram: {
        useMaxWidth: true,
        actorMargin: 50,
        width: 120,
        height: 60,
        boxMargin: 10,
        boxPadding: 10
      },
      erDiagram: {
        useMaxWidth: true
      }
    })
    mermaidReady.value = true
    
    testMermaidRender()
  } catch (e) {
    console.error('Failed to initialize mermaid:', e)
    mermaidReady.value = true
  }
})

const testMermaidRender = async () => {
  if (!mermaid) return
  
  const testScript = `graph TD
    A[节点A] --> B[节点B]
    B --> C[节点C]`
  
  const erScript = `erDiagram
    STUDENT ||--o{ ENROLLS_IN : "注册"
    COURSE ||--o{ ENROLLS_IN : "被注册"
    STUDENT {
        int id PK
        string name
        string email
    }
    COURSE {
        int id PK
        string name
        int credits
    }`
  
  try {
    const result = await mermaid.render('test-chart', testScript)
    if (!result || !result.svg) {
      console.error('Mermaid graph render returned no SVG')
    }
  } catch (err) {
    console.error('Test Mermaid graph render failed:', err)
  }
  
  try {
    const erResult = await mermaid.render('test-er', erScript)
    if (!erResult || !erResult.svg) {
      console.error('Mermaid ER render returned no SVG')
    }
  } catch (err) {
    console.error('Test Mermaid ER render failed:', err)
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const userMsg = inputMessage.value.trim()
  messages.value.push({ role: 'user', content: userMsg })
  inputMessage.value = ''
  isLoading.value = true
  
  try {
    const response = await agentApi.chat({ 
      student_question: userMsg,
      student_id: currentStudentId()
    })
    
    const msgData: MessageData = {
      role: 'assistant', 
      content: response.answer,
      tool_used: response.tool_used,
      media_data: response.media_data,
      questions: response.questions
    }
    
    messages.value.push(msgData)
    loadHistory()
  } catch (error) {
    messages.value.push({ 
      role: 'assistant', 
      content: '抱歉，我遇到了一些问题，请稍后再试。' 
    })
  } finally {
    isLoading.value = false
  }
}

const handleKeydown = (e: Event) => {
  const event = e as KeyboardEvent
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}



const getTagType = (type: string) => {
  const types: Record<string, 'info' | 'warning' | 'success' | 'danger'> = {
    '单选': 'info',
    '多选': 'warning',
    '判断': 'success',
    'SQL编程': 'danger'
  }
  return types[type] || 'info'
}

const toggleAnimationPlay = async (msgIndex: number) => {
  const msg = messages.value[msgIndex]
  const hasSlides = msg.media_data?.slides && msg.media_data.slides.length > 0
  const hasSteps = msg.media_data?.steps && msg.media_data.steps.length > 0
  if (!hasSlides && !hasSteps) return

  if (playingIndex.value === msgIndex) {
    if (isPlaying.value) {
      pauseAnimation()
    } else {
      playAnimation(msgIndex)
    }
  } else {
    if (playingIndex.value !== null) {
      pauseAnimation()
    }
    playingIndex.value = msgIndex
    currentStep.value = 0
    audioProgress.value = 0

    // 若为 PPT 视频，则先确保已生成 TTS 音频
    if (hasSlides && !slideAudioUrls.value[msgIndex]) {
      const ok = await ensureSlideAudio(msgIndex)
      if (!ok) {
        // 即使音频生成失败，也允许按计时方式播放视频
        console.warn('Slide audio generation failed, falling back to timer playback')
      }
    }

    playAnimation(msgIndex)
  }
}

const ensureSlideAudio = async (msgIndex: number): Promise<boolean> => {
  const msg = messages.value[msgIndex]
  if (!msg.media_data?.slides || msg.media_data.slides.length === 0) return false

  audioLoading.value = true
  try {
    const result = await agentApi.generateSlidesAudio({ slides: msg.media_data.slides })
    if (result && result.success && result.audio_urls && result.audio_urls.length > 0) {
      slideAudioUrls.value = { ...slideAudioUrls.value, [msgIndex]: result.audio_urls }
      return true
    }
    console.warn('generateSlidesAudio returned no audio:', result?.error || 'unknown')
    return false
  } catch (err) {
    console.error('Failed to generate slides audio:', err)
    return false
  } finally {
    audioLoading.value = false
  }
}

const playAnimation = (msgIndex: number) => {
  const msg = messages.value[msgIndex]
  const hasSlides = msg.media_data?.slides && msg.media_data.slides.length > 0
  const hasSteps = msg.media_data?.steps && msg.media_data.steps.length > 0
  if (!hasSlides && !hasSteps) return

  isPlaying.value = true

  if (hasSlides) {
    playSlideWithAudio(msgIndex)
  } else {
    playStepsAnimation(msgIndex)
  }
}

const playSlideWithAudio = (msgIndex: number) => {
  const msg = messages.value[msgIndex]
  const slides = msg.media_data?.slides || []
  const audioUrls = slideAudioUrls.value[msgIndex] || []
  const currentAudioUrl = audioUrls[currentStep.value]
  const slideDurationMs = slides[currentStep.value]?.duration ? slides[currentStep.value].duration * 1000 : 15000

  if (!audio.value) return

  // 清理之前的音频事件监听器
  audio.value.onended = null
  audio.value.ontimeupdate = null

  if (currentAudioUrl) {
    audio.value.src = currentAudioUrl
    audio.value.play().catch((err) => {
      console.warn('Audio playback failed, falling back to timer:', err)
      startSlideTimer(msgIndex, slideDurationMs)
    })

    audio.value.onended = () => {
      if (!isPlaying.value || playingIndex.value !== msgIndex) return
      audioProgress.value = ((currentStep.value + 1) / slides.length) * 100

      if (currentStep.value < slides.length - 1) {
        currentStep.value++
        playSlideWithAudio(msgIndex)
      } else {
        isPlaying.value = false
        playingIndex.value = null
      }
    }

    audio.value.ontimeupdate = () => {
      if (!audio.value) return
      const totalSlides = slides.length || 1
      const duration = audio.value.duration || (slideDurationMs / 1000)
      const currentTime = audio.value.currentTime || 0
      const slideBase = (currentStep.value / totalSlides) * 100
      const slideProgress = (currentTime / duration) * (100 / totalSlides)
      audioProgress.value = Math.min(100, slideBase + slideProgress)
    }
  } else {
    // 当前幻灯片无服务端音频，使用浏览器内置语音合成朗读解说词，确保视频有声音
    const speechText = slides[currentStep.value]?.speech || ''
    speakSlide(msgIndex, speechText, slideDurationMs)
  }
}

// 浏览器内置语音合成兜底：当服务端 TTS 不可用时保证视频仍有解说声音
const speakSlide = (msgIndex: number, text: string, fallbackMs: number) => {
  const synth = window.speechSynthesis
  if (!synth || !text) {
    startSlideTimer(msgIndex, fallbackMs)
    return
  }

  const finish = () => {
    if (!isPlaying.value || playingIndex.value !== msgIndex) return
    const msg = messages.value[msgIndex]
    const slides = msg.media_data?.slides || []
    audioProgress.value = ((currentStep.value + 1) / slides.length) * 100
    if (currentStep.value < slides.length - 1) {
      currentStep.value++
      playSlideWithAudio(msgIndex)
    } else {
      isPlaying.value = false
      playingIndex.value = null
    }
  }

  synth.cancel()
  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = 'zh-CN'
  utter.rate = 1
  utter.onend = finish
  utter.onerror = () => startSlideTimer(msgIndex, fallbackMs)
  synth.speak(utter)
}

const startSlideTimer = (msgIndex: number, durationMs: number) => {
  setTimeout(() => {
    if (!isPlaying.value || playingIndex.value !== msgIndex) return
    const msg = messages.value[msgIndex]
    const slides = msg.media_data?.slides || []
    audioProgress.value = ((currentStep.value + 1) / slides.length) * 100

    if (currentStep.value < slides.length - 1) {
      currentStep.value++
      playSlideWithAudio(msgIndex)
    } else {
      isPlaying.value = false
      playingIndex.value = null
    }
  }, durationMs)
}

const playStepsAnimation = (msgIndex: number) => {
  const msg = messages.value[msgIndex]
  const items = msg.media_data!.steps!
  const stepDuration = 3000

  const animate = () => {
    if (!isPlaying.value || playingIndex.value !== msgIndex) return
    audioProgress.value = ((currentStep.value + 1) / items.length) * 100

    if (currentStep.value < items.length - 1) {
      setTimeout(() => {
        currentStep.value++
        animate()
      }, stepDuration)
    } else {
      isPlaying.value = false
      playingIndex.value = null
    }
  }

  animate()
}

const pauseAnimation = () => {
  isPlaying.value = false
  if (audio.value) {
    audio.value.pause()
  }
  window.speechSynthesis?.cancel()
}

const resetAnimation = () => {
  pauseAnimation()
  playingIndex.value = null
  currentStep.value = 0
  audioProgress.value = 0
  window.speechSynthesis?.cancel()
  if (audio.value) {
    audio.value.onended = null
    audio.value.ontimeupdate = null
    audio.value.pause()
    audio.value.currentTime = 0
    audio.value.src = ''
  }
}

const nextStep = (msgIndex: number) => {
  const msg = messages.value[msgIndex]
  const hasSlides = msg.media_data?.slides && msg.media_data.slides.length > 0
  const hasSteps = msg.media_data?.steps && msg.media_data.steps.length > 0
  const itemsLength = hasSlides
    ? msg.media_data!.slides!.length
    : hasSteps ? msg.media_data!.steps!.length : 0

  if (currentStep.value < itemsLength - 1) {
    currentStep.value++
    audioProgress.value = ((currentStep.value + 1) / itemsLength) * 100
    // 正在播放 PPT 视频时，切换到下一张幻灯片的音频
    if (isPlaying.value && playingIndex.value === msgIndex && hasSlides) {
      playSlideWithAudio(msgIndex)
    }
  }
}

const prevStep = (msgIndex: number) => {
  if (currentStep.value > 0) {
    currentStep.value--
    const msg = messages.value[msgIndex]
    const hasSlides = msg.media_data?.slides && msg.media_data.slides.length > 0
    const hasSteps = msg.media_data?.steps && msg.media_data.steps.length > 0
    const itemsLength = hasSlides
      ? msg.media_data!.slides!.length
      : hasSteps ? msg.media_data!.steps!.length : 1
    audioProgress.value = ((currentStep.value + 1) / itemsLength) * 100
    // 正在播放 PPT 视频时，切换到上一张幻灯片的音频
    if (isPlaying.value && playingIndex.value === msgIndex && hasSlides) {
      playSlideWithAudio(msgIndex)
    }
  }
}

const openImagePreview = (src?: string) => {
  previewImage.value = src
  showPreview.value = true
}

const closeImagePreview = () => {
  showPreview.value = false
  previewImage.value = ''
}
</script>

<template>
  <div style="padding: 20px; height: calc(100% - 40px)">
    <ElCard class="agent-card">
      <div class="agent-header">
        <div class="agent-info">
          <div class="agent-details">
            <h2>库库智能助教</h2>
          </div>
        </div>
      </div>
      
      <ElScrollbar class="chat-container">
        <div class="messages-list">
          <div v-for="(msg, index) in messages" :key="index" class="message-item" :class="[msg.role, { 'has-media': msg.media_data }]">
            <div class="avatar-text" v-if="msg.role === 'assistant'">库库</div>
            
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              
              <div v-if="msg.media_data" class="media-container">
                <div v-if="msg.media_data.media_type === 'image'" class="media-item">
                  <div v-if="msg.media_data.format === 'mermaid'" class="mermaid-container">
                    <div class="media-title">{{ msg.media_data.title }}</div>
                    <MermaidChart :script="msg.media_data.content || ''" />
                  </div>
                  <div v-else-if="msg.media_data.format === 'url'" class="image-container">
                    <div class="media-title">{{ msg.media_data.title }}</div>
                    <div class="image-wrapper" @click="openImagePreview(msg.media_data.content)">
                      <ElImage :src="msg.media_data.content" fit="contain" class="generated-image" />
                      <div class="image-overlay">
                        <span class="zoom-icon">🔍</span>
                        <span class="zoom-text">点击放大</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-if="msg.media_data.media_type === 'video'" class="animation-container">
                  <div class="animation-player">
                    <div class="animation-header">
                      <div class="animation-title">🎬 {{ msg.media_data.title }}</div>
                      <div class="animation-controls">
                        <ElButton
                          size="small"
                          circle
                          @click="prevStep(index)"
                          :disabled="(playingIndex === index ? currentStep === 0 : true) && (!msg.media_data.steps || currentStep === 0) && (!msg.media_data.slides || currentStep === 0)"
                          title="上一步"
                          :icon="ArrowLeft"
                        />
                        <ElButton
                          size="small"
                          circle
                          :class="{ 'play-btn': true, 'is-loading': audioLoading && playingIndex === index }"
                          @click="toggleAnimationPlay(index)"
                          :loading="audioLoading && playingIndex === index"
                          :icon="(!audioLoading && isPlaying && playingIndex === index) ? VideoPause : VideoPlay"
                        />
                        <ElButton
                          size="small"
                          circle
                          @click="nextStep(index)"
                          :disabled="(playingIndex === index ? currentStep >= ((msg.media_data.slides?.length || msg.media_data.steps?.length || 1) - 1) : false)"
                          title="下一步"
                          :icon="ArrowRight"
                        />
                        <ElButton
                          size="small"
                          circle
                          @click="resetAnimation"
                          title="重置"
                          :icon="RefreshLeft"
                        />
                      </div>
                    </div>

                    <div class="progress-container">
                      <ElProgress :percentage="audioProgress" :stroke-width="6" />
                      <div class="progress-text">{{ currentStep + 1 }} / {{ msg.media_data.slides?.length || msg.media_data.steps?.length || 0 }}</div>
                    </div>

                    <!-- PPT视频展示 -->
                    <div v-if="msg.media_data.slides" class="ppt-display">
                      <div class="ppt-slide" :class="{ active: true }">
                        <div class="ppt-slide-number">{{ msg.media_data.slides[currentStep]?.slide_number }}</div>
                        <div class="ppt-slide-title">{{ msg.media_data.slides[currentStep]?.title }}</div>
                        <div class="ppt-slide-content">{{ msg.media_data.slides[currentStep]?.content }}</div>
                        <div class="ppt-slide-speech">{{ msg.media_data.slides[currentStep]?.speech }}</div>
                      </div>
                      <div class="ppt-slides-list">
                        <div
                          v-for="(slide, slideIndex) in msg.media_data.slides"
                          :key="slideIndex"
                          class="ppt-thumb"
                          :class="{ active: slideIndex === currentStep }"
                          @click="currentStep = slideIndex"
                        >
                          <span class="ppt-thumb-num">{{ slide.slide_number }}</span>
                          <span class="ppt-thumb-title">{{ slide.title }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- 动画脚本展示（兼容旧格式） -->
                    <div v-else-if="msg.media_data.steps" class="animation-content">
                      <div class="steps-container">
                        <div
                          v-for="(step, stepIndex) in msg.media_data.steps"
                          :key="stepIndex"
                          class="step-item"
                          :class="{ active: stepIndex === currentStep }"
                        >
                          <span class="step-number">{{ step.frame }}</span>
                          <span class="step-speech">{{ step.speech }}</span>
                        </div>
                      </div>
                    </div>

                    <div class="animation-tips">
                      <span class="tip-icon">💡</span>
                      <span v-if="audioLoading && playingIndex === index">正在合成 AI 语音解说，请稍候…</span>
                      <span v-else-if="msg.media_data.slides">
                        点击播放按钮，观看 PPT 视频讲解（含 AI 语音解说）
                      </span>
                      <span v-else>点击播放按钮，观看动态讲解演示</span>
                      <span v-if="msg.media_data.duration" class="duration-info">⏱ {{ msg.media_data.duration }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="msg.questions && msg.questions.length > 0" class="questions-container">
                <div class="questions-list">
                  <div v-for="question in msg.questions" :key="question.id" class="question-item">
                    <div class="question-header">
                      <ElTag :type="getTagType(question.type)" size="small">{{ question.type }}</ElTag>
                      <span class="question-stem">{{ question.stem }}</span>
                    </div>
                    <div v-if="question.options && question.options.length > 0" class="question-options">
                      <div v-for="(option, optIndex) in question.options" :key="optIndex" class="option-item">
                        <span class="option-label">{{ ['A', 'B', 'C', 'D', 'E', 'F'][optIndex] }}.</span>
                        <span>{{ option }}</span>
                      </div>
                    </div>
                    <div v-else-if="question.type === 'SQL编程'" class="question-sql-area">
                      <textarea readonly class="sql-answer" rows="4">{{ question.answer }}</textarea>
                    </div>
                    <div class="question-analysis">
                      <strong>答案：</strong>{{ question.answer }}
                      <div class="analysis-text">
                        <strong>解析：</strong>{{ question.analysis }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="msg.tool_used" class="tool-info">
                <span>已调用{{ msg.tool_used }}工具</span>
              </div>
            </div>
          </div>
          
          <div v-if="isLoading" class="loading-message">
            <div class="avatar-text">库库</div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
          
          <div v-if="messages.length === 0" class="welcome-message">
            <h3>欢迎使用库库智能助教</h3>
            <p>亲爱的同学，你好，我是你的专属答疑学习助手，库库，有什么问题可以向我提问。</p>
            <p style="margin-top: 12px; color: #67c23a">💡 尝试提问："画一下B+树的结构"、"解释一下幻读"、"演示死锁的形成过程"</p>
          </div>
        </div>
      </ElScrollbar>
      
      <div v-if="showPreview" class="preview-modal-overlay" @click="closeImagePreview">
        <div class="preview-modal-content" @click.stop>
          <img :src="previewImage" alt="图片预览" />
          <div class="preview-modal-close" @click="closeImagePreview">✕</div>
        </div>
      </div>
      
      <div v-if="recentQuestions.length > 0" class="recent-questions">
        <span class="recent-label">最近提问</span>
        <div class="recent-list">
          <span
            v-for="(q, qi) in recentQuestions"
            :key="qi"
            class="recent-item"
            :title="q"
            @click="askHistoryQuestion(q)"
          >{{ q }}</span>
        </div>
      </div>

      <div class="input-area">
        <ElInput 
          v-model="inputMessage" 
          type="textarea" 
          :rows="2" 
          placeholder="输入你的问题..." 
          @keydown="handleKeydown"
        />
        <ElButton type="primary" @click="sendMessage" :disabled="!inputMessage.trim() || isLoading" :icon="Message">
          发送
        </ElButton>
      </div>
    </ElCard>
  </div>
</template>

<style scoped>
.agent-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 28px;
  border-bottom: 2px solid #ebeef5;
  margin-bottom: 28px;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.agent-details h2 {
  font-size: 28px;
  color: #303133;
  margin: 0;
  font-weight: 600;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 28px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-item {
  display: flex;
  gap: 20px;
  max-width: 85%;
}

.message-item.has-media {
  max-width: 100%;
}

.message-item.user {
  margin-left: auto;
}

.message-item.user .message-content {
  background-color: #409EFF;
  color: white;
}

.message-content {
  background-color: #f5f7fa;
  border-radius: 12px;
  padding: 20px 24px;
  max-width: 100%;
  min-width: 200px;
}

.message-item.has-media .message-content {
  max-width: 100%;
}

.message-text {
  font-size: 18px;
  line-height: 1.8;
  word-break: break-word;
  color: #303133;
}

.media-container {
  margin-top: 20px;
}

.media-item {
  background-color: #fff;
  border: 2px solid #ebeef5;
  border-radius: 12px;
  padding: 30px;
  overflow: visible;
}

.media-title {
  font-weight: bold;
  font-size: 24px;
  color: #303133;
  margin-bottom: 24px;
}

.mermaid-container {
  margin-top: 24px;
  padding: 0;
  border: none;
  overflow: visible;
}

.mermaid-chart {
  width: 100%;
  height: 800px;
  min-height: 800px;
  max-height: 1000px;
  overflow-x: auto;
  overflow-y: auto;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 30px;
  display: block;
  border: 2px solid #dcdfe6;
  box-sizing: border-box;
}

.mermaid-chart svg {
  width: 100% !important;
  height: auto !important;
  min-height: 700px;
  display: block !important;
  background-color: #ffffff;
  border: 1px solid #eee;
}

.preview-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  cursor: pointer;
  animation: fadeIn 0.2s ease;
  padding: 20px;
  box-sizing: border-box;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.preview-modal-content {
  position: relative;
  max-width: 100%;
  max-height: 100%;
  cursor: default;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-modal-content img {
  max-width: 100%;
  max-height: 90vh;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.preview-modal-close {
  position: absolute;
  top: -50px;
  right: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preview-modal-close:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.image-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.image-wrapper {
  position: relative;
  display: block;
  width: 100%;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  background-color: #f5f7fa;
  border: 1px solid #ebeef5;
  box-sizing: border-box;
}

.generated-image {
  width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: contain;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.image-wrapper:hover .generated-image {
  transform: scale(1.02);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  padding: 24px 16px 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-wrapper:hover .image-overlay {
  opacity: 1;
}

.zoom-icon {
  font-size: 20px;
  margin-right: 8px;
}

.zoom-text {
  font-size: 15px;
  color: #fff;
  font-weight: 500;
}

.animation-container {
  margin-top: 12px;
}

.animation-player {
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.animation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.animation-title {
  font-weight: bold;
  font-size: 14px;
  color: #303133;
}

.animation-controls {
  display: flex;
  gap: 4px;
}

.play-btn {
  background-color: #409EFF;
  color: white;
}

.play-btn:hover {
  background-color: #66b1ff;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background-color: #f5f7fa;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 50px;
}

.animation-content {
  padding: 16px;
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background-color: #f5f7fa;
  transition: all 0.3s ease;
  opacity: 0.5;
  transform: translateX(-10px);
}

.step-item.active {
  background-color: #e6f7ff;
  border-left: 4px solid #409EFF;
  opacity: 1;
  transform: translateX(0);
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #909399;
  color: white;
  font-size: 13px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-item.active .step-number {
  background-color: #409EFF;
}

.step-speech {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.animation-tips {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  background-color: #f0f9eb;
  border-top: 1px solid #e8f5e9;
  font-size: 13px;
  color: #67c23a;
}

.duration-info {
  margin-left: auto;
  color: #409EFF;
  font-weight: 600;
}

.ppt-display {
  padding: 16px;
  background: #f8f9fa;
}

.ppt-slide {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 12px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  border: 2px solid #409EFF;
}

.ppt-slide-number {
  width: 32px;
  height: 32px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 12px;
}

.ppt-slide-title {
  font-size: 22px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
}

.ppt-slide-content {
  font-size: 16px;
  color: #606266;
  margin-bottom: 16px;
  line-height: 1.6;
}

.ppt-slide-speech {
  font-size: 15px;
  color: #909399;
  line-height: 1.8;
  padding: 12px;
  background: #f0f9eb;
  border-radius: 6px;
  width: 100%;
  text-align: left;
}

.ppt-slides-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 8px 0;
}

.ppt-thumb {
  flex: 0 0 auto;
  min-width: 100px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}

.ppt-thumb:hover {
  border-color: #409EFF;
  background: #ecf5ff;
}

.ppt-thumb.active {
  border-color: #409EFF;
  background: #ecf5ff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.ppt-thumb-num {
  width: 20px;
  height: 20px;
  background: #dcdfe6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  flex-shrink: 0;
}

.ppt-thumb.active .ppt-thumb-num {
  background: #409EFF;
}

.ppt-thumb-title {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tip-icon {
  font-size: 14px;
}

.questions-container {
  margin-top: 12px;
}

.questions-list {
  margin-top: 8px;
}

.question-item {
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.question-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 12px;
}

.question-stem {
  font-size: 14px;
  line-height: 1.6;
}

.question-options {
  margin-bottom: 12px;
}

.option-item {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 14px;
}

.option-label {
  font-weight: bold;
  color: #409EFF;
}

.question-sql-area {
  margin-bottom: 12px;
}

.sql-answer {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #303133;
  resize: none;
}

.question-analysis {
  padding-top: 12px;
  border-top: 1px dashed #ebeef5;
  font-size: 14px;
  color: #606266;
}

.analysis-text {
  margin-top: 8px;
  line-height: 1.6;
}

.tool-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 12px;
  color: #e6a23c;
}

.avatar-text {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  flex-shrink: 0;
}

.loading-message {
  display: flex;
  gap: 12px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #c0c4cc;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.welcome-message {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.welcome-message h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 8px;
}

.welcome-message p {
  margin: 4px 0;
}

.recent-questions {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
  padding: 0 4px;
}

.recent-label {
  flex-shrink: 0;
  font-size: 14px;
  color: #909399;
  line-height: 30px;
}

.recent-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.recent-item {
  max-width: 240px;
  padding: 4px 12px;
  font-size: 14px;
  color: #409EFF;
  background-color: #ecf5ff;
  border: 1px solid #d9ecff;
  border-radius: 14px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: all 0.2s ease;
}

.recent-item:hover {
  background-color: #409EFF;
  color: #fff;
  border-color: #409EFF;
}

.input-area {
  display: flex;
  gap: 16px;
}

.input-area :deep(.el-input) {
  flex: 1;
}

.input-area :deep(.el-input__inner) {
  font-size: 18px;
  padding: 16px 20px;
}

.input-area :deep(.el-button) {
  font-size: 18px;
  padding: 16px 32px;
  height: auto;
}

@media (max-width: 768px) {
  .generated-image {
    max-height: 300px;
  }
  
  .image-wrapper {
    border-radius: 8px;
  }
  
  .image-overlay {
    padding: 16px 12px 12px;
  }
  
  .zoom-icon {
    font-size: 16px;
  }
  
  .zoom-text {
    font-size: 12px;
  }
  
  .preview-modal-overlay {
    padding: 10px;
  }
  
  .preview-modal-content img {
    max-height: 85vh;
    border-radius: 8px;
  }
  
  .preview-modal-close {
    top: -45px;
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .generated-image {
    max-height: 250px;
  }
  
  .preview-modal-content img {
    max-height: 80vh;
  }
}

@media (min-width: 1200px) {
  .generated-image {
    max-height: 600px;
  }
  
  .preview-modal-content img {
    max-height: 95vh;
    max-width: 90vw;
  }
}
</style>
