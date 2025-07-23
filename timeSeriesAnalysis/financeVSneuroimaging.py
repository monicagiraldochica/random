#!/usr/bin/env python3
__author__ = "Monica Keith"
__status__ = "Production"

# Requires to have installed quandl, pandas, matplotlib and all its dependencies
# Most matplotlib dependencies can be downloaded with pip3
# List of matplotlib dependencies: https://matplotlib.org/users/installing.html
# To run: python3 timeSeriesTest.py
import quandl # quandl for financial data
import pandas # pandas for data manipulation
import matplotlib.pyplot as plt
import numpy

quandl.ApiConfig.api_key = "48yJPHinVWCGss5QhjsF"

###########################################
### 1. GET DATA INTO A PANDAS DATAFRAME ###
###########################################

### RETRIEVE TSLA AND GM DATA FROM QUANDL ###
tesla = quandl.get('WIKI/TSLA')
gm = quandl.get('WIKI/GM')
# Yearly average number of shares outstanding for both companies
tesla_shares = {2018: 168e6, 2017: 162e6, 2016: 144e6, 2015: 128e6, 2014: 125e6, 2013: 119e6, 2012: 107e6, 2011: 100e6, 2010: 51e6}
gm_shares = {2018: 1.42e9, 2017: 1.50e9, 2016: 1.54e9, 2015: 1.59e9, 2014: 1.61e9, 2013: 1.39e9, 2012: 1.57e9, 2011: 1.54e9, 2010:1.50e9}
# Create a year column 
tesla['Year'] = tesla.index.year
gm['Year'] = gm.index.year
# Take Dates from index and move to Date column 
tesla.reset_index(level=0, inplace = True)
gm.reset_index(level=0, inplace = True)
# Create a new column for the market cap
tesla['cap'] = 0
gm['cap'] = 0
# Calculate market cap for all years
for i, year in enumerate(tesla['Year']):
    shares = tesla_shares.get(year)
    tesla.loc[i, 'cap'] = shares * tesla.loc[i,'Adj. Close'] # cap=share$ x #shares
for i, year in enumerate(gm['Year']):
    shares = gm_shares.get(year)
    gm.loc[i, 'cap'] = shares * gm.loc[i,'Adj. Close']
# Perform an inner merge to save only Date entries that are present in both dataframes
capdata = gm.merge(tesla, how='inner', on='Date')
# Rename the columns so we know which one goes with which car company
capdata.rename(columns={'cap_x':'gm_cap','cap_y':'tesla_cap'}, inplace=True)
# Select only the relevant columns
capdata = capdata.loc[:, ['Date','gm_cap','tesla_cap']]
# Divide to get market cap in billions of dollars
capdata['gm_cap'] = capdata['gm_cap'] / 1e9
capdata['tesla_cap'] = capdata['tesla_cap'] / 1e9

### FMRI BOLD TIME SERIES OF TWO SUBJECTS ###
# These files are examples of what an already cleaned and pre-processed (AFNI) time series from brain activation would look like. 
# **This data is fake and does not come from any real brain**
ts1 = pandas.read_csv("sbj1_rs_ts.csv")
ts2 = pandas.read_csv("sbj2_rs_ts.csv")
# Select only the relevant columns
# Rename the columns so we know which one goes with which subject
# Reset index for merging
# drop=True avoids adding new index column with old index values
ts1 = ts1.rename(columns={'roi1': 'sbj1_bold'}).loc[:,'sbj1_bold'].reset_index(drop=True)
ts2 = ts2.rename(columns={'roi1': 'sbj2_bold'}).loc[:,'sbj2_bold'].reset_index(drop=True)
# Merge the time series of the first region of interest for the two subjects in a new dataframe
bolddata = pandas.concat([ts1, ts2], axis=1)

###########################
### 2. DATA EXPLORATION ###
###########################

# Get an idea of the structure, ranges, outliers or missing values

plt.figure(figsize=(10, 8))

plt.subplot(2, 1, 1)
plt.plot(capdata['Date'], capdata['gm_cap'], 'b-', label = 'GM')
plt.plot(capdata['Date'], capdata['tesla_cap'], 'r-', label = 'TESLA')
plt.xlabel('Years')
plt.ylabel('Market Cap (Billions $)')
plt.legend();

plt.subplot(2, 1, 2)
plt.plot(bolddata.index, bolddata['sbj1_bold'], 'b-', label = 'Subject1')
plt.plot(bolddata.index, bolddata['sbj2_bold'], 'r-', label = 'Subject2')
plt.xlabel('Seconds')
plt.ylabel('Brain activation (BOLD signal)')
plt.legend();

plt.suptitle('Financial (top) vs Neuroimaging (bottom) data')

############################################
### 3. ASK SOME QUESTIONS ABOUT THE DATA ###
############################################

# These questions are probably not too useful but just to give some examples

# At which time point was there the biggest difference between the two companies/subjects?
diff1 = capdata.iloc[:,1]-capdata.iloc[:,2] # difference between gm and tesla
maxdiff1 = numpy.max(diff1) # maximum difference
imaxdiff1 = diff1.tolist().index(maxdiff1) # index of the maximum difference
shade1=numpy.logical_and(capdata['Date'] >= capdata.loc[imaxdiff1-1,'Date'],capdata['Date'] <= capdata.loc[imaxdiff1+1,'Date'])

diff2 = capdata.iloc[:,2]-capdata.iloc[:,1] # difference between tesla and gm
maxdiff2 = numpy.max(diff2)
imaxdiff2 = diff2.tolist().index(maxdiff2)
shade2=numpy.logical_and(capdata['Date'] >= capdata.loc[imaxdiff2-1,'Date'],capdata['Date'] <= capdata.loc[imaxdiff2+1,'Date'])

diff3 = bolddata['sbj1_bold']-bolddata['sbj2_bold'] # difference between subject1 and subject2
maxdiff3 = numpy.max(diff3)
imaxdiff3 = diff3.tolist().index(maxdiff3)
shade3=numpy.logical_and(bolddata.index >= imaxdiff3-1,bolddata.index <= imaxdiff3+1)

diff4 = bolddata['sbj2_bold']-bolddata['sbj1_bold'] # difference between subject2 and subject1
maxdiff4 = numpy.max(diff4)
imaxdiff4 = diff4.tolist().index(maxdiff4)
shade4=numpy.logical_and(bolddata.index >= imaxdiff4-1,bolddata.index <= imaxdiff4+1)

plt.figure(figsize=(10, 8))

plt.subplot(2, 1, 1)
plt.plot(capdata['Date'], capdata['gm_cap'], 'b-', label = 'GM')
plt.plot(capdata['Date'], capdata['tesla_cap'], 'r-', label = 'TESLA')
plt.fill_between(capdata['Date'],capdata['gm_cap'],capdata['tesla_cap'],where=shade1)
plt.fill_between(capdata['Date'],capdata['gm_cap'],capdata['tesla_cap'],where=shade2,facecolor='red')
plt.xticks(ticks=[capdata.loc[imaxdiff1,'Date'],capdata.loc[imaxdiff2,'Date']],labels=None)
plt.ylabel('Market Cap (Billions $)')
plt.legend();

plt.subplot(2, 1, 2)
plt.plot(bolddata.index, bolddata['sbj1_bold'], 'b-', label = 'Subject1')
plt.plot(bolddata.index, bolddata['sbj2_bold'], 'r-', label = 'Subject2')
plt.fill_between(bolddata.index,bolddata['sbj1_bold'],bolddata['sbj2_bold'],where=shade3)
plt.fill_between(bolddata.index,bolddata['sbj1_bold'],bolddata['sbj2_bold'],where=shade4,facecolor='red')
plt.xticks(ticks=[imaxdiff3,imaxdiff4],labels=[str(imaxdiff3),str(imaxdiff4)])
plt.ylabel('Brain activation (BOLD signal)')
plt.legend();

plt.suptitle('Time points with greater difference')

###################
### 4. MODELING ###
###################

##############################
### 5. TRENDS AND PATTERNS ###
##############################

################################
### SHOW ALL THE FANCY PLOTS ###
#################################
plt.show()
