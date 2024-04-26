import zipfile, gensim
import wget, nltk
import spacy
import ru_core_news_md
from numpy import float64


def text_preprocessing(input_text: str) -> str:
    punctuation = """!"#$%&\'()*+,.:;<=>?@[\\]^_`{|}~"""
    tt = str.maketrans(dict.fromkeys(f"{punctuation}“”«»"))
    return input_text.lower().translate(tt).replace("/", " ")


def get_syns(text):
    nlp = ru_core_news_md.load()
    nlp.max_length = 1500000
    document = nlp(text)
    syns = []
    for token in document:
        if token.pos_ == 'NOUN':
            if token.lemma_ not in syns:
                syns.append(token.lemma_)
    return syns


def get_model():
    model = gensim.models.KeyedVectors.load_word2vec_format('model.bin', binary=True)
    return model


def calculate_similarity(txt):
    txt = text_preprocessing(txt)
    syns = get_syns(txt)
    model = get_model()
    temp = []
    Dict = {}
    counter = 1
    calculations = {}
    exceptions = []
    for i in range(len(syns)):
        for j in range(len(syns)):

            if (str(syns[i]) + "-" + str(syns[j]) in calculations):
                similarity = calculations[str(syns[i]) + "-" + str(syns[j])]

            elif (str(syns[j]) + "-" + str(syns[i]) in calculations):
                similarity = calculations[str(syns[j]) + "-" + str(syns[i])]

            else:
                try:
                    first = str(syns[i]) + '_NOUN'
                    second = str(syns[j]) + '_NOUN'

                    if (first in exceptions):
                        continue
                    if (second in exceptions):
                        continue

                    similarity = float64(model.similarity(first, second))
                    calculations[str(syns[i]) + "-" + str(syns[j])] = similarity
                    counter += 1
                except Exception as e:
                    print(e)
                    error = str(e)
                    exceptions.append(error.split("\'")[1])
                    continue
                    # syns.remove(first)

            if (similarity) > 0.5 and (syns[i] != syns[j]):
                temp.append([syns[j], similarity])
                Dict[syns[i]] = temp
        temp = []
    print(Dict)
    return Dict, counter
