IMAGE_NAME ?= apertus-swiss-hvet-eval

.PHONY: build smoke run

build:
	docker build -t $(IMAGE_NAME) .

smoke: build
	docker run --rm $(IMAGE_NAME) --check-runtime

run: build
	@if [ -f ../.env ]; then \
		docker run --rm --env-file ../.env $(IMAGE_NAME) --check-config; \
	else \
		docker run --rm \
			-e LLM_NAME \
			-e LLM_BASE_URL \
			-e LLM_API_KEY \
			$(IMAGE_NAME) --check-config; \
	fi
