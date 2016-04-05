__author__ = "Oier Lopez de Lacalle <oier.lopezdelacalle@gmail.com>"

import sys
import os
import nltk
import utils
import getopt
from LexSampReader import LexSampReader

def usage():
    sys.stderr.write("USAGE: create_gs.py -c configure.file\n")


def write_stdout_gs(instances):
    for (insId, insLabel, offset, tokens) in instances:
        sys.stdout.write("%s\t%s\n" % (insId, insLabel))

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

    #Get number of folds in xvalidation
    if not "XVAL" in props:
        sys.stderr.write("[ERROR] XVAL number of folds not defined\n")
    K = int(props["XVAL"])


    ##
    ## Get XVAL test files for each word in words
    ##
    for word in sorted(words):
        for fold in range(1, K+1):
            #sys.stderr.write("[INFO] Fold %s\n" %str(fold))
            reader = LexSampReader()
            dataset = data_dir + "/" + word + "/xval/fold"+str(fold)
            testInstances = reader.getInstances(dataset+"/"+word+".test.ls.utf8.xml")
            write_stdout_gs(testInstances)
