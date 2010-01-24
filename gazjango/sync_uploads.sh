#!/usr/bin/env bash

# Synchronize the uploads/ folder from daily.swarthmore.edu to your machine.

# This will probably take a little while -- as of January 2010, it was 600MB in
# about 4,000 files.

rsync -vrhz --exclude resized --del --progress dailygazette@daily.swarthmore.edu:gazjango-trunk/gazjango/uploads/ ./uploads/
