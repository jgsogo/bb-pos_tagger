# !/usr/bin/env python
# -*- coding: utf-8 -*-


"""
1
"""
from glob import glob
from codecs import open, BOM_UTF8

def wikicorpus(words=1000000, start=0):
    s = [[]]
    i = 0
    for f in glob("wikicorpus.tagged.es/*")[start:]:
        for line in open(f, encoding="latin-1"):
            if line == "\n" or line.startswith((
              "<doc", "</doc>", "ENDOFARTICLE", "REDIRECT",
              "Acontecimientos",
              "Fallecimientos",
              "Nacimientos")):
                continue
            w, lemma, tag, x = line.split(" ")
            if tag.startswith("Fp"):
                tag = tag[:3]
            elif tag.startswith("V"):  # VMIP3P0 => VMI
                tag = tag[:3]
            elif tag.startswith("NC"): # NCMS000 => NCS
                tag = tag[:2] + tag[3]
            else:
                tag = tag[:2]
            for w in w.split("_"): # Puerto_Rico
                s[-1].append((w, tag)); i+=1
            if tag == "Fp" and w == ".":
                s.append([])
            if i >= words:
                return s[:-1]


"""
2
"""
from collections import defaultdict

# "el" => {"DA": 3741, "NP": 243, "CS": 13, "RG": 7})
lexicon = defaultdict(lambda: defaultdict(int))

for sentence in wikicorpus(1000000):
    for w, tag in sentence:
        lexicon[w][tag] += 1

top = []
for w, tags in lexicon.items():
    freq = sum(tags.values())      # 3741 + 243 + ...
    tag  = max(tags, key=tags.get) # DA
    top.append((freq, w, tag))

top = sorted(top, reverse=True)[:100000] # top 100,000
top = ["%s %s" % (w, tag) for freq, w, tag in top if w]

open("es-lexicon.txt", "w").write(BOM_UTF8 + "\n".join(top).encode("utf-8"))


"""
3
"""
sentences = wikicorpus(words=1000000)

ANONYMOUS = "anonymous"
for s in sentences:
    for i, (w, tag) in enumerate(s):
        if tag == "NP": # NP = proper noun in Parole tagset.
            s[i] = (ANONYMOUS, "NP")


from nltk.tag import UnigramTagger
from nltk.tag import FastBrillTaggerTrainer

from nltk.tag.brill import SymmetricProximateTokensTemplate
from nltk.tag.brill import ProximateTokensTemplate
from nltk.tag.brill import ProximateTagsRule
from nltk.tag.brill import ProximateWordsRule

ctx = [ # Context = surrounding words and tags.
    SymmetricProximateTokensTemplate(ProximateTagsRule,  (1, 1)),
    SymmetricProximateTokensTemplate(ProximateTagsRule,  (1, 2)),
    SymmetricProximateTokensTemplate(ProximateTagsRule,  (1, 3)),
    SymmetricProximateTokensTemplate(ProximateTagsRule,  (2, 2)),
    SymmetricProximateTokensTemplate(ProximateWordsRule, (0, 0)),
    SymmetricProximateTokensTemplate(ProximateWordsRule, (1, 1)),
    SymmetricProximateTokensTemplate(ProximateWordsRule, (1, 2)),
    ProximateTokensTemplate(ProximateTagsRule, (-1, -1), (1, 1)),
]

tagger = UnigramTagger(sentences)
tagger = FastBrillTaggerTrainer(tagger, ctx, trace=0)
tagger = tagger.train(sentences, max_rules=100)

#print tagger.evaluate(wikicorpus(10000, start=1))


ctx = []

for rule in tagger.rules():
    a = rule.original_tag
    b = rule.replacement_tag
    c = rule._conditions
    x = c[0][2]
    r = c[0][:2]
    if len(c) != 1: # More complex rules are ignored in this script.
        continue
    if isinstance(rule, ProximateTagsRule):
        if r == (-1, -1): cmd = "PREVTAG"
        if r == (+1, +1): cmd = "NEXTTAG"
        if r == (-2, -1): cmd = "PREV1OR2TAG"
        if r == (+1, +2): cmd = "NEXT1OR2TAG"
        if r == (-3, -1): cmd = "PREV1OR2OR3TAG"
        if r == (+1, +3): cmd = "NEXT1OR2OR3TAG"
        if r == (-2, -2): cmd = "PREV2TAG"
        if r == (+2, +2): cmd = "NEXT2TAG"
    if isinstance(rule, ProximateWordsRule):
        if r == (+0, +0): cmd = "CURWD"
        if r == (-1, -1): cmd = "PREVWD"
        if r == (+1, +1): cmd = "NEXTWD"
        if r == (-2, -1): cmd = "PREV1OR2WD"
        if r == (+1, +2): cmd = "NEXT1OR2WD"
    ctx.append("%s %s %s %s" % (a, b, cmd, x))

open("es-context.txt", "w").write(BOM_UTF8 + "\n".join(ctx).encode("utf-8"))


"""
4
"""
# {"mente": {"RG": 4860, "SP": 8, "VMS": 7}}
suffix = defaultdict(lambda: defaultdict(int))

for sentence in wikicorpus(1000000):
    for w, tag in sentence:
        x = w[-5:] # Last 5 characters.
        if len(x) < len(w) and tag != "NP":
            suffix[x][tag] += 1

top = []
for x, tags in suffix.items():
    tag = max(tags, key=tags.get) # RG
    f1  = sum(tags.values())      # 4860 + 8 + 7
    f2  = tags[tag] / float(f1)   # 4860 / 4875
    top.append((f1, f2, x, tag))

top = sorted(top, reverse=True)
top = filter(lambda (f1, f2, x, tag): f1 >= 10 and f2 > 0.8, top)
top = filter(lambda (f1, f2, x, tag): tag != "NCS", top)
top = top[:100]
top = ["%s %s fhassuf %s %s" % ("NCS", x, len(x), tag) for f1, f2, x, tag in top]

open("es-morphology.txt", "w").write(BOM_UTF8 + "\n".join(top).encode("utf-8"))