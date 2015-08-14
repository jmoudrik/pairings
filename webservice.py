#!/usr/bin/python

import web
import logging
import time
import json
import cgi
import os
import subprocess
from tempfile import NamedTemporaryFile

import hashlib
import random
import threading


def sha256(txt):
    return hashlib.sha256(txt).hexdigest()

def random_hash(LEN=10):
    return str(random.randint(10**(LEN-1),10**LEN-1))

def unique_hash(length=32):
    """Returns "unique" hash. (the shorter the length, the less unique it is).
    I consider one in 16**32 to be pretty unique. :-).
    """
    return sha256( "%.20f %s %d %d"%(time.time(), random_hash(), os.getpid(), threading.current_thread().ident ) ) [:length]

def check_or_die(cond, msg):
    if not cond:
        logging.info("BadRequest: '%s'"%msg)
        raise web.BadRequest(msg)
    
## Logging, Constants, Globals

logging.basicConfig(filename='log',
                    level=logging.DEBUG,
                    format="WEB: %(asctime)s %(levelname)s %(message)s")
logging.info(os.getcwd())
cgi.maxlen = 512 * 1024

DEBUG = True
USE_PDFLATEX = True

urls = (
    '/',  'PairingsStatic',
    '/submit', 'Submit',
)

class PairingsStatic:
    def GET(self):
        #web.header("Content-Type", 'application/pdf')
        return open('pairings.html',  'rb').read()

class Submit:
    def POST(self):
        logging.info("Submit from '%s'"%(str(web.ctx.ip) ))

        try:
            x = web.input()
        except ValueError:
            check_or_die(False,
                         "File too big. Limit is 512 kB.")

        fname = unique_hash()
        logging.info(fname)

        with open(fname, 'w') as fout:
            fout.write(x['user_file'])
            
        extra_args = []
        if x['user_tournament_name']:
            check_or_die(len(x['user_tournament_name']) <= 30,
                         "Tournament name too long (limit is 30 characters).")
            extra_args.extend(['-tn', x['user_tournament_name']])
            
        if x['user_round_number']:
            check_or_die(len(x['user_round_number']) <= 8,
                         "Round number too long (limit is 8 characters).")
            extra_args.extend(['-tr', x['user_round_number']])

        ret = subprocess.check_call([ './gen.py'] + extra_args + [fname, fname + ".tex" ])
        assert ret == 0

        if USE_PDFLATEX:
            ret = subprocess.check_call([ 'pdflatex', fname + '.tex' ])
            assert ret == 0
        else:
            ret = subprocess.check_call([ 'latex', fname + '.tex' ])
            assert ret == 0

            ret = subprocess.check_call([ 'dvips', '-Ppdf', fname + '.dvi' ])
            assert ret == 0

            ret = subprocess.check_call([ 'ps2pdf', '-dEmbedAllFonts', fname + '.ps' ])
            assert ret == 0

        web.header("Content-Type", 'application/pdf')
        return open(fname + '.pdf',  'rb').read()

#
#   Run...
#

app = web.application(urls, globals())
web.config.debug = DEBUG

if __name__ == '__main__':
    app.run()
