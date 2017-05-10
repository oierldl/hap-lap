__author__ = 'Oier Lopez de Lacalle'

import sys
import os
import getopt
import utils
import numpy as np
import scipy.stats as st
from nltk.metrics import ConfusionMatrix
from LexSampReader import LexSampReader


cl_type = {"WNFIRST": "baseline", "MFS": "baseline", "RND": "baseline",
           "MaxEnt": "classifier", "NB": "classifier", "DT": "classifier",
           "MaxEnt_sklearn": "classifier", "SVM_sklearn": "classifier", "NB_sklearn": "classifier",
           "DT_sklearn": "classifier"}


def usage():
    sys.stderr.write("output_analysis.py -w {word} -c exp.conf [-r]\n")
    sys.stderr.write("\t -w: Target word to be analyzed\n")
    sys.stderr.write("\t -c: Experimentation configure file\n")
    sys.stderr.write("\t -r: Activate raw counts\n")


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:c:r")
    
    except getopt.GetoptError as err :
        usage()
        sys.exit(2)

    defpath = "./data/amt-sense-mt-2013/senses.tsv"
    conf_file = ""
    word = ""
    percents = True
    for o, a in opts:
        if o == "-c":
            conf_file = a
        elif o == "-w":
            word = a
        elif o == "-r":  # raw counts
            percents = False

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

    filename = word + "." + class_name + "." + fs + ".acc"
    f = open(results_dir + "/" + word + "/" + filename, "r")
    res = [float(i) for i in f]
    f.close()

    w_avg = np.mean(res)
    w_std = np.std(res)
    w_ci = st.t.interval(0.95, len(res) - 1, loc=np.mean(res), scale=st.sem(res))
    print ""
    print("  OVERALL: %s\t%6.2f (fscore)\t%6.2f (lwr95)\t%6.2f (upr95)" % (word, w_avg *100, w_ci[0]*100, w_ci[1]*100))

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
        f = open(results_dir + "/" + word + "/" + filename, "r")
        for ins in f:
            ins = ins.rstrip()
            (insId, sense) = ins.split("\t")
            preds[insId] = sense
        f.close()
    
    p_senses = [preds[insId] for insId in sorted(preds.keys())]
    g_senses = [gold[insId] for insId in sorted(gold.keys())]
    cm = ConfusionMatrix(g_senses, p_senses)
    print("")
    try:
        print(cm.pp(sort_by_count=True, show_percents=percents, truncate=9))
    except:
        print(cm.pretty_format(sort_by_count=True, show_percents=percents, truncate=9))

    defs = utils.read_definitions(defpath)
    for sense in sorted(defs[word].keys()):
        if sense in defs[word]:
            d = defs[word][sense]
        else:
            d = "Not in sense inventory"
        s = ' {0:10s}'.format(sense)
        print(s + ": " + d)
    print("")
