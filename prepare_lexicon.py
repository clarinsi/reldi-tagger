#!/usr/bin/python
import sys
import cPickle as pickle
import marisa_trie

def lcs(s1, s2):
  m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
  longest, x_longest, y_longest = 0, 0, 0
  for x in xrange(1, 1 + len(s1)):
    for y in xrange(1, 1 + len(s2)):
      if s1[x - 1] == s2[y - 1]:
        m[x][y] = m[x - 1][y - 1] + 1
        if m[x][y] > longest:
          longest = m[x][y]
          x_longest = x
          y_longest = y
      else:
        m[x][y] = 0
  return s1[x_longest - longest: x_longest],x_longest,y_longest

def extract_rule(token,lemma):
  base,end_token,end_lemma=lcs(token,lemma)
  start_token=end_token-len(base)
  start_lemma=end_lemma-len(base)
  return start_token,lemma[:start_lemma],len(token)-end_token,lemma[end_lemma:]

lexicon={}
lexicon_train=set()

lemma_freq=pickle.load(open(sys.argv[1]))

for line in sys.stdin:
  try:
    token,lemma,msd=line.decode('utf8').strip().split('\t')
  except:
    continue
  token=token.lower()
  #lemma_lower=lemma.lower()
  lemma_rule=str(extract_rule(token,lemma.lower())).replace(' ','')
  key=token+'_'+msd
  lexicon_train.add((token,msd,lemma_rule))
  #newlemma=lemma==prevlemma
  if key not in lexicon:
    lexicon[key]={}#{lemma_rule:1}
  lexicon[key][lemma.encode('utf8')]=lemma_freq.get(lemma.lower()+'_'+msd[:2],0)

for key in lexicon.iterkeys():
  lexicon[key]=sorted(lexicon[key].items(),key=lambda x:-x[1])[0][0]

trie=marisa_trie.BytesTrie(lexicon.items())

#print lexicon.keys()[0],lexicon[lexicon.keys()[0]]
pickle.dump(trie,open(sys.argv[2],'w'),1)
pickle.dump(lexicon_train,open(sys.argv[2]+'.train','w'),1)
