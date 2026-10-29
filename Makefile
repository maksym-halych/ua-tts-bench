.DEFAULT_GOAL := help
.PHONY: help validate-dataset-ids

DATASET ?= dataset.jsonl

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

validate-dataset-ids: ## Check that every id equals the md5 hash of its text
	@python3 scripts/validate_dataset_ids.py $(DATASET)
