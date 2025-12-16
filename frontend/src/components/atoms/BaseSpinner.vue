<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'primary',
})
</script>

<template>
  <div :class="['base-spinner', `size-${size}`, `color-${color}`]">
    <div class="spinner-circle"></div>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.base-spinner {
  @apply inline-flex items-center justify-center;
  
  // Sizes
  &.size-sm {
    @apply w-4 h-4;
  }
  
  &.size-md {
    @apply w-8 h-8;
  }
  
  &.size-lg {
    @apply w-12 h-12;
  }
  
  &.size-xl {
    @apply w-16 h-16;
  }
  
  // Colors
  &.color-primary .spinner-circle {
    border-color: rgba($primary, 0.2);
    border-top-color: $primary;
  }
  
  &.color-success .spinner-circle {
    border-color: rgba($success, 0.2);
    border-top-color: $success;
  }
  
  &.color-error .spinner-circle {
    border-color: rgba($error, 0.2);
    border-top-color: $error;
  }
  
  &.color-white .spinner-circle {
    border-color: rgba(255, 255, 255, 0.2);
    border-top-color: white;
  }
}

.spinner-circle {
  @apply w-full h-full rounded-full border-2;
  animation: spin 0.8s linear infinite;
}
</style>
