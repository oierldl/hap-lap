__author__ = 'Oier Lopez de Lacalle'

import sys
import os
import re
import getopt
import utils
from statistics import mean
from statistics import stdev

cl_type = {"WNFIRST": "baseline", "MFS": "baseline", "RND": "baseline", 
           "MaxEnt" : "classifier", "NB": "classifier", "DT": "classifier" }


def usage():
    sys.stderr.write("output_analysis.py -c exp.conf\n")


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:")
    except getopt.GetoptError as err :
        usage()
        sys.exit(2)

    conf_file = ""
    for o, a in opts:
        if o == "-c":
            conf_file = a

    if conf_file == "":
        usage()
        sys.exit(2)
    props = utils.read_properties(conf_file)    


    if not "WORDLIST" in props:
        sys.stderr.write("[ERROR] WORDLIST file not defined\n")
        sys.exit(2)
    words = utils.read_words(props["WORDLIST"])

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

    avg = []
    sys.stdout.write("%s-%s\tfscore\tstd\n" % (class_name,fs))
    for word in sorted(words):
        filename = word +"."+class_name+"."+fs+".acc"
        f = open(results_dir + "/" + word + "/" + filename, "r")
        res = [float(i) for i in f]
        f.close()
        w_avg = mean(res)
        w_std = stdev(res)
        sys.stdout.write("%s\t%6.4f\t%6.4f\n" % (word, w_avg, w_std))
        avg.append(w_avg)
    fscore = mean(avg)
    std = stdev(avg)
    sys.stdout.write("OVERALL\t%6.4f\t%6.4f\n" % (fscore, std))
