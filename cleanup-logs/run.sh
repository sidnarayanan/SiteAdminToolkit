#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc630
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export EOS_MGM_URL=root://eoscms.cern.ch # this is important 

cd /cvmfs/cms.cern.ch/slc6_amd64_gcc630/cms/cmssw/CMSSW_9_4_6/; eval `scramv1 runtime -sh`
cd /afs/cern.ch/user/s/snarayan/SiteAdminToolkit/cleanup-logs

logbase=/afs/cern.ch/work/s/snarayan/public/logs/cleaner/
logfile=${logbase}/$(date +"%Y%m%d_%H%M").log
mkdir -p $logbase

./logsDelete.py  > $logfile  2>&1 
./logsDelete.py --input dump.txt --delete  >> $logfile 2>&1 
