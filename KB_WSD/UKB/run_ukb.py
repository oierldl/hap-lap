__author__ = "Oier Lopez de Lacalle <oier.lopezdelacalle@gmail.com>"

import sys, os, re
import getopt
import tempfile
import argparse

from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

from utils.LexSampReader import LexSampReader

home = "."
ukbprogram = home + "/ukb/bin/ukb_wsd "
dictionary = home + "/lkb_sources/30/wnet30_dict.txt"
graph = home + "/lkb_sources/30/wn30+gloss.bin"
ukbargs = "--ppr_w2w --dict_weight -D %s -K %s " % (dictionary, graph)
ukbargs_static = "--ppr_w2w --static --dict_weight -D %s -K %s " % (dictionary, graph)

wn_dict = home + "/wn_dict"
lemmatizer = WordNetLemmatizer()


def accuracy(preds, gold):
    correct = [l == r for (l, r) in zip(gold, preds)]
    if correct:
        return float(sum(correct))/len(correct) * 100
    else:
        return 0

def prepare_ukb_input(instances):
    ukb_input = []
    for instance in instances:
        offset = instance[3]
        tokens = instance[-1]
        tagged = pos_tag(tokens)
        
        in_ctx = []
        i = 0
        for tag in tagged:
            if i == offset:
                target = '1'
            else:
                target = '0'
                
            if unicode(tag[0].encode('utf-8'), errors= 'ignore') == "":
                continue

            if re.match("[N].*", tag[1]):
                lemma = lemmatizer.lemmatize(tag[0], pos="n")
                element = lemma + "#n#" + "id"+ str(i) + "#"+target 
                in_ctx.append(element)
            elif re.match("[V].*", tag[1]):
                lemma = lemmatizer.lemmatize(tag[0], pos="v")
                element = lemma + "#v#" + "id"+ str(i) + "#"+target 
                in_ctx.append(element)
            elif re.match("[R].*", tag[1]):
                lemma = lemmatizer.lemmatize(tag[0], pos="r")
                element = lemma + "#r#" + "id"+ str(i) + "#"+target 
                in_ctx.append(element)
            elif re.match("[J].*", tag[1]):
                lemma = lemmatizer.lemmatize(tag[0], pos="a")
                element = lemma + "#a#" + "id"+ str(i) + "#"+target  
                in_ctx.append(element)
            i += 1
        ukb_input.append(" ".join(in_ctx))
    return ukb_input

def process_output(fname):
    preds = {}
    of = open(fname, "r")
    for line in of:
        if not re.search("^\!\!\.*", line):
            line = line.rstrip()

            iid, tok_id, offset, comment, word = re.split('\s+', line)
            preds[iid] = offset
    of.close()
    return preds


def evaluate(preds, gold):
    correct = 0
    for iid in gold:
        if iid in preds and preds[iid] == gold[iid]:
            correct += 1
    prec = float(correct) / len(preds) * 100
    recall = float(correct) / len(gold) * 100
    return prec, recall
            
def wsd(lexsamp_f, static=False, verbose=True, debug=False):
    reader = LexSampReader()
    test_instances = reader.getInstances(lexsamp_f)

    # preprare input for ukb
    ukb_input = prepare_ukb_input(test_instances)
    
    f = tempfile.NamedTemporaryFile(delete=False)
    for i in range(len(test_instances)):
        try:
            ctx = unicode(ukb_input[i].encode('utf-8') , errors='ignore')
            if debug:
                print "%s %s" % (test_instances[i][1], ctx)
            f.write("%s\n" % test_instances[i][1])
            f.write(ctx+'\n')
        except:
            print "something"
    f.close()
    
    # run ukb
    of = tempfile.NamedTemporaryFile(delete=False)
    if static:
        run_call = ukbprogram + ukbargs_static + f.name + ">" + of.name
    else:
        run_call = ukbprogram + ukbargs + f.name + ">" + of.name
    os.system(run_call)
    of.close()

    # process output
    def parse_label(label):
        target, sn = label.split('_')
        word, pos = target.split('-')
        if pos == 'j':
            pos = 'a'
        ss = '{}.{}.{:0>2}'.format(word, pos, sn)
        try:
            ss = wn.synset(ss)
            return ss
        except:
            return ss
        

    def get_offset(ss):
        try:
            return "{:0>8}-{}".format(ss.offset, ss.pos)
        except:
            return "no_offset"

    gold = {str(instance[1]) : get_offset(parse_label(instance[2])) for instance in test_instances}
    preds = process_output(of.name)
    prec, rec = evaluate(preds, gold)

    if verbose:
        for iid in gold:
            if iid not in preds:
                print "{}\t{}\t{}".format(iid, "no-answer", gold[iid])
            else:
                print "{}\t{}\t{}".format(iid, preds[iid], gold[iid])


    print("Precision: {:3.2f}%  -  Recall: {:3.2f}%".format(prec, rec))
    return prec, rec



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Word Sense Disambiguation based on UKB algorithm")

    parser.add_argument("--input", default="", type=str, help="Input file to be disambiguated (lexical sample format)")
    parser.add_argument("--static", action='store_true', help="Run static page rank")
    parser.add_argument("--verbose", action='store_true', help="Show predicted and gold labels for each label")


    arguments = parser.parse_args()

    if arguments.input=='':
        sys.stderr.write('[ERROR] Input file missing')
        parser.print_help()
        sys.exit()
        
    prec, rec = wsd(arguments.input, arguments.static, arguments.verbose)
    
