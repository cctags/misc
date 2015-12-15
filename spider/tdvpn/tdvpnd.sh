#!/usr/bin/env sh

set -x

EMAIL="<email>"
PASSWD="<passwd>"

while [ 1 ]; do

    LOGFILE=$(date "+%Y%m%d_%H_%M_%S").txt
    echo ${LOGFILE}

    python -B tdvpn.py ${EMAIL} ${PASSWD} > ${LOGFILE}

    sleep 725m

done

set +x
