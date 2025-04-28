import nltk
import random
import string
import sys
from nltk.corpus import words
nltk.download('words')

out_file = sys.argv[1]

def generate_random_string(length):
    characters = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'.split(' ')
    random_string = ''.join(random.choices(characters, k=length))
    return random_string

def is_valid_word(word):
    word_list = words.words()
    return word.lower() in word_list
idx = 0
all_set = set()
all_res_list = []

while idx < 10000:
    random_length = random.randint(4, 8)
    random_str = generate_random_string(random_length)
    if random_str in all_set:
        continue
    all_set.add(random_str)
    if is_valid_word(random_str):
        continue

    all_res_list.append(random_str)
    idx += 1
    print(idx)
    #print(random_str)
with open(out_file, 'w') as f:
    for each in all_res_list:
        f.write(each + '\n')

    

    


