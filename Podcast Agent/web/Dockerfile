FROM node:20-alpine AS builder

WORKDIR /app

# Copy only package files first
COPY package.json package-lock.json ./
RUN npm install

# Copy source files
COPY . .

RUN npm run build

# Nginx stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
