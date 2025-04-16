.PHONY: check-system check-python source-conda conda-env deps install test cover lint check format clean docs run

# Environment names
CONDA_ENV_NAME := myenv

# Define Python version
PYTHON_MAJOR := 3
PYTHON_MINOR := 12

# Docker variables
IMAGE_NAME=agency

# Conda path (TODO : adjust as needed -- assumes installation via homebrew)
CONDA_PATH := /opt/homebrew/Caskroom/miniconda/base

# Check system requirements
check-system:
	@echo "Checking system requirements..."
	@which python3 >/dev/null || (echo "python3 is not installed" && exit 1)
	@python3 -c "import venv" >/dev/null 2>&1 || (echo "python3-venv is not installed" && exit 1)
	@which conda >/dev/null || (echo "conda is not installed" && exit 1)

# Check Python version
check-python: check-system
	@python3 -c "import sys; \
	assert sys.version_info >= ($(PYTHON_MAJOR), $(PYTHON_MINOR)), \
	'Python $(PYTHON_MAJOR).$(PYTHON_MINOR) or higher is required'"

# Source conda
source-conda: check-python
	@. $(CONDA_PATH)/etc/profile.d/conda.sh || (echo "Conda not found at $(CONDA_PATH)" && exit 1)

# Create conda environment
conda-env: source-conda
	conda create -n $(CONDA_ENV_NAME) python=$(PYTHON_VERSION) -y || true
	conda activate $(CONDA_ENV_NAME) && \
	conda install pip -y

# Install dependencies using pip
deps: check-python
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

# Install module
install: deps
	python3 -m pip install -e .

# Run tests without coverage
test: deps
	pytest tests/ || true

# Run tests with coverage
cover: deps
	pytest tests/ --cov=./ --cov-report=term-missing

lint:
	flake8 src/
	black --check src/
	black --check /tests
	isort --check-only src/
	isort --check-only /tests
	mypy src/
	mypy tests/
	pylint src/
	pylint tests/

# Run all checks
check: test lint

format:
	black src/
	black tests/
	isort src/
	isort tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	conda env remove -n $(CONDA_ENV_NAME) -y || true
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

docs:
	mkdocs build

docker_build_for_deployment: ## Build and push Docker image for deployment.
	@echo "Building & pushing Docker image ${VERSION} to ${ECR_REPO}..."
	docker build -t ${IMAGE_NAME}:${VERSION} .
	aws ecr get-login-password --region ap-south-1 | docker login -u AWS --password-stdin ${ECR_REPO}
	docker tag ${IMAGE_NAME}:${VERSION} ${ECR_REPO}:${VERSION}
	docker push ${ECR_REPO}:${VERSION}
	@echo "Done building & pushing Docker image!"

docker_build_for_deployment_multiple_tags: ## Build and push Docker image with multiple tags.
	@echo "Building & pushing Docker image ${VERSION} and ${ADDITIONAL_VERSION} to ${ECR_REPO}..."
	docker build -t ${IMAGE_NAME}:${VERSION} .
	aws ecr get-login-password --region ap-south-1 | docker login -u AWS --password-stdin ${ECR_REPO}
	docker tag ${IMAGE_NAME}:${VERSION} ${ECR_REPO}:${VERSION}
	docker push ${ECR_REPO}:${VERSION}
	docker tag ${IMAGE_NAME}:${VERSION} ${ECR_REPO}:${ADDITIONAL_VERSION}
	docker push ${ECR_REPO}:${ADDITIONAL_VERSION}
	@echo "Done building & pushing Docker image!"

# Run the app using uvicorn
run:
	python3 -m uvicorn src:app --reload