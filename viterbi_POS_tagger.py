# coding=utf-8
import nltk
import numpy as np
import pandas as pd
from collections import defaultdict
import operator
import re

pos_dict = defaultdict(dict)
word_dict = defaultdict(dict)
with open("WSJ_24.pos", "r", encoding='utf-8-sig') as f:
    string = f.read()
with open("WSJ_23.words", "r", encoding='utf-8-sig') as f:
    string1 = f.read()

list = string.split("\n")
test_list = string1.split("\n")

num_sentence = len(string.split(".\t."))
pos_list = []
for i in list:
    try:
        if i.split("\t")[1] not in pos_list and i.split("\t")[1][0].isalpha():
            pos_list.append(i.split("\t")[1])

        if i.split("\t")[0] not in pos_dict[i.split("\t")[1]]:
            pos_dict[i.split("\t")[1]].update({i.split("\t")[0]: 1})
        pos_dict[i.split("\t")[1]][i.split("\t")[0]] += 1
        if i.split("\t")[1] not in word_dict[i.split("\t")[0]]:
            word_dict[i.split("\t")[0]].update({i.split("\t")[1]: 1})
        word_dict[i.split("\t")[0]][i.split("\t")[1]] += 1
    except IndexError:
        pass

for i in pos_dict.keys():
    total = sum(pos_dict[i].values())
    for j in pos_dict[i].keys():
        pos_dict[i][j] = pos_dict[i][j] / total

begin_sentence = []
end_sentence = []

for i in range(len(list)):
    if list[i] == ".\t.":
        end_sentence.append(list[i - 1])
        if list[i + 2] != "``\t``":
            begin_sentence.append(list[i + 2])
        else:
            begin_sentence.append(list[i + 3])

Transition = defaultdict(dict)
for word in begin_sentence:
    try:
        if word.split("\t")[1].isalpha():
            if word.split("\t")[1] not in Transition['Begin_Sent']:
                Transition['Begin_Sent'].update({word.split("\t")[1]: 1})
            Transition['Begin_Sent'][word.split("\t")[1]] += 1
    except IndexError:
        pass

for word in end_sentence:
    try:
        if word.split("\t")[1].isalpha():
            if word.split("\t")[1] not in Transition['End_Sent'] and word.split("\t")[1].isalpha():
                Transition['End_Sent'].update({word.split("\t")[1]: 1})
            Transition['End_Sent'][word.split("\t")[1]] += 1
    except IndexError:
        pass

for i in range(len(list)):
    try:
        pos = list[i].split("\t")[1]
        if list[i] != ".\t." and i < len(list) - 1:
            next_pos = list[i + 1].split("\t")[1]
            if next_pos.isalpha():
                if next_pos not in Transition[pos]:
                    Transition[pos].update({next_pos: 1})
                Transition[pos][next_pos] += 1
    except IndexError:
        pass

for i in Transition.keys():
    total = sum(Transition[i].values())
    for j in Transition[i].keys():
        Transition[i][j] = Transition[i][j] / total

sentence_list = string1.replace("\n", " ")
test_list = sentence_list.split(". ")
final_list = sentence_list.split(" ")
test = []
for i in test_list:
    test.append(i.split(" "))

q = defaultdict(dict)

result = []
for i in range(len(test)):  # how many sentence
    list1 = [[0 for x in range(len(test[i]))] for y in range(len(pos_list))]
    q = dict(zip(pos_list, list1))
    df = pd.DataFrame.from_dict(q, orient='index')
    for j in range(len(test[i])):
        try:
            word = test[i][j]
            if re.search('[a-zA-Z0-9]', word):
                for possible_pos in word_dict[word].keys():
                    try:
                        if j == 0:
                            TP = Transition['Begin_Sent'][possible_pos]
                            EP = pos_dict[possible_pos][word]
                        elif test[i][j + 1] == ". ":
                            TP = Transition['End_Sent'][possible_pos]
                            EP = 1
                        else:
                            prev_pos = df.idxmax()[j]
                            TP = Transition[prev_pos][possible_pos]
                            EP = pos_dict[possible_pos][word]
                        likelihood = EP * TP
                        df.loc[possible_pos,j] = likelihood
                    except KeyError:
                        prev_pos = df.idxmax()[j]
                        try:
                            TP = Transition[prev_pos][possible_pos]
                            EP = 1/1000
                            likelihood = EP * TP
                            df.loc[possible_pos, j] = likelihood
                        except KeyError:
                            pass
        except IndexError:
            pass

    result.extend(df.idxmax())
print(result)

out_file = open('submission.pos', 'w')
for i in range(len(result)):
    if re.search('[a-zA-Z0-9]', final_list[i]):
        out_file.writelines(final_list[i] + '\t' + result[i] + '\n')
    else:
        out_file.writelines(final_list[i] + '\t' + final_list[i] + '\n')

out_file.close()

# j = 0
# i = 1
# columns = [x for x in range(200)]
# rows = ["S"]
# rows.extend([x for x in pos_list])
# rows.append("E")
# A = np.zeros((38, 200)).reshape(38, 200)
# df = pd.DataFrame(A, index=rows, columns=columns)
# i += 1

# while True:
#     A[0][0] = 1
#     pos = list[i].split("\t")[1]
#     word = list[i].split("\t")[0]
#         # Handling OOV
#     if word not in word_dict:
#         if i == 0 or list[i + 1] == ".\t.":
#             TP = 1 / 1000
#             EP = 1 / 1000
#         else:
#             TP = Transition[list[i - 1].split("\t")[1]][list[i].split("\t")[1]]
#             EP = 1 / 1000
#         A[pos_list.index(list[i].split("\t")[1])][i] = EP * TP
#     print(word_dict[word].keys())
#     for possible_pos in word_dict[word].keys():
#         try:
#                 if word in word_dict:
#                     if possible_pos in pos_list:
#                         if i == 0:
#                             TP = Transition['Begin_Sent'][possible_pos]
#                             EP = pos_dict[possible_pos][word]
#                         elif list[i + 1] == ".\t.":
#                             TP = Transition['End_Sent'][possible_pos]
#                             EP = 1
#                         else:
#                             prev_pos = list[i - 1].split("\t")[1]
#                             TP = Transition[prev_pos][possible_pos]
#                             EP = pos_dict[possible_pos][word]
#                         A[pos_list.index(possible_pos)][i] = EP * TP
#
#             except KeyError:
#
#                 print(possible_pos, "not in pos_list")
#         i += 1
#         if list[i] == ".\t.":
#             score_list = df.max()
#             pos_output = df.idxmax()
#             for i in range(column_num):
#                 pos_output.drop(df.index[df[i] == 'S'], inplace=True)
#             df.to_csv(fr'~/Downloads/WSJ_POS_CORPUS_FOR_STUDENTS/viterbi_test{j}.csv')
#             print(score_list, pos_output)
#             break


# Make a 2 dimensional array (or equivalent)
# – columns represent tokens at positions in the text
# • 0 = start of sentence
# • N = Nth token (word punctuation at position N)
# • Length+1 = end of sentence
# – rows represent S states: the start symbol, the end symbol and all possible POS (NN, JJ, ...)
# – cells represent the likelihood that a particular word is at a particular state
# • Traverse the chart as per the algorithm (fish sleep slides, etc.)
# – For all states at position 1, multiply transition probability from Start (position 0)  by
# likelihood that word at position 1 occurs in that state.  Choose highest score for each cell.
# – For n from 2 to N (columns)
# • for each cell [n,s] in column n and each state [n-1,s'] in column n-1:
# • get the product of:
# – likelihood that token n occurs in state s
# – the transition probability from  s' to s
# – the score stored in [n-1,s']
# • At each position [n,s], record the max of the s scores calculated
