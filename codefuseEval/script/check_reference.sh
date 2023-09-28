#!/bin/bash

OUTFILE=$1
PROBLEMFILE=$2

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
MAIN_DIR=$(dirname "$SCRIPT_DIR")

echo $MAIN_DIR
 #OUTPUTFILE：file information produced by the model
 #METRIC：pass@k evaluation metrics, pass@k is default
 #PROBLEMFILE：path of evaluation dataset
RUN_EVALUATION_CMD="python
    $MAIN_DIR/evaluation.py \
    --input_file $OUTFILE\
    --metric pass@k  \
    --problem_file $PROBLEMFILE \
    --test_groundtruth False"

echo "----------evaluation start!!!------------"
echo $RUN_EVALUATION_CMD
eval $RUN_EVALUATION_CMD