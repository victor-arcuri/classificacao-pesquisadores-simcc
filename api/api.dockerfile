    from node:18-alpine

    WORKDIR /app

    COPY package*.json ./

    RUN npm install

    COPY . .

    RUN npx prisma generate 

    EXPOSE 5000