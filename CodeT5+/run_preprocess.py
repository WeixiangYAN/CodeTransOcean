# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

"""

import logging
import argparse
import numpy as np
import json
import re

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", default=None, type=str)
    parser.add_argument("--output_file", default=None, type=str)
    parser.add_argument('--source_names', type=str, default=None,
                        help="source_names")
    parser.add_argument('--target_names', type=str, default=None,
                        help="target_names")
    parser.add_argument('--sub_task', type=str, default=None,
                        help="sub_task")
    args = parser.parse_args()

    with open(args.input_file, 'r') as fi:
        with open(args.output_file, 'w') as fw:
            for line in fi:
                json_data = json.loads(line)
                cur_keys = list(json_data.keys())
                if args.sub_task in ['MultilingualTrans', 'RareTrans']:
                    source_lang = cur_keys[2]
                    target_lang = cur_keys[3]
                elif args.sub_task in ['LLMTrans']:
                    source_lang = cur_keys[3]
                    target_lang = cur_keys[2]
                else:
                    source_lang = cur_keys[1]
                    target_lang = cur_keys[2]
                if source_lang in args.source_names.split(',') and target_lang in args.target_names.split(','):
                    source = 'Translate ' + source_lang + ' to ' + target_lang + ': ' + json_data[source_lang]
                    target = json_data[target_lang]
                    del json_data[source_lang]
                    del json_data[target_lang]
                    json_data['source'] = source
                    json_data['target'] = target
                    json_string = json.dumps(json_data)
                    fw.write(json_string + '\n')

if __name__ == "__main__":
    main()
