# Tagger and lemmatiser for Croatian, Slovene and Serbian

## Dependencies

Python modules:

* sklearn(>=0.15) (necessary only if you want to perform lemmatisation as well)
* marisa_trie (https://github.com/pytries/marisa-trie)
* pycrfsuite (https://github.com/tpeng/python-crfsuite)

## Running the tagger

If you have all the files in place for tagging (for Croatian `hr.msd.model` and `hr.marisa`), you can run the tagger like this:

```
$ ./tagger.py hr
Moj
alat
radi
dobro
.

CTRL+D
Moj	Ps1msn
alat	Ncmsn
radi	Vmr3s
dobro	Rgp
.	Z
```

You can, of course, send the data to be tagged to stdin. Additionally, there is a tokeniser in this toolkit, so probably the most convenient way of running the tagger is this:

```
$ echo 'Moj alat radi dobro.' | ../tokeniser/tokeniser.py hr | ./tagger.py hr
1.1.1.1-3	Moj	Ps1msn
1.1.2.5-8	alat	Ncmsn
1.1.3.10-13	radi	Vmr3s
1.1.4.15-19	dobro	Rgp
1.1.5.20-20	.	Z
```
Run `./tagger.py -h` for additional options.

If you want to use both the tagger and the lemmatiser, you should train the lemmatiser as described below OR get the files for guessing the lemmas from these locations:

* http://nlp.ffzg.hr/data/reldi/hr.lexicon.guesser
* http://nlp.ffzg.hr/data/reldi/sr.lexicon.guesser
* http://nlp.ffzg.hr/data/reldi/sl.lexicon.guesser

At the end of the process, for Croatian you should have the following files: `hr.lexicon` and `hr.lexicon.guesser`.

Once you have everything in place, just add the `-l` flag to the tagger:

```
$ echo 'Moj alat radi dobro.' | ../tokeniser/tokeniser.py hr | ./tagger.py hr -l
1.1.1.1-3	Moj	Ps1msn	moj
1.1.2.5-8	alat	Ncmsn	alat
1.1.3.10-13	radi	Vmr3s	raditi
1.1.4.15-19	dobro	Rgp	dobro
1.1.5.20-20	.	Z	.
```

### Converting the output to XML / TEI

For those that prefer to use XML, in particular TEI, instead of the tabular format we
provide a Perl script for this conversion.
If we asume the above output is stored in `tst.tbl`:


```
$ tag2tei.pl < tst.tbl
<body xmlns="http://www.tei-c.org/ns/1.0" xml:lang="sl">
<p>
<s>
<w lemma="moj" ana="mte:Ps1msn">Moj</w>
<c> </c><w lemma="alat" ana="mte:Ncmsn">alat</w>
<c> </c><w lemma="raditi" ana="mte:Vmr3s">radi</w>
<c> </c><w lemma="dobro" ana="mte:Rgp">dobro</w>
<pc ana="mte:Z">.</pc>
</s>
</p>
</body>
```

For simplicity we do not use parameters with the script, but certain variables can be modified inside it,
in particular the value of `body/@xml:lang`, which tokens to treat as punctuation, and the prefix of `@ana`.

## Training your own models

As currently we do not disseminate the lemma prediction models (too large for GitHub), if you want to have lemma prediction models based on the latest version of the lexicon (later than 2016-03-23), you should train your own model. Models for tagging and lexicon files for lemmatisation of know words are included in this distribution.

### Tagger training data format

The tagger training data should be in the one-token-per-line, empty-line-as-sentence-boundary format, with the token, lemma and the tag separated by a tab. An example of the input format can be found in the ```sl.train``` file.

### Preparing the lexicon trie used by the tagger

The lexicon trie is used both during training the tagger and during tagging.

The lexicon file should be formatted in the same manner as the training data, just with no sentence boundaries. Below are commands to be run over the [Croatian](https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1072/hrLex_v1.2.gz), [Serbian](https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1073/srLex_v1.2.gz) and [Slovene lexicon](https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1039/sloleks-en.tbl_v1.2.zip).

```
$ gunzip -c hrLex_v1.2.gz | cut -f 1,2,3 | ./prepare_marisa.py hr.marisa

$ gunzip -c srLex_v1.2.gz | cut -f 1,2,3 | ./prepare_marisa.py sr.marisa

$ cut -f 1,2,3 sloleks-en_v1.2.tbl | ./prepare_marisa.py sl.marisa
```

### Training the tagger

The only argument given to the script is the language code. In case of Croatian (language code `hr`) the corpus training data is expected to be in the file `hr.train`, while the lexicon trie is expected to be in the file `hr.marisa`.

```
$ ./train_tagger.py hr

$ ./train_tagger.py sr

$ ./train_tagger.py sl
```

### Preparing the lexicon for training the lemmatiser

The process of training the lemmatiser is showcased on Slovene. Running corresponding commands for Croatian and Serbian should follow from the previous documentation.

The first step in producing the lexicon for lemmatisation is to calculate the lemma frequency list from the tagger training data. The data in the same format as for training the tagger should be used.

```
$ ./lemma_freq.py sl.lemma_freq < sl.train
```

The second step produces the lexicon in form of a `marisa_trie.BytesTrie`. The lemma frequency information is used in case of `(token,msd)` pair collisions. Only the most frequent lemma is kept in the lexicon.

```
$ cut -f 1,2,3 sloleks-en_v1.2.tbl | ./prepare_lexicon.py sl.lemma_freq sl.lexicon
```

### Training the lemmatiser

The lemmatiser of unknown words is trained on the lexicon prepared in the previous step. The lexicon used for training the lemma guesser has a suffix `.train`. A Multinomial Naive Bayes classifier is learned for each MSD. The classes to be predicted are quatruple transformations in form `(remove_start,prefix,remove_end,suffix)`. The transformation is being applied by removing the first remove_start characters, adding the prefix, removing the last remove_end characters and adding the suffix.

The output of the lemmatiser learning process is a file with the `.lexicon.guesser` suffix.

```
$ ./train_lemmatiser.py sl.lexicon
```
