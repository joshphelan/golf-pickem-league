FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application (for production)
# In dev, we override CMD to use npm run dev
RUN npm run build

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Production command (overridden in dev docker-compose)
CMD ["node", ".next/standalone/server.js"]
