# ==========================================
# FRONTEND DOCKERFILE - Art Manager Astro
# ==========================================

# Usamos Node 22 (la versión que tienes) en su variante ligera Alpine
FROM node:22-alpine

# Configuramos pnpm como gestor de paquetes por defecto
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# Directorio de trabajo
WORKDIR /app

# Copiamos los archivos de dependencias primero (para aprovechar la caché de Docker)
COPY package.json pnpm-lock.yaml ./

# Instalamos las dependencias
RUN pnpm install --frozen-lockfile

# Copiamos el resto del código del frontend
COPY . .

# Puerto que usa Astro por defecto
EXPOSE 4321

# Comando para iniciar en modo desarrollo con hot reload y accesible desde fuera del contenedor
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]