#!/bin/bash

set -e

cd src/01-module

echo "Running synthetic credit card transactions feature pipeline"
jupyter nbconvert --to notebook --execute 2_cc_feature_pipeline.ipynb
echo "Running batch prediction pipeline"
jupyter nbconvert --to notebook --execute 5_batch_predictions.ipynb

