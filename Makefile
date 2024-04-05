help:
	@echo "Usage: make [TARGET]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment Variables:"
	@echo "  DOCKER				 Docker command"
	@echo "  DEV_IMAGE			  Development environment image name"
	@echo "  BOT_IMAGE			  Bot image name"
	@echo "  BOT_TOKEN			  Token required for running the bot container"
	@echo ""
	@echo "Example Usage:"
	@echo "  - To build the development image:"
	@echo "	  make build_dev_image"
	@echo ""
	@echo "  - To run the development container:"
	@echo "	  make run_dev_container"
	@echo ""
	@echo "  - To run linter (Python formatting) within development container:"
	@echo "	  make lint_python_formatting"
	@echo ""
	@echo "  - To build the bot image:"
	@echo "	  make build_bot_image"
	@echo ""
	@echo "  - To run the bot within container with the specified BOT_TOKEN:"
	@echo "	  make run_bot_container BOT_TOKEN=<your_bot_token>"
	
DOCKER = docker
DEV_IMAGE = dev_image
BOT_IMAGE = bot_image
JENKINS_IMAGE = jenkins_image

build_dev_image:
	$(DOCKER) build -t $(DEV_IMAGE) --build-arg USER_ID=$(shell id -u) --build-arg GROUP_ID=$(shell id -g) . -f ./environment/Dockerfile.dev

run_dev_container: build_dev_image
	$(DOCKER) run -it -e USER_ID=$(shell id -u) -e GROUP_ID=$(shell id -g) -v $(CURDIR):/home/whore $(DEV_IMAGE)

lint_python_formatting: build_dev_image
	$(DOCKER) run --rm -e USER_ID=$(shell id -u) -e GROUP_ID=$(shell id -g) -v $(CURDIR):/home/whore $(DEV_IMAGE) ./scripts/python-linter-formatting.sh

build_bot_image:
	$(DOCKER) build -t $(BOT_IMAGE) . -f ./environment/Dockerfile.bot

run_bot_container: build_bot_image
ifndef BOT_TOKEN
	$(error BOT_TOKEN is not set. Please set BOT_TOKEN before running make.)
endif
	$(DOCKER) run --rm -d --name telegram_bot -e BOT_TOKEN=${BOT_TOKEN} -p 443:443 -v $(CURDIR):/home/whore $(BOT_IMAGE) 

build_jenkins_image:
	$(DOCKER) build . -t ${JENKINS_IMAGE} -f ./environment/Dockerfile.jenkins

run_jenkins_server: build_jenkins_image
	$(DOCKER) run -d -p 8080:8080 -p 50000:50000 -p 22:22 -v jenkins_home:/var/jenkins_home ${JENKINS_IMAGE}