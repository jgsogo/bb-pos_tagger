# !/usr/bin/env python
# -*- coding: utf-8 -*-

from pattern.text import Parser

PAROLE = {
    "AO": "JJ"  ,   "I": "UH"  , "VAG": "VBG",
    "AQ": "JJ"  ,  "NC": "NN"  , "VAI": "MD",
    "CC": "CC"  , "NCS": "NN"  , "VAN": "MD",
    "CS": "IN"  , "NCP": "NNS" , "VAS": "MD",
    "DA": "DT"  ,  "NP": "NNP" , "VMG": "VBG",
    "DD": "DT"  ,  "P0": "PRP" , "VMI": "VB",
    "DI": "DT"  ,  "PD": "DT"  , "VMM": "VB",
    "DP": "PRP$",  "PI": "DT"  , "VMN": "VB",
    "DT": "DT"  ,  "PP": "PRP" , "VMP": "VBN",
    "Fa": "."   ,  "PR": "WP$" , "VMS": "VB",
    "Fc": ","   ,  "PT": "WP$" , "VSG": "VBG",
    "Fd": ":"   ,  "PX": "PRP$", "VSI": "VB",
    "Fe": "\""  ,  "RG": "RB"  , "VSN": "VB",
    "Fg": "."   ,  "RN": "RB"  , "VSP": "VBN",
    "Fh": "."   ,  "SP": "IN"  , "VSS": "VB",
    "Fi": "."   ,                  "W": "NN",
    "Fp": "."   ,                  "Z": "CD",
    "Fr": "."   ,                 "Zd": "CD",
    "Fs": "."   ,                 "Zm": "CD",
   "Fpa": "("   ,                 "Zp": "CD",
   "Fpt": ")"   ,
    "Fx": "."   ,
    "Fz": "."
}

def parole2penntreebank(token, tag):
    return token, PAROLE.get(tag, tag)

class SpanishParser(Parser):

    def find_tags(self, tokens, **kwargs):
        # Parser.find_tags() can take an optional map(token, tag) function,
        # which returns an updated (token, tag)-tuple for each token.
        kwargs.setdefault("map", parole2penntreebank)
        return Parser.find_tags(self, tokens, **kwargs)


from pattern.text import Lexicon

import os
me = os.path.dirname(os.path.realpath(__file__))

lexicon = Lexicon(
    path = os.path.join(me, "es-lexicon.txt"),
    )

parser = SpanishParser(
    lexicon = lexicon,
    default = ("NCS", "NP", "Z"),
    morphology = os.path.join(me, "es-morphology.txt"),
    context = os.path.join(me, "es-context.txt"),
    language = "es"
)

def parse(s, *args, **kwargs):
    return parser.parse(s, *args, **kwargs)