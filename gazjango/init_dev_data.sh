#!/usr/bin/env bash

rm -f development.db
./manage.py syncdb --noinput
./init_dev_data.py
