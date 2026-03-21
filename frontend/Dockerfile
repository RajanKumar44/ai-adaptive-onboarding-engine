# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Build-time variables (used by Vite)
ARG VITE_API_URL=http://localhost:8000/api/v1
ARG VITE_APP_NAME="AI Adaptive Onboarding Engine"

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_APP_NAME=$VITE_APP_NAME

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# Copy source
COPY . .

# Build app
RUN npm run build

# Production stage
FROM nginx:1.27-alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy build output
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose correct port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:3000/ || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]