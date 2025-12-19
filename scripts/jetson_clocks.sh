#!/bin/bash
# Enable Jetson Clocks for maximum performance
echo "Enabling Jetson Clocks..."
sudo jetson_clocks
sudo jetson_clocks --show
echo "Done."
