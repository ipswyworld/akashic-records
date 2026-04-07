#!/usr/bin/env bash
# quick helper: use a community Dukascopy downloader or browser widget to get CSVs for XAUUSD
# e.g. use 'duka' tool (see its GitHub) to download ticks and convert to CSV
# This script assumes you already downloaded xauusd_1min.csv into data/
mkdir -p data
echo "Place your downloaded xauusd_1min.csv into ./data and then run ticks_to_kafka.py"
