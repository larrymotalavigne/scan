# Development Dockerfile for frontend
FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source (will be overridden by volume mount in development)
COPY . .

EXPOSE 4200

# Run development server with hot reload
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll", "2000"]
