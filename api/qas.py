import difflib
import json
import os
from typing import Tuple


def read_data():
    data_path = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def bigram_dice_coefficient(a, b):
    '''
        input:
            a: list of words
            b: list of words
        output:
            dice coefficient of a and b
    '''
    # print(a)
    # print(b)
    a_bigram = set(zip(a, a[1:]))
    b_bigram = set(zip(b, b[1:]))
    # print(a_bigram)
    # print(b_bigram)
    return 2 * len(a_bigram & b_bigram) / (len(a_bigram) + len(b_bigram))


def get_answer(question, model) -> Tuple[str, str, str]:
    '''
    Return:
        question: Question to be displayed on website
        taibun:   Answer to be displayed on website
        tailo:    sequence for TTS api
    '''
    score_list = []
    data = read_data()
    for key, value in data['data'].items():
        # if difflib.SequenceMatcher(None, key, question).quick_ratio() > 0.7:
        #     return key, value[1], value[0]
        score = bigram_dice_coefficient(list(key), list(question))
        score_list.append((score, key, value[1], value[0]))
    
    for item in score_list:
        print(item)

    # find the best match
    score_list.sort(reverse=True)
    # return score > 0.3
    if score_list[0][0] > 0.3:
        return score_list[0][1], score_list[0][2], score_list[0][3]
    else:
        return question, data['<UNK>'][1], data['<UNK>'][0]

    
