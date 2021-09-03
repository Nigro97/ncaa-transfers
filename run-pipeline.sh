#!/usr/bin/env bash

# Create database
python3 run.py create_db

# Run clustering
python3 run.py get_clusters --loadpath=s3://2021-msia423-nigro-nicholas/raw/sports_ref.csv

# Populate database
python3 run.py populate_db
