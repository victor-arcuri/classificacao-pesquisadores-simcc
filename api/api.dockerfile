# Builder: instala deps e gera client Prisma
FROM node:18-alpine AS builder
WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY prisma ./prisma
RUN npx prisma generate

COPY . .
RUN npm run build       


# Prod: inicia a apliação em ambiente de produção
FROM node:18-alpine AS prod
WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install --production

COPY --from=builder /usr/src/app/dist ./dist
COPY --from=builder /usr/src/app/node_modules/@prisma/client ./node_modules/@prisma/client
COPY --from=builder /usr/src/app/prisma ./prisma

CMD ["npm", "start"]


# Dev: inicia a aplicação em ambiente de desenvolvimento com hot-reload
FROM node:18-alpine AS dev
WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY prisma ./prisma
RUN npx prisma generate

COPY . .

CMD ["npm", "run", "dev", ]



