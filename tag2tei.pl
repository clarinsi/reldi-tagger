#!/usr/bin/perl
# Program to convert ReLDI tokeniser or tagger (https://github.com/clarinsi/reldi-tagger) output 
# to TEI in-line annotation.
# Generates XML like body/p/s + (w[@lemma][@msd] | pc[@msd] | c)
# i.e. the TEI body containing paragraps, these sentences and these
# words annotated with lemma and msd, if available, and
# punctuation symbols annotated with msd, if available, and
# whitespace between tokens, where it exists.
#
use warnings;
use utf8;

# Parameters are the variables below; change if necessary:

# 0. TEI namespace
$teiNS = 'http://www.tei-c.org/ns/1.0'; # Should not be changed.

# 1. Language of document, goes to body/@xml:lang
$docLang = 'sl';

# 2. MSDs are encoded as values of @ana, which is a pointer; this variable defines where they point to:
# $teiMSDprefix = 'http://nl.ijs.si/ME/V5/msd/tables/msd-fslib-sl.en.xml#';  #Full URI
# $teiMSDprefix = '#';  #Local XML reference, e.g. to fs definitions in <back>
# The CLARIN.SI (https://github.com/clarinsi/TEI-schema) way:
$teiMSDprefix = 'mte:'; #TEI expansion, definition of prefix should be in teiHeader//prefixDef

# 3. Standard TEI has <w> and <pc> (punctuation), 
# we choose the element it according to MSD if present,
# if not, the token is checked with the regular expression:
$punctMSD = '^[ZU]$'; # In MTE V5 specifications punctuation has MSD 'Z' (en) or 'U' (sl) 
$punctRE  = '^[[:punct:]]+$'; # Or, simply punctuation

binmode STDIN, 'utf8';
binmode STDOUT, 'utf8';
binmode STDERR, 'utf8';
#my ($index, $line, $curr_par, $curr_sent, $curr_offset);
my ($index, $line, $curr_par, $curr_sent, $curr_offset) = (0, 0, 0, 0, 0);
my ($token, $msd, $lemma);
print "<body xmlns=\"$teiNS\" xml:lang=\"$docLang\">\n";
while (<>) {
    $line++;
    next unless /.+\t.+/;
    chomp;

    s/&/&amp;/sg;
    s/</&lt;/sg;
    s/>/&gt;/sg;
    s/"/&quot;/sg;

    ($index, $token, $msd, $lemma) = split /\t/
	or die "Bad line $line: '$_'\n";
    my ($par, $sent, $tok, $interval) = split /\./, $index
	or die "Bad index $index in line $line: '$_'\n";
    my ($start_offset, $end_offset) = split /-/, $interval
	or die "Bad interval in $interval in line $line: '$_'\n";

    # $par < $curr_par except if you cat files, then $par > $curr_par
    if ($par != $curr_par) {
	$out .= "</s>\n" unless $curr_sent == 0;
	$out .= "</p>\n" unless $curr_par  == 0;
	$out .= "<p>\n";
	$out .= "<s>\n";
	print $out if $out;
	$out = '';
	$curr_par   = $par;
	$curr_sent  = 0;
	$curr_offset = 0;
    }
    elsif ($sent > $curr_sent) {
	if ($curr_sent) {
	    $out .= "</s>\n";
	    if ($start_offset != $curr_offset) {
		$out .= "<c> </c>\n"
	    }
	}
	$out .= "<s>\n";
    }
    elsif ($start_offset != $curr_offset) {
	$out .= "<c> </c>" unless $curr_offset == 0
    }
    $curr_offset = $end_offset + 1;

    $out .= AnnToken($token, $lemma, $msd);
    $curr_par   = $par;
    $curr_sent  = $sent;
}
$out .= "</s>\n";
$out .= "</p>\n";
print $out;
print "</body>\n";

sub AnnToken  {
    my ($token, $lemma, $msd) = @_;
    my $out;
    if ((defined $msd and $msd =~ /^$punctMSD/) or 
	(not defined $msd and $token =~ m|$punctRE|)) {
	$out = "<pc>$token</pc>\n";
    }
    elsif (defined $lemma) {
	#Only words get @lemma in TEI
	$out = "<w lemma=\"$lemma\">$token</w>\n"
    }
    else {$out = "<w>$token</w>\n"}
    if (defined $msd) {
	$out =~ s/>/ ana="$teiMSDprefix$msd">/;
    }
    return $out
}
