#!/bin/sh

pip install -r requirements.txt --upgrade
pip install -r requirements_full.txt --upgrade
pip install -r requirements_dev.txt --upgrade
pre-commit install
