#!bin/bash

rm .github/coverage.svg || true
coverage-badge -o .github/coverage.svg || true