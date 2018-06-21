#!/bin/bash

cd /afs/cern.ch/user/p/phedex/SiteAdminToolkit/unmerged-cleaner-logs
mkdir -p /tmp/phedex/unmerged_logs/
python2.6 ListDeletable.py > /dev/null
python2.6 ListDeletable.py --delete > /dev/null 
