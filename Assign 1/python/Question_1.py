
# coding: utf-8

# In[71]:


import numpy as np
import pandas as pd
import json

get_ipython().system('pip install python-Levenshtein')
import Levenshtein


# In[72]:


# In[1]:


#df = pd.read_json ('./data/neighbor-districts.json')
f = open('./data/neighbor-districts.json')
neighbor_data = json.load(f)


# In[74]:


neighbor_data


# In[75]:


len(neighbor_data.keys())


# In[76]:


vacc_data = pd.read_csv('./data/cowin_vaccine_data_districtwise.csv', low_memory=False)
vacc_data


# In[77]:


#vacc_data.isna().any()


# In[78]:


covid_data = pd.read_csv('./data/district_wise.csv')
covid_data


# In[79]:


df = pd.merge(vacc_data, covid_data, how ='inner', on =['District_Key'])
df


# In[80]:


#df[df['State_x'] == 'Telangana']
df[df['District_Key'] == 'TG_Bhadradri Kothagudem']
#df[df['State_Code_x'] == 'ML']


# In[81]:


# df[df['State_x'] == 'Gujarat']


# In[82]:


# vacc_data[vacc_data['State'] == 'Gujarat']

'''
# # Preprocessing
# 
# Total 2 Stages are involved in the preprocessing of the data
# 
# * **Stage 1**
# 
#     * **Step 1** - First I removed extra district code mentioned along with the districts in neighbor.json data i.e District Code followed by '/' --- e.g. converting 'adilabad/Q15211' to 'adilabad
#     * **Step 2** - Converted all the districts in title form by removing '_' --- e.g -  'sahibzada_ajit_singh_nagar' to 'Sahibzada Ajit Singh Nagar' 
#     * **Step 3** - Some of the districts are writter in the form of 'xxx_district' where xx is district name so,first I converted into title form and then removed the 'district' word from the original name --- e.g. gandhinagar_district to 'Gandhinagar'
'''
# In[83]:


print("Total no. of district to convert into districtid", len(neighbor_data.keys()))
new_neighbor_data={}
i=0
for k, v in neighbor_data.items():
    new_key = k.split('/')[0]
    if new_key in ['bilaspur', 'hamirpur', 'aurangabad', 'pratapgarh', 'balrampur']:
        if new_key in new_neighbor_data.keys():
            key_value=[]
            for val in v:
                val = val.split('/')[0]
                val = val.title().split('_')
                if 'District' in val: val=val[:-1]
                val = " ".join(val)
                key_value.append(val)
            new_neighbor_data[new_key] = key_value
            continue
    
    new_key = new_key.title().split('_')
    if 'District' in new_key:
        #print("before new_key in district", new_key)
        new_key=new_key[:-1]
        #print("after new_key in district", new_key)
    new_key = " ".join(new_key)
    key_value=[]
    for val in v:
        val = val.split('/')[0]
        val = val.title().split('_')
        if 'District' in val: val=val[:-1]
        val = " ".join(val)
        key_value.append(val)
    new_neighbor_data[new_key] = key_value
print("Total input Neighbor-District data available in the datasets are: ", new_neighbor_data)


# In[84]:


# w='Yanam'
# for d, d_n in new_neighbor_data.items():
#     if Levenshtein.distance(w, d) < 3:
#         print(d, end=' ')
#         print(Levenshtein.distance(w, d))
#     for dd in d_n:
#         if Levenshtein.distance(w, dd) < 5:
#             print(d, end=' ')
#             print(Levenshtein.distance(w, dd))


'''
# Total input Neighbor-District data available in the datasets are 723

# ## Note
# Here these districts **['bilaspur', 'hamirpur', 'aurangabad', 'pratapgarh', 'balrampur']** are occuring twice in the neighbor-district.json file. So, I combined the neighboring districts of both the repeated district into one.

# # Question 1

# * **Stage 2**
# 
#     * Step 1 - **Finding Intersection of all data** :- Discard all districts which are not available in the all the three datasets i.e Vaccine Data, Covid Data, Neighbor-district Data (Finding intersection of all the datas)
#     * Step 2 - **Finding Most Similar Districts** :- Finding the districts from the Neighbor-districts data which are available in intersection of Vaccine Data & Covid data using the technique of finding the similarity score of two words using Levenshtein distance. The Levenshtein distance between two words is basically the minimum number of single-character edits (insertions, deletions or substitutions) required to change one word into the other. (Source - Wiki) 
#     * Step 3 - **Manually editing the matched word** :- After getting most similar word, some of the similar word aren't matched properly. So, I tried to find the correct match from internet by manually going through all the incorrect matching.
#     * Step 4 - **Correcting spelling mistake** :- Some of the words having wrong spelling written. So I corrected them.

# In[85]:
'''

# This function will find the most similar district word from the given district word in the dataset.
def get_most_similar_word(df, w):
    '''
    inputs:
        df : input data containing all the state and districts code i.e DataFrame format
        w : district name
    output:
        output1 : most similar district
        output2 : similarity score between two given word input and most similar word
        
    '''
    temp_df = df.copy()
    temp_df['Levenshtein_dist'] = temp_df['District_x'].apply(lambda x: Levenshtein.distance(w, x))
    temp_df = temp_df.sort_values(by=['Levenshtein_dist'])
    print(temp_df['District_x'].iloc[0])
    #print("with value: ", temp_df['Levenshtein_dist'].iloc[0])
    return temp_df['District_x'].iloc[0], temp_df['Levenshtein_dist'].iloc[0]


# In[86]:


def find_correct_match(distr):
    '''
    inputs:
        distr : district name for finding correct match if  Levenshtein_distance doesn't work
    output:
        output1 : correct match if available otherwise return empty string
        
    '''
    correct_match = {'Belgaum': 'Belagavi', 'Baleshwar': 'Balasore', 'Rangareddy': 'Ranga Reddy','Hugli':'Hooghly', 'Sahibzada Ajit Singh Nagar': 'S.A.S. Nagar', 
                 'Sant Ravidas Nagar':'Bhadohi', 'Muktsar': 'Sri Muktsar Sahib', 'Pashchim Champaran':'West Champaran','Pashchimi Singhbhum': 'West Singhbhum',
                'Bid': 'Beed', 'East Karbi Anglong':'Karbi Anglong', 'The Dangs':'Dang', 'Dantewada':'Dakshin Bastar Dantewada','Purbi Singhbhum':'East Singhbhum',
                'Jyotiba Phule Nagar': 'Amroha', 'Kheri':'Lakhimpur Kheri', 'Kaimur (Bhabua)':'Kaimur', 'Ysr':'Y.S.R. Kadapa'}
    if distr in correct_match.keys():
        return correct_match[distr]
    return ''


# In[87]:


def find_correct_spelling(distr):
    '''
    inputs:
        distr : district name for correcting speliing mistakes
    output:
        output1 : correct spelling of word if available otherwise return empty string
        
    '''
    correct_spelling = {'Kabeerdham' : 'Kabirdham', 'Shrawasti': 'Shravasti'}
    if distr in correct_spelling.keys():
        return correct_spelling[distr]
    return ''


# In[88]:


def is_district_available(distr):
    '''
    inputs:
        distr : district name for checking its availability
    output:
        output1 : True if not available and False if available in the given list
        
    '''
    not_included_in_vacc_and_covid_data = ['Sonapur', 'Faizabad', 'Kochbihar', 'Niwari', 'Noklak']
    if distr in not_included_in_vacc_and_covid_data: return False
    return True


# This will take some time to preprocess all the districts and their neighboring districts.

# In[89]:

print("Starting Name Matching process of the districts")

neighbor_districts_modified={}
for distr, neigh_distr in new_neighbor_data.items():
    if distr in ['Kheri', 'Konkan Division', 'Niwari', 'Noklak', 'Parbhani', 'Pattanamtitta', 
                                    'Chengalpattu', 'Gaurela Pendra Marwahi', 'Nicobars', 'North and Middle Andaman', 
                                    'Seraikela Kharsawan', 'South Andaman', 'Tenkasi', 'Tirupathur', 'Yanam']:
        print('*'*100)
        print("Not including this district: ", distr)
        print('*'*100)
        continue
    if not is_district_available(distr):
        print('*'*100)
        print("District is not available in vaccine and covid data: ", distr)
        print('*'*100)
        continue
    print(distr, end=' ')
    print(' ---> ', end=' ')
    similar_distr, _ = get_most_similar_word(df, distr)
    corr_match = find_correct_match(distr)
    if len(corr_match) > 0: 
        print('*'*100)
        print("Correct Matching of "+distr+" is "+corr_match)
        print('*'*100)
        similar_distr = corr_match
    corr_spelling = find_correct_spelling(similar_distr)
    if len(corr_spelling)>0:
        print('*'*100)
        print("Correct Spelling of "+similar_distr+" is "+corr_spelling)
        print('*'*100)
        
    get_df = df[df['District_x'] == similar_distr]
    district_code = get_df['District_Key'].iloc[0]
    state_code = get_df['State_Code_x'].iloc[0]
    
    i+=1
    distr_code_list=[]
    for n in neigh_distr:
        if n in ['Kheri', 'Konkan Division', 'Niwari', 'Noklak', 'Parbhani', 'Pattanamtitta', 
                                    'Chengalpattu', 'Gaurela Pendra Marwahi', 'Nicobars', 'North and Middle Andaman', 
                                    'Seraikela Kharsawan', 'South Andaman', 'Tenkasi', 'Tirupathur', 'Yanam']:
            print('*'*100)
            print("Not including this district: ", n)
            print('*'*100)
            continue
        if not is_district_available(n): 
            print('*'*100)
            print("District is not available in vaccine and covid data: ", n)
            print('*'*100)
            continue
        print(n, end=' ')
        print(' ---> ', end=' ')
        similar_distr, _ = get_most_similar_word(df, n)
        corr_match = find_correct_match(n)
        if len(corr_match) > 0:
            print('*'*100)
            print("Correct Matching of "+n+" is "+corr_match)
            print('*'*100)
            similar_distr = corr_match
        corr_spelling = find_correct_spelling(similar_distr)
        if len(corr_spelling)>0:
            print('*'*100)
            print("Correct Spelling of "+similar_distr+" is "+corr_spelling)
            print('*'*100)
        n_get_df = df[df['District_x'] == similar_distr]
        i+=1
        n_district_code = n_get_df['District_Key'].iloc[0]
        n_state_code = n_get_df['State_Code_x'].iloc[0]
        distr_code_list.append(n_district_code)
       
    #Handling Last missing data
    if district_code in neighbor_districts_modified.keys():
        print('*'*100)
        print("Combining with previous neighbor district available with same district code: ", district_code)
        print('*'*100)
        distr_code_list = set(neighbor_districts_modified[district_code] + distr_code_list)
    neighbor_districts_modified[district_code] = sorted(distr_code_list)
#neighbor_districts_modified


# In[90]:


print("Total Modified Neighbor-district size: ", len(neighbor_districts_modified))

'''
# Total Input data is 723 
# After preprocessing I got total districts data is 704.
# Total 723-704 = 19 sets of data are arranged in this way:
# * Out of 19, **4** no. of districts are being removed as per question
# * Out of 15, **5** no. of districts are not present in the intersection of vaccine_data and covid data. Refer the **not_included_in_vacc_and_covid_data** list of this function **is_district_available()**
# * Remaining out of 10, **5** no. of districts are occuring twice in the neighbor-district.json file. Refer **Note** section of first preprocessing stage.
# * Remaining 5 are repeating while combining all neighbor district in the neighbor_districts_modified dict. So, I chose their union of the two sets. Refer in the main code at the end of the for loop.
'''
# In[91]:


sorted_neighbor_districts_modified = dict(sorted(neighbor_districts_modified.items()))
sorted_neighbor_districts_modified


# In[92]:


state_distr_sorted_dict={}
n_state_distr_sorted_dict={}
for state_code in df['State_Code_x'].unique():
    state_distr_sorted_dict[state_code] = []
    
#Changing output to state and district wise code.
for distr, neigh_distr in sorted_neighbor_districts_modified.items():
    get_df = df[df['District_Key'] == distr]
    state_code = get_df['State_Code_x'].iloc[0]
    state_distr_sorted_dict[state_code].append({distr:neigh_distr})
    
#Sorting the districts of states
for st_code, distr_list in state_distr_sorted_dict.items():
    keys_list = []
    for i, k in enumerate(distr_list):
        keys_list.append(list(k.keys())[0])
    sort_keys_list = sorted(keys_list)
    #print(sort_keys_list)
    new_idx_keys_list=[]
    for key in sort_keys_list:
        for kk, vv in enumerate(distr_list):
            if list(vv.keys())[0] == key:
                new_idx_keys_list.append(distr_list[kk])
    if len(new_idx_keys_list) > 0:
        n_state_distr_sorted_dict[st_code] = new_idx_keys_list
n_state_distr_sorted_dict


# In[93]:


#print(len(n_state_distr_sorted_dict)) #Two states are not available in their intersections.
#print(len(state_distr_sorted_dict)) #Total States 


# In[94]:


json_object = json.dumps(n_state_distr_sorted_dict,sort_keys = True, indent = 4)
with open("./output/neighbor-states-modified.json", "w") as outfile:
    outfile.write(json_object)


# In[95]:


n_state_distr_sorted_dict


# In[96]:


d_json_object = json.dumps(sorted_neighbor_districts_modified, sort_keys = True, indent = 4)
with open("./output/neighbor-districts-modified.json", "w") as outfile:
    outfile.write(d_json_object)


# In[97]:
