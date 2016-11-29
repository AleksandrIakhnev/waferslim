#!/usr/bin/env bash
docker run -v $(pwd)/..:/waferslim -w /waferslim waferslim-unittests \
    nosetests --verbose \
    -with-coverage --cover-erase --cover-xml \
    --cover-xml-file=test-results/coverage.xml --cover-package waferslim