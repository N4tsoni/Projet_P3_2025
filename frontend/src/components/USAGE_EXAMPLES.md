# Exemples d'Utilisation des Composants Atomic Design

## 🧩 Atoms

### BaseButton

```vue
<script setup>
import { BaseButton } from '@/components/atoms'
</script>

<template>
  <!-- Primary button -->
  <BaseButton variant="primary" size="md" @click="handleClick">
    Cliquer ici
  </BaseButton>
  
  <!-- Success button with loading -->
  <BaseButton variant="success" :loading="isLoading">
    Enregistrer
  </BaseButton>
  
  <!-- Circle icon button -->
  <BaseButton variant="primary" circle size="lg">
    <BaseIcon><Plus /></BaseIcon>
  </BaseButton>
  
  <!-- Ghost button -->
  <BaseButton variant="ghost" size="sm">
    Annuler
  </BaseButton>
</template>
```

### BaseBadge

```vue
<template>
  <!-- Simple badge -->
  <BaseBadge type="success">Actif</BaseBadge>
  
  <!-- Badge with pulsing dot -->
  <BaseBadge type="success" dot pulse>En ligne</BaseBadge>
  
  <!-- Different sizes -->
  <BaseBadge type="warning" size="lg">Attention</BaseBadge>
</template>
```

### BaseIcon

```vue
<template>
  <!-- Basic icon -->
  <BaseIcon :size="24" color="#667eea">
    <ChatDotRound />
  </BaseIcon>
  
  <!-- Spinning icon -->
  <BaseIcon :size="32" spin>
    <Loading />
  </BaseIcon>
</template>
```

### BaseSpinner

```vue
<template>
  <!-- Default spinner -->
  <BaseSpinner />
  
  <!-- Large primary spinner -->
  <BaseSpinner size="lg" color="primary" />
  
  <!-- White spinner for dark backgrounds -->
  <BaseSpinner size="md" color="white" />
</template>
```

### BaseAvatar

```vue
<template>
  <!-- Avatar with icon -->
  <BaseAvatar variant="user" size="md">
    <template #icon>
      <User />
    </template>
  </BaseAvatar>
  
  <!-- Avatar with image -->
  <BaseAvatar :src="userImage" size="lg" />
  
  <!-- Assistant avatar -->
  <BaseAvatar variant="assistant" size="md">
    <template #icon>
      <Cpu />
    </template>
  </BaseAvatar>
</template>
```

## 🔬 Molecules

### StatCard

```vue
<script setup>
import { StatCard } from '@/components/molecules'
import { Grid } from '@element-plus/icons-vue'
</script>

<template>
  <StatCard
    :value="42"
    label="Nœuds"
    variant="primary"
  >
    <template #icon>
      <Grid />
    </template>
  </StatCard>
  
  <StatCard
    :value="15"
    label="Relations"
    variant="success"
  >
    <template #icon>
      <Connection />
    </template>
  </StatCard>
</template>
```

### MessageBubble

```vue
<script setup>
import { MessageBubble } from '@/components/molecules'
import { User, Cpu } from '@element-plus/icons-vue'
</script>

<template>
  <!-- User message -->
  <MessageBubble
    role="user"
    author="Vous"
    content="Bonjour Jarvis"
    timestamp="14:32"
  >
    <template #icon>
      <User />
    </template>
  </MessageBubble>
  
  <!-- Assistant message with audio -->
  <MessageBubble
    role="assistant"
    author="Jarvis"
    content="Bonjour ! Comment puis-je vous aider ?"
    timestamp="14:32"
  >
    <template #icon>
      <Cpu />
    </template>
    <template #actions>
      <AudioPlayer :is-playing="isPlaying" @toggle="toggleAudio" />
    </template>
  </MessageBubble>
</template>
```

### AudioPlayer

```vue
<script setup>
import { AudioPlayer } from '@/components/molecules'
import { ref } from 'vue'

const isPlaying = ref(false)

function toggleAudio() {
  isPlaying.value = !isPlaying.value
}
</script>

<template>
  <AudioPlayer
    :is-playing="isPlaying"
    size="md"
    @toggle="toggleAudio"
  />
</template>
```

## 🧬 Exemple Complet - Organism Refactoré

### ConversationHistory (simplifié)

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { MessageBubble, AudioPlayer } from '@/components/molecules'
import { BaseButton } from '@/components/atoms'
import { useConversationStore } from '@/stores/conversation'
import { User, Cpu, Delete } from '@element-plus/icons-vue'

const conversationStore = useConversationStore()
const messages = computed(() => conversationStore.messages)

function handleClearMessages() {
  // Logic
}
</script>

<template>
  <div class="conversation-history flex flex-col h-full gap-4">
    <!-- Header -->
    <div v-if="messages.length > 0" class="flex items-center justify-between p-3 glass-effect rounded-xl">
      <span class="text-sm text-white/80">
        {{ messages.length }} messages
      </span>
      <BaseButton variant="ghost" size="sm" @click="handleClearMessages">
        <BaseIcon><Delete /></BaseIcon>
        Effacer
      </BaseButton>
    </div>
    
    <!-- Messages List -->
    <div class="flex-1 overflow-auto">
      <div class="flex flex-col gap-4 p-2">
        <MessageBubble
          v-for="message in messages"
          :key="message.id"
          :role="message.role"
          :author="message.role === 'user' ? 'Vous' : 'Jarvis'"
          :content="message.content"
          :timestamp="formatTime(message.timestamp)"
        >
          <template #icon>
            <User v-if="message.role === 'user'" />
            <Cpu v-else />
          </template>
          <template v-if="message.audioUrl && message.role === 'assistant'" #actions>
            <AudioPlayer
              :is-playing="isPlayingMessage(message.id)"
              @toggle="() => toggleAudio(message)"
            />
          </template>
        </MessageBubble>
      </div>
    </div>
  </div>
</template>
```

## 🎨 Avec Tailwind + SCSS

```vue
<script setup>
import { BaseButton, BaseBadge } from '@/components/atoms'
</script>

<template>
  <!-- Tailwind pour layout -->
  <div class="flex items-center justify-between p-4 rounded-xl">
    <div class="flex items-center gap-3">
      <BaseButton variant="primary" size="md">
        Action
      </BaseButton>
      <BaseBadge type="success" dot pulse>
        Actif
      </BaseBadge>
    </div>
  </div>
  
  <!-- SCSS pour styles personnalisés -->
  <div class="custom-card">
    <h3>Titre</h3>
    <p>Contenu</p>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.custom-card {
  @include glass-effect;
  @apply p-6 rounded-2xl;
  
  h3 {
    @include gradient-primary;
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
}
</style>
```

## 📦 Imports Simplifiés

```typescript
// Import multiple atoms
import { BaseButton, BaseBadge, BaseIcon } from '@/components/atoms'

// Import multiple molecules
import { StatCard, MessageBubble, AudioPlayer } from '@/components/molecules'

// Import individual component
import BaseButton from '@/components/atoms/BaseButton.vue'
```
