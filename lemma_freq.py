#!/usr/bin/python
import sys
import cPickle as pickle

lemma_freq={}
for line in sys.stdin:
  try:
    token,lemma,tag=line.decode('utf8').strip().split('\t')
    lemma=lemma.lower()+'_'+tag[:2]
  except:
    continue
  lemma_freq[lemma]=lemma_freq.get(lemma,0)+1
print lemma_freq.items()[:10]
pickle.dump(lemma_freq,open(sys.argv[1],'w'),1)