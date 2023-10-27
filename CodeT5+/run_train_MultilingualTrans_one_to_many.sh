DATADIR=""

run() {
  for seed in 1234 2345 3456; do
    for source_names in "C" "C++" "C#" "Java" "Go" "PHP" "Python" "VB"; do
      #preprocess data
      NAME=$(date +%Y%m%d%H)_MultilingualTrans_one_to_many_seed${seed}_lr${lr}_maxlen1536_warmup200_${source_names}_to_${target_names}
      OUTPUT_DIR=output/saved_models/MultilingualTrans/one_to_many_${lr}_maxlen1536_seed${seed}/${NAME}
      echo ${NAME}
      mkdir -p ${OUTPUT_DIR}
      mkdir -p ${OUTPUT_DIR}/cache_data

      for name in 'test' 'valid' 'train'; do
        python run_preprocess.py --input_file ${DATADIR}/MultilingualTrans/multilingual_${name}.json \
          --output_file ${OUTPUT_DIR}/cache_data/multilingual_${name}.json \
          --source_names ${source_names} --target_names ${target_names} --sub_task 'MultilingualTrans'
      done

      #   train and predict model
      PORT_ID=$(expr $RANDOM + 1000)

      CUDA_VISIBLE_DEVICES=$GPUID python -m torch.distributed.launch --nproc_per_node 2 --master_port ${PORT_ID} \
        run_translation.py \
        --model_name_or_path ./pretrain/codet5p-220m \
        --do_train \
        --do_eval \
        --do_predict \
        --train_file ${OUTPUT_DIR}/cache_data/multilingual_train.json \
        --validation_file ${OUTPUT_DIR}/cache_data/multilingual_valid.json \
        --test_file ${OUTPUT_DIR}/cache_data/multilingual_test.json \
        --source_prefix "" \
        --output_dir ${OUTPUT_DIR} \
        --text_column source \
        --summary_column target \
        --max_source_length 1536 \
        --max_target_length 1536 \
        --per_device_train_batch_size=2 \
        --gradient_accumulation_steps=4 \
        --per_device_eval_batch_size=24 \
        --learning_rate $lr \
        --num_train_epochs 5 \
        --metric_for_best_model loss \
        --save_total_limit 2 \
        --save_strategy epoch \
        --load_best_model_at_end \
        --evaluation_strategy epoch \
        --overwrite_output_dir \
        --predict_with_generate \
        --logging_strategy epoch \
        --logging_dir ${OUTPUT_DIR} \
        --num_beams 1 \
        --seed $seed \
        --fp16 \
        --warmup_steps 200 \
        --report_to tensorboard 2>&1 | tee ${OUTPUT_DIR}/log_train.txt

      #calculate score
      echo ${source_names}_to_${target_names}
      python run_score.py --input_file ${OUTPUT_DIR}/generated_predictions.json \
        --source_names ${source_names} \
        --target_names ${target_names} \
        --codebleu \
        2>&1 | tee ${OUTPUT_DIR}/score_${source_names}_to_${target_names}.log

      source_name=${source_names}
      for target_name in "C" "C++" "C#" "Java" "Go" "PHP" "Python" "VB"; do
        if [ "$source_name" != "$target_name" ]; then
          echo ${source_name}_to_${target_name}
          python run_score.py --input_file ${OUTPUT_DIR}/generated_predictions.json \
            --source_names ${source_name} \
            --target_names ${target_name} \
            --codebleu \
            2>&1 | tee ${OUTPUT_DIR}/score_${source_name}_to_${target_name}.log
        fi
      done
    done
  done

}

GPUID='0,1'
lr=3e-5
target_names="C,C++,C#,Java,Go,PHP,Python,VB"
run &
