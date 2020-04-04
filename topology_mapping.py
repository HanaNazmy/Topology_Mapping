# -*- coding: utf-8 -*-
"""Topology_Mapping.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FKkubM4XK6Zn0xMj3j-7fjaJOdYlGfCS

# **Importing Dataset**
"""

from google.colab import drive 
drive.mount('/content/drive')
root_path = '/content/drive/My Drive/Dataset/'

"""# **Main**"""

import os
import numpy as np
import sklearn
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from numpy import linalg as LA
import networkx as nx
import pandas as pd
import collections
import math 
from math import log2, exp
from scipy.stats import entropy

k_10_array = [2,4,6,8,10]
k_50_array = [2,10,12,15,17,20,25]
# Topology size 10
A_10, D_10 = create_adj_Matrix(10,root_path)
L_10 = D_10 - A_10
# Topology size 50
A_50, D_50 = create_adj_Matrix(50,root_path)
L_50 = D_50 - A_50
# Topology size 100
A_100, D_100 = create_adj_Matrix(100,root_path)
L_100 = D_100 - A_100
ground_10, ground_50 = read_ground_truth(root_path)

"""**Visualization Before Clustering**"""

# Topology size 10
visualize_before_clustering(10,A_10)

# Topology size 50
visualize_before_clustering(50,A_50)

# Topology size 100
visualize_before_clustering(100,A_100)

"""**Clustering Evaluation**"""

#Topology 10
evaluate_spectral_clustering(10,A_10,L_10,D_10,k_10_array,ground_10)

#Topology 50
evaluate_spectral_clustering(50,A_50,L_50,D_50,k_50_array,ground_50)

#Topology 100
evaluate_spectral_clustering(100,A_100,L_100,D_100,k_50_array,None)

"""# **Creating Adjacency matrix and Degree matrix**"""

def create_adj_Matrix(num,path):
  Total = np.zeros((num*10,num))
  degree = np.zeros((num*10,num))
  for i in range(0,10):
    file1 = open(path+'t_'+str(num)+'_'+str(i)+'.txt', 'r') 
    Lines = file1.readlines() 
    # if i != 0:
    #     temp = np.zeros((num,num))
    for line in Lines: 
        l = line.strip()
        data = l.split() #split string into a list
        node_1 = int(data[0])-1
        node_2 = int(data[1])-1
        edge = int(data[2])
        Total[node_1+(i*num)][node_2] += edge
        Total[node_2+(i*num)][node_1] += edge
        degree[node_1+(i*num)][node_1] += edge
        degree[node_2+(i*num)][node_2] += edge
  return Total, degree

"""# **Reading the ground truth**"""

def read_ground_truth(path):
  file1 = open(path+'ground_truth.txt','r') 
  Lines = file1.readlines()
  ground_truth_10 = []
  ground_truth_50 = []
  for i in range(10): 
      line = Lines[i]
      l = line.strip()
      data = l.split() 
      for j in range(0, len(data)): 
          data[j] = int(data[j])
      ground_truth_10.append(data)
  # print(ground_truth_10)
  for i in range(10,20): 
      line = Lines[i]
      l = line.strip()
      data = l.split() 
      for j in range(0, len(data)): 
          data[j] = int(data[j])
      ground_truth_50.append(data)
  return ground_truth_10,ground_truth_50

"""# **Evaluation**"""

def evaluate_spectral_clustering(num,A,L,D,k_array,ground):
  best_k = np.zeros(num)
  maximum = np.zeros(num)
  k_dict= {}
  Eigenvectors, Eigenvalues = get_eigen(L,D,num)
  for k in k_array:
      classes = prepare_vectors(Eigenvectors, Eigenvalues,num,k)
      k_dict[k] = classes
      for j in range(10):
          clusters_dict = create_class_nodes(classes[j,:])
          if num == 100:
            norm_cut = get_normalized_cut(A,classes[j])
            if norm_cut > maximum[j]:
              maximum[j]=norm_cut
              best_k[j]=k
            print('normalized cut = ', norm_cut)
          else:
            entropy = calculate_conditional_entropy(clusters_dict,k,ground[j])
            f_measure = calculate_total_f_measure(clusters_dict, ground[j] )
            if f_measure > maximum[j]:
              maximum[j]=f_measure
              best_k[j]=k
            print('F-measure for topology ',j,'with k = ',k,'is',f_measure)
            print('Entropy for topology = ',j,'with k = ',k,'is',entropy)

  # for i in range (10):
  #   print("Best value for K for topology ",i," is: ",best_k[i])
  
  visualize(num,best_k,A,k_dict)

"""# **Get Eigen Vectors and Values**"""

def get_sorted_eigen(matrix,num):
  eVals , eVecs  = np.linalg.eigh(matrix)
  idx = np.argsort(np.abs(eVals))
  sorted_evecs = eVecs[:,idx]
  sorted_evals = eVals[idx]
  return sorted_evecs, sorted_evals

def get_eigen(L,D, num):
  Eigen_vectors = np.zeros((num*10,num))
  Eigen_values = np.zeros((10,num))
  for i in range(0,10):
      L_small = L[i*num : (i*num)+num,:]
      D_inv = np.linalg.pinv(D[i*num : (i*num)+num,:])
      temp = np.dot(D_inv,L_small)
      eig_vecs , eig_vals = get_sorted_eigen(temp,num)
      Eigen_vectors[i*num : (i*num)+num,:] = eig_vecs 
      Eigen_values[i, :] = eig_vals
  return Eigen_vectors, Eigen_values

def prepare_vectors(eigen_vectors, eigen_values,num,k):
  classes = np.zeros((num,num))
  for i in range(0,10):
      edited_eigen_vectors = cut_eigen(eigen_vectors[i*num : (i*num)+num,:],eigen_values[i,:],num,k)
      # print('eigen',edited_eigen_vectors.shape)
      classes[i,:]=spectral_clustering(k,edited_eigen_vectors)
  return classes

"""# **Cutting the Eigen Vector**"""

def cut_eigen(eigen_vectors,eigen_values,num,k):
  # if num == k:
  #   break
  one_array = np.ones((num,1))
  indices = []
  count = 0
  edited_eig_vecs = np.zeros((num,k))
  for i in range(0,num):
    if eigen_values[i] == 0:
        comparison = eigen_vectors[:,i] == one_array
        equal_arrays = comparison.all()
        if equal_arrays == True:
          continue
    edited_eig_vecs[:,count] = eigen_vectors[:,i] 
    count +=1
    if count == k:
      break
  return edited_eig_vecs

"""# **Getting Nodes of one Class**"""

# for one topology
def create_class_nodes(class_labels):
  dict = {}
  for number in class_labels:
    dict[number] = []
  for i in range(len(class_labels)):
    dict[ class_labels[i]].append( i)
  return dict

"""# **Spectral Clustering and Kmeans**"""

def spectral_clustering(k,edited_eigen_vectors):
  # normalized = LA.norm(edited_eigen_vectors,ord=1, axis=1, keepdims = True)
  normalized = edited_eigen_vectors
  kmeans = KMeans(n_clusters=k).fit(normalized)
  centers = kmeans.cluster_centers_
  clusters = kmeans.labels_
  return clusters

"""# **Internal Measures - Normalized Cut**"""

def get_normalized_cut(A,cluster_labels):
    diction = create_class_nodes(cluster_labels)
    norm_cut = 0
    for i in range(len(diction)):
        w_in = get_internal_weights(A, diction[i])
        print('Internal Traffic of partition',i,'is',w_in,' Mbps')
        # if i == 0:
        # print('diction', diction[0])
        w_out = get_external_weights(A, diction[i])
        print('Emulated Traffic of partition',i,'is',w_out,' Mbps')
        # print('Internal ',w_in,' External', w_out)
        norm_cut += (w_out / (w_in+w_out))
    return norm_cut

def get_internal_weights(A,cluster_nodes):
  weight = 0
  for i in cluster_nodes:
    for j in cluster_nodes:
        weight+= exp((-0.01)*A[i][j])
  weight = weight /2
  return weight

def get_external_weights(A,cluster_nodes):
    weight = 0
    for i in cluster_nodes:
      for j in range(0,100):
        if j in cluster_nodes:
          continue
        weight+= exp(-0.01*A[i][j])
    if weight == 0:
        weight = 1
    weight = weight /2
    return weight

"""# **External Measures - F-measure**"""

#assume cluster nodes are the indecies of the nodes in this current cluster
def calculate_f_measure( cluster_nodes, ground_truth ):
  gt_map = np.zeros((1, len(ground_truth)))
  for node in cluster_nodes:
    index = ground_truth[node]
    gt_map[0][index] = gt_map[0][ index ]+1
  max_value = np.argmax( gt_map)
  max_total = collections.Counter(ground_truth)[ max_value ]
  recall  = gt_map[0][max_value]/max_total
  prec = gt_map[0][max_value]/len(cluster_nodes)
  f_measure = (2*recall*prec)/(recall+prec)
  return f_measure

def calculate_total_f_measure(cluster_dict, ground_truth):
  f_measure = 0
  length = len(cluster_dict)
  for j in range(length):
    f_measure += (calculate_f_measure(cluster_dict[j],ground_truth))/length
  return f_measure

"""# **External Measures - Conditional Entropy**"""

# for one cluster
def calculate_cluster_entropy( cluster_nodes, ground_truth ):
  gt_map = np.zeros((1, len(ground_truth)))
  cluster_entropy = 0
  # loop on each node in cluster
  for i_node in cluster_nodes:
    # get its true index in ground truth
    true_index = ground_truth[i_node]
    # add 1 to its true label
    gt_map[0][true_index] += 1
  # gt map holds for cluster for each class how many
  for j in range(0,len(gt_map[0])):
    nj = gt_map[0][j]
    if nj ==0:
      continue
    ratio = nj / (len(cluster_nodes))
    # print("Ratio is equal ", ratio)
    cluster_entropy += (-1*ratio*log2(ratio))
      # print("Entropy is equal ", cluster_entropy)
  return len(cluster_nodes),cluster_entropy

def calculate_conditional_entropy(clusters_dict,k,ground_truth):
  conditional_entropy=0
  for i in range(k):
    len_cluster,cluster_entropy = calculate_cluster_entropy(clusters_dict[i],ground_truth)
    if cluster_entropy == 0:
        continue
    ratio = len_cluster/len(ground_truth)
    conditional_entropy += (ratio*cluster_entropy)
  return conditional_entropy

"""# **Visualization**"""

def visualize_before_clustering(num,A):
  for i in range(10):
    print("Topology number ",i," of size ",num)
    visualize_topology(i,num,A,np.zeros(num))

def visualize(num,best_k,A,k_dict):
  # takes the best k and visualize   
  for i in range(0,10):
    k_index = best_k[i]
    print("Topology ",i," with K= ",k_index)
    visualize_topology(i,num,A,k_dict[k_index][i])

def visualize_topology(i,num,m_total,classes):
  mat = m_total[i*num : (i*num)+num,:]
  G = nx.from_numpy_matrix(np.matrix(mat))
  pos = nx.circular_layout(G,scale=1)
  # pos = nx.spring_layout(G,scale=1)
  # pos = nx.drawing.nx_pydot.graphviz_layout(G)
  # Carac is a df helps to make each class has a common color
  carac = pd.DataFrame({ 'ID':G.nodes(), 'myvalue':classes })
  edge_labels = nx.get_edge_attributes(G, "weight")

  carac= carac.set_index('ID')
  # carac=carac.reindex(G.nodes())
  carac['myvalue']=pd.Categorical(carac['myvalue'])
  carac['myvalue'].cat.codes
  if num == 10:
      fig= plt.figure(figsize=(7,7))
  else:
      fig= plt.figure(figsize=(10,10))
  nx.draw(G,pos,edge_color='black',node_color=carac['myvalue'].cat.codes,node_size=1500, linewidths=1, font_size=15 , width=5.0, alpha=0.9,
          labels={node:node for node in G.nodes()})
  # Add weights to edges
  nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels,font_color='red')
  plt.show()
  return G