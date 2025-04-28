import sys
import copy
import random
import json
# import queue
import argparse



def load_value_dict(dict_file):
    dict_list = []
    with open(dict_file, 'r') as f:
        for line in f:
            j_d = json.loads(line)
            dict_list.append(j_d)
    return dict_list

# A_pattern = ['All subject are predicate.', 'subject is predicate.', 'None of subject is not predicate.']
# E_pattern = ['All subject are not predicate.', 'subject is not predicate.', 'None of subject is predicate.', 'All predicate are not subject.', 'predicate is not subject.', 'None of predicate is subject.']
# I_pattern = ['There exists a subject that is predicate.', 'There is one subject that is predicate.', 'There exists a predicate that is subject.', 'There is one predicate that is subject.']
# O_pattern = ['There exists a subject that is not predicate.', 'There is one subject that is not predicate.']

A_pattern = ['All subject are predicate.']
E_pattern = ['All subject are not predicate.']
I_pattern = ['There exists one subject that is predicate.']
O_pattern = ['There exists one subject that is not predicate.']

def create_sentence(subject, predicate, c_type, is_reverse=False):
    if is_reverse:
        if c_type == 'A':
            c_type = 'O'
        elif c_type == 'E':
            c_type = 'I'
        elif c_type == 'I':
            c_type = 'E'
        elif c_type == 'O':
            c_type = 'A'

    if c_type == 'A':
        return random.choices(A_pattern, k=1)[0].replace('subject', subject).replace('predicate', predicate)
    if c_type == 'E':
        return random.choices(E_pattern, k=1)[0].replace('subject', subject).replace('predicate', predicate)
    if c_type == 'I':
        return random.choices(I_pattern, k=1)[0].replace('subject', subject).replace('predicate', predicate)
    if c_type == 'O':
        return random.choices(O_pattern, k=1)[0].replace('subject', subject).replace('predicate', predicate)

Prompt_Template = ['Given:\n$PROMPT$']
# Target_Template = ['Prove: "$TARGET$"']
Question_Template = ['Please answer whether "$TARGET$" is True or False.']
#Reverse_Target_Template = ['Prove: $TARGET$ is not correct']

def make_prompt(prompt_list, target, reverse_target, input_dic, save_original_order):
    p_t =  random.choices(Prompt_Template, k=1)[0]
    random.shuffle(prompt_list)
    all_input = p_t.replace('$PROMPT$', '\n'.join(prompt_list))
    r_v = random.random()

    original_input = ""

    if save_original_order: 
        ordered_seq = []
        cur_l = input_dic['start']
        assert len(input_dic['l2s'][cur_l]) == 1
        cur_s = input_dic['l2s'][cur_l][0]
        ordered_seq.append(cur_s)

        while True:
            assert len(input_dic['s2l'][cur_s]) == 2
            assert len(input_dic['l2s'][cur_l]) <= 2
            assert cur_s in input_dic['s2l']
            assert cur_l in input_dic['s2l'][cur_s]
            next_l = input_dic['s2l'][cur_s][1 - input_dic['s2l'][cur_s].index(cur_l)]
            assert cur_s in input_dic['l2s'][next_l]
            if len(input_dic['l2s'][next_l]) == 1:
                break
            next_s = input_dic['l2s'][next_l][1 - input_dic['l2s'][next_l].index(cur_s)]
            ordered_seq.append(next_s)
            cur_s = next_s
            cur_l = next_l

        original_input = p_t.replace('$PROMPT$', '\n'.join(ordered_seq)) 
    # 0 prove
    # 1 correct
    # 2 wrong
    response_type = 0
    # if r_v > 0.7:
    #     t_p = random.choices(Target_Template, k=1)[0]
    #     all_input += '\n' + t_p.replace('$TARGET$', target)
    if r_v > 0.5:
        t_p = random.choices(Question_Template, k=1)[0]
        prompt = all_input + '\n' + t_p.replace('$TARGET$', target)
        original_prompt = original_input + '\n' + t_p.replace('$TARGET$', target)
        response_type = 1
    else:
        t_p = random.choices(Question_Template, k=1)[0]
        prompt = all_input + '\n' + t_p.replace('$TARGET$', reverse_target)
        original_prompt = original_input + '\n' + t_p.replace('$TARGET$', reverse_target)
        response_type = 2
    return prompt, response_type, all_input, original_prompt

def process_replace(line,curr_dict):
    for k, v in curr_dict.items():
        line = line.replace(k, v) 
    return line

def convert_map_dict(map_dict, line, entity_type_dict):
    j_d = json.loads(line)
    leaf_nodes = copy.deepcopy(j_d['leaf_nodes'])
    for leaf_id in leaf_nodes:
         curr_node = j_d["syllogistic_idx_dic"][str(leaf_id)]
         if curr_node['type'] in ['A', 'E']:
            if random.random() > 0.5:
                entity_node = random.choices(entity_type_dict[curr_node['type']], k=1)[0]
                map_dict[curr_node['Subject']] = entity_node['Subject']
                map_dict[curr_node['Predicate']] = entity_node['Predicate']
                break
    return map_dict
                
def load_all_entity_dict(entity_file_path):
    all_type_dict = {}
    with open(entity_file_path, 'r') as f:
        for line in f:
            j_d = json.loads(line)
            curr_type = 'A'
            if ' not ' in j_d['sentence']:
                curr_type = 'E'
            if curr_type not in all_type_dict:
                all_type_dict[curr_type] = []
            curr_node = {}
            curr_node['Subject'] = j_d['subject']
            curr_node['Predicate'] = j_d['predicate']
            all_type_dict[curr_type].append(curr_node)
    return all_type_dict


def process(tree_file, out_file, subject_map_list, task_type, save_original_order):
    if save_original_order:
        original_order_res = []

    with open(tree_file, 'r') as i_f, open(out_file, 'w') as o_f:
        subject_map_idx = -1
        for line in i_f:
            subject_map_idx += 1 
            ori_curr_dict = subject_map_list[subject_map_idx%len(subject_map_list)]
            # if task_type == 'virtual':
            #     curr_dict = copy.deepcopy(ori_curr_dict)
            #     curr_dict = convert_map_dict(curr_dict, line, entity_type_dict)
            # else:
            curr_dict = ori_curr_dict
            line = process_replace(line, curr_dict)
            j_d = json.loads(line)
             
            target_res = ''
            reverse_target_res = ''
            input_list = []
            input_dic = {
                "s2l": {},
                "l2s": {},
                "start": None
            }
            solution_list = []
            for k, v in j_d["syllogistic_idx_dic"].items():
                c_type = v['type']
                if k == '1':    
                    target_res = create_sentence(v['Subject'], v['Predicate'], c_type)
                    input_dic['start'] = random.choice([v['Subject'], v['Predicate']])
                    reverse_target_res = create_sentence(v['Subject'], v['Predicate'], c_type, is_reverse=True)
                else:
                    if 'syllogistic' in v:
                        solution_list.append(create_sentence(v['Subject'], v['Predicate'], c_type))
                        continue
                    new_sentence = create_sentence(v['Subject'], v['Predicate'], c_type)
                    input_list.append(new_sentence)

                    if save_original_order:
                        if v['Subject'] not in input_dic['l2s']:
                            input_dic['l2s'][v['Subject']] = []
                        input_dic['l2s'][v['Subject']].append(new_sentence)
                        if v['Predicate'] not in input_dic['l2s']:
                            input_dic['l2s'][v['Predicate']] = []
                        input_dic['l2s'][v['Predicate']].append(new_sentence)
                        input_dic['s2l'][new_sentence] = [v['Subject'], v['Predicate']]


            j_d['target'] = target_res 
            j_d['reverse_target'] = reverse_target_res
            j_d['input_prompts'] = input_list
            j_d['prompt'], response_type, j_d['conditions'], original_prompt = make_prompt(input_list, target_res, reverse_target_res, input_dic, save_original_order)
            j_d['response_type'] = response_type
            j_d['entity_type'] = task_type
            o_f.write(json.dumps(j_d, ensure_ascii=False) + '\n')

            if save_original_order:
                j_d['prompt'] = original_prompt
                original_order_res.append(j_d)

    if save_original_order:
        with open(out_file.replace('.jsonl', '_original_order.jsonl'), 'w') as o_f:
            for j_d in original_order_res:
                o_f.write(json.dumps(j_d, ensure_ascii=False) + '\n')
                

parser = argparse.ArgumentParser()
parser.add_argument("--map_file", type=str, required=True)
parser.add_argument("--tree_file", type=str, required=True)
parser.add_argument("--task_type", type=str, required=True)
parser.add_argument("--out_file", type=str, required=True)
parser.add_argument("--save_original_order", action='store_true')

args = parser.parse_args()

if __name__ == '__main__':
    map_file = args.map_file
    tree_file = args.tree_file
    task_type = args.task_type
    out_file = args.out_file
    save_original_order = args.save_original_order
    print("save_original_order:", save_original_order)

    subject_map_list = load_value_dict(map_file)
    # entity_type_dict = load_all_entity_dict(entiry_file)  

    process(tree_file, out_file, subject_map_list, task_type, save_original_order)
