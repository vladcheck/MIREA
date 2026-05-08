#!/bin/zsh
set -e

if [ ! -d "node_modules" ]; then
  echo "Installing dependencies via pnpm..."
  pnpm install
fi

echo "Generating Swagger spec..."
pnpm run swagger

echo "Starting server..."
exec pnpm start