#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../frontend"
[ -f .env ] || [ ! -f env.example ] || cp env.example .env
npm run start
