import openai
import json
import time
import argparse
import os

def save_to_folder(base_dir, type):

    
    type_dir = os.path.join(base_dir, type)
    
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)

    return type_dir

def process_content_keys(key_source):
    if key_source == 'VB':
        key_source = 'Visual Basic'
    return key_source

def handle_debug():
    contents = []
    with open("output/final.json", 'r',encoding = 'utf-8') as f:
        for i in f.readlines():
            content = json.loads(i)
            contents.append(content)
    f.close()

    type_dir = save_to_folder('output', 'debug')



    for j, content in enumerate(contents):
        label = content["label"]
        if label == 1:
            with open(type_dir +f"/output{j}.py", "w", encoding="utf-8") as f:
                f.write(content["Python"])
        else:
            corrected_code = debug_code(content)
            with open(type_dir +f"/output{j}.py", "w", encoding="utf-8") as f:
                f.write(corrected_code)

def debug_code(content):
    python_code = content["Python"]
    key_source = list(content.keys())[4]
    source = content[key_source]
    error = content['output']
    text = f"Translate {key_source} to Python :{source}.\n\nChatGPT:{python_code}.\n\nUser: The above python code compiles with the following errors, please correct them.{error}"
    corrected_code = chatgpt(text)
    return corrected_code

def prepare_prompt(type,file_path):
    if type == 'cot_1':
        file_path = "data/data_intro.json"
        texts = []
        targets = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i in f.readlines():
                content = json.loads(i)
                target = content["output"]
                key_source = list(content.keys())[3]
                source = content[key_source]
                key_source = process_content_keys(list(content.keys())[3])
                key_intro = list(content.keys())[4]
                intro = content[key_intro]
                text = f"Function description:{intro}\nPlease translate into Python code according to the following {key_source} code and its functional description:{source}\nDo not return anything including notes and the like except for one translated Python code."
                print(text)
                texts.append(text)
                targets.append(target)
        return texts, targets
    else:
        examples=[]
        with open("data/examples.json", 'r', encoding='utf-8') as f_new:
            for z in f_new.readlines():
                example = json.loads(z)
                examples.append(example)
        f_new.close()
        texts = []
        targets = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i in f.readlines():
                content = json.loads(i)
                target = content["output"]
                key_source = list(content.keys())[3]
                source = content[key_source]
                key_source = process_content_keys(list(content.keys())[3])
                if(type == "zero_shot_1"):
                    text = f"Translate {key_source} to Python:{source}\nDo not return anything including notes and the like except for one translated Python code."
                elif(type == "zero_shot_2" or type == "0shot_3" or type == "0shot_4" or type == "0shot_5"):
                    text = f"Please provide the Python translation for the following {key_source} code:\n{source}\nDo not return anything including notes and the like except for one translated Python code."
                elif(type == "zero_shot_6"):
                    text = f"Please translate the following {key_source} code into Python code:{source}\nDo not return anything including notes and the like except for one translated Python code."
                elif(type == "zero_shot_7"):
                    text = f"Translating {key_source} to Python ensures that Python code can be compiled:{source}\nDo not return anything including notes and the like except for one translated Python code."
                elif(type == "zero_shot_8"):
                    text = f"Can you rewrite this {key_source} code in Python? {source}"
                elif(type == "one_shot_1"):
                    text = '''Here is an example of a translation from Java to Python.\n"Java": "import java.util.ArrayList;\nimport java.util.Arrays;\nimport java.util.LinkedList;\nimport java.util.List;\nimport java.util.Queue;\n\npublic class WordBreak {\n\n public static void main(String[] args) {\n List<String> dict = Arrays.asList(\"a\", \"aa\", \"b\", \"ab\", \"aab\");\n for ( String testString : Arrays.asList(\"aab\", \"aa b\") ) {\n List<List<String>> matches = wordBreak(testString, dict);\n System.out.printf(\"String = %s, Dictionary = %s. Solutions = %d:%n\", testString, dict, matches.size());\n for ( List<String> match : matches ) {\n System.out.printf(\" Word Break = %s%n\", match);\n }\n System.out.printf(\"%n\");\n }\n dict = Arrays.asList(\"abc\", \"a\", \"ac\", \"b\", \"c\", \"cb\", \"d\");\n for ( String testString : Arrays.asList(\"abcd\", \"abbc\", \"abcbcd\", \"acdbc\", \"abcdd\") ) {\n List<List<String>> matches = wordBreak(testString, dict);\n System.out.printf(\"String = %s, Dictionary = %s. Solutions = %d:%n\", testString, dict, matches.size());\n for ( List<String> match : matches ) {\n System.out.printf(\" Word Break = %s%n\", match);\n }\n System.out.printf(\"%n\");\n }\n }\n \n private static List<List<String>> wordBreak(String s, List<String> dictionary) {\n List<List<String>> matches = new ArrayList<>();\n Queue<Node> queue = new LinkedList<>();\n queue.add(new Node(s));\n while ( ! queue.isEmpty() ) {\n Node node = queue.remove();\n \n if ( node.val.length() == 0 ) {\n matches.add(node.parsed);\n }\n else {\n for ( String word : dictionary ) {\n \n if ( node.val.startsWith(word) ) {\n String valNew = node.val.substring(word.length(), node.val.length());\n List<String> parsedNew = new ArrayList<>();\n parsedNew.addAll(node.parsed);\n parsedNew.add(word);\n queue.add(new Node(valNew, parsedNew));\n }\n }\n }\n }\n return matches;\n }\n \n private static class Node {\n private String val; \n private List<String> parsed; \n public Node(String initial) {\n val = initial;\n parsed = new ArrayList<>();\n }\n public Node(String s, List<String> p) {\n val = s;\n parsed = p;\n }\n }\n\n}\n", "Python": "from itertools import (chain)\n\n\n\ndef stringParse(lexicon):\n \n return lambda s: Node(s)(\n tokenTrees(lexicon)(s)\n )\n\n\n\ndef tokenTrees(wds):\n \n def go(s):\n return [Node(s)([])] if s in wds else (\n concatMap(nxt(s))(wds)\n )\n\n def nxt(s):\n return lambda w: parse(\n w, go(s[len(w):])\n ) if s.startswith(w) else []\n\n def parse(w, xs):\n return [Node(w)(xs)] if xs else xs\n\n return lambda s: go(s)\n\n\n\ndef showParse(tree):\n \n def showTokens(x):\n xs = x['nest']\n return ' ' + x['root'] + (showTokens(xs[0]) if xs else '')\n parses = tree['nest']\n return tree['root'] + ':\\n' + (\n '\\n'.join(\n map(showTokens, parses)\n ) if parses else ' ( Not parseable in terms of these words )'\n )\n\n\n\n\ndef main():\n \n\n lexicon = 'a bc abc cd b'.split()\n testSamples = 'abcd abbc abcbcd acdbc abcdd'.split()\n\n print(unlines(\n map(\n showParse,\n map(\n stringParse(lexicon),\n testSamples\n )\n )\n ))\n\n\n\n\n\ndef Node(v):\n \n return lambda xs: {'type': 'Node', 'root': v, 'nest': xs}\n\n\n\ndef concatMap(f):\n \n return lambda xs: list(\n chain.from_iterable(map(f, xs))\n )\n\n\n\ndef unlines(xs):\n \n return '\\n'.join(xs)\n\n\n\nif __name__ == '__main__':\n main()\n" '''+ f"Please imitate this example to translate following code from {key_source} to Python:{source}\nDo not return anything including notes and the like except for one translated Python code."
                elif(type == "one_shot_2"):
                    for j in range(len(examples)):
                        example = examples[j]
                        example_source = list(example.keys())[1]
                        example_source = process_content_keys(example_source)
                        example_target = list(example.keys())[2]
                        if(example_source==key_source and example_target=="Python"):
                                t = str(example)
                                break
                    text = f'''Here is an example of a translation from {key_source} to Python.
                            '''+ t+f"\nPlease imitate this example to translate following code from {key_source} to Python:{source}Do not return anything including notes and the like except for one translated Python code."
                elif(type == "one_shot_3"):
                    text = '''Here is an example of a translation from Go to C++. "Go": "package main\n\nimport (\n \"errors\"\n \"fmt\"\n \"log\"\n)\n\nvar (\n v1 = []int{1, 3, -5}\n v2 = []int{4, -2, -1}\n)\n\nfunc dot(x, y []int) (r int, err error) {\n if len(x) != len(y) {\n return 0, errors.New(\"incompatible lengths\")\n }\n for i, xi := range x {\n r += xi * y[i]\n }\n return\n}\n\nfunc main() {\n d, err := dot([]int{1, 3, -5}, []int{4, -2, -1})\n if err != nil {\n log.Fatal(err)\n }\n fmt.Println(d)\n}\n", "C++": "#include <iostream>\n#include <numeric>\n\nint main()\n{\n int a[] = { 1, 3, -5 };\n int b[] = { 4, -2, -1 };\n\n std::cout << std::inner_product(a, a + sizeof(a) / sizeof(a[0]), b, 0) << std::endl;\n\n return 0;\n}" 
                        '''+ f"Please imitate this example to translate following code from {key_source} to Python:{source}\nDo not return anything including notes and the like except for one translated Python code."
                elif(type == "cot_2"):
                    text = f"First, understand the function of the following {key_source} code. Then, translate the {key_source} code into Python code while keeping the function unchanged.\n{source}\nDo not return anything including notes and the like except for one translated Python code."
                elif(type == "cot_3"):
                    text = f"First, understand the functionality of the following {key_source} code and predict the compilation output. Then, translate the {key_source} code into Python while maintaining the same functionality, ensuring that the translated code can be successfully compiled.\n{source}\nDo not return anything including notes and the like except for one translated Python code."
                elif(type == "cot_4"):
                    for j in range(len(examples)):
                        example = examples[j]
                        example_source = list(example.keys())[1]
                        example_source = process_content_keys(example_source)
                        example_target = list(example.keys())[2]
                        if(example_source==key_source and example_target=="Python"):
                                t = str(example)
                                break
                    text = f'''
                            First, learn how to translate {key_source} code to Python based on the example, '''+t \
                           +f'''. Then, understand the functionality of the following {key_source} code and predict the compilation output, 
                            {key_source}: {source}. Finally, translate the {key_source} code into Python while maintaining the same functionality, ensuring that the translated code can be successfully compiled.
                            '''+ f"Do not return anything including notes and the like except for one translated Python code."
                print(text)    
                texts.append(text)
                targets.append(target)
        return texts, targets

def chatgpt(text='', type='', i=0):
    messages = []
    # Check if a system role is needed based on the type
    if type in ["zero_shot_3", "zero_shot_4", "zero_shot_5"]:
        key_sources = []
        with open("data/LLM_trans.json", 'r', encoding='utf-8') as f:
            key_sources = [list(json.loads(j).keys())[3] for j in f.readlines()]
        text_system = {
            "zero_shot_3": f"You are a code translation system that specializes in {key_sources[i]} and Python programming languages.",
            "zero_shot_4": "You are a programmer proficient in multiple programming languages.",
            "zero_shot_5": f"You are a programmer proficient in {key_sources[i]} and Python programming languages."
        }.get(type)
        messages.append({"role": "system", "content": text_system})
    messages.append({"role": "user", "content": text})
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0,
                top_p=0,
                messages=messages
            )
            return response['choices'][0]['message']['content']
            
        except Exception as e:
            print("An error occurred: ", str(e))
            time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description='Get py file.')
    parser.add_argument('--key', '-key',help="Key of your chatgpt api.")
    parser.add_argument('--type', '-type',help="Experiment type. Options available:['zero_shot_1', 'zero_shot_2', 'zero_shot_3', 'zero_shot_4', 'zero_shot_5', 'zero_shot_6', 'zero_shot_7', 'zero_shot_8', 'one_shot_1', 'one_shot_2', 'one_shot_3', 'cot_1', 'cot_2', cot_3', 'debug']. Please refer to the explanations of the strategists in the paper.")
    parser.add_argument('--path', '-path',help="path of dataset.")

    args = parser.parse_args()

    openai.api_key = args.key
    if args.type == 'debug':
        handle_debug()
    else:
        texts, targets = prepare_prompt(args.type, args.path)
        restexts = [chatgpt(text, args.type, i) for i, text in enumerate(texts)]

        type_dir = save_to_folder('output', args.type)

        for j, (restext) in enumerate(restexts):
            with open(type_dir + f"/output{j}.py", "w", encoding="utf-8") as f:
                f.write(restext)

if __name__ == '__main__':
    main()