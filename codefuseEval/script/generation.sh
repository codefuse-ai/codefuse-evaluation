#!/bin/bash
MODELNAME=$1                 # modle name which in ckpt_config.json
EVALDATASET=$2               # evaluation dataset path information(dataset name which in generation.py)
OUTFILE=$3                   # the path to save the generated results
LANGUAGE=$4                  # evaluated code language

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
MAIN_DIR=$(dirname "$SCRIPT_DIR")

echo $MAIN_DIR

BATCHSIZE=1
DECODEMODE="beams"
SAMPLENUM=1
MAXTOKENS=600
TOPP=0.95
TEMP=0.2

# mbpp_mode parameters, support en and cn
# task_mode parameters：task type -- code_completion, text_to_code
RUN_GENERATION_CMD="python \
    $MAIN_DIR/generation.py \
    --eval_dataset $EVALDATASET\
    --model_name $MODELNAME\
    --decode_mode $DECODEMODE \
    --sample_num $SAMPLENUM\
    --batch_size $BATCHSIZE\
    --language $LANGUAGE\
    --output_file $OUTFILE \
    --temperature $TEMP \
    --task_mode code_completion \
    --mbpp_mode en"

echo "----------generation start!!!------------"
echo $RUN_EVALUATION_CMD
eval $RUN_GENERATION_CMD