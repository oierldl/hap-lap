__author__ = 'Oier Lopez de Lacalle'

import sys
import re
import getopt

def usage():
    sys.stderr.write("stats.py [-w {word} | -l] -d {dataset}\n")


def get_words(filename):
    words = {}
    f = open(filename, "r")
    f.readline()
    for i in f:
        words[i.split("\t")[0]] = 1
        
    return sorted(words.keys())
    
def get_max_sense(stats, cat):
    max = 0
    maxw = ""
    for w in stats:
        p = w.split("-")[1]
        if cat == p and len(stats[w]["senses"].keys()) > max:
           max = len(stats[w]["senses"].keys())
    return max

def get_max_sense_all(stats):
    max = 0
    maxw = ""
    for w in stats:
        p = w.split("-")[1]
        if len(stats[w]["senses"].keys()) > max:
           max = len(stats[w]["senses"].keys())
    return max

def get_min_sense(stats, cat):
    min = 99999
    for w in stats:
        p = w.split("-")[1]
        if cat == p and len(stats[w]["senses"].keys()) < min:
           min = len(stats[w]["senses"].keys())
    if min == 99999:
        return 0
    return min

def get_min_sense_all(stats):
    min = 99999
    for w in stats:
        p = w.split("-")[1]
        if len(stats[w]["senses"].keys()) < min:
           min = len(stats[w]["senses"].keys())
    return min


def read_definitions(filename):
    words = {}
    f = open(filename, "r")
    f.readline()
    for i in f:
        (w, s, d) = i.split("\t")[0:3]
        words[w +"_"+s] = d
    f.close()
    return words


if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:d:l")
    
    except getopt.GetoptError as err :
        usage()
        sys.exit(2)

    dataset = ""
    word = ""
    list_words = False
    for o, a in opts:
        if o == "-d":
            dataset = a
        elif o == "-w":
            word = a
        elif o == "-l":
            list_words = True

    # set dataset path (hard-coded)
    if dataset == "MASC":
        dpath = "./data/amt-sense-mt-2013/gs.all.tsv"
        defpath = "./data/amt-sense-mt-2013/senses.tsv"
    else:
        sys.stderr.write("[ERROR] Unknown dataset.\n")
        sys.exit(0)

    if list_words:
        words = get_words(dpath)
        print "Words in the dataset (%s):" % dataset
        for w in words:
            print "   %s" % w
    else:
        word_stats = {}
        data_stats = {"n" : {"words":set(),
                             "senses":set(),
                             "ins":0},
                      "v" : {"words":set(),
                             "senses":set(),
                             "ins":0}, 
                      "j" : {"words":set(),
                             "senses":set(),
                             "ins":0}, 
                      "r" : {"words":set(),
                             "senses":set(),
                             "ins":0}, 
                      "all": {"words":set(),
                              "senses":set(),
                              "ins":0}}
                
        f = open(dpath, "r")
        f.readline()
        for line in f:
            line = line.rstrip()
            (w, i, s) = line.split("\t")
            p = w.split("-")[1]
            data_stats[p]["senses"].add(w + "_" + s)
            data_stats["all"]["senses"].add(w + "_" + s)
            data_stats[p]["words"].add(w)
            data_stats["all"]["words"].add(w)
            data_stats[p]["ins"] += 1
            data_stats["all"]["ins"] += 1
            
            if not w in word_stats: 
                word_stats[w] = {"senses":{},
                                 "ins":0}
            if not w + "_" + s in word_stats[w]["senses"]:
                word_stats[w]["senses"][w + "_" + s]  = 0
            word_stats[w]["senses"][w + "_" + s] +=  1
            word_stats[w]["ins"] += 1
                    
    # PRINT DATASET 
        print ""
        print " Data set stats:"
        print " -----------------------------------------------"
        print '{0} {1} {2} {3} {4} {5}'.format("             ", "     N", "     V", "     J", "     R", "   ALL")
        print " -----------------------------------------------"
        print '{0} {1:6d} {2:6d} {3:6d} {4:6d} {5:6d}'.format("       #words", len(data_stats["n"]["words"]), 
                                                              len(data_stats["v"]["words"]), 
                                                              len(data_stats["j"]["words"]), 
                                                              len(data_stats["r"]["words"]), 
                                                              len(data_stats["all"]["words"]))
        (p_n, p_v, p_j, p_r, p_all) = [0,0,0,0,0]
        if len(data_stats["n"]["words"]) != 0:
            p_n = float(len(data_stats["n"]["senses"])) / float(len(data_stats["n"]["words"]))
        if len(data_stats["v"]["words"]) != 0:
            p_v = float(len(data_stats["v"]["senses"])) / float(len(data_stats["v"]["words"]))
        if len(data_stats["j"]["words"]) != 0:
            p_j = float(len(data_stats["j"]["senses"])) / float(len(data_stats["j"]["words"]))
        if len(data_stats["r"]["words"]) != 0:
            p_r = float(len(data_stats["r"]["senses"])) / float(len(data_stats["r"]["words"]))
        if len(data_stats["all"]["words"]) != 0:
            p_all = float(len(data_stats["all"]["senses"])) / float(len(data_stats["all"]["words"]))

        print '{0}   {1:.2f}   {2:.2f}   {3:.2f}   {4:.2f}   {5:.2f}'.format("      #senses", p_n, p_v, p_j, p_r, p_all )
        print '{0} {1:6d} {2:6d} {3:6d} {4:6d} {5:6d}'.format("   #instances", data_stats["n"]["ins"], 
                                                              data_stats["v"]["ins"], 
                                                              data_stats["j"]["ins"], 
                                                              data_stats["r"]["ins"], 
                                                              data_stats["all"]["ins"])
        print " -----------------------------------------------"

    # word
        max_n = get_max_sense(word_stats, "n")
        max_v = get_max_sense(word_stats, "v")
        max_j = get_max_sense(word_stats, "j")
        max_r = get_max_sense(word_stats, "r")
        max_all = get_max_sense_all(word_stats)
        print '{0} {1:6d} {2:6d} {3:6d} {4:6d} {5:6d}'.format(" #max. senses", max_n, max_v, max_j, max_r, max_all)
    
        min_n = get_min_sense(word_stats, "n")
        min_v = get_min_sense(word_stats, "v")
        min_j = get_min_sense(word_stats, "j")
        min_r = get_min_sense(word_stats, "r")
        min_all = get_min_sense_all(word_stats)
        print '{0} {1:6d} {2:6d} {3:6d} {4:6d} {5:6d}'.format(" #min. senses", min_n, min_v, min_j, min_r, min_all)
    
        print " -----------------------------------------------"
        print ""
    
        if word != "":
            if not word in word_stats:
                sys.stderr.write("[ERROR] Word %s not in the dataset\n" % word)
                sys.exit(0)
                    
            ins = word_stats[word]["ins"]
            print " Word: %s    #instances: %d" % (word, ins)
            print " -----------------------------------------------"
            print " sense distribtion:"
            print " -----------------------------------------------"
            for sense in sorted(word_stats[word]["senses"].keys(), key=word_stats[word]["senses"].get, reverse=True):
                frq = word_stats[word]["senses"][sense]
                prc = float(frq) / float(ins)
                bars = int(prc * 50 + 1)
                s = ' {0:10s}'.format(sense)
                p = ' (%{0:.1f})'.format(prc * 100)
                print s, bars * "|", p
                    
            print " -----------------------------------------------"
        
            defs = read_definitions(defpath)
            for sense in sorted(word_stats[word]["senses"].keys(), key=word_stats[word]["senses"].get, reverse=True):
                if sense in defs:
                    d = defs[sense]
                else:
                    d = "Not in sense inventory"
                s = ' {0:10s}'.format(sense)
                print s + ": " + d
            print ""
