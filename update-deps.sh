#!/bin/bash

pipdeptree -f --warn silence | grep -P '^[\w0-9\-=.]+' | cut -d = -f 1 | xargs -n1 pip install -U

