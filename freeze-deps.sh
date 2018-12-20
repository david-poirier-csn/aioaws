#!/bin/bash

pipdeptree -f --warn silence | grep -P '^[\w0-9\-=.]+' > requirements-dev.txt
pipdeptree -f --warn silence | grep -P '^[\w0-9\-=.]+' | egrep -iv '^(ipython|pytest|pytest-asyncio|pudb|pipdeptree|pylint|twine|wheel)==' > requirements.txt

