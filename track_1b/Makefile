IMAGE_NAME ?= apertus-swiss-hvet-eval

.PHONY: build run smoke api-smoke

build:
	docker build -t $(IMAGE_NAME) .

run: build
	docker run --rm $(IMAGE_NAME) --reproduce

smoke: build
	docker run --rm $(IMAGE_NAME) --check-runtime

api-smoke: build
	@if [ -f ../.env ]; then \
		docker run --rm --env-file ../.env \
			$(IMAGE_NAME) --api-smoke; \
	else \
		docker run --rm \
			-e LLM_NAME \
			-e LLM_BASE_URL \
			-e LLM_API_KEY \
			$(IMAGE_NAME) --api-smoke; \
	fi
