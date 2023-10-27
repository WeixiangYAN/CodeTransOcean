import json
import time
import re
import subprocess
import argparse
import os

def save_to_folder(base_dir, type):
    type_dir = os.path.join(base_dir, type)
    
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)

    return type_dir

def run_python_script(script_path):
    if not script_path:
        return "Please provide a valid Python script path."
    command = f"python {script_path}"
    k = 0
    try:
        start_time = time.time()
        process = subprocess.Popen(command, shell=True)
        while True:
            if process.poll() is not None:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                break
            elif time.time() - start_time > 20:  
                k = 1
                process.terminate()
                output = "timeout"
                break
            time.sleep(0.1)  
    except subprocess.CalledProcessError as e:
        k = 1
        output = str(e.output)
    return output, k

def deal_code(code):
    code = re.sub(r'\n', ' ', code)
    code = re.sub(r'\s+', ' ', code)
    code = re.sub(r'^[\s\n]+|[\s\n]+$', '', code)
    return code

def save_result_to_json(data, file_path):
    with open(file_path, "a",encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
        file.write('\n')

def process_scripts_and_save(ref_path,type):
    contents = []
    with open(ref_path, 'r', encoding='utf-8') as f:
        for i in f.readlines():
            content = json.loads(i)
            contents.append(content)

    for j, content in enumerate(contents):
        key_source = list(content.keys())[3]
        source = content[key_source]
        target = deal_code(content["output"])
        output, k = run_python_script('output/'+type + f"/output{j}.py")
        output = deal_code(output)

        with open('output/'+type + f"/output{j}.py", "r", encoding="utf-8") as f:
            python_code = f.read()

        if output == target:
            dic = {'id': j, "label": 1, "output": output, "Python": python_code, key_source: source}
        elif k == 0 and output != target:
            dic = {'id': j, "label": 0, "output": "The code compiles but the output is incorrect.", "Python": python_code, key_source: source}
        else:
            if len(output) > 2000:
                output = output[:2000]
            dic = {'id': j, "label": 0, "output": output, "Python": python_code, key_source: source}

        type_dir = save_to_folder("executed_output", type)

        save_result_to_json(dic, os.path.join(type_dir, f"executed_result.json"))

def calculate_accuracy(type):
    contents = []
    dsr = 0
    type_dir = save_to_folder("executed_output", type)
    with open(os.path.join(type_dir, f"executed_result.json"), 'r', encoding='utf-8') as f:
        for i in f.readlines():
            content = json.loads(i)
            contents.append(content)
            if content['label'] == 1:
                dsr += 1

    return dsr / len(contents)

def main():
    parser = argparse.ArgumentParser(description='Get py file.')
    parser.add_argument('--type', '-type', help="Experiment type.")
    parser.add_argument('--ref_path', '-ref_path', help="The ground truth of the execution results.")
    args = parser.parse_args()

    process_scripts_and_save(args.ref_path, args.type)
    dsr = calculate_accuracy(args.type)
    print("DSR:", dsr)

if __name__ == '__main__':
    main()
