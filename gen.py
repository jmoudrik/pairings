#!/usr/bin/env python
import sys
import re
import logging
import argparse

def slt(text):
    """Converts character that have special meaning in latex into latex equivalents."""
    # Those guys: # $ % & ~ _ ^ \ { }
    text = re.sub(r'\\',r'\textbackslash ', text)
    text = re.sub(r'~',r'\texttilde ', text)
    text = re.sub('([#$%&_^{}])',r'\\\1', text)
    return text

def usage():
    return "usage: %s PAIRING_FILE OUTPUT_FILE"% sys.argv[0]

def main(pa):
    with open('template_prj.tex', 'r') as fin:
        templ_prj = fin.read()
    with open('template_one.tex', 'r') as fin:
        templ_one = fin.read()
        
    with open(pa.input, 'r') as fin:
        data = fin.readlines()
    
    tournament_name, when = [ s.strip() for s in data[0].strip().split('-') ]
    num_round = when.split()[-1]
    
    if pa.tn:
        tournament_name = pa.tn
    if pa.tr:
        num_round = pa.tr
    
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
    
    with open(pa.output, 'w') as fout:
        fout.write(doc)
        
if __name__ == "__main__":
    logging.basicConfig(filename='log',
                        level=logging.DEBUG,
                        format="GEN: %(asctime)s %(levelname)s %(message)s")
    logging.info(repr(sys.argv))
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='INPUT_FILE')
    parser.add_argument('output', metavar='OUTPUT_FILE')
                        
    parser.add_argument('-tn', type=str, default='', help='force tournament name')
    parser.add_argument('-tr', type=str, default='', help='force tournament round')

    pa = parser.parse_args()

    main(pa)
