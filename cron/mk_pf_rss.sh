#! /bin/bash

TARGET="/home/ike/public_html/pf-rss/"
mkdir -p "$TARGET"

export PYTHONPATH=$PYTHONPATH:$HOME/lib

/usr/bin/python2.5 /home/ike/bin/mk_pf_rss.py "1. letnik"
/usr/bin/python2.5 /home/ike/bin/mk_pf_rss.py "2. letnik"
/usr/bin/python2.5 /home/ike/bin/mk_pf_rss.py "3. letnik"
/usr/bin/python2.5 /home/ike/bin/mk_pf_rss.py "4. letnik"
/usr/bin/python2.5 /home/ike/bin/mk_pf_rss.py "absolventi"

mv pf_*.xml "$TARGET"
chmod 755 "$TAGRET"
chmod 644 "${TARGET}/*"
