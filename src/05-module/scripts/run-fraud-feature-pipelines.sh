#!/bin/bash

set -e

cd src/05-module

jupyter nbconvert --to notebook --execute 2_cc_feature_pipeline_with_ge.ipynb

