import sys
import random
import json
import queue
import copy

def save_jsonl(data, file_name):
    with open(file_name, "w") as file:
        for d in data:
            json_data = json.dumps(d, ensure_ascii=False)
            file.write(json_data + "\n")

def get_terms_dic(tree):
    all_terms = set()
    term_leaf_dic = {}
    leaf_term_dic = {}
    for n in tree["leaf_nodes"]:
        leaf_term_dic[n] = []
        cur_terms = [tree["syllogistic_idx_dic"][str(n)]["Subject"], tree["syllogistic_idx_dic"][str(n)]["Predicate"]]
        for term in cur_terms:
            idx = term.strip("$")
            all_terms.add(idx)
            leaf_term_dic[n].append(idx)
            if idx not in term_leaf_dic:
                term_leaf_dic[idx] = []
            term_leaf_dic[idx].append(n)
    all_terms = list(all_terms)

    return all_terms, term_leaf_dic, leaf_term_dic

def find_the_other_one(two_term_list, one_term):
    assert one_term in two_term_list
    if len(two_term_list) < 2:
        return None
    for term in two_term_list:
        if term != one_term:
            return term

def find_path(two_terms, term_leaf_dic, leaf_term_dic):
    first_term = two_terms[0]
    last_term = two_terms[1]

    first_term_edges = term_leaf_dic[first_term]
    for e in first_term_edges:
        cur_term = find_the_other_one(leaf_term_dic[e], first_term)
        res = {
            "terms": [first_term, cur_term],
            "edges": [e]
        }
        cur_edge = e
        while (cur_term != last_term):
            cur_edge = find_the_other_one(term_leaf_dic[cur_term], cur_edge)
            if cur_edge is None:
                break
            cur_term = find_the_other_one(leaf_term_dic[cur_edge], cur_term)
            res["terms"].append(cur_term)
            res["edges"].append(cur_edge)
        if cur_term == last_term:
            return res
    raise ValueError("Wrong terms:", two_terms)

def deductive_inference(major_premise, minor_premise, subject, middle, predicate):
    syllogistic_dic = {
        "AA1": "A",
        "EA1": "E",
        "AE2": "E",
        "EA2": "E",
        "AE4": "E",
        "AI1": "I",
        "AI3": "I",
        "IA3": "I",
        "IA4": "I",
        "EI1": "O",
        "AO2": "O",
        "EI2": "O",
        "EI3": "O",
        "OA3": "O",
        "EI4": "O"
    }
    major_premise_s = major_premise["Subject"].strip("$")
    major_premise_type = major_premise["type"]
    minor_premise_s = minor_premise["Subject"].strip("$")
    minor_premise_type = minor_premise["type"]

    if major_premise_s == middle:
        if minor_premise_s == middle:
            figure = 3
        else:
            figure = 1
    else:
        if minor_premise_s == middle:
            figure = 4
        else:
            figure = 2

    key = major_premise_type + minor_premise_type + str(figure)
    if key not in syllogistic_dic:
        return None
    else:
        return {
            "type": syllogistic_dic[key],
            "Subject": subject,
            "Predicate": predicate
        }
    
def get_edge_info(two_terms, tree, ra_dic, term_leaf_dic, leaf_term_dic):
    # print("**********************")
    # print("two terms:", two_terms)
    path = find_path(two_terms, term_leaf_dic, leaf_term_dic)
    # print("path:", path)
    for i in range(1, len(path["edges"])):
        term_1 = path["terms"][0]
        term_2 = path["terms"][i+1]
        # print("term 1 2:", term_1, term_2)

        used = False
        if term_1 + term_2 in ra_dic:
            used = True
        elif term_2 + term_1 in ra_dic:
            used = True
        if used:
            continue

        middle = path["terms"][i]
        # print("not used term 1 2:", term_1, term_2)
        # print("ra dic:", ra_dic)
        if term_1 + middle not in ra_dic and middle + term_1 not in ra_dic:
            print("break at:", term_1, middle)
            break
        for key in [term_1 + term_2, term_2 + term_1]:
            subject = key[0]
            predicate = key[1]
            # print("s,m,p:", subject, middle, predicate)
            for major_premise_key in [predicate + middle, middle + predicate]:
                if key in ra_dic:
                    break
                if major_premise_key not in ra_dic:
                    continue
                major_premise = ra_dic[major_premise_key]
                # print("major_premise_key:", major_premise_key)

                for minor_premis_key in [subject + middle, middle + subject]:
                    if key in ra_dic:
                        break
                    if minor_premis_key not in ra_dic:
                        continue
                    minor_premise = ra_dic[minor_premis_key]
                    # print("minor_premis_key", minor_premis_key)

                    result = deductive_inference(major_premise, minor_premise, subject, middle, predicate)
                    # print("result:", result)
                    if result is not None:
                        result["middle_decay"] = path["terms"][1:i+1]
                        ra_dic[key] = result                 
    return

def get_edges(tree):
    all_terms, term_leaf_dic, leaf_term_dic = get_terms_dic(tree)

    ra_dic = {}
    for n in tree["leaf_nodes"]:
        leaf = tree["syllogistic_idx_dic"][str(n)]
        key = leaf["Subject"].strip("$") + leaf["Predicate"].strip("$")
        ra_dic[key] = {
            "type": leaf["type"],
            "Subject": leaf["Subject"].strip("$"),
            "Predicate": leaf["Predicate"].strip("$"),
            "middle_decay": []
        }
    for i in range(len(all_terms)):
        for j in range(i+1,(len(all_terms))):
            two_terms = [all_terms[i], all_terms[j]]
            if two_terms[0] + two_terms[1] in ra_dic or two_terms[1] + two_terms[0] in ra_dic:
                continue
            get_edge_info(two_terms, tree, ra_dic, term_leaf_dic, leaf_term_dic)
    reference_answer = {}
    for k, v in ra_dic.items():
        new_key = "$$" + k[0] + "$$,$$" + k[1] + "$$"
        new_middle_decay = []
        for c in v["middle_decay"]:
            new_middle_decay.append("$$" + c + "$$")
        reference_answer[new_key] = {
            "type": v["type"],
            "middle_decay": new_middle_decay
        }
    tree["reference_answer"] = reference_answer

    return

def process(in_file):
    res = []
    with open(in_file, 'r') as i_f:
        for line in i_f:
            j_d = json.loads(line)
            get_edges(j_d)
            res.append(j_d)
    return res

if __name__ == '__main__':
    tree_file = sys.argv[1]
    res = process(tree_file)
    save_jsonl(res, sys.argv[2])
