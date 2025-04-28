import json

def convert_model_generate_res_to_struct_json(generate_str, start_id = 0):
    print(start_id, len(generate_str))
    if start_id >= len(generate_str):
        return None, ''
    generate_str = generate_str[start_id:]
    print(generate_str)
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

test_str = '''
##Output:
{
"steps": [
{
"condition": ["All Eta are UPSILON", "There is one Eta that is LAMBDA"],
"conclusion": ["There exists a UPSILON that is LAMBDA"],
"format_conclusion": {"Subject": "UPSILON", "Predicate": "LAMBDA", "type": "I"}
},
{
"condition": ["All Omicron are not LAMBDA", "There exists a UPSILON that is LAMBDA"],
"conclusion": ["There exists a UPSILON that is not Omicron"],
"format_conclusion": {"Subject": "UPSILON", "Predicate": "Omicron", "type": "O"}
},
{
"condition": ["All UPSILON are Omicron", "There exists a UPSILON that is not Omicron"],
"conclusion": ["All UPSILON are Omicron is not true"],
"format_conclusion": {"Subject": "UPSILON", "Predicate": "Omicron", "type": "E"}
}
],
"result": "Wrong"
xdwadlkjflaj
'''
try:
    print(convert_model_generate_res_to_struct_json(test_str, start_id = 10))
except Exception as e:
    print(e)
