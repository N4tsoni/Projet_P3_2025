<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'success' | 'error' | 'warning' | 'ghost'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  circle?: boolean
  loading?: boolean
  disabled?: boolean
  icon?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  circle: false,
  loading: false,
  disabled: false,
  icon: false,
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  const classes = ['base-button']
  
  classes.push(`variant-${props.variant}`)
  classes.push(`size-${props.size}`)
  
  if (props.circle) classes.push('is-circle')
  if (props.loading) classes.push('is-loading')
  if (props.disabled) classes.push('is-disabled')
  if (props.icon) classes.push('is-icon')
  
  return classes
})

function handleClick(event: MouseEvent) {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="button-spinner"></span>
    <span :class="{ 'button-content': true, 'opacity-0': loading }">
      <slot />
    </span>
  </button>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.base-button {
  @apply relative inline-flex items-center justify-center font-medium
         transition-all duration-300 cursor-pointer border-none;
  
  // Variants
  &.variant-primary {
    @include gradient-primary;
    @apply text-white shadow-lg;
    
    &:hover:not(.is-disabled):not(.is-loading) {
      @apply shadow-xl;
      transform: translateY(-2px);
    }
    
    &:active:not(.is-disabled):not(.is-loading) {
      transform: translateY(0);
    }
  }
  
  &.variant-success {
    @include gradient-success;
    @apply text-white shadow-lg;
    
    &:hover:not(.is-disabled):not(.is-loading) {
      @apply shadow-xl;
      transform: translateY(-2px);
    }
  }
  
  &.variant-error {
    background: linear-gradient(135deg, $error 0%, darken($error, 10%) 100%);
    @apply text-white shadow-lg;

    &:hover:not(.is-disabled):not(.is-loading) {
      @apply shadow-xl;
      transform: translateY(-2px);
    }
  }

  &.variant-warning {
    background: linear-gradient(135deg, $warning 0%, darken($warning, 10%) 100%);
    @apply text-white shadow-lg;
    
    &:hover:not(.is-disabled):not(.is-loading) {
      @apply shadow-xl;
      transform: translateY(-2px);
    }
  }
  
  &.variant-ghost {
    @include glass-effect;
    color: rgba(255, 255, 255, 0.8);

    &:hover:not(.is-disabled):not(.is-loading) {
      background: rgba(255, 255, 255, 0.1);
      color: white;
    }
  }
  
  // Sizes
  &.size-sm {
    @apply px-3 py-1.5 text-sm rounded-lg;
  }
  
  &.size-md {
    @apply px-4 py-2 text-base rounded-lg;
  }
  
  &.size-lg {
    @apply px-6 py-3 text-lg rounded-xl;
  }
  
  &.size-xl {
    @apply px-8 py-4 text-xl rounded-2xl;
  }
  
  // Circle
  &.is-circle {
    @apply rounded-full aspect-square p-0;
    
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
  }
  
  // Icon only
  &.is-icon {
    @apply p-2;
  }
  
  // States
  &.is-disabled {
    @apply opacity-50 cursor-not-allowed;
  }
  
  &.is-loading {
    @apply cursor-wait;
  }
}

.button-spinner {
  @apply absolute inset-0 flex items-center justify-center;
  animation: spin 1s linear infinite;
}

.button-content {
  @apply flex items-center justify-center gap-2;
}
</style>
