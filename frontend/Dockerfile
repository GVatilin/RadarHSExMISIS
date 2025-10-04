# ---------- build ----------
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---------- run ----------
FROM node:20-alpine AS run
WORKDIR /app
RUN npm i -g serve
# Vite кладёт сюда:
COPY --from=build /app/dist /app/dist
EXPOSE 8081
CMD ["serve", "-s", "dist", "-l", "8081"]
