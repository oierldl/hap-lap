__author__ = "Oier Lopez de Lacalle <oier.lopezdelacalle@gmail.com>"

import sys
import os
import re
import tempfile
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

home = "."
ukbprogram = home + "/ukb/bin/ukb_wsd "
dictionary = home + "/lkb_sources/30/wnet30_dict.txt"
graph = home + "/lkb_sources/30/wn30+gloss.bin"
ukbargs = "--ppr --dict_weight -D %s -K %s " % (dictionary, graph)

wn_dict = home + "/wn_dict"
lemmatizer = WordNetLemmatizer()

def read_definitions(wn_dir):
    filenames = ["data.adj", "data.adv", "data.noun", "data.verb"]
    defs = {}
    for fn in filenames:
        f = open(wn_dir+"/"+fn, "r")
        for line in f:
            if not re.search("^  ", line):
                (line, definition) = line.split(" | ")
                syn = line.split(" ")[0]
                defs[syn] = definition
        f.close()
    return defs


if __name__ == '__main__':
    c = 0
    while (1):
        print("Enter a sentence (type \"q\" to quit):")
        line = sys.stdin.readline().rstrip()
        if line == "q":
            sys.exit(2)

        tokens = nltk.word_tokenize(line.lower())
        tagged = nltk.pos_tag(tokens)
    
        print("\nInput %s: %s" % (str(c), line))
        in_ctx = []
        i = 0
        for tag in tagged:
            if re.match("[N].*", tag[1]):
                lemma = lemmatizer.lemmatize(tag[0], pos="n")
                element = lemma + "#n#" + "id"+ str(i) + "#1" 
                in_ctx.append(element)
            elif re.match("[V].*", tag[1]):
                lemma = lemmatizer.lemmatize(tag[0], pos="v")
                element = lemma + "#v#" + "id"+ str(i) + "#1" 
                in_ctx.append(element)
            elif re.match("[R].*", tag[1]):
                lemma = lemmatizer.lemmatize(tag[0], pos="r")
                element = lemma + "#r#" + "id"+ str(i) + "#1" 
                in_ctx.append(element)
            elif re.match("[J].*", tag[1]):
                lemma = lemmatizer.lemmatize(tag[0], pos="a")
                element = lemma + "#a#" + "id"+ str(i) + "#1" 
                in_ctx.append(element)
            i += 1

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write("input_%s\n" % str(c))
        f.write(" ".join(in_ctx))
        f.close()

        of = tempfile.NamedTemporaryFile(delete=False)

        run_call = ukbprogram + ukbargs + f.name + ">" + of.name
        os.system(run_call)
        of.close()

        defs = read_definitions(wn_dict)
        of = open(of.name, "r")
        for line in of:
            if not re.search("^\!\!\.*", line):
                line = line.rstrip()
                sys.stdout.write(line + " - ")
                offset_pos = re.split('\s+', line)[2]
                offset = offset_pos.split("-")[0]
                if offset in defs:
                    definition = defs[offset]
                    definition = definition.rstrip()
                sys.stdout.write(definition + "\n")
    
        c +=1
        os.unlink(f.name)
        os.unlink(of.name)
