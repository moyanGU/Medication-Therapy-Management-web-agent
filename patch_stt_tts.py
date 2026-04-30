with open("src/components/AiAssistant.vue", "r") as f:
    content = f.read()

# 1. Add Mic button to input area
old_input = """              <input
                v-model="inputText"
                @keyup.enter="sendMessage"
                type="text"
                :placeholder="inputPlaceholder"
                class="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                :disabled="isLoading"
              />"""

new_input = """              <div class="relative flex-1 flex items-center">
                <input
                  v-model="inputText"
                  @keyup.enter="sendMessage"
                  type="text"
                  :placeholder="isRecording ? '正在倾听...' : inputPlaceholder"
                  class="w-full bg-slate-50 border border-slate-200 rounded-xl pl-4 pr-10 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  :class="{'ring-2 ring-rose-500 bg-rose-50 placeholder-rose-500 text-rose-700': isRecording}"
                  :disabled="isLoading || isRecording"
                />
                <button
                  type="button"
                  class="absolute right-2 p-1.5 rounded-lg transition-colors flex items-center justify-center"
                  :class="isRecording ? 'bg-rose-100 text-rose-600 animate-pulse' : 'text-slate-400 hover:text-blue-600 hover:bg-blue-50'"
                  @click="toggleRecording"
                  title="语音输入"
                >
                  <svg v-if="isRecording" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" x2="12" y1="19" y2="22"></line></svg>
                </button>
              </div>"""

content = content.replace(old_input, new_input)

# 2. Add STT variables
if "const isRecording = ref(false)" not in content:
    stt_code = """
// STT (Speech to Text) variables
const isRecording = ref(false)
let recognition: any = null

const initSpeechRecognition = () => {
  if (typeof window === 'undefined') return
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SpeechRecognition) return

  recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.interimResults = true
  recognition.continuous = false

  let finalTranscript = ''

  recognition.onstart = () => {
    isRecording.value = true
    finalTranscript = inputText.value ? inputText.value + ' ' : ''
  }

  recognition.onresult = (event: any) => {
    let interimTranscript = ''
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript
      } else {
        interimTranscript += event.results[i][0].transcript
      }
    }
    inputText.value = finalTranscript + interimTranscript
  }

  recognition.onerror = (event: any) => {
    console.error('[STT] Speech recognition error', event.error)
    isRecording.value = false
  }

  recognition.onend = () => {
    isRecording.value = false
    // 语音结束后自动发送（针对老年人更友好）
    if (inputText.value.trim() && isOpen.value) {
      setTimeout(() => {
        if (!isRecording.value) sendMessage()
      }, 1000)
    }
  }
}

const toggleRecording = () => {
  if (!recognition) {
    initSpeechRecognition()
  }
  
  if (!recognition) {
    showToast('当前浏览器不支持语音识别', 'error')
    return
  }

  if (isRecording.value) {
    recognition.stop()
  } else {
    recognition.start()
  }
}
"""
    content = content.replace("const { isSpeechEnabled, isSpeechSupported, speak } = useSpeech()", "const { isSpeechEnabled, isSpeechSupported, speak } = useSpeech()\n" + stt_code)


# 3. Add TTS hook when AI replies
# Find the end of sendMessage function
old_send_success = """    scopedMessages.push({ role: 'ai', content: answer, mode })
  } catch (error) {
    console.error('[AiAssistant] request failed', error)"""

new_send_success = """    scopedMessages.push({ role: 'ai', content: answer, mode })
    
    // 如果开启了全局语音播报，AI的回复也同步朗读
    if (isSpeechEnabled.value && isSpeechSupported.value) {
      speak(answer, { priority: 'normal' })
    }
  } catch (error) {
    console.error('[AiAssistant] request failed', error)"""

content = content.replace(old_send_success, new_send_success)

# Fix toast import if needed (using showToast from existing composables/useToast or we can use showError)
content = content.replace("showToast('当前浏览器不支持语音识别', 'error')", "showError('当前浏览器不支持语音识别')")
if "const { success: showSuccess, error: showError } = useToast()" not in content:
    content = content.replace("const { isSpeechEnabled, isSpeechSupported, speak } = useSpeech()", "const { success: showSuccess, error: showError } = useToast()\nconst { isSpeechEnabled, isSpeechSupported, speak } = useSpeech()")


with open("src/components/AiAssistant.vue", "w") as f:
    f.write(content)
