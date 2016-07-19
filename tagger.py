#!/usr/bin/python
#-*-coding:utf8-*-

import warnings
warnings.filterwarnings("ignore")

import sys
import os
reldir=os.path.dirname(os.path.abspath(__file__))

from train_tagger import extract_features_msd
from train_lemmatiser import extract_features_lemma
from subprocess import Popen, PIPE
import cPickle as pickle
from StringIO import StringIO
import pycrfsuite
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

def tag_sent(sent):
  return tagger.tag(extract_features_msd(sent,trie))

def tag_lemmatise_sent(sent):
  return [(a,get_lemma(b,a)) for a,b in zip(tag_sent(sent),sent)]

def get_lemma(token,msd):
  lexicon=lemmatiser['lexicon']
  key=token.lower()+'_'+msd
  if key in lexicon:
    return lexicon[key][0].decode('utf8')
  if msd[:2]!='Np':
    for i in range(len(msd)-1):
      for key in lexicon.keys(key[:-(i+1)]):
        return lexicon[key][0].decode('utf8')
  return guess_lemma(token,msd)

def guess_lemma(token,msd):
  if len(token)<3:
    return apply_rule(token,"(0,'',0,'')",msd)
  model=lemmatiser['model']
  if msd not in model:
    return token
  else:
    lemma=apply_rule(token,model[msd].predict(extract_features_lemma(token))[0],msd)
    if len(lemma)>0:
      return lemma
    else:
      return token

def suffix(token,n):
  if len(token)>n:
    return token[-n:]
      
def apply_rule(token,rule,msd):
  rule=list(eval(rule))
  if msd:
    if msd[:2]=='Np':
      lemma=token
    else:
      lemma=token.lower()	
  else:
    lemma=token.lower()
  rule[2]=len(token)-rule[2]
  lemma=rule[1]+lemma[rule[0]:rule[2]]+rule[3]
  return lemma

def read_and_write(istream,index,ostream):
  entry_list=[]
  sents=[]
  for line in istream:
    if line.strip()=='':
      totag=[]
      for token in [e[index] for e in entry_list]:
        if ' ' in token:
          if len(token)>1:
            totag.extend(token.split(' '))
        else:
          totag.append(token)
      tag_counter=0
      if lemmatiser==None:
        tags=tag_sent(totag)
        tags_proper=[]
        for token in [e[index] for e in entry_list]:
          if ' ' in token:
            if len(token)==1:
              tags_proper.append(' ')
            else:
              tags_proper.append(' '.join(tags[tag_counter:tag_counter+token.count(' ')+1]))
              tag_counter+=token.count(' ')+1
          else:
            tags_proper.append(tags[tag_counter])
            tag_counter+=1
        ostream.write(u''.join(['\t'.join(entry)+'\t'+tag+'\n' for entry,tag in zip(entry_list,tags_proper)])+'\n')
      else:
        tags=tag_lemmatise_sent(totag)
        tags_proper=[]
        for token in [e[index] for e in entry_list]:
          if ' ' in token:
            if len(token)==1:
              tags_proper.append([' ',' '])
            else:
              tags_temp=tags[tag_counter:tag_counter+token.count(' ')+1]
              tag=' '.join([e[0] for e in tags_temp])
              lemma=' '.join([e[1] for e in tags_temp])
              tags_proper.append([tag,lemma])
              tag_counter+=token.count(' ')+1
          else:
            tags_proper.append(tags[tag_counter])
            tag_counter+=1
        ostream.write(''.join(['\t'.join(entry)+'\t'+tag[0]+'\t'+tag[1]+'\n' for entry,tag in zip(entry_list,tags_proper)])+'\n')
      entry_list=[]
    else:
      entry_list.append(line[:-1].decode('utf8').split('\t'))

def load_models(lang,dir=None):
  global trie
  global tagger
  global lemmatiser
  if dir!=None:
    reldir=dir
  trie=pickle.load(open(os.path.join(reldir,lang+'.marisa')))
  tagger=pycrfsuite.Tagger()
  tagger.open(os.path.join(reldir,lang+'.msd.model'))
  lemmatiser={'model':pickle.load(open(os.path.join(reldir,lang+'.lexicon.guesser'))),'lexicon':pickle.load(open(os.path.join(reldir,lang+'.lexicon')))}

if __name__=='__main__':
  import argparse
  parser=argparse.ArgumentParser(description='Tagger and lemmatiser for Slovene, Croatian and Serbian')
  parser.add_argument('lang',help='language of the text',choices=['sl','hr','sr'])
  parser.add_argument('-l','--lemmatise',help='perform lemmatisation as well',action='store_true')
  parser.add_argument('-i','--index',help='index of the column to be processed',type=int,default=0)
  args=parser.parse_args()
  trie=pickle.load(open(os.path.join(reldir,args.lang+'.marisa')))
  tagger=pycrfsuite.Tagger()
  tagger.open(os.path.join(reldir,args.lang+'.msd.model'))
  if args.lemmatise:
    lemmatiser={'model':pickle.load(open(os.path.join(reldir,args.lang+'.lexicon.guesser'))),'lexicon':pickle.load(open(os.path.join(reldir,args.lang+'.lexicon')))}
  else:
    lemmatiser=None
  read_and_write(sys.stdin,args.index-1,sys.stdout)
