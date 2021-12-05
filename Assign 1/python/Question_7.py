
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from datetime import timedelta
pd.options.mode.chained_assignment = None

'''
# ## Problem statement
# For each state, district and overall, find the following ratios: total number of Covishield vaccinated persons (either 1 or 2 doses) to total number of Covaxin vaccinated persons (same).
# Output them in the following manner: districtid, vaccineratio.
'''
# In[2]:


vacc_data1 = pd.read_csv('./data/cowin_vaccine_data_districtwise.csv', low_memory=False)
vacc_data1


# In[3]:

print("Vaccine Data Columns: ", vacc_data1.iloc[0])


# In[4]:

print("Converting columns' data types to int")
vacc_data = vacc_data1.iloc[1:]
vacc_data.fillna(0, inplace=True)
col = list(vacc_data.columns[6:])
vacc_data[col] = vacc_data[col].astype(int)
vacc_data


# In[5]:


distr_data = pd.read_csv('./output/edge-graph.csv', index_col='District_Key')
distr_data.drop(columns=['Unnamed: 0'], inplace=True)
districts_key = list(distr_data.index)
districts_key


# In[6]:


distr_df = pd.DataFrame({"District_Key":districts_key})
distr_df


# In[7]:


df = pd.merge(vacc_data, distr_df, how ='inner', on =['District_Key'])
df.fillna(0, inplace=True)
df


# In[8]:


start_date = pd.to_datetime('16/01/2021', format='%d/%m/%Y').date()
end_date = pd.to_datetime('14/08/2021', format='%d/%m/%Y').date()
vacc_col = []
get_original_date=[]
while start_date<=end_date:
    start_date = start_date.strftime('%d/%m/%Y')
    cx_dt = str(start_date)+'.8'
    cs_dt = str(start_date)+'.9'
    
    #Convert back to datetime format
    start_date = start_date.split('.')[0]
    start_date = pd.to_datetime(start_date, format='%d/%m/%Y').date()
    
    if cx_dt not in df.columns or cs_dt not in df.columns:
        print("Date not available: ", start_date)
        continue
    df[cx_dt] = df[cx_dt].astype(int)
    df[cs_dt] = df[cs_dt].astype(int)
    get_original_date.append(start_date.strftime('%d/%m/%Y'))
    vacc_col.append(start_date.strftime('%d/%m/%Y')+'_cx')
    vacc_col.append(start_date.strftime('%d/%m/%Y')+'_cs')
    df[start_date.strftime('%d/%m/%Y')+'_cx'] = df[cx_dt] 
    df[start_date.strftime('%d/%m/%Y')+'_cs'] = df[cs_dt]
    start_date += timedelta(days=1)


# In[9]:


dkey_skey_col = ['State_Code', 'District_Key']
final_col = dkey_skey_col + vacc_col

final_df = df[final_col]
final_df.sort_values('District_Key', inplace=True)
final_df


# In[10]:


def get_districtwise_df(final_df, dt):
    ddf = final_df.copy()
    ddf = ddf[ddf['District_Key'] == dt]

    d1 = [c for c in ddf.columns[2::2]]
    d2 = [c for c in ddf.columns[3::2]]
    covaxin_df = ddf.loc[:, d1]
    covishield_df = ddf.loc[:, d2]
    
    return covaxin_df.iloc[0][-1], covishield_df.iloc[0][-1]

def get_statewise_df(state_final_df, st):
    ddf = state_final_df.copy()
    ddf = ddf[ddf['State_Code'] == st]
    ddf = ddf.groupby('State_Code').sum()

    d1 = [c for c in ddf.columns[::2]]
    d2 = [c for c in ddf.columns[1::2]]
    covaxin_df = ddf.loc[:, d1]
    covishield_df = ddf.loc[:, d2]
    
    return covaxin_df.iloc[0][-1], covishield_df.iloc[0][-1]


# In[11]:


dt_df = final_df.copy()
for dt in dt_df['District_Key'].unique():
    print(dt)
    cx, cs = get_districtwise_df(final_df, dt)
    dt_df.loc[dt_df['District_Key'] == dt, 'Covaxin'] = cx
    dt_df.loc[dt_df['District_Key'] == dt, 'Covishield'] = cs


# In[12]:


st_df = pd.DataFrame()
for st in final_df['State_Code'].unique():
    cx, cs = get_statewise_df(final_df, st)
    st_df.loc[st, 'Covaxin'] = cx
    st_df.loc[st, 'Covishield'] = cs
st_df


# In[13]:


overall_df = pd.DataFrame()
overall_df.loc['india', 'Covaxin'] = st_df['Covaxin'].sum()
overall_df.loc['india', 'Covishield'] = st_df['Covishield'].sum()
overall_df


# In[14]:


district_wise = dt_df.copy()
district_wise = district_wise[['District_Key', 'Covaxin', 'Covishield']]
district_wise


# In[15]:


state_wise = st_df.copy()
state_wise.index.name = 'State_Code'
state_wise = state_wise.reset_index()
state_wise


# In[16]:


district_wise['vaccinationratio'] = district_wise['Covishield']/district_wise['Covaxin']
district_wise['vaccinationratio'] = district_wise['vaccinationratio'].apply(lambda x: np.nan if x == np.inf else x)
district_wise = district_wise[['District_Key', 'vaccinationratio']]
district_wise.rename(columns={'District_Key':'districtid'}, inplace=True)
district_wise = district_wise.sort_values('vaccinationratio')
district_wise = district_wise.set_index('districtid')
district_ratio = district_wise.copy()
print("Disrict ratio")
print(district_ratio)


# In[17]:


state_wise['vaccinationratio'] = state_wise['Covishield']/state_wise['Covaxin']
state_wise['vaccinationratio'] = state_wise['vaccinationratio'].apply(lambda x: np.nan if x == np.inf else x)
state_wise = state_wise[['State_Code', 'vaccinationratio']]
state_wise.rename(columns={'State_Code':'stateid'}, inplace=True)
state_wise = state_wise.sort_values('vaccinationratio')
state_wise = state_wise.set_index('stateid')
state_ratio = state_wise.copy()
print("State ratio")
print(state_ratio)


# In[18]:


overall_ddf = overall_df.copy()
overall_ddf['vaccinationratio'] = overall_ddf['Covishield']/overall_ddf['Covaxin']
overall_ddf = overall_ddf[['vaccinationratio']]
overall_ddf.index.name = 'id'
overall_ratio = overall_ddf.copy()
print("Overall ratio")
print(overall_ratio)


# In[19]:


district_ratio.to_csv('./output/district-vaccine-type-ratio.csv')


# In[20]:


state_ratio.to_csv('./output/state-vaccine-type-ratio.csv')


# In[21]:


overall_ratio.to_csv('./output/overall-vaccine-type-ratio.csv')

