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

def average(d):
    c = 0
    somma = 0
    for key in d:
        somma += d[key]
        c = c + 1
    return somma/c


def massimo(d):
    max = 0
    for key in d:
        if d[key] > max:
            max = d[key]
    return max


def remove_none(l):
    res = []
    for e in l:
        if e is None:
            continue
        res.append(e)
    return res


def lch(senses):
    lch = wn.synset(senses[0].name())
    for i in range(1,len(senses)):
        lch = wn.synset(lch.name()).lowest_common_hypernyms(wn.synset(senses[i].name()))
    return lch


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
    l = 0
    for t in terms:
        frequency_queue.put((-frequences[t],t))
        l = l + 1
    media = round(average(frequences)) + 1
    m = massimo(frequences)
    temp = frequency_queue
    res = []
    for i in range(len(temp.queue)):
        e = frequency_queue.queue[i]
        f = (e[0],e[1])
        if not abs(f[0]) == m:
            break
        genus = f[1]
        genus_sense = wsd(genus,terms)
        #print(genus_sense.name())
        for i in range(len(frequency_queue.queue)):
            res.append(search(frequency_queue.get(i)[1],genus_sense.name()))
        return remove_none(res)
    #return lch(remove_none(res))



def search(term,sense):
    #print('search {} in {} hyponyms'.format(term,sense))
    r = None
    for s in wn.synset(sense).hyponyms():
        name = s.name()
        if term in name or term in s.definition() or term in s.examples():
            return s
        else:
            r = search(term,s.name())
            if r is None:
                continue
    return r

defn = read_file()
for i in range(8):
    print('************ DEFINITION {}*************'.format(str(i+1)))
    res = content_to_form(defn[i])
    for s in res:
        print(wn.synset(s.name()).lemmas()[0].name() + ': ' + wn.synset(s.name()).definition())
