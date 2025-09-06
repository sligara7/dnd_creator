.PHONY: install format lint test coverage migrate clean build docs load-test load-test-ci load-test-report

# Development Setup
install:
	poetry install

# Code Quality
format:
	poetry run black .
	poetry run isort .

lint:
	poetry run ruff check .
	poetry run mypy .
	poetry run black --check .
	poetry run isort --check-only .

# Testing
test:
	poetry run pytest

coverage:
	poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml

test-watch:
	poetry run pytest-watch -- --cov=src --cov-report=term-missing

# Database
migrate:
	poetry run alembic upgrade head

migrate-create:
	poetry run alembic revision --autogenerate -m "$(message)"

migrate-down:
	poetry run alembic downgrade -1

migrate-reset:
	poetry run alembic downgrade base
	poetry run alembic upgrade head

# Development Server
run:
	poetry run uvicorn character_service.main:app --reload

shell:
	poetry run ipython

clean:
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.pyc" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +

# Docker
docker-build:
	docker build -t character-service .

docker-run:
	docker run -p 8000:8000 character-service

docker-compose:
	docker-compose up -d

# Documentation
docs:
	poetry run pdoc --html --output-dir docs src/character_service

# Help
# Load Testing
load-test:
	# Start service for testing (background)
	poetry run uvicorn character_service.main:app --port 8000 & \
	SERVER_PID=$$! ; \
	echo "Waiting for service to start..." ; \
	sleep 5 ; \
	# Run Locust with UI
	mkdir -p reports/locust ; \
	poetry run locust -f tests/performance/locust/locustfile.py --config tests/performance/locust/locust.conf ; \
	kill $$SERVER_PID

load-test-ci:
	# Start service for testing (background)
	poetry run uvicorn character_service.main:app --port 8000 & \
	SERVER_PID=$$! ; \
	echo "Waiting for service to start..." ; \
	sleep 5 ; \
	# Run Locust headless
	mkdir -p reports/locust ; \
	poetry run locust -f tests/performance/locust/locustfile.py \
		--headless \
		--users 100 \
		--spawn-rate 10 \
		--run-time 300 \
		--host http://localhost:8000 \
		--html reports/locust/report.html \
		--csv reports/locust/history ; \
	EXIT_CODE=$$? ; \
	kill $$SERVER_PID ; \
	exit $$EXIT_CODE

load-test-report:
	@echo "Generating load test report..."
	@if [ -f reports/locust/report.html ]; then \
		echo "Report available at: reports/locust/report.html" ; \
		echo "CSV data available in: reports/locust/history_*.csv" ; \
	else \
		echo "No report found. Run load-test-ci first." ; \
		exit 1 ; \
	fi

# Help
help:
	@echo "Available commands:"
	@echo "  make install        Install dependencies"
	@echo "  make format        Format code"
	@echo "  make lint          Lint code"
	@echo "  make test          Run tests"
	@echo "  make coverage      Run tests with coverage"
	@echo "  make migrate       Run database migrations"
	@echo "  make run           Start development server"
	@echo "  make shell         Start IPython shell"
	@echo "  make clean         Clean build artifacts"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docs          Generate documentation"
	@echo "  make load-test     Run load tests with UI"
	@echo "  make load-test-ci  Run load tests headless (CI)"
	@echo "  make load-test-report  View latest load test report"
