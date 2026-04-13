<script setup lang="ts"></script>

<template>
  <div
    class="relative min-h-screen overflow-hidden bg-gradient-to-br from-blue-50 via-slate-50 to-indigo-100"
  >
    <div
      class="absolute inset-0 pointer-events-none bg-center bg-cover opacity-35 blur-xl scale-110"
      style="background-image: url('/images/mtm-cover-logo.svg')"
    ></div>
    <div
      class="absolute inset-0 pointer-events-none bg-white/45 backdrop-blur-[2px]"
    ></div>
    <div
      class="relative z-10 max-w-5xl mx-auto px-6 py-20 md:py-28 text-center flex flex-col items-center"
    >
      <h1 class="text-4xl md:text-6xl font-extrabold text-slate-900 tracking-wide">
        MTM Helper
      </h1>
      <p class="mt-4 text-lg md:text-xl text-slate-700">
        智能药品管理系统
      </p>
      <p class="mt-3 text-sm md:text-base text-slate-600 max-w-2xl">
        科学管理药品、按时提醒服药、追踪健康记录，让用药更安全更省心。
      </p>
      <div class="mt-8 flex gap-4">
        <router-link
          to="/login"
          class="px-6 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
        >
          登录
        </router-link>
        <router-link
          to="/register"
          class="px-6 py-3 rounded-lg bg-white/85 text-slate-700 font-medium border border-slate-200 hover:bg-white transition-colors"
        >
          注册
        </router-link>
      </div>
    </div>
  </div>
</template>
