import sys
import json
import random
import numpy as np


def visual_refer(all_entity_list, all_visual_words_set):
    final_res = {} 
    # curr_visual_words = random.choices(all_visual_words_set, k=len(all_entity_list))
    curr_visual_words = list(np.random.choice(all_visual_words_set, size=len(all_entity_list), replace=False))
    for k, v in zip(all_entity_list, curr_visual_words):
        final_res[k] = v
    return final_res
        

def random_refer(all_entity_list):
    # all_target_list = 'Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota Kappa Lambda Mu Nu Xi Omicron Pi Rho Sigma Tau Upsilon Phi Chi Psi Omega ALPHA BETA GAMMA DELTA EPSILON ZETA ETA THETA IOTA KAPPA LAMBDA MU NU XI OMICRON PI RHO SIGMA TAU UPSILON PHI CHI PSI OMEGA'.split(' ')
    all_target_list = 'Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota Kappa Lambda Mu Nu Xi Omicron Pi Rho Sigma Tau Upsilon Phi Chi Psi Omega'.split(' ')
    random.shuffle(all_target_list)
    used_entity_list = all_entity_list[:len(all_target_list)]
    res_dict = {}
    for from_value, target_value in zip(used_entity_list, all_target_list):
        res_dict[from_value] = target_value
    return res_dict

def load_all_visual_words(all_visual_words_file):
    res_set = []
    with open(all_visual_words_file, 'r') as f:
        for line in f:
            res_set.append(line.strip())
    return res_set
            
    

def process(name_type, out_file, generate_count, all_entity, all_visual_words):
    all_visual_words_set = load_all_visual_words(all_visual_words)
    all_entity_list = all_entity.split(' ')
    with open(out_file, 'w') as o_f:
        for i in range(generate_count):
            res_dict = {}
            if name_type == 'random_refer':
                res_dict = random_refer(all_entity_list)
            elif name_type == 'virtual_refer':
                res_dict = visual_refer(all_entity_list, all_visual_words_set)
            o_f.write(json.dumps(res_dict, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    all_entity = '$$A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h i j k l m n o p q r s t u v w x y z$$'.replace(' ', '$$ $$')
    name_type = sys.argv[1]
    generate_count = int(sys.argv[2])
    all_visual_words = sys.argv[3] 
    out_file = sys.argv[4] 
    print('name_type:', name_type)
    print('generate_count:', generate_count)
    print('all_visual_words:', all_visual_words)
    print('out_file:', out_file)
    process(name_type, out_file, generate_count, all_entity, all_visual_words)
