import sys
import random
import json
import queue

'''
{"conclusion": {"type": "O", "syllogistic": "AOO-2"}, "syllogistic_idx_dic": {"1": {"type": "O", "syllogistic": "AOO-2"}, "2": {"type": "A"}, "3": {"type": "O", "syllogistic": "EIO-1"}, "6": {"type": "E", "syllogistic": "AEE-2"}, "7": {"type": "I"}, "12": {"type": "A", "syllogistic": "AAA-1"}, "13": {"type": "E"}, "24": {"type": "A"}, "25": {"type": "A"}}, "depth": 5, "tree_depth_dic": {"1": [1], "2": [2, 3], "3": [6, 7], "4": [12, 13], "5": [24, 25]}, "leaf_nodes": [2, 7, 13, 24, 25], "level": 5}
'''


def process(tree_file, out_file, all_entity_list):
    q = queue.Queue() 

    with open(tree_file, 'r') as i_f, open(out_file, 'w') as o_f:
        
        for line in i_f:
            entity_q = queue.Queue() 
            for entity in all_entity_list:
                entity_q.put(entity)
            j_d = json.loads(line)
            root_node = j_d["syllogistic_idx_dic"]['1']
            s_entity = entity_q.get()
            p_entity = entity_q.get()
            j_d["syllogistic_idx_dic"]['1']['Subject'] = s_entity
            j_d["syllogistic_idx_dic"]['1']['Predicate'] = p_entity
            q.put('1')

            while not q.empty():
            #while q.qsize() > 0:
                father_idx = q.get()
                # print(father_idx)
                curr_node = j_d["syllogistic_idx_dic"][father_idx]
                if 'syllogistic' not in curr_node:
                    continue
                figure = curr_node['syllogistic'][4]
                father_s = curr_node['Subject']
                father_p = curr_node['Predicate']
                
                left_child_id = str(int(father_idx) * 2)
                right_child_id = str(int(father_idx) * 2 + 1)
                
                left_child_node = j_d["syllogistic_idx_dic"][left_child_id]
                right_child_node = j_d["syllogistic_idx_dic"][right_child_id]
                middle_entity = entity_q.get()
                curr_node['Middle'] = middle_entity

                if figure in ['1', '3']:
                    left_child_node['Subject'] = middle_entity
                    left_child_node['Predicate'] = father_p
                else:
                    left_child_node['Subject'] = father_p 
                    left_child_node['Predicate'] = middle_entity 
                if figure in ['1', '2']:
                    right_child_node['Subject'] = father_s
                    right_child_node['Predicate'] = middle_entity
                else:
                    right_child_node['Subject'] = middle_entity 
                    right_child_node['Predicate'] = father_s 
                q.put(left_child_id)
                q.put(right_child_id)
            o_f.write(json.dumps(j_d, ensure_ascii=False) + '\n')
                

if __name__ == '__main__':
    tree_file = sys.argv[1]
    out_file = sys.argv[2]
    #out_file = './tmp'
    all_entity = '$$A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h i j k l m n o p q r s t u v w x y z$$'.replace(' ', '$$ $$')
    process(tree_file, out_file, all_entity.split(' '))
