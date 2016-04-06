__author__ = 'Oier Lopez de Lacalle'

import sys
import re 
from xml.dom import minidom
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import numpy as np
from sklearn.feature_extraction import DictVectorizer


"""

A class that contains a variety of methods for extracting
features. Most of them take an instance (see below) as an argument and
return a set of features.

Input instance is defined as a tuple of:

   (instance_id, instance_label, offset, list_of_tokens)

The featureset is defined as a dictionary mapping string to boolean:

   {'bow(dog)': True, ...}


"""

class FeatureExtractor:

    def __init__(self):
        self.vec = DictVectorizer()

    """
    Bag of Words are the surrounding words features, and include all
    the individual words in the surrounding context of an ambiguous
    word w. Open-class words are only extracted. 

    The remaining words are converted to their lemma forms in lower
    case. Each lemma is considered as one feature
    """
    def getBoW(self, instance):
        bowFeatures = {}

        # tokens in the third position
        tokens = instance[3]
        # pos tag
        wordnet_lemmatizer = WordNetLemmatizer()
        tagged = nltk.pos_tag(tokens)
        i = 0
        for tag in tagged:
            if instance[2] == i:
                i +=1
                continue
                #sys.stderr.write('remove target word (%s)\n' % tag[0])
            elif tag[0] in stopwords.words("english"):
                i +=1
                continue
                #sys.stderr.write('stopword (%s)\n' % tag[0])
            elif re.match("N.*", tag[1]):
                bowFeatures['bow(%s)' %  wordnet_lemmatizer.lemmatize(tag[0], pos="n")] = True
            elif re.match("V.*", tag[1]):
                bowFeatures['bow(%s)' % wordnet_lemmatizer.lemmatize(tag[0], pos="v")] = True
            elif re.match("R.*", tag[1]):
                bowFeatures['bow(%s)' % wordnet_lemmatizer.lemmatize(tag[0], pos="r")] = True
            elif re.match("J.*", tag[1]):
                bowFeatures['bow(%s)' % wordnet_lemmatizer.lemmatize(tag[0], pos="a")] = True
            i += 1
        return bowFeatures

    """
    POS Tags of Surrounding Words We use the POS tags of three words
    to the left and three words to the right of the target ambiguous word,
    and the target word itself.
    """
    def getSurroundPoS(self, instance):
        posFeatures = {}

        offset = instance[2]
        window = 3
        tokens = instance[3]

        tagged = nltk.pos_tag(tokens)
        for i in range(-window, window+1):
            pos = offset - i
            if pos < 0:
                fname = "pos%s(null)" % str(i)
            elif pos > len(tokens) -1 :
                fname = "pos%s(null)" % str(i)
            else:
                fname = "pos%s(%s)" % (str(i), tagged[i][1])

            posFeatures[fname] = True
            
        return posFeatures

    """
    Local Collocations. The method creates 11 local collocations features
    including: C-2-2, C-1,-1 , C2,2, C-1-,1 ... and C1,3, where Ci,j
    refers to an ordered sequence of words in the same sentence of
    w. Offsets i and j denote the starting and ending positions of the
    sequence relative to w, where a negative (positive) offset refers
    to a word to the left (right) of w.

    """
    def getLocalCollocations(self,instance):
        colFeatures = {}

        begins = []
        ends = []
        ## set starts and ends of each collocations.
        begins.append(-2)
        ends.append(-2)
        begins.append(-1)
        ends.append(-1)
        begins.append(1)
        ends.append(1)
        begins.append(2)
        ends.append(2)
        begins.append(-2)
        ends.append(-1)
        begins.append(-1)
        ends.append(1)
        begins.append(1)
        ends.append(2)
        begins.append(-3)
        ends.append(-1)
        begins.append(-2)
        ends.append(1)
        begins.append(-1)
        ends.append(2)
        begins.append(1)
        ends.append(3)
        
        if len(begins) != len(ends):
            sys.stderr.write("[ERROR] Different number of begins and ends of collocations")
            return None

        offset = instance[2]
        tokens = instance[3]
        for ci in range(0, len(begins)):
            begin = offset - begins[ci]
            end = offset - ends[ci]
            
            if (begin >= 0) or (end <= len(tokens)):
                iname = str(begins[ci]) + "," + str(ends[ci])
                fname = "col%s(%s)" % (iname, "_".join(tokens[begin:end+1]))
                colFeatures[fname] = True
                
        return colFeatures


    def convert2sklearn(self, features, train=True):
        X = list()
        y = list()

        for i in range(0,len(features)):
            X.append(features[i][0])
            y.append(features[i][1])

        if train:
            X = self.vec.fit_transform(X).toarray()
        else:
            X = self.vec.transform(X).toarray()
        y = np.array(y)
        return (X, y)
    
