<script setup lang="ts">
import { ElIcon } from 'element-plus'

interface Props {
  size?: number | string
  color?: string
  spin?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 20,
})
</script>

<template>
  <ElIcon
    :size="size"
    :color="color"
    :class="{ 'icon-spin': spin }"
  >
    <slot />
  </ElIcon>
</template>

<style lang="scss" scoped>
.icon-spin {
  animation: spin 1s linear infinite;
}
</style>
