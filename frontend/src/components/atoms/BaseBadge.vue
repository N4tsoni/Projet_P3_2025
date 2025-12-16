<script setup lang="ts">
interface Props {
  type?: 'success' | 'error' | 'warning' | 'info' | 'primary'
  dot?: boolean
  pulse?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  dot: false,
  pulse: false,
  size: 'md',
})
</script>

<template>
  <span :class="['base-badge', `type-${type}`, `size-${size}`, { 'has-dot': dot }]">
    <span v-if="dot" :class="['badge-dot', { 'is-pulse': pulse }]"></span>
    <slot />
  </span>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.base-badge {
  @apply inline-flex items-center gap-2 font-medium rounded-full backdrop-blur-md
         border transition-all duration-300;
  
  // Types
  &.type-success {
    background: rgba($success, 0.2);
    color: $success;
    border-color: rgba($success, 0.3);
  }
  
  &.type-error {
    background: rgba($error, 0.2);
    color: $error;
    border-color: rgba($error, 0.3);
  }
  
  &.type-warning {
    background: rgba($warning, 0.2);
    color: $warning;
    border-color: rgba($warning, 0.3);
  }
  
  &.type-info {
    background: rgba(#3b82f6, 0.2);
    color: #3b82f6;
    border-color: rgba(#3b82f6, 0.3);
  }
  
  &.type-primary {
    background: rgba($primary, 0.2);
    color: $primary;
    border-color: rgba($primary, 0.3);
  }
  
  // Sizes
  &.size-sm {
    @apply px-2 py-1 text-xs;
  }
  
  &.size-md {
    @apply px-3 py-1.5 text-sm;
  }
  
  &.size-lg {
    @apply px-4 py-2 text-base;
  }
}

.badge-dot {
  @apply w-2 h-2 rounded-full bg-current;
  
  &.is-pulse {
    animation: pulse 2s ease-in-out infinite;
  }
}
</style>
