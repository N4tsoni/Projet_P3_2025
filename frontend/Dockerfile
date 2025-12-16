# Dockerfile pour le frontend Vue.js
FROM node:20-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste des fichiers
COPY . .

# Exposer le port Vite
EXPOSE 5173

# Commande par défaut (sera overridée par docker-compose)
CMD ["npm", "run", "dev", "--", "--host"]
