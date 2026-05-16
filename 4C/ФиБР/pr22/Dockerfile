FROM node:18

WORKDIR /app

ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --only=production

COPY . .

CMD ["npm", "run", "start"]