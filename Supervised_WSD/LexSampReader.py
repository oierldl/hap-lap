__author__ = 'Oier Lopez de Lacalle'

import sys
import re 
from xml.dom import minidom
import nltk

"""

A helper class that reads Senseval/Semeval format file and returns
a list the tokenized contexts of the target words, instance id,
instance label, and target-word offset. The tuple contains the
information in the following order:

  (instance_id, instance_label, offset, list_of_tokens)


Lexical Sample Format example:
<corpus>
   <lexelt item="add-v" pos="v">
     <instance docsrc="amt-sense-mt-2013" id="add-v_1_99,7">
       <answer instance="add-v_1_99,7" senseid="add-v_6"/>
       <context>
         skills you know you don't just <head>add</head> one plus one
         you figure out why you're adding it and what you're going to
         do with it once you've got it together and i think that
         that's something that is drastically needed because most of
         these kids cannot think they literally cannot come in out of
         the rain
        </context>
    </instance>
    ...

"""

class LexSampReader: 

    def __init__(self):
        self.instances = []
        self.lexSampFile = None

        
    def getInstances(self,lexFile):
        try:
            self.xmlDoc = minidom.parse(lexFile)
        except Exception:
            sys.stderr.write("Cannot parse "+ lexFile)

        instances = []
        lexs = self.xmlDoc.getElementsByTagName("lexelt")
        for lex in lexs:
            target = lex.getAttribute("item")
            inss = lex.getElementsByTagName("instance")
            for ins in inss:
                insId = ins.getAttribute("id")
                insLab = ins.getElementsByTagName("answer")[0].getAttribute("senseid")
                #match = re.search("([0-9]+)", insLab)
                #if match:
                #    insLab = match.group(1)

                context = ins.getElementsByTagName("context")[0]
                cStr = self.getContext(context)
                #print(cStr)

                tokens = nltk.word_tokenize(cStr)
                offset = self.getTargetOffset(tokens)
                tokens = self.removeHead(tokens)
                #print(tokens)
                
                instance = (insId, insLab, offset, tokens)
                instances.append(instance)
                
        return instances
    

    def getContext(self, ctx):
        text = "";
        for node in ctx.childNodes:
            if node.nodeType == node.TEXT_NODE:
                cstr = node.data
                cstr = cstr.replace("\n", "")
                cstr = cstr.replace("\t", "")
                text += cstr;
            elif node.nodeType == node.ELEMENT_NODE:
                if node.nodeName == "head":
                    cstr = node.childNodes[0].data
                    text += "HEAD-"+ cstr +"-HEAD "
        return text

    
    def getTargetOffset(self, tokens):
        i = 0
        for token in tokens:
            if re.search("HEAD-(.*)-HEAD", token):
                return i
            i += 1
        return i

            
    def removeHead(self, tokens):
        for i in range(0,len(tokens)):
            match = re.search("HEAD-(.*)-HEAD", tokens[i])
            if match:
                tokens[i] = match.group(1)
        return tokens


def usage():
    print """
    python LexSampReader.py lex_samp_file
 """
    
    
## Debugging purposes
if __name__ == '__main__':
    if len(sys.argv)!=2:
        usage()
        sys.exit(2)

    reader = LexSampReader()
    instances = reader.getInstances(sys.argv[1])
    for i in range(0,5):
        print "Ins-ID: " + instances[i][0]
        print "Label: " + instances[i][1]
        print "Offset: " + str(instances[i][2])
        print "Target: " + instances[i][3][instances[i][2]]
        print "tokens: " + " ".join(instances[i][3])
        print ""
