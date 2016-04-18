__author__ = "Oier Lopez de Lacalle <oier.lopezdelacalle@gmail.com>"

import sys
import os
import nltk
import utils
import getopt
from LexSampReader import LexSampReader
from WSD import WSD
from Baseline import Baseline




cl_type = {"WNFIRST": "baseline", "MFS": "baseline", "RND": "baseline", 
           "MaxEnt" : "classifier", "NB": "classifier", "DT": "classifier",
           "LR_sklearn" : "classifier", "SVM_sklearn" : "classifier"}


def usage():
    sys.stderr.write("USAGE: experimenter.py -c configure.file")


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:")
    
    except getopt.GetoptError as err :
        usage()
        sys.exit(2)

    if len(args)!=0:
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
    
    ##
    ## INITIALIZE MOST OF THE STUFF
    ##

    #Read target words list
    if not "WORDLIST" in props:
        sys.stderr.write("[ERROR] WORDLIST file not defined\n")
        sys.exit(2)
    words = utils.read_words(props["WORDLIST"])
        
    #Get dataset path (file structured is hard-coded for simplicity)
    if not "DATADIR" in props:
        sys.stderr.write("[ERROR] DATADIR not defined\n")
        sys.exit(2)
    data_dir = props["DATADIR"]
    results_dir = os.getcwd()
    if "RESULTSDIR" in props:
        results_dir = props["RESULTSDIR"]

    #Init classifier:
    if "CLASSIFIER" not in props:
        sys.stderr.write("[ERROR] Incorrect CLASSIFIER\n")
        sys.exit(2)
    
    class_name = props["CLASSIFIER"]
    if not class_name in cl_type:
        sys.stderr.write("[ERROR] Classifier type not defined\n")
        sys.stderr.write("\tAvailable classifiers " + cl_type)
        sys.exit(2)

    if cl_type[class_name] == "baseline":
        wsd = Baseline()
        wsd.setBaseline(class_name)
        featsset = ["NONE"]
    else:
        wsd = WSD()
        wsd.setClassifier(class_name)
        if not "FEATURESETS" in props:
            sys.stderr.write("[ERROR] Classifier type not defined\n")
            sys.exit(2)
        featsset = props["FEATURESETS"].split(",")
        wsd.setFeatureSet(featsset)

    #Get number of folds in xvalidation
    if not "XVAL" in props:
        sys.stderr.write("[ERROR] XVAL number of folds not defined\n")
    K = int(props["XVAL"])


    ##
    ## Run the XVAL experiments for each word in words
    ##
    sys.stderr.write("WSD EXPERIMENTER\n")
    sys.stderr.write("[INFO] Classifier: %s\n" % class_name)
    sys.stderr.write("[INFO] Feature set: %s\n" % str(featsset))
    for word in sorted(words):
        sys.stderr.write("[INFO] Running WSD for %s\n" % word)

        res_dir_w = results_dir + "/" + word
        if not os.path.exists(res_dir_w):
            os.makedirs(res_dir_w)
        acc_list = []
        word_acc = 0
        fs = "+".join(featsset)
        for fold in range(1, K+1):
            #sys.stderr.write("[INFO] Fold %s\n" %str(fold))
            reader = LexSampReader()
            dataset = data_dir + "/" + word + "/xval/fold"+str(fold)
            trainInstances = reader.getInstances(dataset+"/"+word+".train.ls.utf8.xml")
            testInstances = reader.getInstances(dataset+"/"+word+".test.ls.utf8.xml")
            wsd.setTrain(trainInstances)
            wsd.setTest(testInstances)

            wsd.learn()
            preds = wsd.predict()
            gold = [insLabel for (insId, insLabel, offset, tokens) in testInstances]
            acc = wsd.accuracy(preds, gold)
            acc_list.append(acc)
            word_acc += acc
            sys.stderr.write("[INFO] %s fold %s: %s\n" % (word, str(fold), str(acc)))

            pred_filename = word + ".f"+str(fold)+"."+class_name+"."+fs+".out"
            res_file = res_dir_w + "/" + pred_filename
            utils.print_predictions(preds, testInstances, res_file)
        acc_filename = word +"."+class_name+"."+fs+".acc"
        acc_file = res_dir_w + "/" + acc_filename
        utils.print_accuracy(acc_list, acc_file)
        word_acc = float(word_acc) / K
        sys.stderr.write("[INFO] %s avg fscore: %s\n" % (word, str(word_acc)))
        sys.stderr.write("[INFO] Results stored in %s\n\n" % res_dir_w)
