
# coding: utf-8

# In[29]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
pd.options.mode.chained_assignment = None

'''
# ## Problem statement
# Find the number of people vaccinated with 1 or 2 doses of any vaccine, and sort the output file with district id and state id. Output this for all districts and all states weekly, monthly and overall in the following manner: districtid, timeid, dose1, dose2.
'''
# In[30]:


vacc_data = pd.read_csv('./data/cowin_vaccine_data_districtwise.csv', low_memory=False)
vacc_data


# In[31]:


distr_data = pd.read_csv('./output/edge-graph.csv', index_col='District_Key')
distr_data.drop(columns=['Unnamed: 0'], inplace=True)
districts_key = list(distr_data.index)
districts_key


# In[32]:


map_dkey_sname = {}
for dt in districts_key:
    map_dkey_sname[dt] = vacc_data[vacc_data['District_Key'] == dt]['State_Code'].iloc[0]
# map_dkey_sname


# In[33]:


#Creaing a dataFrame of the all the districts considering for this assignment 
districts_key_df = pd.DataFrame({'District_Key': districts_key})
districts_key_df


# In[34]:


vacc_col = vacc_data.iloc[0]
vacc_col

'''
# These columns are there in cowin data. For dose 1 and dose 2 we'll consider xxx.3 and xxx.4 respectively where xxx is date.
'''
# In[35]:


df = pd.merge(vacc_data, districts_key_df, how ='inner', on =['District_Key'])
df.fillna(0, inplace=True)
df


# In[36]:

print('Converting cases columns types to int')
col = list(df.columns[6:])
df[col] = df[col].astype(int)
df

'''
# Few Districts in CoWin data has been repeated, merging them into one. For example, for Ahmedabad and Ahmedabad corporation, merged into Ahmedabad.
'''

# In[37]:

print('Merging duplicate rows')
df = df.groupby(['State_Code', 'State', 'District_Key', 'District'])[col].sum()
df = df.reset_index()
df


# In[38]:


start_date = pd.to_datetime('16/01/2021', format='%d/%m/%Y').date()
end_date = pd.to_datetime('14/08/2021', format='%d/%m/%Y').date()
vacc_col = []
get_original_date=[]
while start_date<=end_date:
    start_date = start_date.strftime('%d/%m/%Y')
    first_dose_dt = str(start_date)+'.3'
    second_dose_dt = str(start_date)+'.4'
    
    #Convert back to datetime format
    start_date = start_date.split('.')[0]
    start_date = pd.to_datetime(start_date, format='%d/%m/%Y').date()
    
    if first_dose_dt not in df.columns or second_dose_dt not in df.columns:
        print("Date not available: ", start_date)
        continue
    df[first_dose_dt] = df[first_dose_dt].astype(int)
    df[second_dose_dt] = df[second_dose_dt].astype(int)
    get_original_date.append(start_date.strftime('%d/%m/%Y'))
    vacc_col.append(start_date.strftime('%d/%m/%Y')+'_1')
    vacc_col.append(start_date.strftime('%d/%m/%Y')+'_2')
    df[start_date.strftime('%d/%m/%Y')+'_1'] = df[first_dose_dt] 
    df[start_date.strftime('%d/%m/%Y')+'_2'] = df[second_dose_dt]
    start_date += timedelta(days=1)


# In[39]:


df


# In[40]:


df.columns


# In[41]:


dkey_skey_col = ['State_Code', 'District_Key']
final_col = dkey_skey_col + vacc_col

final_df = df[final_col]
final_df.sort_values('District_Key', inplace=True)
final_df


# In[42]:


final_df[final_df['District_Key'] == 'GJ_Ahmedabad']


# In[43]:


add_prev_date=[]
i=1
st_date = pd.to_datetime('15/03/2020', format='%d/%m/%Y')
end_date = pd.to_datetime(get_original_date[0], format='%d/%m/%Y')

while st_date < end_date:
    add_prev_date.append(st_date.strftime('%d/%m/%Y'))
    st_date = st_date + timedelta(days=1)
    st_date = pd.to_datetime(st_date, format='%d/%m/%Y')
    i+=1
add_prev_date += get_original_date


# In[44]:


wdf = pd.DataFrame({'Date': add_prev_date})
wdf['Date'] = pd.to_datetime(wdf['Date'], format='%d/%m/%Y')

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


# In[45]:


# from datetime import timedelta
start_date = pd.to_datetime('15/03/2020', format='%d/%m/%Y')
end_date = pd.to_datetime('14/08/2021', format='%d/%m/%Y')
mdf = get_week_or_month_wise_data(wdf, start_date, end_date, 30)
wdf = get_week_or_month_wise_data(wdf, start_date, end_date, 7)
wdf = wdf.reset_index()
mdf = mdf.reset_index()
# wdf = wdf[wdf['Date'] >= '2021-01-16']
# mdf = mdf[mdf['Date'] >= '2021-01-16']
wdf = wdf.set_index('Date')
mdf = mdf.set_index('Date')
wdf


# In[46]:


# ddf = final_df.copy()
# new_df = pd.concat([ddf, wdf, mdf], axis=1)
# new_df = new_df[["State", "District", "District_Key", "week1", "week2", "month1", "month2", "Confirmed"]]
# new_df


# In[47]:


wdf.index


# In[48]:


wdf


# In[49]:


def get_districtwise_df(ddf,wdf,mdf, dt):
    
    ddf = ddf[ddf['District_Key'] == dt]
    
    d1 = [c for c in ddf.columns[2::2]]
    d2 = [c for c in ddf.columns[3::2]]
    dose1_df = ddf.loc[:, d1]
    dose2_df = ddf.loc[:, d2]
    new_dose1_col = [s.split('_')[0] for s in dose1_df.columns]
    new_dose2_col = [s.split('_')[0] for s in dose2_df.columns]
    
    dose1_df.columns = new_dose1_col
    dose2_df.columns = new_dose2_col
    
    dose1_df = pd.DataFrame({"dose1" : dose1_df.iloc[0]})
    dose2_df = pd.DataFrame({"dose2" : dose2_df.iloc[0]})
    
    dose1_df['dose1'] = dose1_df['dose1'].diff().fillna(dose1_df['dose1'].iloc[0])
    dose2_df['dose2'] = dose2_df['dose2'].diff().fillna(dose2_df['dose2'].iloc[0])
    
    dose_data = pd.concat([dose1_df, dose2_df], axis=1)

    dose_data = dose_data.reset_index()
    dose_data.rename(columns={"index": "Date"}, inplace=True)

    dose_data['Date'] = pd.to_datetime(dose_data['Date'], format='%d/%m/%Y')
    dose_data = dose_data.set_index('Date')
    dose_data['dose1'] = dose_data['dose1'].astype(int)
    
    
    new_ddf = pd.concat([dose_data, wdf, mdf], axis=1)
    new_df = new_ddf[["week", "month", "dose1", "dose2"]]
    new_df.fillna(0, inplace=True)
    return new_df


# In[50]:


weekly_vaccination = pd.DataFrame({"districtid":[], "timeid":[], "dose1":[], "dose2":[]})
monthly_vaccination = pd.DataFrame({"districtid":[], "timeid":[], "dose1":[], "dose2":[]})
overall_vaccination = pd.DataFrame({"districtid":[], "dose1":[], "dose2":[]})

for dt in districts_key:
    print("District: ", dt)
    ddf = final_df.copy()
    new_df = get_districtwise_df(ddf,wdf,mdf, dt)
    
    final_week_wise_output = new_df.groupby(["week"]).sum()
    final_week_wise_output = final_week_wise_output.reset_index()
    final_week_wise_output = final_week_wise_output[["week", "dose1", "dose2"]]
    final_week_wise_output.rename(columns={"week":"timeid"}, inplace=True)

    final_week_wise_output = final_week_wise_output.astype({"timeid": int, "dose1": int, "dose2":int})
    
    final_week_wise_output['districtid'] = dt
    weekly_vaccination = weekly_vaccination.append(final_week_wise_output, sort=True)
    
    final_month_wise_output = new_df.groupby(["month"]).sum()
    final_month_wise_output = final_month_wise_output.reset_index()
    final_month_wise_output = final_month_wise_output[["month", "dose1", "dose2"]]
    final_month_wise_output.rename(columns={"month":"timeid"}, inplace=True)

    final_month_wise_output = final_month_wise_output.astype({"timeid": int, "dose1": int, "dose2":int})
    
    final_month_wise_output['districtid'] = dt
    monthly_vaccination = monthly_vaccination.append(final_month_wise_output, sort=True)
    
    overall_vaccination = overall_vaccination.append({"districtid":dt, "dose1":new_df['dose1'].sum(), "dose2":new_df['dose2'].sum()}, ignore_index = True)


# In[51]:


weekly_vaccination = weekly_vaccination[["districtid", "timeid", "dose1", "dose2"]]
weekly_vaccination = weekly_vaccination.sort_values(['districtid', 'timeid'])
weekly_vaccination = weekly_vaccination.set_index('districtid')
weekly_vaccination = weekly_vaccination.astype({"dose1":int, "dose2":int})
print('weekly_vaccination')
print(weekly_vaccination)


# In[52]:


monthly_vaccination = monthly_vaccination[["districtid", "timeid", "dose1", "dose2"]]
monthly_vaccination = monthly_vaccination.sort_values(['districtid', 'timeid'])
monthly_vaccination = monthly_vaccination.set_index('districtid')
monthly_vaccination = monthly_vaccination.astype({"dose1":int, "dose2":int})
print('monthly_vaccination')
print(monthly_vaccination)


# In[53]:


overall_vaccination = overall_vaccination.set_index('districtid')
overall_vaccination = overall_vaccination.astype({"dose1":int, "dose2":int})
print('overall_vaccination')
print(overall_vaccination)


# In[54]:


weekly_vaccination_st_wise = weekly_vaccination.copy()
weekly_vaccination_st_wise = weekly_vaccination_st_wise.reset_index()
weekly_vaccination_st_wise['stateid'] = weekly_vaccination_st_wise['districtid'].apply(lambda x: map_dkey_sname[x])
weekly_vaccination_st_wise = weekly_vaccination_st_wise[['stateid','timeid', 'dose1', 'dose2']]
weekly_vaccination_st_wise = weekly_vaccination_st_wise.groupby(['stateid', 'timeid']).sum()
weekly_vaccination_st_wise = weekly_vaccination_st_wise.reset_index()
print('weekly_vaccination_st_wise')
print(weekly_vaccination_st_wise)



# In[55]:


monthly_vaccination_st_wise = monthly_vaccination.copy()
monthly_vaccination_st_wise = monthly_vaccination_st_wise.reset_index()
monthly_vaccination_st_wise['stateid'] = monthly_vaccination_st_wise['districtid'].apply(lambda x: map_dkey_sname[x])
monthly_vaccination_st_wise = monthly_vaccination_st_wise[['stateid','timeid', 'dose1', 'dose2']]
monthly_vaccination_st_wise = monthly_vaccination_st_wise.groupby(['stateid', 'timeid']).sum()
monthly_vaccination_st_wise = monthly_vaccination_st_wise.reset_index()
print('monthly_vaccination_st_wise')
print(monthly_vaccination_st_wise)


# In[56]:


overall_vaccination_st_wise = overall_vaccination.copy()
overall_vaccination_st_wise = overall_vaccination_st_wise.reset_index()
overall_vaccination_st_wise['stateid'] = overall_vaccination_st_wise['districtid'].apply(lambda x: map_dkey_sname[x])
overall_vaccination_st_wise = overall_vaccination_st_wise[['stateid', 'dose1', 'dose2']]
overall_vaccination_st_wise = overall_vaccination_st_wise.groupby(['stateid']).sum()
overall_vaccination_st_wise = overall_vaccination_st_wise.reset_index()
print('overall_vaccination_st_wise')
print(overall_vaccination_st_wise)


# In[57]:


weekly_vaccination.to_csv('./output/district-vaccinated-count-week.csv')
monthly_vaccination.to_csv('./output/district-vaccinated-count-month.csv')
overall_vaccination.to_csv('./output/district-vaccinated-count-overall.csv')

weekly_vaccination_st_wise.to_csv('./output/state-vaccinated-count-week.csv')
monthly_vaccination_st_wise.to_csv('./output/state-vaccinated-count-month.csv')
overall_vaccination_st_wise.to_csv('./output/state-vaccinated-count-overall.csv')

