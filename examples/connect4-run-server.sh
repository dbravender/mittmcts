#!/bin/bash

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/..

websocketd --staticdir $(pwd)/examples/connect4_static --port 8080 $(pwd)/examples/connect4-play.sh

