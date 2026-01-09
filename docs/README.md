# 📚 Jarvis Documentation - Vault Obsidian

Ce dossier est un **vault Obsidian** contenant toute la documentation du projet Jarvis.

## 🚀 Comment Ouvrir

### Option 1 : Avec Obsidian (Recommandé)
1. Téléchargez [Obsidian](https://obsidian.md/) si ce n'est pas déjà fait
2. Lancez Obsidian
3. Cliquez sur "Ouvrir un dossier comme vault"
4. Sélectionnez le dossier `/home/sofian/Bureau/Projet_P3/docs`
5. Ouvrez le fichier **[[Home]]** pour commencer

### Option 2 : Sans Obsidian
Tous les fichiers sont en Markdown standard. Vous pouvez les lire avec n'importe quel éditeur de texte ou visualiseur Markdown.

## 📁 Structure

```
docs/
├── .obsidian/              # Configuration Obsidian
│   ├── app.json
│   ├── appearance.json
│   └── workspace.json
│
├── Home.md                 # 🏠 Point d'entrée principal
│
├── Architecture/
│   ├── ARCHITECTURE.md     # Architecture système complète
│   ├── PIPELINE_ARCHITECTURE.md  # Pipeline détaillée
│   └── README_PIPELINE.md  # Guide pipeline utilisateur
│
├── Implementation/
│   └── IMPLEMENTATION_SUMMARY.md  # Résumé des changements
│
├── Guides/
│   ├── START.md           # Démarrage 30 secondes
│   ├── QUICK_START.md     # Guide complet
│   └── KG_PIPELINE.md     # Overview KG
│
├── Config/
│   ├── CLAUDE.md          # Instructions Claude backend
│   └── frontend/CLAUDE.md # Instructions Claude frontend
│
├── Planning/
│   └── TODO.md            # Liste des tâches
│
└── Jarvis Architecture.canvas  # 🎨 Visualisation graphique
```

## 🎯 Navigation

### Commencer
- **[[Home]]** - Page d'accueil avec tous les liens
- **[[START]]** - Guide de démarrage rapide (30 secondes)
- **[[QUICK_START]]** - Installation complète

### Architecture
- **[[ARCHITECTURE]]** - Architecture système complète
- **[[PIPELINE_ARCHITECTURE]]** - Pipeline modulaire détaillée
- **[[README_PIPELINE]]** - Guide utilisateur pipeline

### Développement
- **[[TODO]]** - Suivi des tâches
- **[[IMPLEMENTATION_SUMMARY]]** - Fonctionnalités implémentées
- **[[CLAUDE]]** - Instructions pour développement

### Visualisation
- **Jarvis Architecture.canvas** - Vue graphique de l'architecture

## 🔗 Liens Wiki

Obsidian utilise la syntaxe `[[NomDuFichier]]` pour créer des liens entre documents.

Exemples :
- `[[Home]]` → Lien vers Home.md
- `[[ARCHITECTURE]]` → Lien vers ARCHITECTURE.md
- `[[README_PIPELINE|Guide Pipeline]]` → Lien avec alias

## 🏷️ Tags

Les documents sont organisés avec des tags :

- `#jarvis` - Général
- `#pipeline` - Pipeline KG
- `#architecture` - Architecture
- `#frontend` - Frontend Vue.js
- `#backend` - Backend FastAPI
- `#neo4j` - Base de données graphe
- `#ai-assistant` - Assistant vocal

## 🎨 Canvas

Le fichier **Jarvis Architecture.canvas** est une visualisation interactive de l'architecture. Ouvrez-le dans Obsidian pour voir :
- Les composants du système
- Les connexions entre modules
- Les technologies utilisées
- Le flow de données

## 🔍 Recherche

Dans Obsidian :
- `Ctrl/Cmd + O` : Recherche rapide de fichiers
- `Ctrl/Cmd + Shift + F` : Recherche globale dans tous les fichiers
- `Ctrl/Cmd + G` : Vue graphe des connexions

## 📊 Graphe de Connaissances

Obsidian génère automatiquement un graphe montrant les connexions entre tous les documents. Cliquez sur l'icône "Graph view" pour le voir.

## ✨ Fonctionnalités Obsidian Utiles

1. **Backlinks** - Voir tous les fichiers qui référencent le document actuel
2. **Outline** - Table des matières automatique
3. **Tags Panel** - Vue d'ensemble de tous les tags
4. **Canvas** - Visualisation graphique personnalisée
5. **Templates** - Créer des templates pour nouveaux documents

## 🚀 Commandes Utiles

- `Ctrl/Cmd + P` : Palette de commandes
- `Ctrl/Cmd + E` : Basculer mode édition/lecture
- `Ctrl/Cmd + Click` : Suivre un lien dans un nouvel onglet
- `Alt/Option + Click` : Ouvrir un lien dans un nouveau panneau

## 📝 Contribuer

Pour ajouter de la documentation :

1. Créez un nouveau fichier `.md` dans le dossier approprié
2. Ajoutez un front-matter avec tags :
```markdown
---
tags: [jarvis, votre-tag]
---
```
3. Ajoutez des liens depuis/vers d'autres documents
4. Mettez à jour [[Home]] si nécessaire

## 🎓 Ressources

- [Documentation Obsidian](https://help.obsidian.md/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Obsidian Community](https://obsidian.md/community)

---

**Version** : 1.0.0
**Dernière mise à jour** : 2026-01-07
**Maintenu par** : Équipe Jarvis

Bon voyage dans la documentation ! 🚀
