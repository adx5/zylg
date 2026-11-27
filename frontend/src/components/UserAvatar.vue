<!-- frontend/src/components/UserAvatar.vue —— 统一默认头像：灰色扁平剪影 -->
<template>
  <div class="ua" :style="boxStyle">
    <img v-if="src" :src="src" class="ua-img" alt="" />
    <svg v-else class="ua-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round">
      <circle cx="12" cy="8.4" r="3.6" />
      <path d="M4.6 20.2c0-3.7 3.3-6.2 7.4-6.2s7.4 2.5 7.4 6.2" />
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  size: { type: Number, default: 48 },
  round: { type: Boolean, default: true },
  radius: { type: Number, default: 0 }
})

const boxStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  borderRadius: props.round ? '50%' : `${props.radius || 12}px`
}))
</script>

<style scoped>
.ua {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9edf2;
  color: #9aa6b5;
  overflow: hidden;
  flex-shrink: 0;
}
.ua-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ua-ico { width: 62%; height: 62%; }
</style>
