import sys
import json
import numpy as np
import pandas as pd

def convert_model_generate_res_to_struct_json(generate_str, start_id = 0):
    if start_id >= len(generate_str):
        return None, ''
    generate_str = generate_str[start_id:]
    start = generate_str.find('{')
    stack = ['{']
    for i in range(start + 1, len(generate_str)):
        if generate_str[i] == '{':
            stack.append('{')
        elif generate_str[i] == '}':
            stack.pop()
            if not stack:
                end = i + 1
                break

    json_str = generate_str[start:end]
    data = json.loads(json_str)
    return data, json_str

def get_json_result(in_str):
    model_json_res = None
    try_count = 0
    start_idx = 0
    while try_count < 5:
        try:
            model_json_res, json_str = convert_model_generate_res_to_struct_json(in_str, start_idx)
            print('-----model_json_res:', model_json_res, try_count)
            start_idx += len(json_str)
            break
        except Exception as e:
            pass
        try_count += 1
        if try_count > 5:
            break
    return model_json_res

def medical_examination_rule_rm(j_d):
    response = j_d['gen'].lower()
    if '<|output_start|>' in response and '<|output_end|>' in response:
        model_json_res = get_json_result(response.split('<|output_start|>')[1].split('<|output_end|>')[0])
    else:
        model_json_res = get_json_result(response)

    right_count = 0.0
    solution = j_d['solution']
    all_is_right = 0.0
    accuracy = 0.0
    recall = 0.0
    if model_json_res is not None and 'result' in model_json_res:
        for i in range(len(solution)):
            for each_ans in model_json_res['result']:
                if solution[i].lower() in each_ans:
                    right_count += 1.0
                    break

        accuracy = float(right_count/float(len(model_json_res['result'])))
        recall = float(right_count/float(len(j_d['solution'])))
        if accuracy == 1 and recall == 1:
            all_is_right = 1.0

    return accuracy, recall, all_is_right
   

def zebra_rule_rm(j_d):
    response = j_d['gen']
    if '<|output_start|>' in response and '<|output_end|>' in response:
        model_json_res = get_json_result(response.split('<|output_start|>')[1].split('<|output_end|>')[0])
    else:
        model_json_res = get_json_result(response)
    result_score = 0.0
    all_is_right = 0.0
    solution = j_d['solution']
    
    for i in range(len(solution)):
        if model_json_res is not None and "Q" + str(i+1) in model_json_res and model_json_res["Q" + str(i+1)] == solution[i]:
            result_score += 1
    if result_score == len(solution):
        all_is_right = 1.0
    return result_score, all_is_right
    
def cypher_rule_rm(j_d):
    response = j_d['gen']
    score = 0.0
    all_right_score = 0.0
    solution = j_d['solution'].lower()
    ori_solution = solution
    solution_len = len(solution)
    if '<|output_start|>' in response and '<|output_end|>' in response:
        answer = response.split('<|output_start|>')[1].split('<|output_end|>')[0]
    else:
        answer = response
    answer = answer.lower()

    if solution in answer:
        all_right_score = 1.0
    print('-----solution:', solution)
    print('-----answer:', answer)

    while True:
        if solution in answer:
            score = len(solution) * 1.0 / solution_len
            break
        else:
            solution = solution[:-1]
    
    non_empty_score = 0.0
    solution = ori_solution.replace(' ', '')
    answer = answer.replace(' ', '')
    solution_len = len(solution)
    while True:
        if solution in answer:
            non_empty_score = len(solution) * 1.0 / solution_len
            break
        else:
            solution = solution[:-1]

    # if j_d['solution'] in response.split('<|output_start|>')[1].split('<|output_end|>')[0]:
    #     score = 1.0
    score = max(0.8*non_empty_score, score)
    return score, all_right_score

def get_rule_score(input_list, task_name):
    res_list = []
    for j_d in input_list:
        if task_name == 'zebra':
            result_score, is_right = zebra_rule_rm(j_d)
            j_d['result_score'] = result_score
            j_d['is_right'] = is_right
        elif task_name == 'cypher':
            result_score, is_right = cypher_rule_rm(j_d)
            j_d['result_score'] = result_score
            j_d['is_right'] = is_right
        elif task_name == 'medical_examination':
            acc_score, recall_score, is_right = medical_examination_rule_rm(j_d)
            j_d['acc_score'] = acc_score
            j_d['recall_score'] = recall_score 
            j_d['is_right'] = is_right
        res_list.append(j_d)
    return res_list

def process(in_file, task_name, res_file, report_file, excel_report_file):
    res = []
    with open(in_file, 'r') as i_f:
        for line in i_f:
            res.append(json.loads(line))
    res_list = get_rule_score(res, task_name)
    with open(res_file, 'w') as w_f:
        for each_res in res_list:
            w_f.write(json.dumps(each_res, ensure_ascii=False) + '\n')
    summary_all_score(res_list, report_file, excel_report_file)

def merge_to_excel_dict(target_dict, key_list, value_list=None, none_str=''):

    if value_list is None:
        value_list = ['' for i in range(len(key_list))]
        value_list[0] = none_str
    for key_s, value_s in zip(key_list, value_list):
        if key_s not in target_dict:
            target_dict[key_s] = []
        try:
            value_s = float(value_s)
        except Exception as e:
            print(e)
        target_dict[key_s].append(value_s)
    return target_dict

'''tags": {"plaintexts": ["i grant thou wert not married to my muse", "of mo    uthed graves will give thee memory"], "cyphertexts": ["o ukqfz zigx vtkz fgz dqkkotr zg dn dxlt", "gy dgxzitr ukqctl voss uoct zitt dtdgkn"], "cypher_method_tags": {"name": "QWE"}}'''

def summary_all_score(j_d_list, report_file, excel_report_file):
    acc_score_res_dict = {}
    recall_score_res_dict = {}

    all_right_level_res_dict = {}
    to_excel_dict = {}
    all_right_res_list = []
    for j_d in j_d_list:
        #level = j_d['tags']['level']
        #"tags": {"attribute_count": "3", "house_count": "2"
        #level = j_d['tags']['cypher_method_tags']['name']
        #level = int(j_d['tags']['house_count'])
        #level = '__'.join([j_d['tags']['house_count'], j_d['tags']['attribute_count']])
        level = '0'
        acc_score = j_d['acc_score']
        recall_score = j_d['recall_score']
        all_right_score = j_d['is_right']

        if level not in acc_score_res_dict:
            acc_score_res_dict[level] = []

        if level not in recall_score_res_dict:
            recall_score_res_dict[level] = []

        if level not in all_right_level_res_dict:
            all_right_level_res_dict[level] = []

        acc_score_res_dict[level].append(float(acc_score))
        recall_score_res_dict[level].append(float(recall_score))
        all_right_level_res_dict[level].append(float(all_right_score))
        all_right_res_list.append(float(all_right_score))

    excel_head_list = ['KEY', 'Count', 'acc_score', 'recall_score', 'all_right_score']  
    with open(report_file, 'w') as w_f:
        w_f.write('\t'.join(excel_head_list) + '\n')

        for k, v in sorted(acc_score_res_dict.items(), key=lambda item: item[0]):

            acc_score = np.mean(acc_score_res_dict[k])
            recall_score = np.mean(recall_score_res_dict[k])
            all_right_score = np.mean(all_right_level_res_dict[k])

            res_list = [str(k), str(len(acc_score_res_dict[k])), str(acc_score), str(recall_score), str(all_right_score)]
            w_f.write('\t'.join(res_list) + '\n')
            to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=res_list, none_str='')

    df = pd.DataFrame(to_excel_dict)
    df.to_excel(excel_report_file, index=False)

           
#{\n  \"Q1\": \"2\",\n  \"Q    2\": \"Unknown\"\n}<|output_end|><|im_end|> ", "model_id": "", "solution": ["2", "2"],

if __name__ == '__main__':
    #in_file, task_name, report_file, excel_report_file
    in_file = sys.argv[1]
    task_name = sys.argv[2]
    res_file = sys.argv[3]
    report_file = sys.argv[4]
    excel_report_file = sys.argv[5]
    process(in_file, task_name, res_file, report_file, excel_report_file)
    #process('/cpfs/29f69eb5e2e60f26/user/rlhf/liufeng/Aristotelian_logic_data/eval_res/passion_32B_sft_v2/zebra_puzzles_res.jsonl', 'zebra')

