import numpy as np
import random
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--output-path", type=str, required=True)
parser.add_argument("--num-trees", type=int, required=True)
# parser.add_argument("--max-depth", type=int, default=5)
parser.add_argument("--max-sentences", type=int, default=10)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--depth-type", type=str, default="fixed")
args = parser.parse_args()

random.seed(args.seed)
np.random.seed(args.seed)


def read_json(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data

def save_json(data, file_name):
    json_object = json.dumps(data, ensure_ascii = False)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(json_object)

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

def balance_sample(syllogistic_tree):
    """
    对给定的三段论树进行平衡采样
    
    参数:
        syllogistic_tree: 字典,包含三段论树的信息
            - all_nodes_type_dic: 字典,记录所有节点的类型(A/E/I/O)
            - line_nodes_type_dic: 字典,记录链末节点的类型
            - leaf_nodes: 列表,记录叶子节点的编号
    返回:
        chosen_type: 采样得到的节点类型
        chosen_node: 采样得到的节点编号
    """
    all_nodes_type_dic = syllogistic_tree["all_nodes_type_dic"]
    line_nodes_type_dic = syllogistic_tree["line_nodes_type_dic"]
    leaf_nodes = syllogistic_tree["leaf_nodes"]
    count_dic = {x: len(all_nodes_type_dic[x]) for x in all_nodes_type_dic if len(line_nodes_type_dic[x]) > 0}
    inverse_count_dic = {x: 1.0 / count_dic[x] for x in count_dic}
    total_count = sum(inverse_count_dic.values())
    probability_dic = {x: inverse_count_dic[x] / total_count for x in inverse_count_dic}
    chosen_type = random.choices(list(count_dic.keys()), weights=list(probability_dic.values()), k=1)[0]
    chosen_node_idx = random.choice(range(len(line_nodes_type_dic[chosen_type])))
    chosen_node = line_nodes_type_dic[chosen_type].pop(chosen_node_idx)

    leaf_node_idx = leaf_nodes.index(chosen_node)
    leaf_nodes.pop(leaf_node_idx)

    return chosen_type, chosen_node

def expand_syllogistic_tree(syllogistic_tree, link_dic):
    # sampled_node_idx = random.choice(range(len(syllogistic_tree["leaf_nodes"])))
    # sampled_node = syllogistic_tree["leaf_nodes"].pop(sampled_node_idx)
    sampled_type, sampled_node = balance_sample(syllogistic_tree)
    # syllogistic_tree["leaf_nodes"].extend([2 * sampled_node, 2 * sampled_node + 1])
    new_major_premise_idx = 2 * sampled_node
    new_minor_premise_idx = 2 * sampled_node + 1

    sampled_node_depth = int(np.log2(sampled_node)) + 1
    new_node_depth = sampled_node_depth + 1
    if new_node_depth > syllogistic_tree["depth"]:
        syllogistic_tree["depth"] = new_node_depth
    if new_node_depth not in syllogistic_tree["tree_depth_dic"]:
        syllogistic_tree["tree_depth_dic"][new_node_depth] = []
    syllogistic_tree["tree_depth_dic"][new_node_depth].extend([2 * sampled_node, 2 * sampled_node + 1])

    # sampled_node_syllogistic = syllogistic_tree["syllogistic_idx_dic"][sampled_node]["type"]
    new_edge = random.choice(link_dic[sampled_type])
    syllogistic_tree["syllogistic_idx_dic"][sampled_node]["syllogistic"] = new_edge

    syllogistic_tree["syllogistic_idx_dic"][new_major_premise_idx] = {"type": new_edge[0]}
    syllogistic_tree["syllogistic_idx_dic"][new_minor_premise_idx] = {"type": new_edge[1]}
    
    # syllogistic_tree["leaf_nodes_type_dic"][new_edge[0]].append(new_major_premise_idx)
    # syllogistic_tree["leaf_nodes_type_dic"][new_edge[1]].append(new_minor_premise_idx)
    syllogistic_tree["line_nodes_type_dic"] = {
        "A": [],
        "E": [],
        "I": [],
        "O": []
    }
    syllogistic_tree["line_nodes_type_dic"][new_edge[0]].append(new_major_premise_idx)
    syllogistic_tree["line_nodes_type_dic"][new_edge[1]].append(new_minor_premise_idx)

    syllogistic_tree["all_nodes_type_dic"][new_edge[0]].append(new_major_premise_idx)
    syllogistic_tree["all_nodes_type_dic"][new_edge[1]].append(new_minor_premise_idx)

    syllogistic_tree["leaf_nodes"].extend([new_major_premise_idx, new_minor_premise_idx])
    syllogistic_tree["line_nodes"] = [new_major_premise_idx, new_minor_premise_idx]


if __name__ == "__main__":
    link_dic = read_json("../codes/elements/conclusion_dic.json")

    # max_depth = args.max_depth
    max_sentences = args.max_sentences

    all_data = []

    for i in range(args.num_trees):
        conclusion_type = np.random.choice(["A", "E", "I", "O"], size=1, p=[0.25, 0.25, 0.25, 0.25])[0]
        # conclusion_type = np.random.choice(["A", "E", "I", "O"], size=1, p=[0.1, 0.25, 0.25, 0.4])[0]
        conclusion = {
            "type": conclusion_type
        }
        if args.depth_type == "fixed":
            sample_count = max_sentences
        elif args.depth_type == "random":
            sample_count = random.choice(range(1, max_sentences + 1))
        # print("sample_count:", sample_count)

        syllogistic_tree = {
            "conclusion": conclusion,
            "syllogistic_idx_dic": {
                1: conclusion,
            },
            "depth": 1,
            "tree_depth_dic": {
                1: [1]
            },
            "leaf_nodes": [1],
            "line_nodes": [],
            "line_nodes_type_dic": {
                "A": [],
                "E": [],
                "I": [],
                "O": []
            },
            "all_nodes_type_dic": {
                "A": [],
                "E": [],
                "I": [],
                "O": []
            },
            "level": sample_count
        }
        syllogistic_tree["line_nodes_type_dic"][conclusion_type].append(1)
        syllogistic_tree["all_nodes_type_dic"][conclusion_type].append(1)
        for i in range(sample_count):
            # if syllogistic_tree["depth"] >= max_depth:
            #     syllogistic_tree["level"] = i + 1
            #     break
            expand_syllogistic_tree(syllogistic_tree, link_dic)
        all_data.append(syllogistic_tree)

    save_jsonl(all_data, args.output_path)
