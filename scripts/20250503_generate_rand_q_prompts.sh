DATA_PATH="../outputs/prompts"
NAME="20250503_generate_rand_q_prompts"
OUTPUT_PATH="${DATA_PATH}/${NAME}"

mkdir -p $OUTPUT_PATH
all_count=2000
max_sentences=15

# # # generate A E I O trees
# python ../codes/data_generation/generate_sentence_line.py --output-path "${OUTPUT_PATH}/structure_trees.jsonl" --num-trees $all_count --max-sentences ${max_sentences} --seed 20250503
# python ../codes/data_generation/generate_subject_predicate_middle_from_trees.py "${OUTPUT_PATH}/structure_trees.jsonl" "${OUTPUT_PATH}/structure_s_p_m_trees_clean.jsonl"


# # # # genrate random noise node to trees
# # # python ../codes/data_generation/generate_random_node_to_tree.py "${OUTPUT_PATH}/structure_s_p_m_trees_clean.jsonl" "${OUTPUT_PATH}/structure_s_p_m_trees_noise.jsonl"

# # generate solution 
# python ../codes/data_generation/calculate_all_edges.py "${OUTPUT_PATH}/structure_s_p_m_trees_clean.jsonl" "${OUTPUT_PATH}/structure_s_p_m_trees.jsonl" 

# # generate random map of xilazifu
# python3 ../codes/data_generation/generate_virtual_map.py random_refer $all_count ../codes/common/all_virtual_words ${OUTPUT_PATH}/random_entiry_name_map.jsonl
# python3 ../codes/data_generation/generate_query_from_subject_predicate_middle_trees.py --map_file "${OUTPUT_PATH}/random_entiry_name_map.jsonl" --tree_file "${OUTPUT_PATH}/structure_s_p_m_trees.jsonl" --task_type "random" --out_file "${OUTPUT_PATH}/random_name_logic_prompts_d_${max_sentences}.jsonl" --save_original_order

# # generate random map of virtual
# python3 ../codes/data_generation/generate_virtual_map.py virtual_refer $all_count ../codes/common/all_virtual_words ${OUTPUT_PATH}/virtual_entiry_name_map.jsonl
# python3 ../codes/data_generation/generate_query_from_subject_predicate_middle_trees.py --map_file "${OUTPUT_PATH}/virtual_entiry_name_map.jsonl" --tree_file "${OUTPUT_PATH}/structure_s_p_m_trees.jsonl" --task_type "virtual" --out_file "${OUTPUT_PATH}/virtual_name_logic_prompts_d_${max_sentences}.jsonl" --save_original_order

# # generate data for v probing
python3 ../codes/data_generation/post_process_for_step_probing.py --input-path "${OUTPUT_PATH}/" --output-path "${OUTPUT_PATH}/final_res/" --select-reason-step
