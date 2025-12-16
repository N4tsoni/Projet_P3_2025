<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, Refresh, CircleClose, Grid, Check } from '@element-plus/icons-vue'
import { BaseButton, BaseIcon, BaseSpinner } from '../atoms'
import { StatCard } from '../molecules'
import { jarvisApi } from '@/services/api'
import type { KnowledgeGraph } from '@/types/api'

// State
const graph = ref<KnowledgeGraph | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// Methods
async function loadGraph() {
  try {
    loading.value = true
    error.value = null

    graph.value = await jarvisApi.getKnowledgeGraph()

    if (graph.value.nodes.length > 0) {
      ElMessage.success('Graphe chargé avec succès')
    }
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || err.message || 'Erreur lors du chargement'
    error.value = errorMsg
    console.error('Erreur chargement graphe:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadGraph()
})
</script>

<template>
  <div class="knowledge-graph-viz flex flex-col h-full gap-4">
    <!-- Header -->
    <div class="flex items-center justify-between p-3 glass-effect rounded-xl">
      <div class="flex items-center gap-2 text-sm text-white/80">
        <BaseIcon :size="20" color="#667eea">
          <Connection />
        </BaseIcon>
        <span>Graphe de Connaissances</span>
      </div>
      <BaseButton
        variant="ghost"
        size="sm"
        :loading="loading"
        @click="loadGraph"
      >
        <BaseIcon :size="16">
          <Refresh />
        </BaseIcon>
        Actualiser
      </BaseButton>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center gap-4">
      <BaseSpinner size="xl" color="primary" />
      <p class="text-sm text-white/60">Chargement du graphe...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center">
      <div class="w-24 h-24 rounded-full flex items-center justify-center"
           style="background: rgba(239, 68, 68, 0.1); border: 2px solid rgba(239, 68, 68, 0.3);">
        <BaseIcon :size="48" color="#ef4444">
          <CircleClose />
        </BaseIcon>
      </div>
      <h3 class="text-xl font-semibold text-white/80">Erreur</h3>
      <p class="text-sm text-white/50">{{ error }}</p>
      <BaseButton variant="primary" @click="loadGraph">
        Réessayer
      </BaseButton>
    </div>

    <!-- Graph Content -->
    <div v-else-if="graph && graph.nodes.length > 0" class="flex-1 flex flex-col gap-6 overflow-auto">
      <!-- Stats -->
      <div class="grid grid-cols-2 gap-4">
        <StatCard
          :value="graph.nodes.length"
          label="Nœuds"
          variant="primary"
        >
          <template #icon>
            <Grid />
          </template>
        </StatCard>

        <StatCard
          :value="graph.edges.length"
          label="Relations"
          variant="success"
        >
          <template #icon>
            <Connection />
          </template>
        </StatCard>
      </div>

      <!-- Viz Placeholder -->
      <div class="p-8 glass-effect rounded-2xl min-h-[300px] flex items-center justify-center">
        <div class="flex flex-col items-center gap-4 text-center">
          <BaseIcon :size="64" color="rgba(255, 255, 255, 0.2)">
            <Connection />
          </BaseIcon>
          <h3 class="text-lg font-semibold text-white/80">Visualisation Interactive</h3>
          <p class="text-sm text-white/50">La visualisation du graphe sera disponible prochainement</p>

          <div class="flex flex-wrap gap-3 justify-center mt-4">
            <div class="flex items-center gap-2 px-4 py-2 glass-effect rounded-full text-xs text-white/70">
              <BaseIcon :size="14" color="#10b981">
                <Check />
              </BaseIcon>
              <span>Nodes interactifs</span>
            </div>
            <div class="flex items-center gap-2 px-4 py-2 glass-effect rounded-full text-xs text-white/70">
              <BaseIcon :size="14" color="#10b981">
                <Check />
              </BaseIcon>
              <span>Relations dynamiques</span>
            </div>
            <div class="flex items-center gap-2 px-4 py-2 glass-effect rounded-full text-xs text-white/70">
              <BaseIcon :size="14" color="#10b981">
                <Check />
              </BaseIcon>
              <span>Exploration 3D</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Nodes List -->
      <div class="flex flex-col gap-3">
        <h4 class="text-base font-semibold text-white/80">Entités du Graphe</h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            v-for="node in graph.nodes"
            :key="node.id"
            class="flex items-center gap-3 p-3 glass-effect rounded-xl hover:bg-white/5
                   hover:-translate-y-0.5 hover:border-primary transition-all cursor-pointer"
          >
            <div class="w-9 h-9 rounded-lg flex items-center justify-center gradient-primary flex-shrink-0">
              <BaseIcon :size="20">
                <Grid />
              </BaseIcon>
            </div>
            <div class="flex flex-col gap-0.5 min-w-0 flex-1">
              <div class="text-sm font-medium text-white/90 truncate">
                {{ node.label }}
              </div>
              <div class="text-xs text-white/50">
                {{ node.type }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center">
      <div class="w-32 h-32 rounded-full glass-effect flex items-center justify-center">
        <BaseIcon :size="64" color="rgba(255, 255, 255, 0.3)">
          <Connection />
        </BaseIcon>
      </div>
      <h3 class="text-xl font-semibold text-white/80">Graphe Vide</h3>
      <p class="text-sm text-white/50 max-w-md">
        Le knowledge graph sera construit au fur et à mesure de vos conversations avec Jarvis
      </p>
      <BaseButton variant="primary" @click="loadGraph">
        Actualiser
      </BaseButton>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';
</style>
