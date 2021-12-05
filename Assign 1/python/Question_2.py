
# coding: utf-8

# In[4]:


import numpy as np
import pandas as pd
import json

'''
# ## Problem statement
# Construct an undirected graph of districts out of this new file. In the graph, every
# district is a node. A district node is connected by an edge to every adjacent district of it, and vice
# versa.
# Output the graph in an edge list format. If district i has an edge with district j, output i, j.
'''
# In[5]:


with open('./output/neighbor-districts-modified.json') as f:
    neighb_distr = json.load(f)
neighb_distr


# In[6]:


len(neighb_distr)


# In[7]:


distr_edge_graph = {}
for distr, n_distr in neighb_distr.items():
    distr_edge_graph[distr]=[]
    for d in n_distr:
        distr_edge_graph[d]=[]

max_neighb_distr_count=-1
for distr, n_distr in neighb_distr.items():
    for d in n_distr:
        if d not in distr_edge_graph[distr]:
            distr_edge_graph[distr].append(d)
        if distr not in distr_edge_graph[d]:
            distr_edge_graph[d].append(distr)
        max_neighb_distr_count = max(max_neighb_distr_count, max(len(distr_edge_graph[d]), len(distr_edge_graph[distr])))


# In[8]:


print("Total no. of districts: ", len(distr_edge_graph))


# In[9]:


print("Maximum possible edges: ", max_neighb_distr_count)


# In[10]:


#print(distr_edge_graph)


# In[11]:


df = pd.DataFrame(sorted(list(distr_edge_graph.items())), columns=['District_Key', 'n_dist'])
df[["edge_"+str(x+1) for x in range(max_neighb_distr_count)]] = pd.DataFrame(list(df["n_dist"]))
df.drop(columns=['n_dist'], inplace=True)
df


# In[12]:


df.to_csv('./output/edge-graph.csv')

