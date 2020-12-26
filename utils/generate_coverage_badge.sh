#!bin/bash
cd ..
docker-compose up -d postgres
pytest app
docker-compose down || true
rm .github/coverage.svg || true
coverage-badge -o .github/coverage.svg || true