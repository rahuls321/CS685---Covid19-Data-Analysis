
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd
import json
from datetime import timedelta
pd.options.mode.chained_assignment = None

'''
# ## Problem statement
# For every district i, find the number of cases from the Covid-19 portal. Take the time-period of analysis from 15th March, 2020 to 14th August, 2021. Output the total number of cases per week for every district in the following manner: districtid, timeid, cases, where timeid is the id of the time (week/month/overall) starting from 1.
'''
# In[3]:


#Using previous results to get all the districts which has to be considered for this assignment
distr_data = pd.read_csv('./output/edge-graph.csv', index_col='District_Key')
distr_data.drop(columns=['Unnamed: 0'], inplace=True)
distr_data


# In[4]:


districts_key = distr_data.index
print("Total districts available: ", len(districts_key))

'''
# So now we have to find the number of cases during the period 15th March, 2020 to 14th August, 2021. Since 'districts.csv' doesn't contain 'District_Key' where as 'district_wise.csv' contains district keys so we have to map keys with district and state to get datas from 'districts.csv'
'''
# In[5]:


dt_wise_covid_data = pd.read_csv('./data/districts.csv', parse_dates=['Date'], index_col='Date')
dt_wise_covid_data = dt_wise_covid_data.loc['2020-03-15':'2021-08-14']
dt_wise_covid_data


# In[6]:


distr_wise_data = pd.read_csv('./data/district_wise.csv')
distr_wise_data


# In[7]:


#dt_wise_covid_data.loc['2020-03-15':'2021-08-14']

'''
# Since 'districts.csv' contains data from '2020-04-26' onwards. So, I'm including raw data from this api https://data.covid19india.org/ to collect data between 15th March 2020 to 25th April 2020.
'''
# In[8]:


raw_data1 = pd.read_csv('./data/covid-raw-data/raw_data1.csv', parse_dates=['Date Announced'])
raw_data2 = pd.read_csv('./data/covid-raw-data/raw_data2.csv', parse_dates=['Date Announced'])


# In[9]:


raw_data1 = raw_data1.sort_values(by=['Date Announced'])
raw_data1


# In[10]:


raw_data1 = raw_data1[(raw_data1['Date Announced'] >= '2020-03-15') & (raw_data1['Date Announced'] < '2020-04-20')]
raw_data1


# In[11]:


raw_data2 = raw_data2[raw_data2['Date Announced'] < '2020-04-26']
raw_data2


# In[12]:


# raw_data1 = raw_data1.groupby(['Date Announced','Detected State', 'Detected District']).sum()
# raw_data1.drop(columns=['Patient Number', 'Estimated Onset Date'], inplace=True)
# raw_data1


# In[13]:


# raw_data2 = raw_data2.groupby(['Date Announced', 'Detected State', 'Detected District']).sum()
# raw_data2.drop(columns=['Patient Number', 'Estimated Onset Date', 'Age Bracket', 'Nationality', 'Backup Notes'], inplace=True)
# raw_data2


# In[14]:


final_raw_data = pd.concat([raw_data1, raw_data2])
final_raw_data = final_raw_data[["Date Announced", "Detected District", "Detected State", "Num Cases"]]
final_raw_data = final_raw_data.rename(columns={'Date Announced': 'Date', 'Detected District': 'District', 'Detected State':'State','Num Cases':'Confirmed'})
final_raw_data = final_raw_data[['Date', 'State', 'District', 'Confirmed']]
# final_raw_data


# In[15]:


final_raw_data = final_raw_data.groupby(['Date', 'State', 'District']).agg('sum')
final_raw_data = final_raw_data.reset_index()
#final_raw_data = final_raw_data.set_index('Date')
print('Final raw data')
print(final_raw_data.head(10))

'''
# final_raw_data contains all the datas from 15th March 2020 to 25th April 2020 and we already have covid data from 26th August 2020 onwards
'''
# In[16]:


#Removing other columns 
df = dt_wise_covid_data.copy()
df.drop(columns=['Recovered', 'Deceased', 'Other', 'Tested'], inplace=True)
df = df.reset_index()
print('Covid data')
print(df.head(10))


# In[17]:


final_df = pd.concat([final_raw_data, df])
print(final_df.head(10))


# In[18]:


# map_dkey_dname={}
# map_dkey_sname={}
# for d_key in districts_key:
#     dd_ff = distr_wise_data[distr_wise_data['District_Key'] == d_key]
#     d_name = dd_ff['District'].iloc[0]
#     s_name = dd_ff['State'].iloc[0]
#     map_dkey_dname[d_key] = d_name
#     map_dkey_sname[d_key] = s_name
# map_dkey_dname


# In[19]:


# map_dkey_sname

'''
# Since 'districts.csv' data contains cumulative values in the 'Confirmed' column so for finding actual no. of cases in that day we need to subtract it from the previous day.
'''

# In[20]:

print("Converting cumulative data to actual value for each districts")
not_available_distr = []
for dt_key in districts_key:
    print(dt_key)
    #Getting district name and state corresponding to the districts key
    get_dt = distr_wise_data[distr_wise_data['District_Key'] == dt_key]
    original_dt_name = get_dt['District'].iloc[0]
    original_st_name = get_dt['State'].iloc[0]
    tt = final_df[(final_df['District'] == original_dt_name) & (final_df['State'] == original_st_name) & (final_df['Date'] >= '2020-04-25')]
    if len(tt)==0:
        not_available_distr.append(original_dt_name)
        continue
    tt.loc[: ,'Confirmed'] = tt['Confirmed'].diff().fillna(tt['Confirmed'].iloc[0])
    final_df.loc[((final_df['District']==original_dt_name) & (final_df['State'] == original_st_name) & (final_df['Date'] >= '2020-04-25')), 'Confirmed'] = tt[['Confirmed']]


# In[21]:


districts_availble = distr_wise_data['District_Key'].unique()
for distr_key in districts_availble: 
    temp_df = distr_wise_data[distr_wise_data['District_Key'] == distr_key]
    dt_name = temp_df['District'].iloc[0]
    st_name = temp_df['State'].iloc[0]
    if distr_key not in list(districts_key):
        print("Dropping this district key: ", distr_key)
        idx_list = list(final_df[(final_df['District'] == dt_name) & (final_df['State'] == st_name)].index)
        if len(idx_list) > 0:
            final_df.drop(idx_list, inplace=True)
    else:
        final_df.loc[((final_df['District'] == dt_name) & (final_df['State'] == st_name)), 'District_Key'] = distr_key


# In[22]:


final_df = final_df.set_index('Date')
print('final_df')
print(final_df)


# In[23]:


# final_df['District_Key'] = final_df['District'].apply(lambda x: map_dname_dkey[x])


# In[24]:


final_df = final_df[['State', 'District', 'District_Key', 'Confirmed']]
final_df


# In[25]:

'''
#These districts are not available in the districts.csv and raw_data.csv files
#So I'm dropping these districts from the final_df
'''
print("Not available these district in the data: " ,not_available_distr)


# In[26]:


wdf = pd.DataFrame(index = final_df.index)
wdf = wdf.reset_index()
wdf['Date'] = pd.to_datetime(wdf['Date'], format='%d/%m/%Y')


# In[27]:


def get_week_or_month_wise_data(wdf, start_date, end_date, timedelay):
    i=1
    wwdf=wdf.copy()
    start_date1 = start_date
    if timedelay==7:
        word='week'
    else: word='month'
    while start_date <= end_date:
        wwdf.loc[((wwdf['Date'] >= start_date) & (wwdf['Date'] < start_date+timedelta(days=timedelay))), word] = i
        start_date += timedelta(days=timedelay)
        start_date = pd.to_datetime(start_date,format='%d/%m/%Y')
        i+=1
    wwdf = wwdf.set_index('Date')
    return wwdf


# In[28]:


# from datetime import timedelta
start_date = pd.to_datetime('15/03/2020', format='%d/%m/%Y')
end_date = pd.to_datetime('14/08/2021', format='%d/%m/%Y')
mdf = get_week_or_month_wise_data(wdf, start_date, end_date, 30)
wdf = get_week_or_month_wise_data(wdf, start_date, end_date, 7)
wdf


# In[29]:


mdf


# In[30]:


ddf = final_df.copy()
new_df = pd.concat([ddf, wdf, mdf], axis=1)
new_df = new_df[["State", "District", "District_Key", "week", "month", "Confirmed"]]
new_df


# In[31]:


final_week_wise_output = new_df.groupby(["State", "District", "District_Key", "week"]).sum()
final_week_wise_output = final_week_wise_output.reset_index()
final_week_wise_output = final_week_wise_output[["District_Key", "week", "Confirmed"]]
final_week_wise_output.rename(columns={"District_Key":"districtid", "week":"timeid", "Confirmed":"cases"}, inplace=True)
final_week_wise_output = final_week_wise_output.astype({"timeid": int, "cases": int})
print('final_week_wise_output')
print(final_week_wise_output.head(10))


# In[32]:


final_month_wise_output = new_df.groupby(["State", "District", "District_Key", "month"]).sum()
final_month_wise_output = final_month_wise_output.reset_index()
final_month_wise_output = final_month_wise_output[["District_Key", "month", "Confirmed"]]
final_month_wise_output.rename(columns={"District_Key":"districtid", "month":"timeid", "Confirmed":"cases"}, inplace=True)

final_month_wise_output = final_month_wise_output.astype({"timeid": int, "cases": int})
print('final_month_wise_output')
print(final_month_wise_output.head(10))


# In[33]:


overall_df = new_df.groupby(["District_Key"]).sum()
overall_df = overall_df.reset_index()
overall_df = overall_df[["District_Key", "Confirmed"]]
overall_df = overall_df.astype({"Confirmed": int})
overall_df.rename(columns={"District_Key":"districtid", "Confirmed": "cases"}, inplace=True)
print('overall_df')
print(overall_df.head(10))


# In[34]:


final_week_wise_output = final_week_wise_output.set_index('districtid')
final_month_wise_output = final_month_wise_output.set_index('districtid')
overall_df = overall_df.set_index('districtid')


# In[39]:


#final_week_wise_output = final_week_wise_output.sort_index()
#final_month_wise_output = final_month_wise_output.sort_index()
#overall_df = overall_df.sort_index()


# In[40]:


# final_week_wise_output = final_week_wise_output.sort_values('timeid')
# final_month_wise_output = final_month_wise_output.sort_values('timeid')


# In[41]:


final_week_wise_output.to_csv('./output/cases-week.csv')


# In[42]:


final_month_wise_output.to_csv('./output/cases-month.csv')


# In[43]:


overall_df.to_csv('./output/cases-overall.csv')

