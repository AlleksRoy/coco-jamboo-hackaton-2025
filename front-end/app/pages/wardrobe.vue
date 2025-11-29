<script setup lang="ts">
import { ref } from 'vue'

// Categories for the top scrollable bar
const categories = ['All', 'Tops', 'Bottoms', 'Shoes', 'Accessories', 'Outerwear']
const activeCategory = ref('All')

// Mock Data for Wardrobe Items
const wardrobeItems = [
  {
    id: 1,
    name: 'Classic Jeans',
    category: 'Bottoms',
    image: 'https://images.unsplash.com/photo-1542272617-08f086302520?auto=format&fit=crop&q=80&w=400'
  },
  {
    id: 2,
    name: 'Navy Blazer',
    category: 'Tops',
    image: 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&q=80&w=400'
  },
  {
    id: 3,
    name: 'White T-Shirt',
    category: 'Tops',
    image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&q=80&w=400'
  },
  {
    id: 4,
    name: 'Canvas Sneakers',
    category: 'Shoes',
    image: 'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&q=80&w=400'
  },
  {
    id: 5,
    name: 'Cargo Pants',
    category: 'Bottoms',
    image: 'https://images.unsplash.com/photo-1551028919-ac6635f0e5c9?auto=format&fit=crop&q=80&w=400'
  },
  {
    id: 6,
    name: 'Leather Jacket',
    category: 'Outerwear',
    image: 'https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?auto=format&fit=crop&q=80&w=400'
  }
]

// Filter logic (optional, for interactivity)
const filteredItems = computed(() => {
  if (activeCategory.value === 'All') return wardrobeItems
  return wardrobeItems.filter(item => item.category === activeCategory.value)
})

const handleAddClick = () => {
  console.log('Open upload modal...')
  // Emit event or toggle modal state here
}
</script>

<template>
  <div class="relative min-h-full pb-32 bg-white">
    <header class="sticky top-0 z-30 bg-white/95 backdrop-blur-sm px-5 py-4 flex justify-between items-center border-b border-slate-100 h-[72px]">
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Wardrobe</h1>
      
    </header>
    
    <div class="sticky top-0 z-20 bg-white/95 backdrop-blur-sm border-b border-slate-100 py-3 px-5">
      <div class="flex gap-3 overflow-x-auto no-scrollbar pb-1">
        <button 
          v-for="cat in categories" 
          :key="cat"
          @click="activeCategory = cat"
          :class="[
            'whitespace-nowrap px-5 py-2 rounded-full text-sm font-medium transition-all duration-300',
            activeCategory === cat 
              ? 'bg-slate-900 text-white border border-slate-900 shadow-md' 
              : 'bg-white text-slate-600 border border-slate-200 hover:border-blue-600 hover:text-blue-600'
          ]"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <div class="px-5 pt-6">
      <div class="grid grid-cols-2 gap-x-4 gap-y-6">
        
        <div 
          v-for="item in filteredItems" 
          :key="item.id" 
          class="group cursor-pointer"
        >
          <div class="aspect-[3/4] rounded-2xl bg-slate-50 overflow-hidden mb-3 border border-slate-100 relative shadow-sm">
            <img 
              :src="item.image" 
              :alt="item.name" 
              class="w-full h-full object-cover mix-blend-multiply group-hover:scale-105 transition duration-500 ease-out"
              loading="lazy"
            >
            
            <div class="absolute top-2 right-2 w-7 h-7 rounded-full bg-white/90 backdrop-blur shadow-sm flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-slate-700">
              <i class="fa-solid fa-pen"></i>
            </div>
          </div>

          <div class="flex justify-between items-start">
            <div class="flex flex-col">
              <span class="font-bold text-slate-900 text-sm leading-tight">{{ item.name }}</span>
              <span class="text-[10px] text-slate-400 font-medium uppercase tracking-wide mt-0.5">{{ item.category }}</span>
            </div>
            <button class="w-6 h-6 flex items-center justify-center text-slate-300 hover:text-blue-600 transition">
              <i class="fa-solid fa-ellipsis-vertical text-xs"></i>
            </button>
          </div>
        </div>

      </div>
      
      <div v-if="filteredItems.length === 0" class="py-20 text-center text-slate-400">
        <p>No items found in this category.</p>
      </div>
    </div>

    <button 
      @click="handleAddClick"
      class="fixed z-30 bottom-24 left-1/2 transform -translate-x-1/2 w-16 h-16 bg-slate-900 text-white rounded-full shadow-xl shadow-slate-400/40 flex items-center justify-center text-2xl hover:scale-105 hover:bg-blue-600 transition duration-300 active:scale-95"
      aria-label="Add Item"
    >
      <i class="pi pi-plus"></i>
    </button>

  </div>
</template>

<style scoped>
/* Utility to hide scrollbar but keep functionality */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>