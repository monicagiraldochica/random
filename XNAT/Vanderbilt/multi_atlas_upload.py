#!/usr/bin/env python3
from dax import XnatUtils
import sys
import os
import datetime

def parse_args():
    """Set up the argument parser"""
    from argparse import ArgumentParser
    ap = ArgumentParser(prog='ma_upload', description="Download Multi Atlas"
                        " from a scan on XNAT")
    ap.add_argument('assessor_label', help='Assessor Label')
    ap.add_argument('proc_suffix', help='Proc name suffix', nargs='?',
                    default='')
    ap.add_argument('-f', dest='file', help='Full path to orig_target_seg.nii.gz file',
                    required=True)
    return ap.parse_args()

if __name__ == '__main__':
    XNAT = XnatUtils.get_interface()

    ARGS = parse_args()
    AS_LABEL = ARGS.assessor_label

    # Split the assessor label to get the project, subject, session
    PROJ_LABEL = AS_LABEL.split('-x-')[0]
    SUBJ_LABEL = AS_LABEL.split('-x-')[1]
    SESS_LABEL = AS_LABEL.split('-x-')[2]

    # Assign the file
    SEG_FILE = ARGS.file

    if not os.path.isfile(SEG_FILE):
        sys.stderr.write('ERROR: Seg file %s does not exist' % SEG_FILE)
        sys.exit(1)

    if ARGS.proc_suffix:
        AS_LABEL = ''.join([AS_LABEL, ARGS.proc_suffix])

    # Select the Multi Atlas resource
    MA_RES = XNAT.select('/project/{proj_label}/subjects/{subj_label}/'
                         'experiments/{sess_label}/assessors/{as_label}/'
                         'out/resources/SEG'.format(proj_label=PROJ_LABEL,
                                                    subj_label=SUBJ_LABEL,
                                                    sess_label=SESS_LABEL,
                                                    as_label=AS_LABEL))
    # Check to make sure resource exists
    if not MA_RES.exists():
        sys.stderr.write('ERROR: Multi Atlas assessor %s does not exist\n'
                         % AS_LABEL)
        sys.exit(1)

    # Check to see if the EDITS resource exist. If it doesn't, create it.
    MA_EDITS_RES = XNAT.select('/project/{proj_label}/subjects/{subj_label}/'
                               'experiments/{sess_label}/assessors/{as_label}/'
                               'out/resources/EDITS'.format(proj_label=PROJ_LABEL,
                                                            subj_label=SUBJ_LABEL,
                                                            sess_label=SESS_LABEL,
                                                            as_label=AS_LABEL))
    if not MA_EDITS_RES.exists():
        sys.stdout.write('Creating EDITS resource for %s ' % AS_LABEL)
        MA_EDITS_RES.create()

    # Append the date so we retain when the edits were made
    TODAY = datetime.date.today()
    NEW_SEG_FILE = SEG_FILE.replace('.nii.gz', '%s.nii.gz' % TODAY)
    os.rename(SEG_FILE, NEW_SEG_FILE)
    MA_EDITS_RES.file(os.path.basename(NEW_SEG_FILE)).insert(NEW_SEG_FILE)

    MA = XNAT.select('/project/{proj_label}/subjects/{subj_label}/'
                     'experiments/{sess_label}/assessors/'
                     '{as_label}'.format(proj_label=PROJ_LABEL,
                                         subj_label=SUBJ_LABEL,
                                         sess_label=SESS_LABEL,
                                         as_label=AS_LABEL))

    # Set the flag so the module will handle the updates.
    MA.attrs.set('proc:genProcData/procstatus',
                 'REPROC')
    XNAT.disconnect()

