.PHONY: format lint test clean

format:
	@echo "Formatting code with Black and isort..."
	black src/ tests/
	isort src/ tests/
	@echo "✅ Code formatting completed successfully!"

lint:
	@echo "Linting code with flake8 and mypy..."
	flake8 src/ tests/
	mypy --ignore-missing-imports src/
	@echo "✅ Linting completed successfully!"

test:
	@echo "Running tests with pytest..."
	pytest tests/ --cov=src --cov-report=xml --cov-report=term

clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .mypy_cache
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ci: format lint test
	@echo "✅ CI checks completed successfully!"

# For Windows users (use these instead of make commands)
format-win:
	@echo "Formatting code with Black and isort..."
	python -m black src tests
	python -m isort src tests
	@echo "✅ Code formatting completed successfully!"

lint-win:
	@echo "Linting code with flake8 and mypy..."
	python -m flake8 src tests
	python -m mypy --ignore-missing-imports src
	@echo "✅ Linting completed successfully!"

test-win:
	@echo "Running tests with pytest..."
	python -m pytest tests --cov=src --cov-report=xml --cov-report=term

ci-win: format-win lint-win test-win
	@echo "✅ CI checks completed successfully!"
