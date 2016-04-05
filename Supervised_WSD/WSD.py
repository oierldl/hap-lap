__author__ = 'Oier Lopez de Lacalle'

import sys
import re 
import time
import nltk
from FeatureExtractor import FeatureExtractor
from nltk.classify import maxent

class WSD:

    def __init__(self):
        self.classifier = None
        self.className = "NB"   # other options in the future: MaxEnt, DT
        self.featSets = ["BoW"] # other options: combination of BoW, LocalCol, PoS
        self.training = []      # original train instances  
        self.trainFeatures = [] # train features
        self.test = []          # original test instances
        self.testFeatures = []  # test features

        self.featExtractor = FeatureExtractor()


    def setTrain(self, instances):
        self.training = instances

    def setTest(self, instances):
        self.test = instances

    def setClassifier(self, className):
        self.className = className

    def setFeatureSet(self, featSets):
        self.featSets = featSets


    def learn(self):
        # check if variables are initialized
        if len(self.training) == 0:
            sys.stderr.write("No training assigned\n")
            return 0

        sys.stderr.write("[Time] %s : Extracting training features\n" % time.asctime())
        self.trainFeatures = [(self.getFeatures(instance), instance[1]) for (instance) in self.training]

        if self.className == "NB":
            sys.stderr.write("[Time] %s : Learning a Naive Bayes classifier\n" % time.asctime())
            self.classifier = nltk.NaiveBayesClassifier.train(self.trainFeatures)

        if self.className == "MaxEnt":
            sys.stderr.write("[Time] %s : Learning a Maximum Entropy classifier\n" % time.asctime())
            #self.classifier = nltk.classify.MaxentClassifier.train(self.trainFeatures, "IIS", trace=3, max_iter=100)
            self.classifier = nltk.classify.MaxentClassifier.train(self.trainFeatures, "IIS", trace=3, max_iter=30)

        if self.className == "DT":
            sys.stderr.write("[Time] %s : Learning a Decission Tree classifier\n" % time.asctime())
            self.classifier = nltk.classify.DecisionTreeClassifier.train(self.trainFeatures, entropy_cutoff=0, support_cutoff=0)

        sys.stderr.write("[Time] %s : Learning finished\n" % time.asctime())
        #self.classifier.show_most_informative_features(20)


    def predict(self):
        if self.classifier == None:
            sys.stderr.write("[ERROR] No classifier learnt")
            return 0
        if len(self.test) == 0:
            sys.stderr.write("[ERROR] No test assigned")
            return 0

        
        sys.stderr.write("[Time] %s : Extracting test features\n" % time.asctime())
        self.testFeatures = [(self.getFeatures(instance), instance[1]) for (instance) in self.test]
       
        sys.stderr.write("[Time] %s : Predictions on test\n" % time.asctime())
        predictions = [self.classifier.classify(feats[0]) for feats in self.testFeatures]
        
        return predictions


    def accuracy(self, preds=None, gold=None):
        if preds == None:
            if len(self.testFeatures) == 0:
                if len(self.test) == 0:
                    sys.stderr.write("[ERROR] No test assigned")
                    return 0
                    sys.stderr.write("[Time] %s : Extracting test features\n" % time.asctime())
                self.testFeatures = self.getFeatures(self.test)

            acc = nltk.classify.accuracy(self.classifier, self.testFeatures)
            return acc
        else:
            correct = [l == r for (l, r) in zip(gold, preds)]
            if correct:
                return float(sum(correct))/len(correct)
            else:
                return 0


    def getFeatures(self, instance):
        features = {}
        for ft in self.featSets:
            if ft == "BoW":
                features.update(self.featExtractor.getBoW(instance))
            if ft == "SPoS":
                features.update(self.featExtractor.getSurroundPoS(instance))
            if ft == "LCOL":
                features.update(self.featExtractor.getLocalCollocations(instance))
        return features
