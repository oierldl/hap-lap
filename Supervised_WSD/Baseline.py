__author__ = 'Oier Lopez de Lacalle'

import sys
import re 
import time
import nltk
from FeatureExtractor import FeatureExtractor
from nltk.classify import maxent
from nltk.corpus import wordnet as wn
import random

class Baseline:
    def __init__(self):
        random.seed(0)
        self.baseline = "WNFIRST" # MFS, RND
        self.training = []  # only used in MFS 
        self.test = []      

    def setTrain(self, instances):
        self.training = instances

    def setTest(self, instances):
        self.test = instances

    def setBaseline(self, basname):
        self.baseline = basname

    def __transform(self, synset):
        synset = str(synset).replace("Synset('","")
        synset = synset.replace("')","")
        (w, p, s) = synset.split(".")
        return  w +"-"+ p + "_" + str(int(s))
        

    def __randomSense(self, word, pos=None):
        """ Returns a random sense. """
        if pos is None:
            sn = random.randint(1, len(n.synsets(word)))
            pos = ""
        else:
            if pos == "j":
                pos = "a"
            sn = random.randint(1, len(wn.synsets(word, pos)))
        wordSense = word + "-" + pos + "_" + str(sn)
        return wordSense

    def __firstSense(self, word, pos=None):
        """ Returns the first sense. """
        if pos is None:
            synset = wn.synsets(word)[0]
        else:
            if pos == "j":
                pos = "a"
            synset = wn.synsets(word, pos)[0]
        wordSense = self.__transform(synset)
        return wordSense

    def learnMFS(self):
        """ Calculate the most frequent label in training set. """
        if len(self.training) == 0:
            sys.stderr.write("[ERROR] No training assigned\n")
            return 0

        mfs = {}
        for instance in self.training:
            label = instance[1]
            if not label in mfs:
                mfs[label] = 0
            mfs[label] += 1
        
        self.mfsLabel = sorted(mfs.keys(), key=mfs.get, reverse=True)[0]
        return self.mfsLabel

    def learn(self):
        if self.baseline == "MFS":
            self.learnMFS()

    def predict(self):
        """ Predict test instances depending on the activated baseline. """
        """ Assume target word is coded in instance ID: word-pos_index. """
        
        predictions = []
        if len(self.test) == 0:
            sys.stderr.write("[ERROR] No test assigned")
            return 0

        for instance in self.test:
            insId = instance[0]
            targetWord = re.search("[^_]+", insId).group(0)
            sense = ""
            if self.baseline == "WNFIRST":
                (word, pos) = targetWord.split("-")
                sense = self.__firstSense(word, pos)
            
            elif self.baseline == "MFS":
                sense = self.mfsLabel

            elif self.baseline == "RND":
                (word, pos) = targetWord.split("-")
                sense = self.__randomSense(word, pos)
            predictions.append(sense)
        return predictions

    def accuracy(self, preds, gold):
        #results = classifier.classify_many([fs for (fs, l) in gold])
        correct = [l == r for (l, r) in zip(gold, preds)]
        if correct:
            return float(sum(correct))/len(correct)
        else:
            return 0
        
