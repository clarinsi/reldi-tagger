#!/usr/bin/python
#-*-coding:utf8-*-
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
import cPickle as pickle
import sys

def suffix(token,n):
  if len(token)>n:
    return token[-n:]

def extract_features_lemma(token):
  features={}
  for i in range(4):
    suf=suffix(token,i+1)
    if suf!=None:
      features['suf'+str(i+1)]=suf
  if len(token)>3:
    features['pref3']=token[:3]
  return features

if __name__=='__main__':
  lexicon=pickle.load(open(sys.argv[1]+'.train'))

  train={}
  for token,msd,label in lexicon:
    if msd not in train:
      train[msd]=set()
    train[msd].add((token,label))

  models={}
  for msd in train:
    if msd[0] not in 'NAVRM' or msd[:2]=='Va':
      continue
    x=[]
    y=[]
    for token,label in train[msd]:
      x.append(extract_features_lemma(token))
      y.append(label)
    p=Pipeline([('vect',DictVectorizer()),('clf',MultinomialNB())])
    p.fit(x,y)
    #print p.predict(extract_features(u'kolege'))
    #break
    print msd
    models[msd]=p

  pickle.dump(models,open(sys.argv[1]+'.guesser','w'),1)
