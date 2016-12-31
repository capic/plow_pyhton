#!/bin/bash
# PATH=/opt/someApp/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

cd /opt/plowshare/
git stash
git reset --hard
git pull
make install
cd /root/.config/plowshare/modules.d/legacy.git
git stash
git reset --hard
git pull
# plowmod --update
# cp -r /root/.config /
