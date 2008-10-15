#!/usr/bin/env bash

cd $(dirname $0)
python=${1:-python}

./reset_db.sh && \
echo -n "initializing data..." && \
$python init_dev_data.py && \
echo "done."
