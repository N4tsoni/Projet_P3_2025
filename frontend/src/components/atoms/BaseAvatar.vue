<script setup lang="ts">
import BaseIcon from './BaseIcon.vue'

interface Props {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'user' | 'assistant' | 'primary' | 'success'
  src?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  variant: 'primary',
})
</script>

<template>
  <div :class="['base-avatar', `size-${size}`, `variant-${variant}`]">
    <img v-if="src" :src="src" alt="Avatar" class="avatar-image" />
    <div v-else class="avatar-icon">
      <slot>
        <BaseIcon :size="size === 'sm' ? 16 : size === 'md' ? 20 : size === 'lg' ? 24 : 32">
          <slot name="icon" />
        </BaseIcon>
      </slot>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.base-avatar {
  @apply relative flex items-center justify-center rounded-full
         shadow-lg overflow-hidden flex-shrink-0;
  
  // Sizes
  &.size-sm {
    @apply w-8 h-8;
  }
  
  &.size-md {
    @apply w-10 h-10;
  }
  
  &.size-lg {
    @apply w-12 h-12;
  }
  
  &.size-xl {
    @apply w-16 h-16;
  }
  
  // Variants
  &.variant-user {
    @include gradient-primary;
    @apply text-white;
  }
  
  &.variant-assistant {
    @include gradient-success;
    @apply text-white;
  }
  
  &.variant-primary {
    @include gradient-primary;
    @apply text-white;
  }
  
  &.variant-success {
    @include gradient-success;
    @apply text-white;
  }
}

.avatar-image {
  @apply w-full h-full object-cover;
}

.avatar-icon {
  @apply flex items-center justify-center w-full h-full;
}
</style>
