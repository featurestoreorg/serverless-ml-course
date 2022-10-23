#!/bin/bash


if [ "$HOPSWORKS_API_KEY" == "" ] ; then
  echo "Enter your HOPSWORKS_API_KEY:"
  read KEY
  export HOPSWORKS_API_KEY="$KEY"
fi

if [ "$HOPSWORKS_PROJECT" == "" ] ; then
  echo "Enter the name of your project:"
  read proj
  export HOPSWORKS_PROJECT=$proj
export 

python -m streamlit run cc-fraud-streamlit-ui.py
