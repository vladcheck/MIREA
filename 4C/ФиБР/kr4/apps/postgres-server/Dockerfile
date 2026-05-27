FROM node:26-alpine

WORKDIR /app

RUN apk add --no-cache corepack && corepack enable

COPY package.json yarn.lock ./
COPY apps/postgres-server/package.json ./apps/postgres-server/

RUN yarn install --mode=skip-build

COPY . .

WORKDIR /app/apps/postgres-server

EXPOSE 3000

CMD ["node", "server.ts"]
