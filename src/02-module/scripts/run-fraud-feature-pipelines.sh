#!/bin/bash

set -e

cd src/02-module

jupyter nbconvert --to notebook --execute 2_cc_feature_pipeline.ipynb

