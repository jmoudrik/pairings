#!/usr/bin/env python
import sys
import re
import logging

def slt(text):
    """Converts character that have special meaning in latex into latex equivalents."""
    # Those guys: # $ % & ~ _ ^ \ { }
    text = re.sub(r'\\',r'\textbackslash ', text)
    text = re.sub(r'~',r'\texttilde ', text)
    text = re.sub('([#$%&_^{}])',r'\\\1', text)
    return text

def usage():
    return "usage: %s PAIRING"% sys.argv[0]

logging.basicConfig(filename='log', level=logging.DEBUG)

logging.info(repr(sys.argv))

if len(sys.argv) != 3:
    sys.exit(1)

with open('template_prj.tex', 'r') as fin:
    templ_prj = fin.read()
with open('template_one.tex', 'r') as fin:
    templ_one = fin.read()
    
with open(sys.argv[1], 'r') as fin:
    data = fin.readlines()

tournament_name, when = [ s.strip() for s in data[0].strip().split('-') ]
num_round = when.split()[-1]

out = []
keys = [ tag.upper() for tag in data[1].strip().split('\t')]

for line in data[2:]:
    match = re.search("^([0-9]*)\t?([^\t]*)\t?([^\t]*)\t?([^\t]*)\t?([^\t]*)\t?", line.strip())
    assert match
    
    g = match.groups()
    
    tups = zip(keys, g) + [("TOURNAMENT_NAME", tournament_name), 
                           ("ROUND", num_round)]
    
    one = templ_one
    
    for key, val in tups:
        one = one.replace("$" + key, slt(val))
    
    out.append(one)
    
doc = templ_prj.replace("$CONTENT",  '\n'.join(out))


with open(sys.argv[2], 'w') as fout:
    fout.write(doc)

