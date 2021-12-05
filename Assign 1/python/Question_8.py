
# coding: utf-8

# In[32]:


import numpy as np
import pandas as pd
from datetime import timedelta
import Levenshtein
pd.options.mode.chained_assignment = None

'''
# ## Problem statement
# For each state, district and overall, find the following ratio: total number of persons vaccinated (both 1 and 2 doses) to total population. (If a district is absent in 2011 census, drop it from analysis.)
# Output them in the following manner: districtid, vaccinateddose1ratio, vaccinateddose2ratio.
'''
# In[33]:


vacc_data1 = pd.read_csv('./data/cowin_vaccine_data_districtwise.csv', low_memory=False)
vacc_data1


# In[34]:


print("Vaccine Data Columns: ", vacc_data1.iloc[0])


# In[35]:

print("Converting columns' data types to int")
vacc_data = vacc_data1.iloc[1:]
vacc_data.fillna(0, inplace=True)
col = list(vacc_data.columns[6:])
vacc_data[col] = vacc_data[col].astype(int)
vacc_data


# In[36]:


distr_data = pd.read_csv('./output/edge-graph.csv', index_col='District_Key')
distr_data.drop(columns=['Unnamed: 0'], inplace=True)
districts_key = list(distr_data.index)
districts_key


# In[37]:


map_dkey_sname, map_dkey_dname = {}, {}
for dt in districts_key:
    map_dkey_sname[dt] = vacc_data[vacc_data['District_Key'] == dt]['State'].iloc[0]
    map_dkey_dname[dt] = vacc_data[vacc_data['District_Key'] == dt]['District'].iloc[0]
map_dkey_dname


# In[38]:


pop_data = pd.read_excel('./data/DDW_PCA0000_2011_Indiastatedist.xlsx')
pop_data = pop_data[['Name', 'Level', 'TRU', 'TOT_P']]
pop_data = pop_data[pop_data['TRU'] == 'Total']
pop_data.drop(columns=['TRU'], inplace=True)
pop_data


# In[39]:


overall_pop_data = pop_data[pop_data['Level'] == 'India']
overall_pop_data


# In[40]:


vacc_data[vacc_data['District_Key'] == 'AP_Anantapur'].iloc[:, :100]


# In[41]:


# This function will find the most similar district word from the given district word in the dataset.
def get_most_similar_word(df, w, name):
    '''
    inputs:
        df : input data containing all the state and districts code i.e DataFrame format
        w : district name
    output:
        output1 : most similar district
        output2 : similarity score between two given word input and most similar word
        
    '''
    temp_df = df.copy()
    temp_df = temp_df[1:]
    temp_df['Levenshtein_dist'] = temp_df[name].apply(lambda x: Levenshtein.distance(w, x))
    temp_df = temp_df.sort_values(by=['Levenshtein_dist'])
#     print(temp_df['District'].iloc[0])
    #print("with value: ", temp_df['Levenshtein_dist'].iloc[0])
    return temp_df[name].iloc[0], temp_df['Levenshtein_dist'].iloc[0]


# In[42]:


def find_correct_match(distr):
    '''
    inputs:
        distr : district name for finding correct match if  Levenshtein_distance doesn't work
    output:
        output1 : correct match if available otherwise return empty string
        
    '''
    correct_match = {'Belgaum': 'Belagavi', 'Leh(Ladakh)':'Leh', 'Gurgaon':'Gurugram', 'Baleshwar': 'Balasore', 'Rangareddy': 'Ranga Reddy', 'Hugli':'Hooghly', 'Sahibzada Ajit Singh Nagar': 'S.A.S. Nagar', 
                 'Sant Ravidas Nagar':'Bhadohi','Faizabad':'Ayodhya', 'Muktsar': 'Sri Muktsar Sahib', 'Pashchim Champaran':'West Champaran','Pashchimi Singhbhum': 'West Singhbhum',
                'Bid': 'Beed', 'East Karbi Anglong':'Karbi Anglong', 'The Dangs':'Dang', 'Dantewada':'Dakshin Bastar Dantewada','Purbi Singhbhum':'East Singhbhum', 'Warangal':'Warangal Urban',
                'Jyotiba Phule Nagar': 'Amroha', 'Allahabad ':'Prayagraj', 'Khandwa (East Nimar)':'Khandwa', 'Dohad':'Dahod', 'Kachchh':'Kutch', 'Kheri':'Lakhimpur Kheri', 'Kaimur (Bhabua)':'Kaimur', 
                'Y.S.R.':'Y.S.R. Kadapa', "Sant Ravidas Nagar (Bhadohi)": "Bhadohi", 'Gulbarga':'Kalaburagi', 'Shimoga':'Shivamogga', 'Bangalore':'Bengaluru Urban'}
    if distr in correct_match.keys():
        return correct_match[distr]
    return ''


# In[43]:


def not_included_district(dt):
    not_included = ['Mewat ', 'North West', 'North', 'North East', 'East', 
                    'Central', 'West', 'South West', 'South',
                    'Kanshiram Nagar', 'North  District','West District', 'Barddhaman ',
                    'South District', 'East District', 'Mumbai Suburban', 'Mahamaya Nagar']
    
    if dt not in not_included: return True
    return False


# In[44]:


df = pop_data.copy()
df = df[df['Level'] == 'DISTRICT']
map_dt_cor_dt={}
map_dname_dkey={}
for dt in df['Name'].unique():
    if not not_included_district(dt): 
        print("Not including this district: ", dt)
        continue
    if dt not in map_dkey_dname.values():
        sm_dt, score = get_most_similar_word(vacc_data, dt, 'District')
        cor_match_dt = find_correct_match(dt)
        if len(cor_match_dt)>0:
            sm_dt = cor_match_dt
            map_dt_cor_dt[dt] = sm_dt
            map_dname_dkey[dt] = vacc_data[vacc_data['District'] == sm_dt]['District_Key'].iloc[0]
            print("District available: ", dt)
            print("Correct Matched found with: ", cor_match_dt)
        elif sm_dt in map_dkey_dname.values():
            print("District available: ", dt)
            print("Correct Matched with: ", sm_dt)
            map_dt_cor_dt[dt] = sm_dt
            map_dname_dkey[dt] = vacc_data[vacc_data['District'] == sm_dt]['District_Key'].iloc[0]
    else:
        map_dt_cor_dt[dt] = dt
        map_dname_dkey[dt] = vacc_data[vacc_data['District'] == dt]['District_Key'].iloc[0]

df['District'] = df['Name'].apply(lambda x: map_dt_cor_dt[x] if x in map_dt_cor_dt.keys() else np.nan)
df.dropna(subset=['District'], inplace=True)
df['District_Key'] = df['Name'].apply(lambda x: map_dname_dkey[x])
df.drop(columns=['Name', 'District', 'Level'], inplace=True)
df = df[['District_Key', 'TOT_P']]


# In[45]:


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


# In[46]:


distr_wise = pd.merge(vacc_data, df, how ='inner', on =['District_Key'])
distr_wise.fillna(0, inplace=True)
distr_wise


# In[47]:


state_wise_pop_data = sdf.copy()
state_wise_pop_data = state_wise_pop_data.reset_index()
state_wise_pop_data


# In[48]:


ddf = distr_wise.copy()
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


# In[49]:


ddf


# In[50]:


dkey_skey_col = ['State_Code', 'District_Key', 'TOT_P']
final_col = dkey_skey_col + vacc_col

final_df = ddf[final_col]
final_df.sort_values('District_Key', inplace=True)
final_df


# In[51]:


def get_districtwise_df(final_df, dt):
    ddf = final_df.copy()
    ddf = ddf[ddf['District_Key'] == dt]

    d1 = [c for c in ddf.columns[3::2]]
    d2 = [c for c in ddf.columns[4::2]]
    dose1_df = ddf.loc[:, d1]
    dose2_df = ddf.loc[:, d2]
    
    return dose1_df.iloc[0][-1], dose2_df.iloc[0][-1]

def get_statewise_df(state_final_df, st):
    ddf = state_final_df.copy()
    ddf = ddf[ddf['State_Code'] == st]
    ddf = ddf.groupby('State_Code').sum()
    

    d1 = [c for c in ddf.columns[1::2]]
    d2 = [c for c in ddf.columns[2::2]]
    dose1_df = ddf.loc[:, d1]
    dose2_df = ddf.loc[:, d2]

    return dose1_df.iloc[0][-1], dose2_df.iloc[0][-1]


# In[52]:


dt_df = final_df.copy()
for dt in dt_df['District_Key'].unique():
    print(dt)
    d1, d2 = get_districtwise_df(final_df, dt)
    dt_df.loc[dt_df['District_Key'] == dt, 'dose1'] = d1
    dt_df.loc[dt_df['District_Key'] == dt, 'dose2'] = d2


# In[53]:


state_final_df = final_df.copy()
for st in state_wise_pop_data['State_Code'].unique():
    if st not in state_final_df['State_Code'].unique(): continue
    d1, d2 = get_statewise_df(state_final_df, st)
    state_wise_pop_data.loc[state_wise_pop_data['State_Code'] == st, 'dose1'] = d1
    state_wise_pop_data.loc[state_wise_pop_data['State_Code'] == st, 'dose2'] = d2
state_wise_pop_data = state_wise_pop_data.dropna()
state_wise_pop_data


# In[54]:


new_df = dt_df.copy()
new_df = new_df[['District_Key', 'dose1', 'dose2', 'TOT_P']]
new_df


# In[55]:


st_df = state_wise_pop_data.copy()
st_df = st_df[['State_Code', 'dose1', 'dose2', 'TOT_P']]
st_df


# In[56]:


overall_pop_data['dose1'] = st_df['dose1'].sum()
overall_pop_data['dose2'] = st_df['dose2'].sum()
overall_pop_data


# In[57]:


new_df['vaccinateddose1ratio'] = new_df['dose1']/new_df['TOT_P']
new_df['vaccinateddose2ratio'] = new_df['dose2']/new_df['TOT_P']
new_df = new_df[['District_Key', 'vaccinateddose1ratio', 'vaccinateddose2ratio']]
new_df.rename(columns={'District_Key':'districtid'}, inplace=True)
new_df = new_df.sort_values('vaccinateddose1ratio')
new_df = new_df.set_index('districtid')
district_ratio = new_df.copy()
print('district_ratio')
print(district_ratio)


# In[58]:


st_df['vaccinateddose1ratio'] = st_df['dose1']/st_df['TOT_P']
st_df['vaccinateddose2ratio'] = st_df['dose2']/st_df['TOT_P']
st_df = st_df[['State_Code', 'vaccinateddose1ratio', 'vaccinateddose2ratio']]
st_df.rename(columns={'State_Code':'stateid'}, inplace=True)
st_df = st_df.sort_values('vaccinateddose1ratio')
st_df = st_df.set_index('stateid')
state_ratio = st_df.copy()
print('state_ratio')
print(state_ratio)


# In[59]:


overall_df = overall_pop_data.copy()
overall_df['vaccinateddose1ratio'] = overall_df['dose1']/overall_df['TOT_P']
overall_df['vaccinateddose2ratio'] = overall_df['dose2']/overall_df['TOT_P']
overall_df = overall_df[['Name', 'vaccinateddose1ratio', 'vaccinateddose2ratio']]
overall_df.rename(columns={'Name':'id'}, inplace=True)
overall_df = overall_df.set_index('id')
overall_ratio = overall_df.copy()
print('Overall ratio')
print(overall_ratio)


# In[60]:


district_ratio.to_csv('./output/district-vaccinated-dose-ratio.csv')


# In[61]:


state_ratio.to_csv('./output/state-vaccinated-dose-ratio.csv')


# In[62]:


overall_ratio.to_csv('./output/overall-vaccinated-dose-ratio.csv')

