#!/bin/bash

set -e

cd src/03-module

jupyter nbconvert --to notebook --execute 4_batch_predictions.ipynb
