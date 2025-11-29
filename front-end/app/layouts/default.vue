<script setup lang="ts">
// Используем NuxtLink для переходов.
// Классы active-class автоматически применяются, когда маршрут активен.
</script>

<template>
  <div class="flex flex-col min-h-screen bg-white font-sans text-slate-800">
    
    <main class="flex-1 relative pb-[90px]">
      <slot />
    </main>

    <nav class="fixed bottom-0 w-full bg-white/95 backdrop-blur-md border-t border-slate-100 h-[80px] px-6 flex justify-between items-start pt-4 z-40">
      
      <NuxtLink to="/" class="flex flex-col items-center gap-1.5 w-14 group text-slate-400 hover:text-slate-900 transition-colors" active-class="!text-blue-600 font-semibold">
<i class="pi pi-home"></i>
        <span class="text-[10px] font-medium">Home</span>
      </NuxtLink>

      <NuxtLink to="/wardrobe" class="flex flex-col items-center gap-1.5 w-14 group text-slate-400 hover:text-slate-900 transition-colors" active-class="!text-blue-600 font-semibold">
<i class="pi pi-shopping-bag"></i>
        <span class="text-[10px] font-medium">Wardrobe</span>
      </NuxtLink>

      <NuxtLink to="/chat" class="flex flex-col items-center gap-1.5 w-14 group text-slate-400 hover:text-slate-900 transition-colors" active-class="!text-blue-600 font-semibold">
<i class="pi pi-comment"></i>
        <span class="text-[10px] font-medium">Chat</span>
      </NuxtLink>

      <NuxtLink to="/profile" class="flex flex-col items-center gap-1.5 w-14 group text-slate-400 hover:text-slate-900 transition-colors" active-class="!text-blue-600 font-semibold">
<i class="pi pi-user"></i>
        <span class="text-[10px] font-medium">Profile</span>
      </NuxtLink>

    </nav>
  </div>
</template>

<style scoped>
/* Дополнительные стили для активного состояния иконок, если нужно менять regular на solid */
.router-link-active i {
  /* Пример: если нужно принудительно менять стиль иконки */
}
</style>