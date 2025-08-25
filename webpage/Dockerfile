# Build stage
FROM oven/bun:latest AS builder
WORKDIR /app
COPY . .
RUN bun i && bun run build

# Production stage
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built static files from builder
COPY --from=builder /app/.output/public /usr/share/nginx/html

# Set recommended nginx configuration for production static serving
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
