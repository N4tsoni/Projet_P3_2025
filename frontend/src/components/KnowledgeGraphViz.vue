<template>
  <div class="knowledge-graph-viz">
    <!-- Header -->
    <div class="graph-header">
      <div class="header-title">
        <el-icon><Connection /></el-icon>
        <span>Graphe de Connaissances</span>
      </div>
      <el-button
        size="small"
        :icon="Refresh"
        @click="loadGraph"
        :loading="loading"
        class="refresh-button"
      >
        Actualiser
      </el-button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">
        <el-icon class="spinning" :size="48">
          <Loading />
        </el-icon>
      </div>
      <p>Chargement du graphe...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">
        <el-icon :size="48">
          <CircleClose />
        </el-icon>
      </div>
      <h3>Erreur</h3>
      <p>{{ error }}</p>
      <el-button @click="loadGraph" type="primary">
        Réessayer
      </el-button>
    </div>

    <!-- Graph Content -->
    <div v-else-if="graph && graph.nodes.length > 0" class="graph-content">
      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon nodes-icon">
            <el-icon :size="24"><Grid /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ graph.nodes.length }}</div>
            <div class="stat-label">Nœuds</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon edges-icon">
            <el-icon :size="24"><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ graph.edges.length }}</div>
            <div class="stat-label">Relations</div>
          </div>
        </div>
      </div>

      <!-- Graph Visualization Placeholder -->
      <div class="graph-viz-container">
        <div class="viz-placeholder">
          <el-icon :size="64" class="viz-icon">
            <Connection />
          </el-icon>
          <h3>Visualisation Interactive</h3>
          <p>La visualisation du graphe sera disponible prochainement</p>
          <div class="viz-features">
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>Nodes interactifs</span>
            </div>
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>Relations dynamiques</span>
            </div>
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>Exploration 3D</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Nodes List -->
      <div class="nodes-list">
        <h4 class="list-title">Entités du Graphe</h4>
        <div class="nodes-grid">
          <div
            v-for="node in graph.nodes"
            :key="node.id"
            class="node-item"
          >
            <div class="node-icon">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="node-info">
              <div class="node-label">{{ node.label }}</div>
              <div class="node-type">{{ node.type }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <el-icon :size="64">
          <Connection />
        </el-icon>
      </div>
      <h3>Graphe Vide</h3>
      <p>Le knowledge graph sera construit au fur et à mesure de vos conversations avec Jarvis</p>
      <el-button @click="loadGraph" type="primary">
        Actualiser
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ElButton,
  ElIcon,
  ElMessage,
} from 'element-plus'
import {
  Connection,
  Refresh,
  Loading,
  CircleClose,
  Grid,
  Check,
} from '@element-plus/icons-vue'
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

<style scoped>
.knowledge-graph-viz {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

/* Header */
.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.header-title .el-icon {
  color: #667eea;
}

.refresh-button {
  color: rgba(255, 255, 255, 0.8) !important;
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  transition: all 0.3s ease;
}

.refresh-button:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: #667eea !important;
  color: #667eea !important;
}

/* Loading State */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem;
}

.loading-spinner .spinning {
  color: #667eea;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

/* Error State */
.error-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
}

.error-icon {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.1);
  border: 2px solid rgba(239, 68, 68, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
}

.error-state h3 {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.error-state p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  margin: 0;
}

/* Graph Content */
.graph-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
  overflow: auto;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.nodes-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.edges-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* Graph Visualization */
.graph-viz-container {
  padding: 2rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  min-height: 300px;
}

.viz-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}

.viz-icon {
  color: rgba(255, 255, 255, 0.2);
}

.viz-placeholder h3 {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.viz-placeholder p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  margin: 0;
}

.viz-features {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.feature-item .el-icon {
  color: #10b981;
}

/* Nodes List */
.nodes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.nodes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.node-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.node-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
  border-color: #667eea;
}

.node-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.node-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.node-label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-type {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
}

.empty-icon {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.3);
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.empty-state p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  max-width: 400px;
}
</style>
