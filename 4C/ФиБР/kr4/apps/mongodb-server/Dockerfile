FROM node:26-alpine

WORKDIR /app

RUN apk add --no-cache corepack && corepack enable

COPY package.json yarn.lock ./
COPY apps/mongodb-server/package.json ./apps/mongodb-server/

RUN yarn install --mode=skip-build

COPY . .

WORKDIR /app/apps/mongodb-server

EXPOSE 3000

CMD ["node", "server.ts"]
