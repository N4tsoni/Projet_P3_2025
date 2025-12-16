<script setup lang="ts">
import { computed } from 'vue'
import BaseButton from '../atoms/BaseButton.vue'
import BaseIcon from '../atoms/BaseIcon.vue'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'

interface Props {
  isPlaying?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  isPlaying: false,
  size: 'sm',
})

const emit = defineEmits<{
  play: []
  pause: []
  toggle: []
}>()

function handleToggle() {
  emit('toggle')
  if (props.isPlaying) {
    emit('pause')
  } else {
    emit('play')
  }
}
</script>

<template>
  <button
    :class="['audio-player', `size-${size}`, { 'is-playing': isPlaying }]"
    @click="handleToggle"
    class="flex items-center gap-2 px-4 py-2 rounded-full glass-effect border border-white/20 
           hover:bg-white/10 hover:border-primary transition-all duration-300 cursor-pointer"
  >
    <BaseIcon :size="16">
      <VideoPlay v-if="!isPlaying" />
      <VideoPause v-else />
    </BaseIcon>
    
    <span class="audio-player-text text-sm font-medium text-white/80">
      {{ isPlaying ? 'Pause' : 'Écouter' }}
    </span>
  </button>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.audio-player {
  &:hover {
    transform: translateX(2px);
    color: $primary;
  }
  
  &.is-playing {
    background: linear-gradient(135deg, rgba($primary, 0.2) 0%, rgba($primary-dark, 0.2) 100%);
    border-color: $primary;
    color: $primary;
  }
  
  &.size-sm {
    @apply text-xs;
  }
  
  &.size-lg {
    @apply px-6 py-3 text-base;
  }
}
</style>
