#!/usr/bin/env python3
from dax import XnatUtils
import sys

if __name__ == '__main__':

    XNAT = XnatUtils.get_interface()
    SCANS = XnatUtils.list_project_scans(XNAT, 'WOODWARD_TCP')

    if len(sys.argv) != 4:
        print len(sys.argv)
        sys.stderr.write('ERROR: args must be <SESSION> <SCAN_ID> <STATUS>')
        sys.exit(1)
    MY_SESSION = sys.argv[1]
    MY_SCAN = sys.argv[2]
    STATUS = sys.argv[3]

    for SCAN in SCANS:
        if SCAN['session_label'] == MY_SESSION and \
                        SCAN['ID'] == MY_SCAN:
            print "Setting QC of scan %s in session %s to %s" % (MY_SCAN,
                                                                 MY_SESSION,
                                                                 STATUS)
            OBJECT = XnatUtils.get_full_object(XNAT, SCAN)
            OBJECT.attrs.set('quality', STATUS)

    XNAT.disconnect()


