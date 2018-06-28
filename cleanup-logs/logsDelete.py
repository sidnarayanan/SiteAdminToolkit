#!/usr/bin/env python2.7

import cPickle as pickle
import subprocess
import time
from os.path import join
from sys import stdout
from os import remove
from shutil import rmtree 
from tqdm import tqdm
from multiprocessing import Pool
from argparse import ArgumentParser

LS = ['/usr/bin/eos', 'ls', '-lt']
NOW = int(time.time())
YEAR = str(time.gmtime().tm_year)
NPROC = 4
MAX_AGE = 60 * 86400

# produce Node from output of eos ls -lt
# make this a global so it can be pickled 
def fromLine(l, parent=None, max_age=None):
    try:
        if parent is None:
            l,parent,max_age = l 
        is_file = l.startswith('-')
        ll = l.split()
        rel_path = ll[-1]
        ts = ll[5:8]
        try:
            year = int(ts[-1])
            ts = ts[:2] + ['00:00', year]
        except ValueError:
            ts.append(YEAR)
        age = NOW - time.mktime(time.strptime(' '.join(ts),
                                              '%b %d %H:%M %Y'))
        size = int(ll[4])
        child = Node(parent, is_file, rel_path, age, size, parent.depth+1)
        child.traverse(max_age)
        return child 
    except Exception as e:
        print parent.path, str(e)
        return Node(parent, True, 'broken', 0, 0, parent.depth+1)

# file or directory object
class Node(object):
    __slots__ = ['is_file','rel_path','parent','age','children','size','depth','removed']
    def __init__(self, parent, is_file, rel_path, age, size, depth):
        self.parent = parent
        self.is_file = is_file
        self.rel_path = rel_path 
        self.age = age 
        self.size = size
        self.children = []
        self.depth = depth
        self.removed = False
    @property
    def path(self):
        if self.parent is None:
            return self.rel_path
        else:
            return join(self.parent.path, self.rel_path)
    def dummy_rm(self, fhandle):
        if self.removed:
            return
        info = '%i %s %f %f %i\n'%(int(self.is_file),
                                   self.path,
                                   self.age,
                                   self.size,
                                   self.depth)
        if self.is_file:
            fhandle.write(info)
        else:
            fhandle.write(info)
            for c in self.children:
                c.removed = True 
        self.removed = True
    def rm(self):
        if self.removed:
            return
        try:
            if self.is_file:
                remove(self.path)
            else:
                rmtree(self.path)
                for c in self.children:
                    c.removed = True 
        except OSError:
            pass 
        self.removed = True
    def traverse(self, max_age):
        if self.is_file:
            return 
        if self.age > max_age:
            return
        args = LS + [self.path]
        lines = subprocess.check_output(args, shell=False).strip().split('\n')
        N = len(lines)
        if self.depth == 0:
            print N,'in',self.path
            stdout.flush()
        if N == 0:
            return 
        if self.depth == 0 and NPROC > 1:
            pool = Pool(NPROC)
            self.children.extend(
                    list(tqdm(
                        pool.imap_unordered(fromLine,
                                            [(l, self, max_age) for l in lines
                                             if len(l.strip()) > 0]),
                        total=N
                        )))
        else:
            self.children += [fromLine(l, self, max_age) for l in lines
                              if len(l.strip()) > 0]
    def get(self, max_age):
        if self.age > max_age:
            return [self]
        r = []
        for c in self.children:
            r += c.get(max_age)
        return r 


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--delete', action='store_true')
    parser.add_argument('--input', type=str, default=None)
    args = parser.parse_args()

    head = Node(None, False, '/eos/cms/store/logs/prod/recent/', -1, 0, 0)

    if args.input:
        with open(args.input) as finput:
            for l in finput.readlines():
                ll = l.strip().split()
                ll[0] = int(ll[0]) == 1
                ll[1].replace(head.rel_path, '')
                ll[2] = float(ll[2])
                ll[3] = float(ll[3])
                ll[4] = int(ll[4])
                head.children.append(Node(head, *ll))
    else:
        head.traverse(MAX_AGE) 

    if args.delete:
        for r in tqdm(head.get(MAX_AGE)):
            r.rm()
    else:
        with open('dump.txt','w') as fdump: 
            for r in tqdm(head.get(MAX_AGE)):
                r.dummy_rm(fdump)
                r.dummy_rm(stdout) # so we can retain logging
