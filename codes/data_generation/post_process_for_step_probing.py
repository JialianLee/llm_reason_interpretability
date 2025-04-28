import json
import glob
import os
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("--input-path", type=str, required=True)
parser.add_argument("--output-path", type=str, required=True)
parser.add_argument("--select-reason-step", action="store_true", default=False)
args = parser.parse_args()


def read_jsonl(file_name):
    json_data = []
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            e_d = json.loads(line)
            json_data.append(e_d)
    return json_data

def save_jsonl(data, file_name):
    with open(file_name, "w") as file:
        for d in data:
            json_data = json.dumps(d, ensure_ascii=False)
            file.write(json_data + "\n")

if __name__ == "__main__":
    files = glob.glob(args.input_path + "*.jsonl")
    output_path = args.output_path
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    labels = {
        "A": 0,
        "E": 1,
        "I": 2,
        "O": 3,
        "U": 4
    }
    for f in files:
        name = f.split("/")[-1]
        data = read_jsonl(f)

        new_data = []
        for d in data:
            cur_dic = {}
            prompt = d["conditions"]
            for s_p, info in d["reference_answer"].items():
                sps = s_p.split(",")
                assert len(sps) == 2
                sub = sps[0]
                pre = sps[1]
                l_type = info["type"]
                steps = len(info["middle_decay"])
                nd = {
                    "prompt": prompt,
                    "response": "<|START|>" + sub + "<|MID|>" + pre + "<|END|>",
                    "type": l_type,
                    "label": labels[l_type],
                    "reason_steps": steps
                }
                if steps not in cur_dic:
                    cur_dic[steps] = []
                cur_dic[steps].append(nd)
            for nds in cur_dic.values():
                if args.select_reason_step:
                    new_data.append(random.choice(nds))
                else:
                    new_data.extend(nds)

        save_jsonl(new_data, os.path.join(output_path, "process_" + name))