#!/bin/bash

# Run tests with coverage
poetry run pytest tests/ -v --cov=src --cov-report=term-missing $@