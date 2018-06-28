#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc630
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

cd /cvmfs/cms.cern.ch/slc6_amd64_gcc630/cms/cmssw/CMSSW_9_4_6/; eval `scramv1 runtime -sh`
cd /afs/cern.ch/user/p/phedex/SiteAdminToolkit/cleanup-logs
logfile=/afs/cern.ch/work/p/phedex/public/logs/cleaner/$(date +"%s").log
./logsDelete.py # > $logfile  2>&1 
./logsDelete.py --input dump.txt --delete #  >> $logfile 2>&1 
