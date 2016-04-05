__author__ = 'Oier Lopez de Lacalle'

import sys
import os
import re
import getopt
import utils
from nltk.metrics import ConfusionMatrix
from LexSampReader import LexSampReader

cl_type = {"WNFIRST": "baseline", "MFS": "baseline", "RND": "baseline", 
           "MaxEnt" : "classifier", "NB": "classifier", "DT": "classifier" }


def usage():
    sys.stderr.write("output_analysis.py -w {word} -c exp.conf\n")


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:c:")
    
    except getopt.GetoptError as err :
        usage()
        sys.exit(2)

    defpath = "./data/amt-sense-mt-2013/senses.tsv"
    conf_file = ""
    word = ""
    for o, a in opts:
        if o == "-c":
            conf_file = a
        elif o == "-w":
            word = a

    if conf_file == "" or word == "":
        usage()
        sys.exit(2)
    props = utils.read_properties(conf_file)    

    if not "DATADIR" in props:
        sys.stderr.write("[ERROR] DATADIR not defined\n")
        sys.exit(2)
    data_dir = props["DATADIR"]

    results_dir = os.getcwd()
    if "RESULTSDIR" in props:
        results_dir = props["RESULTSDIR"]

    if "CLASSIFIER" not in props:
        sys.stderr.write("[ERROR] Incorrect CLASSIFIER\n")
        sys.exit(2)    
    class_name = props["CLASSIFIER"]

    if not class_name in cl_type:
        sys.stderr.write("[ERROR] Classifier type not defined\n")
        sys.stderr.write("\tAvailable classifiers " + cl_type)
        sys.exit(2)

    if cl_type[class_name] == "baseline":
        featsset = ["NONE"]
    else:
        if not "FEATURESETS" in props:
            sys.stderr.write("[ERROR] Classifier type not defined\n")
            sys.exit(2)
        featsset = props["FEATURESETS"].split(",")
    fs = "+".join(featsset)

    if not "XVAL" in props:
        sys.stderr.write("[ERROR] XVAL number of folds not defined\n")
    K = int(props["XVAL"])

    gold = dict()
    preds = dict()
    for fold in range(1, K+1):
        reader = LexSampReader()
        dataset = data_dir + "/" + word + "/xval/fold"+str(fold)
        testInstances = reader.getInstances(dataset+"/"+word+".test.ls.utf8.xml")

        # READ GOLD        
        for ins in testInstances:
            gold[ins[0]] = ins[1]
        
        # READ PREDICTIONS
        filename = word + ".f"+str(fold)+"."+class_name+"."+fs+".out"
        f = open(results_dir + "/" + word +"/"+filename,"r")
        for ins in f:
            ins = ins.rstrip()
            (insId, sense) = ins.split("\t")
            preds[insId] = sense
        f.close()
    
    p_senses = [preds[insId] for insId in sorted(preds.keys())]
    g_senses = [gold[insId] for insId in sorted(gold.keys())]
    cm = ConfusionMatrix(g_senses, p_senses)
    print("")
    print(cm.pp(sort_by_count=True, show_percents=True, truncate=9))

    defs = utils.read_definitions(defpath)
    for sense in sorted(defs[word].keys()):
        if sense in defs[word]:
            d = defs[word][sense]
        else:
            d = "Not in sense inventory"
        s = ' {0:10s}'.format(sense)
        print(s + ": " + d)
    print("")
