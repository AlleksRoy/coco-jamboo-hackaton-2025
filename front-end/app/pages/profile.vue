<script setup lang="ts">
import { ref } from 'vue'

// Mock User Data
const user = ref({
  name: 'Alex Surname',
  email: 'alex.style@example.com',
  avatar: 'https://ui-avatars.com/api/?name=Alex&background=random&color=fff',
  isOnline: true
})

// Physical Characteristics
const stats = ref({
  height: 182, 
  weight: 78,
  bodyType: 'Rectangle',
  skinTone: 'Deep Winter',
  skinColorHex: '#312e81' 
})

// Body Measurements
const measurements = ref({
  chest: 102,
  waist: 85, 
  hips: 98
})

// Clothing Sizes
const sizes = ref({
  top: 'M / 48',
  bottom: '32',
  shoes: '43 EU'
})

// Bio
const bio = ref({
  text: "I prefer minimalism and smart-casual. I work in an office on weekdays (no strict dress code), and spend weekends actively.",
  tags: ['#minimalism', '#casual', '#sneakers']
})
</script>

<template>
  <div class="bg-white min-h-full pb-32">
    
    <header class="sticky top-0 z-30 bg-white/95 backdrop-blur-sm px-5 py-4 flex justify-between items-center border-b border-slate-100 h-[72px]">
       <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Profile</h1>
       <button class="w-10 h-10 rounded-full bg-slate-50 hover:bg-slate-100 flex items-center justify-center text-slate-900 transition">
          <i class="pi pi-cog text-lg"></i>
       </button>
    </header>

    <div class="px-5 pt-6">
      
      <div class="bg-slate-900 rounded-2xl p-5 flex items-center gap-4 mb-6 shadow-xl shadow-slate-200">
        <div class="relative">
          <div class="w-16 h-16 rounded-full overflow-hidden border-2 border-white/20">
            <img :src="user.avatar" alt="User" class="w-full h-full object-cover">
          </div>
          <div v-if="user.isOnline" class="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-slate-900 rounded-full"></div>
        </div>
        <div class="flex-1 min-w-0">
          <h2 class="text-white text-lg font-bold truncate">{{ user.name }}</h2>
          <p class="text-slate-400 text-sm truncate">{{ user.email }}</p>
        </div>
        <button class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white hover:bg-white/20 transition active:scale-95">
          <i class="pi pi-pencil text-sm"></i>
        </button>
      </div>

      <div class="mb-6">
        <h3 class="text-lg font-bold text-slate-900 mb-3 pl-1">Parameters</h3>
        <div class="bg-slate-50 border border-slate-100 rounded-2xl p-5">
          
          <div class="grid grid-cols-2 gap-y-6 gap-x-4 mb-6">
            <div>
              <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Height</p>
              <p class="text-slate-900 font-bold text-lg">{{ stats.height }} <span class="text-sm font-medium text-slate-500">cm</span></p>
            </div>
            <div>
              <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Weight</p>
              <p class="text-slate-900 font-bold text-lg">{{ stats.weight }} <span class="text-sm font-medium text-slate-500">kg</span></p>
            </div>
            <div>
              <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Body Type</p>
              <p class="text-slate-900 font-bold text-base">{{ stats.bodyType }}</p>
            </div>
            <div>
              <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Skin Tone</p>
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full border border-slate-200" :style="{ backgroundColor: stats.skinColorHex }"></div>
                <p class="text-slate-900 font-bold text-base truncate">{{ stats.skinTone }}</p>
              </div>
            </div>
          </div>

          <div class="border-t border-slate-200/60 pt-4 mb-6">
            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Body Measurements</p>
            <div class="grid grid-cols-3 gap-2 text-center">
              <div class="bg-white p-2 rounded-xl border border-slate-100">
                <span class="block text-[10px] text-slate-400 font-bold uppercase">Chest</span>
                <span class="text-slate-900 font-bold">{{ measurements.chest }}</span>
              </div>
              <div class="bg-white p-2 rounded-xl border border-slate-100">
                <span class="block text-[10px] text-slate-400 font-bold uppercase">Waist</span>
                <span class="text-slate-900 font-bold">{{ measurements.waist }}</span>
              </div>
              <div class="bg-white p-2 rounded-xl border border-slate-100">
                <span class="block text-[10px] text-slate-400 font-bold uppercase">Hips</span>
                <span class="text-slate-900 font-bold">{{ measurements.hips }}</span>
              </div>
            </div>
          </div>

          <div class="border-t border-slate-200/60 pt-4">
            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Clothing Sizes</p>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-white p-3 rounded-xl border border-slate-100 flex flex-col justify-between">
                <span class="text-[10px] text-slate-400 font-bold uppercase">Top Size</span>
                <span class="text-slate-900 font-bold text-lg">{{ sizes.top }}</span>
              </div>
              <div class="bg-white p-3 rounded-xl border border-slate-100 flex flex-col justify-between">
                <span class="text-[10px] text-slate-400 font-bold uppercase">Bottom Size</span>
                <span class="text-slate-900 font-bold text-lg">{{ sizes.bottom }}</span>
              </div>
              <div class="col-span-2 bg-white p-3 rounded-xl border border-slate-100 flex justify-between items-center">
                 <span class="text-[10px] text-slate-400 font-bold uppercase">Shoe Size</span>
                 <span class="text-slate-900 font-bold text-lg">{{ sizes.shoes }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <div>
        <h3 class="text-lg font-bold text-slate-900 mb-3 pl-1">About Me</h3>
        <div class="bg-slate-50 border border-slate-100 rounded-2xl p-5">
          <p class="text-sm text-slate-600 leading-relaxed">
            {{ bio.text }}
          </p>
          <div class="mt-4 flex flex-wrap gap-2">
            <span v-for="tag in bio.tags" :key="tag" class="px-3 py-1 bg-white border border-slate-200 rounded-full text-xs font-bold text-slate-500">
              {{ tag }}
            </span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>