<script setup lang="ts">
import { computed } from 'vue'
import BaseAvatar from '../atoms/BaseAvatar.vue'

interface Props {
  role: 'user' | 'assistant'
  content: string
  author: string
  timestamp: string
}

const props = defineProps<Props>()

const avatarVariant = computed(() => {
  return props.role === 'user' ? 'user' : 'assistant'
})

const isUser = computed(() => props.role === 'user')
</script>

<template>
  <div :class="['message-bubble', `role-${role}`]" class="flex gap-3">
    <BaseAvatar
      v-if="!isUser"
      :variant="avatarVariant"
      size="md"
    >
      <template #icon>
        <slot name="icon" />
      </template>
    </BaseAvatar>
    
    <div class="message-content-wrapper flex flex-col gap-1 max-w-[70%]">
      <div class="message-header flex items-center gap-2 text-xs">
        <span class="message-author font-semibold text-white/90">
          {{ author }}
        </span>
        <span class="message-time text-white/40">
          {{ timestamp }}
        </span>
      </div>
      
      <div :class="['message-content', `content-${role}`]" class="p-3 rounded-2xl backdrop-blur-md border border-white/10 transition-all duration-300">
        {{ content }}
      </div>
      
      <div v-if="$slots.actions" class="message-actions">
        <slot name="actions" />
      </div>
    </div>
    
    <BaseAvatar
      v-if="isUser"
      :variant="avatarVariant"
      size="md"
    >
      <template #icon>
        <slot name="icon" />
      </template>
    </BaseAvatar>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.message-bubble {
  animation: slideIn 0.3s ease forwards;
  
  &.role-user {
    @apply flex-row-reverse;
    
    .message-content-wrapper {
      @apply items-end;
    }
    
    .message-content {
      background: linear-gradient(135deg, rgba($primary, 0.2) 0%, rgba($primary-dark, 0.2) 100%);
      @apply rounded-tr-sm;
      color: rgba(255, 255, 255, 0.95);

      &:hover {
        background: linear-gradient(135deg, rgba($primary, 0.3) 0%, rgba($primary-dark, 0.3) 100%);
      }
    }
  }
  
  &.role-assistant {
    .message-content {
      @apply rounded-tl-sm;
      background: rgba(255, 255, 255, 0.05);
      color: rgba(255, 255, 255, 0.9);

      &:hover {
        background: rgba(255, 255, 255, 0.08);
      }
    }
  }
}

.message-content {
  @apply text-sm leading-relaxed;
  
  &:hover {
    transform: translateY(-1px);
  }
}
</style>
