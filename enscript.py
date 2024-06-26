import nltk
import re
from nltk.corpus import wordnet as wn

# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('omw-1.4')


def clear_text(txt):
    regex = re.compile('[^A-Za-z0-9 ]+')
    txt = regex.sub('', txt)
    return txt


def get_nouns(txt):
    nouns = []
    syns = []
    for (word, pos) in nltk.pos_tag(nltk.word_tokenize(clear_text(txt))):
        if pos[0] == 'N':
            # nouns.append(word)
            if word not in nouns:
                try:
                    nouns.append(word)
                    syns.append(wn.synsets(word)[0])
                except Exception as e:
                    print('Failed to : ' + word + " " + str(e))
    return syns, nouns


def calculate_similarity(txt):
    temp = []
    Dict = {}
    counter = 1
    calculations = {}
    syns, nouns = get_nouns(txt)
    for i in range(len(syns)):
        for j in range(len(syns)):

            if (str(syns[i]) + "-" + str(syns[j]) in calculations):
                wup_s = calculations[str(syns[i]) + "-" + str(syns[j])]

            elif (str(syns[j]) + "-" + str(syns[i]) in calculations):
                wup_s = calculations[str(syns[j]) + "-" + str(syns[i])]

            else:
                try:
                    wup_s = syns[i].wup_similarity(syns[j])
                    calculations[str(syns[i]) + "-" + str(syns[j])] = wup_s
                    counter += 1
                except Exception as e:
                    print(e)

            try:
                if (wup_s) > 0.5 and (nouns[i] != nouns[j]):
                    temp.append([nouns[j], wup_s])
                    Dict[nouns[i]] = temp
            except Exception as e:
                print(e)

        temp = []
    print(Dict)
    return Dict, counter