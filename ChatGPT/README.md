# Experiments based on ChatGPT.

We performed all experiments on the `gpt-3.5-turbo` model.


# How to Use?

## Environment

```bash
conda create -n codetransocean python=3.9
conda activate codetransocean
pip install openai
```

## Inference

``` inference_scripts.py ``` used to perform various advanced strategies for inference on ChatGPT.

```shell
python inference_scripts.py \
        --key your_openai_api_key \
        --type the name of the strategy \
        --path your_LLMTrans_dataset_path \
```

## Evaluation

``` execute_scripts.py ``` used to execute inference results.

```shell
python execute_scripts.py \
        --ref_path your_LLMTrans_dataset_path \
        --type the name of the strategy \
```

## Experimental results

<div align="center">
  <img src="./images/zero_shot.png">
  <img src="./images/one_shot_cot.png">
  <img src="./images/debug.png">
</div>

For more detailed experimental results, please see our paper.
