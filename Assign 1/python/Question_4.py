
# coding: utf-8

# In[66]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
pd.options.mode.chained_assignment = None

'''
# ## Problem Statement
# For every district, state and overall, find the week and month having peak (highest) number of active cases for wave-1 and wave-2. The output file contains columns: districtid, wave1 − weekid, wave2 − weekid, wave1 − monthid, wave2 − monthid.
'''
# In[67]:


#Using previous results to get all the districts which has to be considered for this assignment
week_cases = pd.read_csv('./output/cases-week.csv')
district_keys = list(week_cases['districtid'].unique())
print("Total districts available: ", len(district_keys))


# In[68]:


district_keys


# In[69]:


dt_wise_covid_data = pd.read_csv('./data/districts.csv', parse_dates=['Date'], index_col='Date')
dt_wise_covid_data = dt_wise_covid_data.loc['2020-03-15':'2021-08-14']
dt_wise_covid_data


# In[70]:


distr_wise_data = pd.read_csv('./data/district_wise.csv')
distr_wise_data


# In[71]:


#Mapping all the state with their corresponding keys
map_sname_skey = {}
for state in distr_wise_data['State'].unique():
    map_sname_skey[state] = distr_wise_data[distr_wise_data['State'] == state]['State_Code'].iloc[0]
map_sname_skey

'''
# Since 'districts.csv' contains data from '2020-04-26' onwards. So, I'm including raw data from this api https://data.covid19india.org/ to collect data between 15th March 2020 to 25th April 2020.
'''
# In[72]:


raw_data1 = pd.read_csv('./data/covid-raw-data/raw_data1.csv', parse_dates=['Date Announced'])
raw_data2 = pd.read_csv('./data/covid-raw-data/raw_data2.csv', parse_dates=['Date Announced'])


# In[73]:


raw_data1 = raw_data1.sort_values(by=['Date Announced'])
raw_data1 = raw_data1[(raw_data1['Date Announced'] >= '2020-03-15') & (raw_data1['Date Announced'] < '2020-04-20')]

raw_data2 = raw_data2[raw_data2['Date Announced'] < '2020-04-26']

final_raw_data = pd.concat([raw_data1, raw_data2])
final_raw_data = final_raw_data[["Date Announced", "Detected District", "Detected State", "Num Cases"]]
final_raw_data = final_raw_data.rename(columns={'Date Announced': 'Date', 'Detected District': 'District', 'Detected State':'State','Num Cases':'Active'})
final_raw_data = final_raw_data[['Date', 'State', 'District', 'Active']]

final_raw_data = final_raw_data.groupby(['Date', 'State', 'District']).agg('sum')
final_raw_data = final_raw_data.reset_index()
#final_raw_data = final_raw_data.set_index('Date')
final_raw_data


# In[74]:


df = dt_wise_covid_data.copy()
df = df.reset_index()
df['Active'] = df['Confirmed'] - df['Recovered'] - df['Deceased'] #Active cases = Confirmed - Recovered - Deceased
df.drop(columns=['Confirmed', 'Recovered', 'Deceased', 'Other', 'Tested'], inplace=True)
df


# In[75]:


final_df = pd.concat([final_raw_data, df], sort=True)
final_df = final_df[['Date', 'State', 'District', 'Active']]
final_df

'''
# ### Note
# Considering Active cases as in cumulative form but if you want to consider exact number of cases as active cases you can uncomment below code and re-run the program
'''
# In[76]:


# not_available_distr = []
# for dt_key in district_keys:
#     print(dt_key)
#     get_dt = distr_wise_data[distr_wise_data['District_Key'] == dt_key]
#     original_dt_name = get_dt['District'].iloc[0]
#     original_st_name = get_dt['State'].iloc[0]
#     tt = final_df[(final_df['District'] == original_dt_name) & (final_df['State'] == original_st_name) & (final_df['Date'] > '2020-04-25')]
#     if len(tt)==0:
#         not_available_distr.append(original_dt_name)
#         continue
#     tt['Active'] = tt['Active'].diff().fillna(tt['Active'].iloc[0])
#     final_df.loc[((final_df['District']==original_dt_name) & (final_df['State'] == original_st_name) & (final_df['Date'] > '2020-04-25')), 'Active'] = tt[['Active']]


# In[77]:


districts_availble = distr_wise_data['District_Key'].unique()
for distr_key in districts_availble: 
    temp_df = distr_wise_data[distr_wise_data['District_Key'] == distr_key]
    dt_name = temp_df['District'].iloc[0]
    st_name = temp_df['State'].iloc[0]
    if distr_key not in list(district_keys):
        print("Not avilable in districts_key: ", distr_key)
        idx_list = list(final_df[(final_df['District'] == dt_name) & (final_df['State'] == st_name)].index)
        if len(idx_list) > 0:
            final_df.drop(idx_list, inplace=True)
    else:
        final_df.loc[((final_df['District'] == dt_name) & (final_df['State'] == st_name)), 'District_Key'] = distr_key


# In[78]:


final_df


# In[79]:


final_df = final_df[['Date', 'State', 'District', 'District_Key', 'Active']]
final_df = final_df.set_index('Date')
final_df

'''
# Inorder to find overlapping week, I assigned week1 as odd numer like 1,3,5,etc according to the data mentioned in the problem statement and another week2 as even number like 2,4,6,etc then I merged both week1 & week2
'''
# In[80]:


#Finding Overlapping week
def get_week_or_month_wise_data(wdf, start_date, end_date, timedelay):
    i=1
    wwdf=wdf.copy()
    start_date1 = start_date
    if timedelay==7:
        word='week'
    else: word='month'
    while start_date <= end_date:
        wwdf.loc[((wwdf['Date'] >= start_date) & (wwdf['Date'] < start_date+timedelta(days=timedelay))), word+'1'] = i
        start_date += timedelta(days=timedelay)
        start_date = pd.to_datetime(start_date,format='%d/%m/%Y')
        i+=2
    start_date = start_date1 + timedelta(days=4)
    i=2
    while start_date <= end_date:
        wwdf.loc[((wwdf['Date'] >= start_date) & (wwdf['Date'] < start_date+timedelta(days=timedelay))), word+'2'] = i
        start_date += timedelta(days=timedelay)
        start_date = pd.to_datetime(start_date,format='%d/%m/%Y')
        i+=2
    wwdf = wwdf.set_index('Date')
    return wwdf


# In[81]:


wdf = pd.DataFrame(index = final_df.index)
wdf = wdf.reset_index()
wdf['Date'] = pd.to_datetime(wdf['Date'], format='%d/%m/%Y')

# from datetime import timedelta
start_date = pd.to_datetime('15/03/2020', format='%d/%m/%Y')
end_date = pd.to_datetime('14/08/2021', format='%d/%m/%Y')
mdf = get_week_or_month_wise_data(wdf, start_date, end_date, 30)
wdf = get_week_or_month_wise_data(wdf, start_date, end_date, 7)
wdf


# In[82]:


ddf = final_df.copy()
new_df = pd.concat([ddf, wdf, mdf], axis=1)
new_df = new_df[["State", "District", "District_Key", "week1","week2", "month1", "month2", "Active"]]
new_df.fillna(0, inplace=True)
new_df


# In[83]:


first_week_wise = new_df.groupby(["State", "District", "District_Key", "week1"]).sum()
first_week_wise = first_week_wise.reset_index()
first_week_wise = first_week_wise[["State", "District_Key", "week1", "Active"]]
first_week_wise.rename(columns={"District_Key":"districtid", "week1":"timeid", "Active":"cases"}, inplace=True)

second_week_wise = new_df.groupby(["State", "District", "District_Key", "week2"]).sum()
second_week_wise = second_week_wise.reset_index()
second_week_wise = second_week_wise[["State", "District_Key", "week2", "Active"]]
second_week_wise.rename(columns={"District_Key":"districtid", "week2":"timeid", "Active":"cases"}, inplace=True)

final_week_wise_output = pd.concat([first_week_wise, second_week_wise])
final_week_wise_output = final_week_wise_output.astype({"timeid": int, "cases": int})
final_week_wise_output


# In[84]:


first_month_wise = new_df.groupby(["State", "District", "District_Key", "month1"]).sum()
first_month_wise = first_month_wise.reset_index()
first_month_wise = first_month_wise[["State", "District_Key", "month1", "Active"]]
first_month_wise.rename(columns={"District_Key":"districtid", "month1":"timeid", "Active":"cases"}, inplace=True)

second_month_wise = new_df.groupby(["State", "District", "District_Key", "month2"]).sum()
second_month_wise = second_month_wise.reset_index()
second_month_wise = second_month_wise[["State", "District_Key", "month2", "Active"]]
second_month_wise.rename(columns={"District_Key":"districtid", "month2":"timeid", "Active":"cases"}, inplace=True)

final_month_wise_output = pd.concat([first_month_wise, second_month_wise])
final_month_wise_output = final_month_wise_output.astype({"timeid": int, "cases": int})
final_month_wise_output


# In[85]:


overall_first_week_wise = new_df.groupby(["week1"]).sum()
overall_first_week_wise = overall_first_week_wise.reset_index()
overall_first_week_wise = overall_first_week_wise[["week1", "Active"]]
overall_first_week_wise.rename(columns={"week1":"timeid", "Active":"cases"}, inplace=True)

overall_second_week_wise = new_df.groupby(["week2"]).sum()
overall_second_week_wise = overall_second_week_wise.reset_index()
overall_second_week_wise = overall_second_week_wise[["week2", "Active"]]
overall_second_week_wise.rename(columns={"week2":"timeid", "Active":"cases"}, inplace=True)

overall_week_wise_output = pd.concat([overall_first_week_wise, overall_second_week_wise])
overall_week_wise_output = overall_week_wise_output.astype({"timeid": int, "cases": int})
overall_week_wise_output = overall_week_wise_output.sort_values('timeid')
overall_week_wise_output = overall_week_wise_output.set_index('timeid')
overall_week_wise_output


# In[86]:


overall_first_month_wise = new_df.groupby(["month1"]).sum()
overall_first_month_wise = overall_first_month_wise.reset_index()
overall_first_month_wise = overall_first_month_wise[["month1", "Active"]]
overall_first_month_wise.rename(columns={"month1":"timeid", "Active":"cases"}, inplace=True)

overall_second_month_wise = new_df.groupby(["month2"]).sum()
overall_second_month_wise = overall_second_month_wise.reset_index()
overall_second_month_wise = overall_second_month_wise[["month2", "Active"]]
overall_second_month_wise.rename(columns={"month2":"timeid", "Active":"cases"}, inplace=True)

overall_month_wise_output = pd.concat([overall_first_month_wise, overall_second_month_wise])
overall_month_wise_output = overall_month_wise_output.astype({"timeid": int, "cases": int})
overall_month_wise_output = overall_month_wise_output.sort_values('timeid')
overall_month_wise_output = overall_month_wise_output.set_index('timeid')
overall_month_wise_output


# In[87]:


week_cases = final_week_wise_output.copy()
month_cases = final_month_wise_output.copy()
overall_week_cases = overall_week_wise_output.copy()
overall_month_cases = overall_month_wise_output.copy()


# In[88]:


plt.plot(overall_week_cases.index, overall_week_cases['cases'])
plt.plot(overall_week_cases.index)
plt.xlabel('timeid')
plt.ylabel('cases')
plt.title('Weekly Covid Cases Analysis')
plt.savefig('./output/weekly_peaks.jpg')
plt.close()


# In[89]:


plt.plot(overall_month_cases.index, overall_month_cases['cases'])
plt.plot(overall_month_cases.index)
plt.xlabel('timeid')
plt.ylabel('cases')
plt.title('Monthly Covid Cases Analysis')
plt.savefig('./output/monthly_peaks.jpg')

# In[90]:


# plt.plot(month_cases1.groupby('timeid').sum())
# plt.xlabel('timeid')
# plt.ylabel('cases')
# plt.title('Monthly Covid Cases Analysis')


# In[91]:


# plt.figure(figsize=(20,10))
# plt.hist(overall_cases['cases'],  density=True, bins=30)
# plt.xlabel('timeid')
# plt.ylabel('cases')
# plt.xticks(rotation=90)
# plt.title('Overall Analysis Covid Cases District-Wise')

'''
# From the above two graph which is saved in output folder, we can easily say between two waves the timeid cutoff is in between 80 to 100 for weekly cases and in between 22 to 25 for monthly cases. Based on these cutoffs we'll calculate the exact timeid of the peaks.
'''
# In[92]:


#Choosing these cutoffs based on the above ranges
weekly_cutoff=90
monthly_cutoff=24


# In[93]:


peak1_dict, peak2_dict={}, {}
peak1_st_dict, peak2_st_dict={}, {}
for dt in district_keys:
    print(dt)
    df = week_cases[week_cases['districtid'] == dt]
    st = df['State'].iloc[0]
    st_df = week_cases[week_cases['State'] == st]
    
    wave1_df = df[df['timeid'] <= weekly_cutoff]
    max_wave1_cases = max(wave1_df['cases'])
    peak1 = wave1_df[wave1_df['cases'] == max_wave1_cases]
    peak1_dict[dt] = peak1['timeid'].iloc[0]
    
    wave1_st_df = st_df[st_df['timeid'] <= weekly_cutoff]
    max_wave1_st_cases = max(wave1_st_df['cases'])
    peak1_st = wave1_st_df[wave1_st_df['cases'] == max_wave1_st_cases]
    peak1_st_dict[st] = peak1_st['timeid'].iloc[0]
    
    wave2_df = df[df['timeid'] > weekly_cutoff]
    wave2_st_df = st_df[st_df['timeid'] > weekly_cutoff]
    
    if len(wave2_df) == 0:
        print("Second Wave not found in district: ", dt)
        continue
    if len(wave2_st_df) == 0:
        print("Second Wave not found in state: ", df['State'].iloc[0])
        continue
    max_wave2_cases = max(wave2_df['cases'])
    peak2 = wave2_df[wave2_df['cases'] == max_wave2_cases]
    peak2_dict[dt] = peak2['timeid'].iloc[0]
    
    max_wave2_st_cases = max(wave2_st_df['cases'])
    peak2_st = wave2_st_df[wave2_st_df['cases'] == max_wave2_st_cases]
    peak2_st_dict[st] = peak2_st['timeid'].iloc[0]


# In[94]:


weekly_peaks = pd.DataFrame({"districtid": [], "wave1 − weekid": [], "wave2 − weekid":[]})
weekly_peaks["districtid"] = district_keys
weekly_peaks["wave1 − weekid"] = list(peak1_dict.values())
weekly_peaks["wave2 − weekid"] = weekly_peaks['districtid'].apply(lambda x: peak2_dict[x] if x in peak2_dict.keys() else '')
weekly_peaks = weekly_peaks.set_index('districtid')
weekly_peaks

st_weekly_peaks = pd.DataFrame({"state": [], "wave1 − weekid": [], "wave2 − weekid":[]})
st_weekly_peaks["state"] = list(peak1_st_dict.keys())
st_weekly_peaks["wave1 − weekid"] = list(peak1_st_dict.values())
st_weekly_peaks["wave2 − weekid"] = st_weekly_peaks['state'].apply(lambda x: peak2_st_dict[x] if x in peak2_st_dict.keys() else '')
st_weekly_peaks = st_weekly_peaks.set_index('state')
st_weekly_peaks


# In[95]:


mpeak1_dict, mpeak2_dict={}, {}
mpeak1_st_dict, mpeak2_st_dict={}, {}
for dt in district_keys:
    df = month_cases[month_cases['districtid'] == dt]
    st = df['State'].iloc[0]
    st_df = month_cases[month_cases['State'] == st]
    
    wave1_df = df[df['timeid'] <= monthly_cutoff]
    max_wave1_cases = max(wave1_df['cases'])
    peak1 = wave1_df[wave1_df['cases'] == max_wave1_cases]
    mpeak1_dict[dt] = peak1['timeid'].iloc[0]
    
    wave1_st_df = st_df[st_df['timeid'] <= monthly_cutoff]
    max_wave1_st_cases = max(wave1_st_df['cases'])
    peak1_st = wave1_st_df[wave1_st_df['cases'] == max_wave1_st_cases]
    mpeak1_st_dict[st] = peak1_st['timeid'].iloc[0]
    
    wave2_df = df[df['timeid'] > monthly_cutoff]
    wave2_st_df = st_df[st_df['timeid'] > monthly_cutoff]
    if len(wave2_df) == 0:
        print("Second Wave not found in district: ", dt)
        continue
    if len(wave2_st_df) == 0:
        print("Second Wave not found in state: ", st)
        continue
    max_wave2_cases = max(wave2_df['cases'])
    peak2 = wave2_df[wave2_df['cases'] == max_wave2_cases]
    mpeak2_dict[dt] = peak2['timeid'].iloc[0]
    
    max_wave2_st_cases = max(wave2_st_df['cases'])
    peak2_st = wave2_st_df[wave2_st_df['cases'] == max_wave2_st_cases]
    mpeak2_st_dict[st] = peak2_st['timeid'].iloc[0]


# In[96]:


overall_wave1_df = overall_week_cases[overall_week_cases.index <= weekly_cutoff]
max_overall_wave1_cases = max(overall_wave1_df['cases'])
overall_week_peak1 = overall_wave1_df[overall_wave1_df['cases'] == max_overall_wave1_cases]

overall_wave2_df = overall_week_cases[overall_week_cases.index > weekly_cutoff]
max_overall_wave2_cases = max(overall_wave2_df['cases'])
overall_week_peak2 = overall_wave2_df[overall_wave2_df['cases'] == max_overall_wave2_cases]

overall_wave1_df = overall_month_cases[overall_month_cases.index <= monthly_cutoff]
max_overall_wave1_cases = max(overall_wave1_df['cases'])
overall_month_peak1 = overall_wave1_df[overall_wave1_df['cases'] == max_overall_wave1_cases]

overall_wave2_df = overall_month_cases[overall_month_cases.index > monthly_cutoff]
max_overall_wave2_cases = max(overall_wave2_df['cases'])
overall_month_peak2 = overall_wave2_df[overall_wave2_df['cases'] == max_overall_wave2_cases]

overall_peaks = pd.DataFrame({"id":["India"], "wave1 - weekid": overall_week_peak1.index.values, "wave2 - weekid": overall_week_peak2.index.values, 
                              "wave1 - monthid": overall_month_peak1.index.values,  "wave2 - monthid": overall_month_peak2.index.values})
overall_peaks = overall_peaks[['id', 'wave1 - weekid', 'wave2 - weekid', 'wave1 - monthid', 'wave2 - monthid']]
overall_peaks = overall_peaks.set_index('id')
overall_peaks


# In[97]:


monthly_peaks = pd.DataFrame({"districtid": [], "wave1 − monthid": [], "wave2 − monthid":[]})
monthly_peaks["districtid"] = district_keys
monthly_peaks["wave1 − monthid"] = list(mpeak1_dict.values())
monthly_peaks["wave2 − monthid"] = monthly_peaks['districtid'].apply(lambda x: mpeak2_dict[x] if x in mpeak2_dict.keys() else '')
monthly_peaks = monthly_peaks.set_index('districtid')
monthly_peaks

st_monthly_peaks = pd.DataFrame({"state": [], "wave1 − monthid": [], "wave2 − monthid":[]})
st_monthly_peaks["state"] = list(mpeak1_st_dict.keys())
st_monthly_peaks["wave1 − monthid"] = list(mpeak1_st_dict.values())
st_monthly_peaks["wave2 − monthid"] = st_monthly_peaks['state'].apply(lambda x: mpeak2_st_dict[x] if x in mpeak2_st_dict.keys() else '')
st_monthly_peaks = st_monthly_peaks.set_index('state')
st_monthly_peaks


# In[98]:


final_peaks_data = pd.concat([weekly_peaks, monthly_peaks], axis=1)
final_peaks_data


# In[99]:


st_final_peaks_data = pd.concat([st_weekly_peaks, st_monthly_peaks], axis=1)
st_final_peaks_data = st_final_peaks_data.reset_index()
st_final_peaks_data['stateid'] = st_final_peaks_data['state'].apply(lambda x: map_sname_skey[x])
st_final_peaks_data.drop(columns=['state'], inplace=True)
st_final_peaks_data = st_final_peaks_data.set_index('stateid')
st_final_peaks_data


# In[100]:


final_peaks_data = final_peaks_data.sort_index()
st_final_peaks_data = st_final_peaks_data.sort_index()


# In[101]:


final_peaks_data.to_csv('./output/district-peaks.csv')


# In[102]:


st_final_peaks_data.to_csv('./output/state-peaks.csv')


# In[103]:


overall_peaks.to_csv('./output/overall-peaks.csv')

