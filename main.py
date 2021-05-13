import collections

import content as content
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import RegexpTokenizer
try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

def read_file():
    file = open("definizioni.txt", "r")
    defn = {}
    d = []
    i = 0
    for line in file:
        if line == '\n':
            defn[i] = d
            i = i + 1
            d = []
        else:
            d.append(line.replace('\n',''))
    file.close()
    return defn


def listToString(s):
    # initialize an empty string
    str1 = ""
    # traverse in the string
    for ele in s:
        str1 += ' ' + ele
        # return string
    return str1

def preprocess(_w):
    tokens = word_tokenize(_w)
    tokenizer = RegexpTokenizer(r"\w+")
    tokens = tokenizer.tokenize(listToString(tokens))
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    t = set(lemmatizer.lemmatize(w) for w in tokens if not w in stop_words)
    return t


def _print(q):
    res = ''
    for i in range(q.qsize()):
        res += ' ' + str(q.get(i))
    print(res)


def depth(max_sense,d):
    sense = wn.synset(max_sense.name())
    root = sense.root_hypernyms()
    for h in sense.hypernyms():
        if (h.name() == root.name()):
            return d
        else:
            return depth(h,d+1)


def wsd(genus, terms):
    bows = []
    bow = set()
    s = wn.synsets(genus)
    for i in range(len(s)):
        bow = bow.union(preprocess(s[i].definition()))
        for e in s[i].examples():
            bow = bow.union(preprocess(e))
        bows.append((s[i],bow))
        bow = set()
    max_len = 0
    for i in range(len(bows)):
        overlap = bows[i][1] & terms
        if len(overlap) > max_len:
            max_sense = bows[i][0]
            max_len = len(overlap)
    return max_sense


def content_to_form(defn):
    terms = set()
    frequences = {}
    for i in range(len(defn)):
        defn[i] = preprocess(defn[i])
        for w in defn[i]:
            frequences[w] = 0
        terms = terms.union(defn[i])
    for t in terms:
        for d in defn:
            for w in d:
                if t == w:
                    frequences[t] = frequences[t] + 1
    frequency_queue = Q.PriorityQueue()
    for t in terms:
        frequency_queue.put((-frequences[t],t))
    genus = frequency_queue.get()[1]
    genus_sense = wsd(genus,terms)
    t = frequency_queue.get()[1]
    _print(frequency_queue)
    for s in wn.synset(genus_sense.name()).hyponyms():
        print('searching {} in {}'.format(t,s.name()))
        print(search(t,s.name()))


def search(term,sense):
    for s in wn.synset(sense).hyponyms():
        if term in s.name():
            return s
        else:
            if search(term,s.name()) is None:
                continue
    return None





defn = read_file()
#for c in range(len(defn)):
print(defn[0])
content_to_form(defn[0])