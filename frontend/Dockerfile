# ==========================================
# Stage 1: Build Vue 3 Frontend
# ==========================================
FROM node:20-alpine AS build-stage

WORKDIR /app

# Install dependencies using clean install
COPY package*.json ./
RUN npm ci

# Copy source code and build production bundle
COPY . .
RUN npm run build

# ==========================================
# Stage 2: Serve via Nginx
# ==========================================
FROM nginx:alpine AS production-stage

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy built production assets from builder
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
