<script setup lang="ts">
import { ref } from 'vue'

// User & Weather Mock Data
const userName = ref('Alex')
const weather = ref({ temp: '+18°C', condition: 'Sunny' })

// Mock Data for "Look of the Day" variants
const outfits = ref([
  {
    id: 1,
    title: 'Linen + Cotton',
    date: 'Today',
    tags: ['Work', 'Sunny'],
    images: [
      'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&q=80&w=300', // Shirt
      'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&q=80&w=300'  // Pants
    ],
    selected: false
  },
  {
    id: 2,
    title: 'Smart Casual',
    date: 'Yesterday',
    tags: ['Meeting', 'Comfort'],
    images: [
      'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&q=80&w=300', // Blazer
      'https://images.unsplash.com/photo-1542272617-08f086302520?auto=format&fit=crop&q=80&w=300'  // Jeans
    ],
    selected: false
  },
  {
    id: 3,
    title: 'Friday Night',
    date: '2 days ago',
    tags: ['Casual', 'Evening'],
    images: [
      'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&q=80&w=300', // T-Shirt
      'https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?auto=format&fit=crop&q=80&w=300'  // Jacket
    ],
    selected: false
  }
])

const toggleSelection = (id: number) => {
  const item = outfits.value.find(o => o.id === id)
  if (item) item.selected = !item.selected
}
</script>

<template>
  <div class="bg-white min-h-full pb-32">
    
    <header class="sticky top-0 z-30 bg-white/95 backdrop-blur-sm px-5 py-4 flex justify-between items-center border-b border-slate-100 h-[72px]">
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Home</h1>
        <div class="flex gap-3">
            <button class="w-10 h-10 rounded-full bg-slate-50 hover:bg-slate-100 flex items-center justify-center text-slate-900 transition">
                <i class="pi pi-bell text-lg"></i>
            </button>
        </div>
    </header>

    <div class="px-5 pt-6">
        
        <div class="bg-slate-900 text-white rounded-[2rem] p-6 mb-8 relative overflow-hidden shadow-xl shadow-slate-900/10">
            <div class="absolute top-0 right-0 w-32 h-32 bg-blue-600/30 rounded-full blur-3xl -mr-10 -mt-10"></div>
            
            <div class="relative z-10">
                <div class="flex items-center gap-3 mb-3">
                    <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold">AI</div>
                    <span class="text-slate-300 text-sm">Personal Stylist</span>
                </div>
                <h2 class="text-xl font-medium leading-snug mb-5">
                  Hello, {{ userName }}! 
                  It's <span class="text-blue-300">{{ weather.temp }}</span> today. <br>
                  Need an office look?
                </h2>
                <button class="bg-white text-slate-900 px-6 py-3 rounded-xl text-sm font-bold hover:bg-slate-100 transition w-full sm:w-auto active:scale-95 duration-200">
                    Generate Outfit
                </button>
            </div>
        </div>

        <div class="mb-4">
            <div class="flex justify-between items-end mb-6 px-1">
                <h3 class="text-lg font-bold text-slate-900">Look of the Day</h3>
                <a href="#" class="text-blue-600 text-xs font-bold hover:underline">History</a>
            </div>
            
            <div class="flex flex-col gap-8">
                
                <div 
                  v-for="outfit in outfits" 
                  :key="outfit.id" 
                  class="w-full bg-white border border-slate-100 rounded-[1.5rem] p-4 shadow-sm"
                >
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex gap-2">
                            <span 
                            v-for="tag in outfit.tags" 
                            :key="tag"
                            class="px-3 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold uppercase tracking-wider rounded-full"
                            >
                            {{ tag }}
                            </span>
                        </div>
                        <span class="text-xs text-slate-400 font-medium">{{ outfit.date }}</span>
                    </div>

                    <div class="grid grid-cols-2 gap-3 mb-4">
                        <div class="aspect-[4/5] bg-slate-50 rounded-2xl overflow-hidden relative">
                            <img :src="outfit.images[0]" class="w-full h-full object-cover mix-blend-multiply" alt="Top">
                        </div>
                        <div class="aspect-[4/5] bg-slate-50 rounded-2xl overflow-hidden relative">
                            <img :src="outfit.images[1]" class="w-full h-full object-cover mix-blend-multiply" alt="Bottom">
                        </div>
                    </div>
                    
                    <div class="flex justify-between items-center px-1">
                        <div>
                            <div class="text-sm font-bold text-slate-900">{{ outfit.title }}</div>
                            <div class="text-xs text-slate-400">Based on weather</div>
                        </div>
                        
                        <button 
                          @click="toggleSelection(outfit.id)"
                          class="w-10 h-10 rounded-full border flex items-center justify-center transition-all duration-300"
                          :class="outfit.selected ? 'bg-blue-600 border-blue-600 text-white' : 'border-slate-200 text-slate-300 hover:text-blue-600 hover:border-blue-600'"
                        >
                            <i class="pi" :class="outfit.selected ? 'pi-check' : 'pi-bookmark'"></i>
                        </button>
                    </div>
                </div>

            </div>
        </div>

    </div>
  </div>
</template>