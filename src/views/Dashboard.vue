<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">📊 数据仪表盘</h2>
    <div class="grid grid-cols-4 gap-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">今日待办</div>
        <div class="text-3xl font-bold text-blue-600 mt-2">{{ todayTodos }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">本周完成</div>
        <div class="text-3xl font-bold text-green-600 mt-2">{{ weekCompleted }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">进行中项目</div>
        <div class="text-3xl font-bold text-purple-600 mt-2">{{ activeProjects }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">OKR 进度</div>
        <div class="text-3xl font-bold text-orange-600 mt-2">{{ okrProgress }}%</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const todayTodos = ref(5)
const weekCompleted = ref(12)
const activeProjects = ref(3)
const okrProgress = ref(35)
</script>
