# Alibaba Cloud Container Registry
REGISTRY = msp24053-registry.cn-hongkong.cr.aliyuncs.com
PROJECT = fyp-demo
BACKEND_IMAGE = $(REGISTRY)/$(PROJECT)/newsense-backend
FRONTEND_IMAGE = $(REGISTRY)/$(PROJECT)/newsense-frontend
TAG = latest

# Build platforms
PLATFORM = linux/amd64

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make login     - Login to Alibaba Cloud ACR"
	@echo "  make build     - Build both backend and frontend images"
	@echo "  make build-backend  - Build only backend image"
	@echo "  make build-frontend - Build only frontend image"
	@echo "  make push      - Push both images to ACR"
	@echo "  make push-backend   - Push only backend image"
	@echo "  make push-frontend  - Push only frontend image"
	@echo "  make build-push     - Build and push both images"
	@echo "  make clean     - Remove local images"

# Login to ACR
.PHONY: login
login:
	@echo "Logging in to Alibaba Cloud ACR..."
	docker login $(REGISTRY)

# Build backend
.PHONY: build-backend
build-backend:
	@echo "Building backend image..."
	docker buildx build --platform $(PLATFORM) \
		-t $(BACKEND_IMAGE):$(TAG) \
		.

# Build frontend
.PHONY: build-frontend
build-frontend:
	@echo "Building frontend image..."
	docker buildx build --platform $(PLATFORM) \
		--build-arg REACT_APP_API_URL=http://msp24053-registry-vpc.cn-hongkong.cr.aliyuncs.com/fyp-demo/newsense-backend:8000 \
		-t $(FRONTEND_IMAGE):$(TAG) \
		./frontend

# Build both images
.PHONY: build
build: build-backend build-frontend

# Push backend
.PHONY: push-backend
push-backend:
	@echo "Pushing backend image..."
	docker push $(BACKEND_IMAGE):$(TAG)

# Push frontend
.PHONY: push-frontend
push-frontend:
	@echo "Pushing frontend image..."
	docker push $(FRONTEND_IMAGE):$(TAG)

# Push both images
.PHONY: push
push: push-backend push-frontend

# Build and push both images
.PHONY: build-push
build-push: build push

# Build and push in one command (using --push flag)
.PHONY: build-push-fast
build-push-fast:
	@echo "Building and pushing backend..."
	docker buildx build --platform $(PLATFORM) \
		-t $(BACKEND_IMAGE):$(TAG) \
		--push \
		.
	@echo "Building and pushing frontend..."
	docker buildx build --platform $(PLATFORM) \
		--build-arg REACT_APP_API_URL=http://backend:8000 \
		-t $(FRONTEND_IMAGE):$(TAG) \
		--push \
		./frontend

# Clean local images
.PHONY: clean
clean:
	@echo "Removing local images..."
	docker rmi $(BACKEND_IMAGE):$(TAG) || true
	docker rmi $(FRONTEND_IMAGE):$(TAG) || true

# Show image info
.PHONY: info
info:
	@echo "Registry: $(REGISTRY)"
	@echo "Project: $(PROJECT)"
	@echo "Backend Image: $(BACKEND_IMAGE):$(TAG)"
	@echo "Frontend Image: $(FRONTEND_IMAGE):$(TAG)"
	@echo "Platform: $(PLATFORM)"