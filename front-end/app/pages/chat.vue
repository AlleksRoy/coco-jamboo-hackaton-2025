<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'

const chatContainer = ref<HTMLElement | null>(null)
const newMessage = ref('')

const messages = ref([
  { id: 1, type: 'ai', text: "Got any plans for the weekend? I can suggest something casual." },
  { id: 2, type: 'user', text: "I'm going to a birthday party outdoors." },
  { id: 3, type: 'ai', text: "Great! Since it's outdoors, I'd recommend layers. Maybe the cargo pants with a light hoodie?" },
  { id: 4, type: 'user', text: "Sounds good, show me." },
  { id: 5, type: 'ai', text: "Checking your wardrobe..." },
  { id: 5, type: 'ai', text: "Checking your wardrobe..." },
  { id: 5, type: 'ai', text: "Checking your wardrobe..." },
  { id: 5, type: 'ai', text: "Checking your wardrobe..." },
  // Добавил побольше текста для теста скролла
  { id: 6, type: 'ai', text: "Found a match! Also, don't forget comfortable shoes if you'll be standing a lot." }
])

// Скролл вниз
const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim()) return

  messages.value.push({
    id: Date.now(),
    type: 'user',
    text: newMessage.value.trim()
  })
  
  newMessage.value = ''
  scrollToBottom()

  // Имитация ответа
  setTimeout(() => {
    messages.value.push({
      id: Date.now() + 1,
      type: 'ai',
      text: "I'll check your wardrobe for matching items..."
    })
    scrollToBottom()
  }, 1000)
}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-100px)] bg-white relative ">

    <header class="flex-none sticky top-0 z-30 bg-white/95 backdrop-blur-sm px-5 py-4 flex justify-between items-center border-b border-slate-100 h-[72px]">
      <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Assistant</h1>
    </header>

    <div ref="chatContainer" class="flex-1 overflow-y-auto p-5 scroll-smooth bg-slate-50/50">
      <div class="flex flex-col justify-end min-h-full gap-4 pb-2">
        
        <div 
          v-for="msg in messages" 
          :key="msg.id" 
          class="flex gap-3 max-w-[85%] animate-fade-in"
          :class="msg.type === 'user' ? 'self-end flex-row-reverse' : ''"
        >
          <div 
            class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-[10px] font-bold mt-auto"
            :class="msg.type === 'user' ? 'bg-slate-200 text-slate-600' : 'bg-blue-600 text-white'"
          >
            {{ msg.type === 'user' ? 'YOU' : 'AI' }}
          </div>

          <div 
            class="p-4 rounded-2xl text-sm leading-relaxed shadow-sm"
            :class="[
              msg.type === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none shadow-blue-500/20' 
                : 'bg-white text-slate-900 rounded-bl-none border border-slate-100'
            ]"
          >
            {{ msg.text }}
          </div>
        </div>

      </div>
    </div>

    <div class="flex-none p-4 bg-white border-t border-slate-100">
      <div class="relative">
        <input 
          v-model="newMessage"
          @keyup.enter="sendMessage"
          type="text" 
          placeholder="Type a message..." 
          class="w-full bg-slate-50 border border-slate-200 rounded-full py-3.5 pl-5 pr-12 text-sm focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 transition-all placeholder:text-slate-400 text-slate-900"
        >
        <button 
          @click="sendMessage"
          :disabled="!newMessage.trim()"
          class="absolute right-1.5 top-1.5 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200"
          :class="{
            'bg-slate-900 text-white hover:bg-blue-600 hover:scale-105': newMessage.trim(),
            'bg-slate-200 text-slate-400 cursor-not-allowed': !newMessage.trim()
          }"
        >
          <i class="pi pi-arrow-up font-bold"></i>
        </button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>