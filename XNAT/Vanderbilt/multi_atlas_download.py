#!/usr/bin/env python3
from dax import XnatUtils
import sys
import os
from argparse import ArgumentParser

def parse_args():
    # Set up the argument parser
    ap = ArgumentParser(prog='ma_download', description="Download Multi Atlas\nfrom a scan on XNAT")
    ap.add_argument('assessor_label', help='Assessor Label')
    ap.add_argument('proc_suffix', help='Proc name suffix', nargs='?',default='')
    ap.add_argument('-d', '--directory', dest='downloaddir',help='Directory to download data to', default='/tmp',required=False)
    return ap.parse_args()

if __name__ == '__main__':
    XNAT = XnatUtils.get_interface()
    ARGS = parse_args()
    AS_LABEL = ARGS.assessor_label

    # Split the assessor label to get the project, subject, session
    PROJ_LABEL = AS_LABEL.split('-x-')[0]
    SUBJ_LABEL = AS_LABEL.split('-x-')[1]
    SESS_LABEL = AS_LABEL.split('-x-')[2]

    DOWNLOAD_DIR = ARGS.downloaddir

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
        sys.stderr.write(f"ERROR: Multi Atlas assessor {AS_LABEL} does not exist")
        sys.exit(1)

    EXPECTED_FILE_NAME = 'orig_target_seg.nii.gz'
    EXPECTED_FILE_PATH = os.path.join(DOWNLOAD_DIR, EXPECTED_FILE_NAME)

    # Download the file to the user dir
    MA_RES.file(EXPECTED_FILE_NAME).get(EXPECTED_FILE_PATH)
    XNAT.disconnect()

    if not os.path.isfile(EXPECTED_FILE_PATH):
        sys.stderr.write('ERROR: Failed to download '
                         '{file} to {path}'.format(file=EXPECTED_FILE_NAME,path=EXPECTED_FILE_PATH))
        sys.exit(1)
