#!/bin/bash

pip install coverage

export PYTHONPATH=$(pwd)

for f in $(ls ./tests/*.py); do
    coverage run -a $f
done

