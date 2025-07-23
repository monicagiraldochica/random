#!/usr/bin/env python3
from dax import XnatUtils
import sys

if __name__ == '__main__':

    XNAT = XnatUtils.get_interface()
    ASSESSORS = XnatUtils.list_project_assessors(XNAT, 'DyslexiaYorkU')

    if len(sys.argv) != 3:
        print len(sys.argv)
        sys.stderr.write('ERROR: args must be <ASSESSOR_LABEL> <STATUS>')
        sys.exit()
    MY_ASSESSOR = sys.argv[1]
    STATUS = sys.argv[2]

    for ASSESSOR in ASSESSORS:
        if ASSESSOR['label'] == MY_ASSESSOR:
            print "Setting QC of assessor %s to %s" % (MY_ASSESSOR,
                                                       STATUS)
            OBJECT = XnatUtils.get_full_object(XNAT, ASSESSOR)
            if not MY_ASSESSOR.endswith('-x-FS'):
                OBJECT.attrs.set('proc:genProcData/validation/status', STATUS)
            else:
                OBJECT.attrs.set('fs:fsData/validation/status', STATUS)

    XNAT.disconnect()


