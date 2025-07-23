#!/usr/bin/env python3
from dax import XnatUtils
import sys
XNAT_STATUS_LIST = ['Passed', 'Good', 'OK', 'Poor', 'Rerun', 'Needs QA', 'Needs Edits', 'Bad', 'Failed']
if __name__ == '__main__':

    XNAT = XnatUtils.get_interface()
    ASSESSORS = XnatUtils.list_project_assessors(XNAT, 'WOODWARD_TCP')

    if len(sys.argv) != 4:
        print len(sys.argv)
        sys.stderr.write('ERROR: args must be <ASSESSOR_LABEL> <STATUS> <COMMENTS>')
        sys.exit()
    MY_ASSESSOR = sys.argv[1]
    STATUS = sys.argv[2]
    COMMENTS = sys.argv[3]
    if STATUS not in XNAT_STATUS_LIST:
        sys.stderr.write('ERROR: Status "%s" not in known list: %s\n'
                         %(STATUS, ','.join(XNAT_STATUS_LIST)))

    for ASSESSOR in ASSESSORS:
        if ASSESSOR['label'] == MY_ASSESSOR:
            print "Setting QC of assessor %s to %s" % (MY_ASSESSOR,
                                                       STATUS)
            OBJECT = XnatUtils.get_full_object(XNAT, ASSESSOR)
            if not MY_ASSESSOR.endswith('-x-FS'):
                OBJECT.attrs.set('proc:genProcData/validation/status', STATUS)
                OBJECT.attrs.set('proc:genProcData/validation/notes', COMMENTS)
            else:
                OBJECT.attrs.set('fs:fsData/validation/status', STATUS)
                OBJECT.attrs.set('fs:fsData/validation/notes', COMMENTS)

    XNAT.disconnect()


