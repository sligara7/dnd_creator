#!/bin/bash

# Run development server
poetry run uvicorn metrics_service.main:app --reload --host 0.0.0.0 --port 8000