#!/usr/bin/env bash
docker run -v $(pwd)/..:/waferslim -v $(pwd)/..:/usr/local/lib/python3.5/site-packages/waferslim \
    -w /waferslim/tests waferslim-unittests \
    nosetests --verbose \
    --with-coverage --cover-erase --cover-xml \
    --cover-xml-file=test-results/coverage.xml --cover-package waferslim