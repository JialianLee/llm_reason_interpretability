import sys
import copy
import random
import json
import queue




def load_value_dict(dict_file):
    dict_list = []
    with open(dict_file, 'r') as f:
        for line in f:
            j_d = json.loads(line)
            dict_list.append(j_d)
    return dict_list

A_pattern = ['All subject are predicate.', 'subject is predicate.', 'None of subject is not predicate.']
E_pattern = ['All subject are not predicate.', 'subject is not predicate.', 'None of subject is predicate.', 'All predicate are not subject.', 'predicate is not subject.', 'None of predicate is subject.']
I_pattern = ['There exists a subject that is predicate.', 'There is one subject that is predicate.', 'There exists a predicate that is subject.', 'There is one predicate that is subject.']
O_pattern = ['There exists a subject that is not predicate.', 'There is one subject that is not predicate.']

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

Prompt_Template = ['Given a problem statement as contexts, the task is to answer a logical reasoning question. \nContext:\n$PROMPT$\n\n']
Multi_Choice_Template = ['Question:Based on the above information, is the following statement true, or false? $TARGET$\n\nOptions:\n[\'A) True\', \'B) False\']\n']
# Target_Template = ['Prove: "$TARGET$"']
# Question_Template = ['Show "$TARGET$" is correct or not.']
#Reverse_Target_Template = ['Prove: $TARGET$ is not correct']

def make_prompt(prompt_list, target, reverse_target):
    random.shuffle(prompt_list)
    p_t =  random.choices(Prompt_Template, k=1)[0]
    all_input = p_t.replace('$PROMPT$', '\n'.join(prompt_list))
    r_v = random.random()
    # 0 prove
    # 1 correct
    # 2 wrong
    response_type = 0
    if r_v > 0.5:
        t_p = random.choices(Multi_Choice_Template, k=1)[0]
        all_input += t_p.replace('$TARGET$', target)
        response_type = 1
    else:
        t_p = random.choices(Multi_Choice_Template, k=1)[0]
        all_input += t_p.replace('$TARGET$', reverse_target)
        response_type = 2

    return all_input, response_type

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


def process(tree_file, out_file, subject_map_list, entity_type_dict, task_type):

    with open(tree_file, 'r') as i_f, open(out_file, 'w') as o_f:
        subject_map_idx = -1
        for line in i_f:
            subject_map_idx += 1 
            ori_curr_dict = subject_map_list[subject_map_idx%len(subject_map_list)]
            if task_type == 'virtual':
                curr_dict = copy.deepcopy(ori_curr_dict)
                curr_dict = convert_map_dict(curr_dict, line, entity_type_dict)
            else:
                curr_dict = ori_curr_dict
            line = process_replace(line, curr_dict)
            j_d = json.loads(line)
             
            target_res = ''
            reverse_target_res = ''
            input_list = []
            solution_list = []
            for k, v in j_d["syllogistic_idx_dic"].items():
                c_type = v['type']
                if k == '1':    
                    target_res = create_sentence(v['Subject'], v['Predicate'], c_type)
                    reverse_target_res = create_sentence(v['Subject'], v['Predicate'], c_type, is_reverse=True)
                else:
                    if 'syllogistic' in v:
                        solution_list.append(create_sentence(v['Subject'], v['Predicate'], c_type))
                        continue
                    input_list.append(create_sentence(v['Subject'], v['Predicate'], c_type))


            j_d['target'] = target_res 
            j_d['reverse_target'] = reverse_target_res
            j_d['input_prompts'] = input_list
            j_d['prompt'], response_type = make_prompt(input_list, target_res, reverse_target_res)
            j_d['response_type'] = response_type
            if response_type == 1:
                j_d["solution"] = "A"
            else:
                j_d["solution"] = "B"
            j_d['entity_type'] = task_type
            o_f.write(json.dumps(j_d, ensure_ascii=False) + '\n')
                

if __name__ == '__main__':
    map_file = sys.argv[1]
    entiry_file = sys.argv[2]
    tree_file = sys.argv[3]
    task_type = sys.argv[4]
    out_file = sys.argv[5]
    subject_map_list = load_value_dict(map_file)
    entity_type_dict = load_all_entity_dict(entiry_file)  

    process(tree_file, out_file, subject_map_list, entity_type_dict, task_type)
