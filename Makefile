CONTAINER_CMD := $(or $(CONTAINER_CMD), $(shell command -v podman 2> /dev/null))
ifndef CONTAINER_CMD
CONTAINER_CMD := docker
endif

PROW_JOBS_SCRAPER_IMAGE := $(or $(PROW_JOBS_SCRAPER_IMAGE),quay.io/edge-infrastructure/prow-jobs-scraper)
PROW_JOBS_SCRAPER_TAG := $(or $(PROW_JOBS_SCRAPER_TAG),latest)

install:
	pip install .
	$(MAKE) clean-install

install-lint:
	pip install .[lint]
	$(MAKE) clean-install

install-unit-tests:
	pip install .[test-runner]
	$(MAKE) clean-install

full-install: install install-lint install-unit-tests

# setuptools leaves a build/ directory behind after "pip install"
# clean it up in order to be able to install packages during
# "build" and "test" phases in Prow
clean-install:
	rm -rf ./build

unit-tests:
	tox

format:
	black src/ tests/
	isort --profile black src tests/

mypy:
	mypy --non-interactive --install-types src/

lint-manifest:
	oc process --local=true -f openshift/template.yaml --param IMAGE_TAG=foobar --param REMOVE_ELASTICSEARCH_DUPLICATIONS_ES_COMPARABLE_INDEX=foobar | oc apply --dry-run=client -f -

lint: mypy format
	git diff --exit-code

publish-coverage:
	@if [ "${OPENSHIFT_CI}" = "true" ]; then \
		hack/publish-codecov.sh; \
	fi

build-image:
	$(CONTAINER_CMD) build $(CONTAINER_BUILD_EXTRA_PARAMS) -t $(PROW_JOBS_SCRAPER_IMAGE):$(PROW_JOBS_SCRAPER_TAG) .

.PHONY: install install-lint install-unit-tests full-install unit-tests format mypy lint lint-manifest build-image publish-coverage
