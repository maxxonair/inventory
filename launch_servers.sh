#!/bin/bash

uv run -m backend.InventoryServer &
uv run -m backend.CameraServer &