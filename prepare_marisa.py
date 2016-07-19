#!/usr/bin/python
import cPickle as pickle
import marisa_trie
import sys

def search_trie(token,trie,iscomplete=False):
  token='_'+token
  for i in range(len(token)):
    if token[-len(token)+i:] in trie:
      if iscomplete:
        if i==0:
          return (trie[token[-len(token)+i:]],True)
        else:
          return (trie[token[-len(token)+i:]],False)
      return trie[token[-len(token)+i:]]

def search_marisa(token,trie,iscomplete=False):
  token=reverse('_'+token)
  if token in trie:
    return [decode(e) for e in trie[token]]
  else:
    prefixes=trie.prefixes(token)
    if len(prefixes)>0:
      return [decode(e) for e in trie[sorted([(len(e),e) for e in prefixes],reverse=True)[0][1]]]

def decode(s):
  return ''.join(s).strip('0')

def reverse(s):
  t=''
  for u in s:
    t=u+t
  return t

"""
e=pickle.load(open(sys.argv[1]))

l=[]
for key in e:
  if key.startswith('_'):
    for value in e[key]:
      l.append((reverse(key),value.encode('utf8').zfill(9)))
trie = marisa_trie.RecordTrie('sssssssss',l)
pickle.dump(trie,open(sys.argv[1]+'.marisa','w'),1)
"""

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

memory_msd=set()
#memory_lemma=set()
for line in sys.stdin:
  try:
    token,lemma,msd=line.strip().split('\t')
    token=token.decode('utf8')
    #lemma=lemma.decode('utf8')
  except:
    continue
  #lemma=str(extract_rule(token.lower(),lemma.lower())).replace(' ','')
  token=reverse('_'+token.lower())
  memory_msd.add((token,msd))
  #memory_msd.add((token,msd.zfill(9)))
  #memory_lemma.add((token,lemma.zfill(40)))

trie_msd=marisa_trie.BytesTrie(memory_msd)
#trie_msd=marisa_trie.RecordTrie('s'*9,memory_msd)
#trie_lemma=marisa_trie.RecordTrie('s'*40,memory_lemma)
#trie={'msd':trie_msd,'lemma':trie_lemma}

pickle.dump(trie_msd,open(sys.argv[1],'w'),1)

"""
from time import time
for t in (e,trie):
  start=time()
  for i in range(100000):
    f=search_trie(u'susjeda',t)
  print time()-start
"""

