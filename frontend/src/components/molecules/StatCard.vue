<script setup lang="ts">
import BaseIcon from '../atoms/BaseIcon.vue'

interface Props {
  value: number | string
  label: string
  variant?: 'primary' | 'success' | 'error' | 'warning'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
})
</script>

<template>
  <div :class="['stat-card', `variant-${variant}`]" class="flex items-center gap-4 p-4 rounded-2xl glass-effect hover:bg-white/5 transition-all duration-300 cursor-default group">
    <div :class="['stat-icon', `icon-${variant}`]" class="flex items-center justify-center w-12 h-12 rounded-xl">
      <BaseIcon :size="24">
        <slot name="icon" />
      </BaseIcon>
    </div>
    
    <div class="stat-info flex flex-col gap-1">
      <div class="stat-value text-2xl font-bold text-white/90">
        {{ value }}
      </div>
      <div class="stat-label text-sm text-white/50">
        {{ label }}
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.stat-card {
  &:hover {
    transform: translateY(-2px);
  }
}

.stat-icon {
  @apply text-white shadow-lg;
  
  &.icon-primary {
    @include gradient-primary;
  }
  
  &.icon-success {
    @include gradient-success;
  }
  
  &.icon-error {
    background: linear-gradient(135deg, $error 0%, darken($error, 10%) 100%);
  }
  
  &.icon-warning {
    background: linear-gradient(135deg, $warning 0%, darken($warning, 10%) 100%);
  }
}
</style>
