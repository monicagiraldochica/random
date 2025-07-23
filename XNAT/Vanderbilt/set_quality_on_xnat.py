# Rename a scan on XNAT

# Libraries
import pyxnat
import pandas

# XNAT config file
xnatconffile = '/Users/rogersbp/.xnat.cfg'

# Spreadsheet containing scan info
metafile = 'download_report_temp_nw_20170206.csv'
subj_info = pandas.read_csv(metafile)

# XNAT project we will upload to
xnatproj = 'NDW_ROCKLAND'

# Connect to XNAT server
try :
    X = pyxnat.Interface( config=xnatconffile )
except :
    raise Exception('Unable to connect to XNAT')

# Check for global XNAT project
Proj = X.select.project(xnatproj)
if not Proj.exists() :
    raise Exception('Project not found')


# Loop through files (rows of subj_info)
for c in range(0,len(subj_info.index)) :
#for c in range(0,1) :

    # SUBJECT
    subjtag = str(subj_info.subject_label[c])
    Subj = Proj.subject(subjtag)
    if not Subj.exists() :
        raise Exception('Subject not found')

    # EXPERIMENT
    expttag = subj_info.session_label[c]
    Expt = Subj.experiment(expttag)
    if not Expt.exists() :
        raise Exception('Experiment not found')
               
    # ASSESSOR
    assrtag = subj_info.as_label[c]
    Assr = Expt.assessor(assrtag)
    if not Assr.exists() :
        raise Exception('Assessor not found')
    else :
        Assr.attrs.set('proc:genprocdata/validation/status',subj_info.quality[c])
        print(expttag + ' ' + subj_info.quality[c])

## Close XNAT connection
X.disconnect()

