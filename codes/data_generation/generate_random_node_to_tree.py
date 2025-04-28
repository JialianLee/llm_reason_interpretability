import sys
import random
import json
import queue

def generate_on_node(used_node, other_node):
    new_node = {}
    if random.random() > 0.5:
        new_node['Subject'] = used_node
        new_node['Predicate'] = other_node
    else:
        new_node['Subject'] = other_node
        new_node['Predicate'] = used_node

    type_list = ['A', 'E', 'I', 'O']
    random_type = random.choices(type_list, k=1)[0]
    new_node['type'] = random_type
    return new_node
 

def process(tree_file, out_file, all_entity_list):

    with open(tree_file, 'r') as i_f, open(out_file, 'w') as o_f:
        
        for line in i_f:
            j_d = json.loads(line)
            max_id = 0
            all_used_entity_list = set()
            # "type": "O", "syllogistic": "EIO-4", "Subject": "$$A$$", "Predicate": "$$B$$", "Middle": "$$C$$"
            for k, v in j_d["syllogistic_idx_dic"].items():
                curr_id = int(k)
                all_used_entity_list.add(v['Subject']) 
                all_used_entity_list.add(v['Predicate'])


            # "46": {"type": "A", "syllogistic": "AAA-1", "Subject": "$$F$$", "Predicate": "$$K$$", "Middle": "$$L$$"}
            other_entitys = all_entity_list[len(all_used_entity_list):]
            all_used_entity_list = list(all_used_entity_list)
            random.shuffle(all_used_entity_list)
            new_node_list = []
            other_idx = 0
            all_noise_node_list=[]
            for each_used in all_used_entity_list:
                if random.random() > 0.7:
                    new_node = generate_on_node(each_used, other_entitys[other_idx])
                    all_noise_node_list.append(other_entitys[other_idx])
                    other_idx += 1
                    new_node_list.append(new_node)
                    if other_idx >= len(other_entitys):
                        break

            start_idx = 10000 
            for each_new_node in new_node_list:
                j_d["syllogistic_idx_dic"][str(start_idx)] = each_new_node
                start_idx += 1
            j_d['noise_node_count'] = other_idx
            j_d['all_noise_node_list'] = all_noise_node_list
                
            o_f.write(json.dumps(j_d, ensure_ascii=False) + '\n')
                

if __name__ == '__main__':
    tree_file = sys.argv[1]
    out_file = sys.argv[2]
    #out_file = './tmp'
    all_entity = '$$A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h i j k l m n o p q r s t u v$$'.replace(' ', '$$ $$')
    process(tree_file, out_file, all_entity.split(' '))
