#!/usr/bin/env python3
from dax import XnatUtils
import sys

if __name__ == '__main__':

    XNAT = XnatUtils.get_interface()
    ASSESSORS = XnatUtils.list_project_assessors(XNAT, 'WOODWARD_TCP')

    if len(sys.argv) != 4:
        print len(sys.argv)
        sys.stderr.write('ERROR: args must be <SESSION> <PROC_TYPE> <STATUS>')
        sys.exit(1)
    MY_SESSION = sys.argv[1]
    PROC_TYPE = sys.argv[2]
    STATUS = sys.argv[3]

    for ASSESSOR in ASSESSORS:
        if ASSESSOR['session_label'] == MY_SESSION and \
                        ASSESSOR['proctype'] == PROC_TYPE:
            print "Setting QC of assessor %s in session %s to %s" % (PROC_TYPE,
                                                                 MY_SESSION,
                                                                 STATUS)
            OBJECT = XnatUtils.get_full_object(XNAT, ASSESSOR)
            if PROC_TYPE != 'FreeSurfer':
                OBJECT.attrs.set('proc:genProcData/validation/status', STATUS)
            else:
                OBJECT.attrs.set('fs:fsData/validation/status', STATUS)

    XNAT.disconnect()


