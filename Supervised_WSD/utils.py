__author__ = "Oier Lopez de Lacalle <oier.lopezdelacalle@gmail.com>"

import sys
import os
import re
import gzip
import tempfile
from xml.dom import minidom

def read_properties(prop_file):
    fh = open(prop_file)
    properties = {}
    for prop in fh:
        prop = prop.rstrip()
        if re.search("=", prop):
            (prop, value) = re.split("=", prop)
            properties[prop] = value
    return properties

def read_words(filename):
    words = set()
    f = open(filename, "r")
    for w in f:
        w = w.rstrip()
        words.add(str(w))
    f.close()
    return words

def print_predictions(preds, instances, outfile):
    f = open(outfile, "w")
    for i in range(0, len(preds)):
        insId =instances[i][0]
        pred = preds[i]
        f.write(insId + "\t"+ pred+"\n")
    f.close()


def print_accuracy(res, outfile):
    f = open(outfile, "w")
    for r in res:
        f.write(str(r)+"\n")
    f.close()
    
def read_definitions(filename):
    words = {}
    f = open(filename, "r")
    f.readline()
    for i in f:
        (w, s, d) = i.split("\t")[0:3]
        if not w in words:
            words[w] = {}
        words[w][w +"_"+s] = d
    f.close()
    return words

def read_key(filename):
    instances = []
    f = open(filename, "r")
    for line in f:
        w, iid, s = line.rstrip().split(" ")
        instances.append((w, iid, s))
    f.close()
    return instances

def read_key_by_lexelt(filename):
    instances = {}
    f = open(filename, "r")
    for line in f:
        w, iid, s = line.rstrip().split(" ")[0:3] # take first sense
        if w not in instances:
            instances[w] = {}
        instances[w][iid] = ((w, iid, s))
    f.close()
    return instances
