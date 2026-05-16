#!/bin/zsh
set -e

echo "Installing dependencies..."
pnpm install --silent

echo "Cleaning old Swagger output..."
rm -f ./swagger_output.json

echo "Generating Swagger spec..."
pnpm run swagger

echo "Starting server..."
exec pnpm start