# Frontend Dockerfile per DDFR
FROM node:18-alpine AS builder

# Imposta directory di lavoro
WORKDIR /app

# Copia file di dipendenze
COPY package*.json ./

# Installa dipendenze
RUN npm ci

# Copia il codice sorgente
COPY . .

# Variabili d'ambiente per il build (WebSocket config)
# Queste vengono incorporate nel bundle JavaScript al momento del build
ARG REACT_APP_WS_PROTOCOL=ws
ARG REACT_APP_WS_HOST=localhost
ARG REACT_APP_WS_PORT=8000

ENV REACT_APP_WS_PROTOCOL=${REACT_APP_WS_PROTOCOL} \
    REACT_APP_WS_HOST=${REACT_APP_WS_HOST} \
    REACT_APP_WS_PORT=${REACT_APP_WS_PORT}

# Build dell'applicazione React
RUN npm run build

# Stage di produzione con nginx
FROM nginx:alpine

# Copia i file buildati dallo stage builder
COPY --from=builder /app/build /usr/share/nginx/html

# Copia configurazione nginx personalizzata (opzionale)
# Se necessario, possiamo aggiungere una configurazione custom
RUN echo 'server { \
    listen 3000; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Espone la porta 3000
EXPOSE 3000

# Avvia nginx
CMD ["nginx", "-g", "daemon off;"]
