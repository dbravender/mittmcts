#!/bin/bash

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/..
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
exec python examples/euchre_play.py
