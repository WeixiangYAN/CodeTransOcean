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

from evaluator.CodeBLEU import calc_code_bleu
from evaluator.bleu import _bleu, _bleu_json, _bleu_json_select

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", default=None, type=str)
    parser.add_argument('--source_names', type=str, default=None,
                        help="source_names")
    parser.add_argument('--target_names', type=str, default=None,
                        help="target_names")
    parser.add_argument('--codebleu', action='store_true')
    parser.add_argument('--naive', action='store_true')
    args = parser.parse_args()
    dev_accs = []
    hypothesis = []
    pre_references = []
    with open(args.input_file, 'r') as f:
        for line in f:
            json_data = json.loads(line)
            matches = re.search(r"^Translate (\S+) to (\S+): ", json_data['source'])
            source_name = matches.groups()[0]
            target_name = matches.groups()[1]
            source_code = re.sub(r"^Translate (\S+) to (\S+): ", "", json_data['source'])
            if source_name in args.source_names.split(',') and target_name in args.target_names.split(','):
                if args.naive:
                    dev_accs.append(source_code.strip() == json_data['target'].strip())
                    hypothesis.append(source_code.strip())
                else:
                    dev_accs.append(json_data['prediction'].strip() == json_data['target'].strip())
                    hypothesis.append(json_data['prediction'].strip())
                pre_references.append(json_data['target'].strip())

    pre_references = [pre_references]
    bleu = round(_bleu_json_select(args.input_file, args, args.naive), 2)
    if args.codebleu:
        codebleu = calc_code_bleu.get_codebleu_list(pre_references, hypothesis, 'python')
        result = {'em': round(np.mean(dev_accs) * 100, 2), 'bleu': bleu, 'codebleu': round(codebleu * 100, 2)}
    else:
        result = {'em': round(np.mean(dev_accs) * 100, 2), 'bleu': bleu}
    print(result)


if __name__ == "__main__":
    main()
