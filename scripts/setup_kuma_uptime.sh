#!/bin/bash

# Script to automatically set up Uptime Kuma using podman-compose

mkdir uptime-kuma
cd uptime-kuma
curl -o compose.yaml https://raw.githubusercontent.com/louislam/uptime-kuma/master/compose.yaml
podman-compose up -d