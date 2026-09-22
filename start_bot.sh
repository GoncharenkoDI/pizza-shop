#!/usr/bin/env bash

ruff check . --fix
black . 
python3 -m bot