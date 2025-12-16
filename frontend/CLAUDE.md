# CLAUDE.md - Frontend Jarvis

Ce fichier fournit des instructions à Claude Code lors du travail sur le frontend de l'application Jarvis.

## 📋 Vue d'Ensemble du Projet

**Jarvis Frontend** - Interface web moderne pour l'assistant vocal intelligent Jarvis utilisant Vue.js 3, Vite, TypeScript, Tailwind CSS et Atomic Design.

### Stack Technique

- **Vue 3** - Framework JavaScript progressif avec Composition API
- **Vite** - Build tool ultra-rapide avec HMR instantané
- **TypeScript** - Type safety et meilleure expérience développeur
- **Tailwind CSS** - Utility-first CSS pour layouts et positionnements
- **SCSS** - Styles personnalisés et variables CSS
- **Element Plus** - Bibliothèque de composants UI Vue 3
- **Pinia** - State management officiel pour Vue 3
- **Axios** - Client HTTP pour les appels API

### Architecture

- **Atomic Design** - Méthodologie de design system (Atoms → Molecules → Organisms → Templates → Pages)
- **Composition API** - API Vue 3 moderne avec `<script setup>`
- **TypeScript strict** - Types définis pour tous les composants et services
- **SCSS Modules** - Styles scopés par composant

## 🏗️ Structure du Projet

```
frontend/
├── src/
│   ├── components/
│   │   ├── atoms/           # Composants de base réutilisables
│   │   │   ├── BaseButton.vue
│   │   │   ├── BaseBadge.vue
│   │   │   ├── BaseIcon.vue
│   │   │   └── ...
│   │   ├── molecules/       # Combinaisons d'atoms
│   │   │   ├── StatCard.vue
│   │   │   ├── MessageBubble.vue
│   │   │   ├── AudioPlayer.vue
│   │   │   └── ...
│   │   ├── organisms/       # Sections complexes
│   │   │   ├── VoiceRecorder.vue
│   │   │   ├── ConversationHistory.vue
│   │   │   ├── KnowledgeGraphViz.vue
│   │   │   └── ...
│   │   └── templates/       # Layouts de pages
│   ├── views/               # Pages de l'application
│   ├── stores/              # Pinia stores
│   │   └── conversation.ts
│   ├── services/            # Services API
│   │   └── api.ts
│   ├── types/               # Types TypeScript
│   │   └── api.ts
│   ├── styles/              # Styles globaux
│   │   ├── main.scss        # Point d'entrée des styles
│   │   ├── _variables.scss
│   │   └── _mixins.scss
│   ├── assets/              # Images, fonts, etc.
│   ├── App.vue              # Composant racine
│   └── main.ts              # Point d'entrée de l'app
├── public/                  # Fichiers statiques
├── index.html               # HTML de base
├── vite.config.ts           # Configuration Vite
├── tailwind.config.js       # Configuration Tailwind
├── tsconfig.json            # Configuration TypeScript
└── package.json             # Dépendances npm
```

## 🎨 Design System

### Couleurs (Tailwind Config)

```javascript
colors: {
  primary: {
    DEFAULT: '#667eea',  // Violet principal
    light: '#a855f7',    // Violet clair
    dark: '#764ba2',     // Violet foncé
  },
  success: {
    DEFAULT: '#10b981',  // Vert émeraude
    dark: '#059669',
  },
  error: {
    DEFAULT: '#ef4444',  // Rouge
    dark: '#dc2626',
  },
  warning: {
    DEFAULT: '#f59e0b',  // Orange
    dark: '#d97706',
  },
  dark: {
    DEFAULT: '#0a0e27',  // Background principal
    light: '#1a1e3f',
    lighter: '#2a2e4f',
  },
}
```

### Utilisation des Couleurs

**Tailwind** (pour classes utilitaires) :
```html
<div class="bg-primary text-white">...</div>
<button class="bg-success hover:bg-success-dark">...</button>
```

**SCSS** (pour styles personnalisés) :
```scss
.custom-element {
  background: $primary;
  color: $success;
}
```

### Mixins SCSS

```scss
@include glass-effect;        // Effet glassmorphism
@include gradient-primary;     // Gradient violet
@include gradient-success;     // Gradient vert
```

## 📦 Atomic Design

### Atoms (Composants de Base)

Les atoms sont les plus petits composants réutilisables :
- **BaseButton** - Boutons avec variants (primary, success, error, etc.)
- **BaseBadge** - Badges de status
- **BaseIcon** - Wrapper pour icons Element Plus
- **BaseInput** - Input customisé
- **BaseSpinner** - Loading spinner

**Exemple Atom** :
```vue
<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'success' | 'error'
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
})
</script>

<template>
  <button :class="['base-button', `variant-${variant}`, `size-${size}`]">
    <slot />
  </button>
</template>

<style lang="scss" scoped>
.base-button {
  @apply px-4 py-2 rounded-lg transition-all;

  &.variant-primary {
    @include gradient-primary;
    @apply text-white;
  }

  &.size-lg {
    @apply px-6 py-3 text-lg;
  }
}
</style>
```

### Molecules (Combinaisons)

Les molecules combinent plusieurs atoms :
- **StatCard** - Card de statistique (icon + valeur + label)
- **MessageBubble** - Bulle de message avec avatar
- **AudioPlayer** - Lecteur audio avec contrôles
- **NodeCard** - Card représentant un nœud du graphe

### Organisms (Sections Complexes)

Les organisms sont des sections complètes :
- **VoiceRecorder** - Interface d'enregistrement vocal
- **ConversationHistory** - Liste des messages
- **KnowledgeGraphViz** - Visualisation du graphe

### Templates & Pages

Templates = layouts réutilisables  
Pages = vues spécifiques de l'app

## 🔧 Conventions de Code

### Nomenclature

**Composants** :
- Atoms : `Base*.vue` (ex: `BaseButton.vue`)
- Molecules : `*Card.vue`, `*Player.vue` (ex: `StatCard.vue`)
- Organisms : Nom descriptif (ex: `VoiceRecorder.vue`)

**Fichiers** :
- Composants : PascalCase (ex: `BaseButton.vue`)
- Services : camelCase (ex: `apiService.ts`)
- Types : camelCase (ex: `api.ts`)
- Styles : kebab-case (ex: `main.scss`)

### Structure Composant Vue

```vue
<script setup lang="ts">
// 1. Imports
import { ref, computed } from 'vue'
import type { PropType } from 'vue'

// 2. Props
interface Props {
  title: string
  variant?: 'primary' | 'secondary'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary'
})

// 3. Emits
const emit = defineEmits<{
  click: [value: string]
}>()

// 4. State
const isActive = ref(false)

// 5. Computed
const classes = computed(() => ({
  'is-active': isActive.value
}))

// 6. Methods
function handleClick() {
  emit('click', 'value')
}
</script>

<template>
  <div :class="classes">
    <!-- Template -->
  </div>
</template>

<style lang="scss" scoped>
// Styles
</style>
```

### Styles

**Utiliser Tailwind pour** :
- Layouts (flex, grid, spacing)
- Positionnements
- Responsive
- Utilitaires de base

**Utiliser SCSS pour** :
- Animations complexes
- Effets visuels (glassmorphism, gradients)
- Styles spécifiques au composant
- Variables de couleurs

**Exemple** :
```vue
<template>
  <div class="flex items-center justify-between p-4 rounded-lg">
    <div class="custom-glow">...</div>
  </div>
</template>

<style lang="scss" scoped>
.custom-glow {
  @include glass-effect;
  box-shadow: 0 8px 32px rgba($primary, 0.4);
}
</style>
```

## 🔌 API Communication

### Service API (`src/services/api.ts`)

```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export const jarvisApi = {
  async healthCheck() {
    const { data } = await apiClient.get('/health')
    return data
  },

  async processVoice(audioBlob: Blob) {
    const formData = new FormData()
    formData.append('audio', audioBlob)
    const { data } = await apiClient.post('/voice/process', formData)
    return data
  },

  async getKnowledgeGraph() {
    const { data } = await apiClient.get('/knowledge/graph')
    return data
  },
}
```

### Types (`src/types/api.ts`)

```typescript
export interface VoiceProcessResponse {
  transcription: string
  response: string
  audioUrl: string
}

export interface KnowledgeGraph {
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
}
```

## 🗄️ State Management (Pinia)

```typescript
// src/stores/conversation.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useConversationStore = defineStore('conversation', () => {
  // State
  const messages = ref<Message[]>([])
  const isRecording = ref(false)

  // Getters
  const messageCount = computed(() => messages.value.length)

  // Actions
  function addMessage(message: Message) {
    messages.value.push(message)
  }

  return {
    messages,
    isRecording,
    messageCount,
    addMessage,
  }
})
```

## 🧪 Développement

### Commandes

```bash
# Développement
npm run dev          # Démarrer le serveur de dev (HMR)
npm run build        # Build de production
npm run preview      # Preview du build

# Code Quality
npm run lint         # Linter
npm run type-check   # Vérification TypeScript

# Tests (à configurer)
npm run test         # Tests unitaires
npm run test:e2e     # Tests end-to-end
```

### Hot Module Replacement

Vite fournit le HMR automatique. Les changements dans les fichiers `.vue`, `.ts`, `.scss` sont reflétés instantanément sans recharger la page.

### Proxy API

Le fichier `vite.config.ts` configure un proxy vers le backend :

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://backend:8000',
      changeOrigin: true,
    },
  },
}
```

Les requêtes `/api/*` sont automatiquement redirigées vers le backend.

## ✨ Features Implémentées

### Push-to-Talk Vocal
- Bouton microphone avec animations
- Enregistrement audio via MediaRecorder API
- Visualisation waveform temps réel
- Feedback visuel des états (idle, recording, processing)

### Historique Conversations
- Messages avec avatars (User/Jarvis)
- Animations slide-in
- Lecteur audio pour les réponses
- Clear history avec confirmation

### Knowledge Graph
- Statistiques (nœuds/relations)
- Liste des entités
- Placeholder pour visualisation interactive future

## 🎯 Best Practices

### Performance

1. **Lazy Loading** des composants lourds :
```typescript
const HeavyComponent = defineAsyncComponent(() =>
  import('./components/HeavyComponent.vue')
)
```

2. **Computed** au lieu de methods dans templates
3. **v-memo** pour listes longues
4. **Suspense** pour async components

### Accessibilité

1. Utiliser les attributs ARIA appropriés
2. Support clavier complet
3. Contrastes de couleurs suffisants
4. Labels pour les inputs

### TypeScript

1. Typer toutes les props et emits
2. Utiliser `interface` pour les types d'objets
3. Éviter `any` - préférer `unknown`
4. Définir les types dans `src/types/`

### CSS

1. Préférer Tailwind pour layouts
2. SCSS pour styles spécifiques
3. Scoped styles par défaut
4. Variables pour couleurs/spacing

## 📚 Ressources

- [Vue 3 Docs](https://vuejs.org/)
- [Vite Docs](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Element Plus](https://element-plus.org/)
- [Pinia](https://pinia.vuejs.org/)
- [Atomic Design](https://bradfrost.com/blog/post/atomic-web-design/)

## 🔄 Workflow Git

### Branches

- `main` - Production
- `develop` - Développement
- `feature/*` - Nouvelles fonctionnalités
- `fix/*` - Corrections de bugs

### Commits

Format : `type(scope): message`

Types :
- `feat` - Nouvelle fonctionnalité
- `fix` - Correction de bug
- `style` - Changements de style/CSS
- `refactor` - Refactoring de code
- `docs` - Documentation
- `test` - Tests

Exemples :
```
feat(atoms): add BaseButton component
fix(voice-recorder): resolve audio capture issue
style(app): update glassmorphism effects
refactor(api): simplify axios instance configuration
```

## 🐛 Debugging

### Vue Devtools

Installer [Vue Devtools](https://devtools.vuejs.org/) pour :
- Inspector les composants
- Voir l'état Pinia
- Timeline des événements
- Performance profiling

### Console

```typescript
console.log('[Component]', data)  // Logs
console.warn('[Warning]', issue)  // Warnings
console.error('[Error]', error)   // Errors
```

### Vite Debug

```bash
# Mode debug
vite --debug
vite build --debug
```

## 🚀 Déploiement

### Build de Production

```bash
npm run build
```

Génère les fichiers dans `dist/` optimisés pour production :
- Code minifié
- Assets optimisés
- Source maps
- Lazy loading

### Docker

Le `Dockerfile` dans `frontend/` build l'application :

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

## 📝 Notes Importantes

1. **Ne jamais commit** :
   - `node_modules/`
   - `dist/`
   - `.env.local`
   - Fichiers de config IDE personnels

2. **Toujours** :
   - Tester avant de commit
   - Suivre les conventions de nommage
   - Documenter les composants complexes
   - Typer en TypeScript
   - Utiliser Atomic Design

3. **Code Review** :
   - Props bien typées
   - Emits déclarés
   - Styles scopés
   - Performance optimisée
   - Accessibilité respectée

## 🆘 Support

Pour toute question ou problème :
1. Consulter cette documentation
2. Vérifier les docs officielles
3. Chercher dans les issues GitHub
4. Créer une issue avec label approprié

---

**Dernière mise à jour** : 2025-12-16
**Version** : 1.0.0
