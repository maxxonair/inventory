!/bin/bash

PRJCT_DIR=$PWD

cd ${PRJCT_DIR}/backend/src

uv run -m printer.PrinterServer