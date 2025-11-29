// https://nuxt.com/docs/api/configuration/nuxt-config
import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  
  modules: [
    '@nuxtjs/tailwindcss',
    '@primevue/nuxt-module',
    '@nuxt/ui',
    '@pinia/nuxt',
  ],

  srcDir: 'app/',
  css: [
    '~/assets/styles/index.css',
    'primeicons/primeicons.css',

  ],

})
