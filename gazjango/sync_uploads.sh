#!/usr/bin/env bash

# Synchronize the uploads/ folder from daily.swarthmore.edu to your machine.
# This will probably take a little while -- as of January 2009, it was 318 MB.

rsync -vrhz --del --progress dailygazette@daily.swarthmore.edu:gazjango-trunk/gazjango/uploads/ ./uploads/
