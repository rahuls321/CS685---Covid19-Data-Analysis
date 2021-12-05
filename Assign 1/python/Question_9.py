
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd
from datetime import timedelta
import Levenshtein
pd.options.mode.chained_assignment = None

'''
# ## Problem statement
# For every state, find the date on which the entire population will get at least one does of vaccination. Assume the same rate of vaccination as in the week ending on 14th Aug, 2021. (Do not treat children separately, and assume the same rate of vaccination.)
# Output them in the following manner: stateid, populationleft, rateofvaccination, date.
'''
# In[3]:


vacc_data1 = pd.read_csv('./data/cowin_vaccine_data_districtwise.csv', low_memory=False)
vacc_data1


# In[4]:


print("Vaccine Data Columns: ", vacc_data1.iloc[0])


# In[5]:

print("Converting columns' data types to int")
vacc_data = vacc_data1.iloc[1:]
vacc_data.fillna(0, inplace=True)
col = list(vacc_data.columns[6:])
vacc_data[col] = vacc_data[col].astype(int)
vacc_data


# In[6]:


distr_data = pd.read_csv('./output/edge-graph.csv', index_col='District_Key')
distr_data.drop(columns=['Unnamed: 0'], inplace=True)
districts_key = list(distr_data.index)
districts_key


# In[7]:


map_dkey_sname, map_dkey_dname = {}, {}
for dt in districts_key:
    map_dkey_sname[dt] = vacc_data[vacc_data['District_Key'] == dt]['State'].iloc[0]
    map_dkey_dname[dt] = vacc_data[vacc_data['District_Key'] == dt]['District'].iloc[0]
map_dkey_dname


# In[8]:


pop_data = pd.read_excel('./data/DDW_PCA0000_2011_Indiastatedist.xlsx')
pop_data = pop_data[['Name', 'Level', 'TRU', 'TOT_P']]
pop_data = pop_data[pop_data['TRU'] == 'Total']
pop_data.drop(columns=['TRU'], inplace=True)
pop_data


# In[9]:


overall_pop_data = pop_data[pop_data['Level'] == 'India']
overall_pop_data


# In[10]:


vacc_data[vacc_data['District_Key'] == 'AP_Anantapur'].iloc[:, :100]


# In[11]:


# This function will find the most similar district word from the given district word in the dataset.
def get_most_similar_word(df, w, name):
    '''
    inputs:
        df : input data containing all the state and districts code i.e DataFrame format
        w : district name
    output:
        output1 : most similar district or state
        output2 : similarity score between two given word input and most similar word
        
    '''
    temp_df = df.copy()
    temp_df = temp_df[1:]
    temp_df['Levenshtein_dist'] = temp_df[name].apply(lambda x: Levenshtein.distance(w, x))
    temp_df = temp_df.sort_values(by=['Levenshtein_dist'])
#     print(temp_df['District'].iloc[0])
    #print("with value: ", temp_df['Levenshtein_dist'].iloc[0])
    return temp_df[name].iloc[0], temp_df['Levenshtein_dist'].iloc[0]


# In[12]:


sdf = pop_data.copy()
sdf = sdf[sdf['Level'] == 'STATE']
is_available = {'DAMAN & DIU':'Dadra and Nagar Haveli and Daman and Diu', 
                'DADRA & NAGAR HAVELI': 'Dadra and Nagar Haveli and Daman and Diu'}
for st in sdf['Name'].unique():
    if st in is_available.keys():
        sdf.loc[sdf['Name'] == st, 'State_Code'] = vacc_data[vacc_data['State'] == is_available[st]]['State_Code'].iloc[0]
    else:
        sm_st, _ = get_most_similar_word(vacc_data, st.title(), 'State')
        sdf.loc[sdf['Name'] == st, 'State_Code'] = vacc_data[vacc_data['State'] == sm_st]['State_Code'].iloc[0]
sdf.drop(columns=['Name', 'Level'], inplace=True)
sdf = sdf.groupby('State_Code').sum()
sdf


# In[13]:


state_wise_pop_data = sdf.copy()
state_wise_pop_data = state_wise_pop_data.reset_index()
state_wise_pop_data


# In[14]:


state_wise = pd.merge(vacc_data, state_wise_pop_data, how ='inner', on =['State_Code'])
state_wise.fillna(0, inplace=True)
state_wise


# In[15]:


ddf = state_wise.copy()
start_date = pd.to_datetime('16/01/2021', format='%d/%m/%Y').date()
end_date = pd.to_datetime('14/08/2021', format='%d/%m/%Y').date()
vacc_col = []
get_original_date=[]
while start_date<=end_date:
    start_date = start_date.strftime('%d/%m/%Y')
    dose1 = str(start_date)+'.3'
    dose2 = str(start_date)+'.4'
    
    #Convert back to datetime format
    start_date = start_date.split('.')[0]
    start_date = pd.to_datetime(start_date, format='%d/%m/%Y').date()
    
    if dose1 not in ddf.columns or dose2 not in ddf.columns:
        print("Date not available: ", start_date)
        continue
    ddf[dose1] = ddf[dose1].astype(int)
    ddf[dose2] = ddf[dose2].astype(int)
    get_original_date.append(start_date.strftime('%d/%m/%Y'))
    vacc_col.append(start_date.strftime('%d/%m/%Y')+'_1')
    vacc_col.append(start_date.strftime('%d/%m/%Y')+'_2')
    ddf[start_date.strftime('%d/%m/%Y')+'_1'] = ddf[dose1] 
    ddf[start_date.strftime('%d/%m/%Y')+'_2'] = ddf[dose2] 
    start_date += timedelta(days=1)


# In[16]:


ddf


# In[17]:


dkey_skey_col = ['State_Code', 'TOT_P']
final_col = dkey_skey_col + vacc_col

final_df = ddf[final_col]
final_df.sort_values('State_Code', inplace=True)
final_df


# In[18]:


def get_statewise_df(state_final_df, st):
    ddf = state_final_df.copy()
    ddf = ddf[ddf['State_Code'] == st]
    ddf = ddf.groupby('State_Code').sum()
    

    d1 = [c for c in ddf.columns[1::2]]
    d2 = [c for c in ddf.columns[2::2]]
    dose1_df = ddf.loc[:, d1]
    dose2_df = ddf.loc[:, d2]
    
    #Vaccination Rate as per last week data
    vacc_rate_per_week = dose1_df.iloc[0][-8:][-1] - dose1_df.iloc[0][-8:][0]

    return dose1_df.iloc[0][-1], dose2_df.iloc[0][-1], vacc_rate_per_week


# In[19]:


state_final_df = final_df.copy()
for st in state_wise_pop_data['State_Code'].unique():
    if st not in state_final_df['State_Code'].unique(): continue
    d1, d2, vacc_rate_per_week = get_statewise_df(state_final_df, st)
    state_wise_pop_data.loc[state_wise_pop_data['State_Code'] == st, 'dose1'] = d1
    state_wise_pop_data.loc[state_wise_pop_data['State_Code'] == st, 'dose2'] = d2
    state_wise_pop_data.loc[state_wise_pop_data['State_Code'] == st, 'rateofvaccination'] = vacc_rate_per_week
state_wise_pop_data = state_wise_pop_data.dropna()
state_wise_pop_data


# In[23]:


st_df = state_wise_pop_data.copy()
st_df = st_df[['State_Code', 'dose1', 'dose2','rateofvaccination', 'TOT_P']]
st_df


# In[27]:


st_df['populationleft'] = st_df['TOT_P'] - st_df['dose1']
st_df['remainingweeks'] = st_df['populationleft']/st_df['rateofvaccination']
st_df['date'] = st_df['remainingweeks'].apply(lambda x: pd.to_datetime('14/08/2021')+timedelta(days=np.round(x)*7) if x>0 else pd.to_datetime('14/08/2021'))
st_df = st_df[['State_Code', 'populationleft', 'rateofvaccination', 'date']]
st_df.rename(columns={'State_Code':'stateid'}, inplace=True)
st_df.set_index('stateid', inplace=True)
state_ratio = st_df.copy()
print("State ratio")
print(state_ratio)


# In[28]:


state_ratio.to_csv('./output/complete-vaccination.csv')

