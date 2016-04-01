#!/bin/bash

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/..

websocketd --staticdir $(pwd)/examples/euchre_static --port 8080 $(pwd)/examples/euchre-play-hand.sh
