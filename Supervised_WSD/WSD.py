__author__ = 'Oier Lopez de Lacalle'

import sys
import os
import time
import nltk
import cPickle as pickle
from FeatureExtractor import FeatureExtractor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier

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
        self.trainFeatures = []

    def setTest(self, instances):
        self.test = instances
        self.testFeatures = []

    def setClassifier(self, className):
        self.className = className

    def setFeatureSet(self, featSets):
        self.featSets = featSets


    def learn(self):
        # check if variables are initialized
        if len(self.training) == 0:
            sys.stderr.write("No training assigned\n")
            return 0

        if len(self.trainFeatures) == 0:
            sys.stderr.write("[Time] %s : Extracting training features\n" % time.asctime())
            self.trainFeatures = [(self.getFeatures(instance), instance[1]) for (instance) in self.training]
        else:
            sys.stderr.write("[Time] %s : Features already extracted\n" % time.asctime())

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

        if self.className == "NB_sklearn":
            sys.stderr.write(
                "[Time] %s : Learning a Multinomial Naive Bayes (scikit-learn) classifier\n" % time.asctime())
            X, y = self.featExtractor.convert2sklearn(self.trainFeatures)
            self.classifier = MultinomialNB()
            self.classifier.fit(X, y)

        if self.className == "DT_sklearn":
            sys.stderr.write(
                "[Time] %s : Learning a Decision Tree (scikit-learn) classifier\n" % time.asctime())
            X, y = self.featExtractor.convert2sklearn(self.trainFeatures)
            self.classifier =  DecisionTreeClassifier(random_state=0)
            self.classifier.fit(X, y)

        if self.className == "MaxEnt_sklearn":
            sys.stderr.write("[Time] %s : Learning a Logistic Regression (scikit-learn) classifier\n" % time.asctime())
            X, y = self.featExtractor.convert2sklearn(self.trainFeatures)
            self.classifier = LogisticRegression()
            self.classifier.fit(X, y)

        if self.className == "SVM_sklearn":
            sys.stderr.write("[Time] %s : Learning a Linear Support Vector Machine (scikit-learn) classifier\n" % time.asctime())
            X, y = self.featExtractor.convert2sklearn(self.trainFeatures)
            self.classifier = LinearSVC(C=1.0)
            self.classifier.fit(X, y)
            
        sys.stderr.write("[Time] %s : Learning finished\n" % time.asctime())
        #self.classifier.show_most_informative_features(20)


    def predict(self):
        if self.classifier == None:
            sys.stderr.write("[ERROR] No classifier learnt")
            return 0
        if len(self.test) == 0:
            sys.stderr.write("[ERROR] No test assigned")
            return 0
        
        if len(self.testFeatures) == 0:
            sys.stderr.write("[Time] %s : Extracting test features\n" % time.asctime())
            self.testFeatures = [(self.getFeatures(instance), instance[1]) for (instance) in self.test]
        else:
            sys.stderr.write("[Time] %s : Test features aldready extracted\n" % time.asctime())

        sys.stderr.write("[Time] %s : Predictions on test\n" % time.asctime())
        if self.className == "MaxEnt_sklearn" or self.className == "SVM_sklearn" or self.className == "DT_sklearn" or self.className == "NB_sklearn":
            X, y = self.featExtractor.convert2sklearn(self.testFeatures, train=False)
            predictions = self.classifier.predict(X)
        else:
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

            if self.className == "MaxEnt_sklearn" or self.className == "SVM_sklearn" or self.className == "DT_sklearn" or self.className == "NB_sklearn":
                X_test, y_test = self.featExtractor.convert2sklearn(self.testFeatures, train=False)
                acc = self.classifier.score(X_test, y_test)
            else:
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


    def saveModel(self, fileName):
        try:
            f = open(fileName, 'wb')
            save = {
                'classifier': self.classifier,
                'className': self.className,
                'featSets': self.featSets
            }
            pickle.dump(save, f, pickle.HIGHEST_PROTOCOL)
            f.close()
        except Exception as e:
            print('Unable to save data to', pickle_file, ':', e)
            raise

        statinfo = os.stat(fileName)
        sys.stderr.write('[INFO] Saved model in %s' % fileName)
        sys.stderr.write('[INFO] Compressed pickle size: ' + statinfo.st_size + "\n")


    def loadModel(self, fileName):
        with open(fileName, 'rb') as f:
            save = pickle.load(f)
            self.classifier = save['classifier']
            self.className = save['className']
            self.featSets = save['featSets']
            del save  # hint to help gc free up memory
        
        sys.stderr.write("[INFO] Loaded model name: %s\n" % self.className)
        sys.stderr.write("[INFO] Loaded model features set: " + self.featsSets + "\n")
