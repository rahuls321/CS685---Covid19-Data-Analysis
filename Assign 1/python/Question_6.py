
# coding: utf-8

# In[74]:


import numpy as np
import pandas as pd
from datetime import timedelta
import Levenshtein
pd.options.mode.chained_assignment = None

'''
# ## Problem statement
# For each state, district and overall, find the following ratios: total number of females vaccinated (either 1 or 2 doses) to total number of males vaccinated (same). For that district/state/country, find the ratio of population of females to males. (If a district is absent in 2011 census, drop it from analysis.) Now find the ratio of the two ratios, i.e., vaccination ratio to population ratio.
# Output them in the following manner: districtid, vaccinationratio, populationratio, ratioofratios.
'''
# In[75]:


vacc_data1 = pd.read_csv('./data/cowin_vaccine_data_districtwise.csv', low_memory=False)
print('Vaccine data')
print(vacc_data1)


# In[76]:


print(vacc_data1.iloc[0])

'''
# Few Districts in CoWin data has been repeated, merging them into one. For example, for Ahmedabad and Ahmedabad corporation, merged into Ahmedabad.
'''
# In[77]:


print('Converting cases columns\' type to int')
vacc_data = vacc_data1.iloc[1:]
vacc_data.fillna(0, inplace=True)
col = list(vacc_data.columns[6:])
vacc_data[col] = vacc_data[col].astype(int)
vacc_data


# In[78]:


distr_data = pd.read_csv('./output/edge-graph.csv', index_col='District_Key')
distr_data.drop(columns=['Unnamed: 0'], inplace=True)
districts_key = list(distr_data.index)
print('District keys: ', districts_key)


# In[79]:


map_dkey_sname, map_dkey_dname = {}, {}
for dt in districts_key:
    map_dkey_sname[dt] = vacc_data[vacc_data['District_Key'] == dt]['State'].iloc[0]
    map_dkey_dname[dt] = vacc_data[vacc_data['District_Key'] == dt]['District'].iloc[0]
map_dkey_dname


# In[80]:


pop_data = pd.read_excel('./data/DDW_PCA0000_2011_Indiastatedist.xlsx')
pop_data = pop_data[['Name', 'Level', 'TRU', 'TOT_M', 'TOT_F']]
pop_data = pop_data[pop_data['TRU'] == 'Total']
pop_data.drop(columns=['TRU'], inplace=True)
pop_data


# In[81]:


overall_pop_data = pop_data[pop_data['Level'] == 'India']
overall_pop_data
# vacc_data[vacc_data['State'] == 'Dadra and Nagar Haveli and Daman and Diu']


# In[82]:


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


# In[83]:


#Manually created correct match from population datasets.
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


# In[84]:


#Not including this district 
def not_included_district(dt):
    not_included = ['Mewat ', 'North West', 'North', 'North East', 'East', 
                    'Central', 'West', 'South West', 'South',
                    'Kanshiram Nagar', 'North  District','West District', 'Barddhaman ',
                    'South District', 'East District', 'Mumbai Suburban', 'Mahamaya Nagar']
    
    if dt not in not_included: return True
    return False


# In[85]:


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
df = df[['District_Key', 'TOT_M', 'TOT_F']]


# In[86]:


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


# In[87]:


distr_wise = df.copy()
distr_wise


# In[88]:


ddf = pd.merge(vacc_data, distr_wise, how ='inner', on =['District_Key'])
ddf.fillna(0, inplace=True)
ddf


# In[89]:


state_wise_pop_data = sdf.copy()
state_wise_pop_data = state_wise_pop_data.reset_index()
state_wise_pop_data


# In[90]:


start_date = pd.to_datetime('16/01/2021', format='%d/%m/%Y').date()
end_date = pd.to_datetime('14/08/2021', format='%d/%m/%Y').date()
vacc_col = []
get_original_date=[]
while start_date<=end_date:
    start_date = start_date.strftime('%d/%m/%Y')
    male_vacc_dt = str(start_date)+'.5'
    female_vacc_dt = str(start_date)+'.6'
    
    #Convert back to datetime format
    start_date = start_date.split('.')[0]
    start_date = pd.to_datetime(start_date, format='%d/%m/%Y').date()
    
    if male_vacc_dt not in ddf.columns or female_vacc_dt not in ddf.columns:
        print("Date not available: ", start_date)
        continue
    ddf[male_vacc_dt] = ddf[male_vacc_dt].astype(int)
    ddf[female_vacc_dt] = ddf[female_vacc_dt].astype(int)
    get_original_date.append(start_date.strftime('%d/%m/%Y'))
    vacc_col.append(start_date.strftime('%d/%m/%Y')+'_m')
    vacc_col.append(start_date.strftime('%d/%m/%Y')+'_f')
    ddf[start_date.strftime('%d/%m/%Y')+'_m'] = ddf[male_vacc_dt] 
    ddf[start_date.strftime('%d/%m/%Y')+'_f'] = ddf[female_vacc_dt]
    start_date += timedelta(days=1)


# In[91]:


ddf


# In[92]:


dkey_skey_col = ['State_Code', 'District_Key', 'TOT_M', 'TOT_F']
final_col = dkey_skey_col + vacc_col

final_df = ddf[final_col]
final_df.sort_values('District_Key', inplace=True)
final_df


# In[93]:


def get_districtwise_df(final_df, dt):
    ddf = final_df.copy()
    ddf = ddf[ddf['District_Key'] == dt]

    d1 = [c for c in ddf.columns[4::2]]
    d2 = [c for c in ddf.columns[5::2]]
    male_df = ddf.loc[:, d1]
    female_df = ddf.loc[:, d2]
    
    return male_df.iloc[0][-1], female_df.iloc[0][-1]

def get_statewise_df(state_final_df, st):
    ddf = state_final_df.copy()
    ddf = ddf[ddf['State_Code'] == st]
    ddf = ddf.groupby('State_Code').sum()
    

    d1 = [c for c in ddf.columns[2::2]]
    d2 = [c for c in ddf.columns[3::2]]
    male_df = ddf.loc[:, d1]
    female_df = ddf.loc[:, d2]

    return male_df.iloc[0][-1], female_df.iloc[0][-1]


# In[94]:


dt_df = final_df.copy()
for dt in dt_df['District_Key'].unique():
    print(dt)
    mv, fv = get_districtwise_df(final_df, dt)
    dt_df.loc[dt_df['District_Key'] == dt, 'M_V'] = mv
    dt_df.loc[dt_df['District_Key'] == dt, 'F_V'] = fv


# In[95]:


state_final_df = final_df.copy()
for st in state_wise_pop_data['State_Code'].unique():
    if st not in state_final_df['State_Code'].unique(): continue
    mv, fv = get_statewise_df(state_final_df, st)
    state_wise_pop_data.loc[state_wise_pop_data['State_Code'] == st, 'M_V'] = mv
    state_wise_pop_data.loc[state_wise_pop_data['State_Code'] == st, 'F_V'] = fv
state_wise_pop_data = state_wise_pop_data.dropna()
state_wise_pop_data


# In[96]:


new_df = dt_df.copy()
new_df = new_df[['State_Code', 'District_Key', 'M_V', 'F_V', 'TOT_M', 'TOT_F']]
new_df


# In[97]:


st_df = state_wise_pop_data.copy()
st_df = st_df[['State_Code', 'M_V', 'F_V', 'TOT_M', 'TOT_F']]
st_df


# In[98]:


overall_pop_data['M_V'] = st_df['M_V'].sum()
overall_pop_data['F_V'] = st_df['F_V'].sum()
print('Overall pop data')
print(overall_pop_data)


# In[99]:


new_df['vaccinationratio'] = new_df['F_V']/new_df['M_V']
new_df['populationratio'] = new_df['TOT_F']/new_df['TOT_M']
new_df['ratioofratios'] = new_df['vaccinationratio']/new_df['populationratio']
new_df = new_df[['District_Key', 'vaccinationratio', 'populationratio', 'ratioofratios']]
new_df.rename(columns={'District_Key':'districtid'}, inplace=True)
new_df = new_df.sort_values('ratioofratios')
new_df = new_df.set_index('districtid')
district_ratio = new_df.copy()
print('Distric ratio')
print(district_ratio)


# In[100]:


st_df['vaccinationratio'] = st_df['F_V']/st_df['M_V']
st_df['populationratio'] = st_df['TOT_F']/st_df['TOT_M']
st_df['ratioofratios'] = st_df['vaccinationratio']/st_df['populationratio']
st_df = st_df[['State_Code', 'vaccinationratio', 'populationratio', 'ratioofratios']]
st_df.rename(columns={'State_Code':'stateid'}, inplace=True)
st_df = st_df.sort_values('ratioofratios')
st_df = st_df.set_index('stateid')
state_ratio = st_df.copy()
print('State ratio')
state_ratio


# In[101]:


overall_df = overall_pop_data.copy()
overall_df['vaccinationratio'] = overall_df['F_V']/overall_df['M_V']
overall_df['populationratio'] = overall_df['TOT_F']/overall_df['TOT_M']
overall_df['ratioofratios'] = overall_df['vaccinationratio']/overall_df['populationratio']
overall_df = overall_df[['Name', 'vaccinationratio', 'populationratio', 'ratioofratios']]
overall_df.rename(columns={'Name':'id'}, inplace=True)
overall_df = overall_df.set_index('id')
overall_ratio = overall_df.copy()
print('Overall ratio')
print(overall_ratio)

'''
# Sorting all the ratios by final ratio 'ratioofratios'
'''
# In[102]:


district_ratio.to_csv('./output/district-vaccination-population-ratio.csv')


# In[103]:


state_ratio.to_csv('./output/state-vaccination-population-ratio.csv')


# In[104]:


overall_ratio.to_csv('./output/overall-vaccination-population-ratio.csv')

