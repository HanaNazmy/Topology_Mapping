# Topology_Mapping
PATTERN RECOGNITION CCE
TOPOLOGY MAPPING
SPECTRAL CLUSTERING AND CLUSTER EVALUATION TECHNIQUES


Noha Nomier ID:4638
Hana Nazmy ID:4952
Fatma Sherif Tawfik ID:4701












PROBLEM STATEMENT
Simulating large-scale network experiments requires powerful physical resources. However, partitioning could be used to reduce the required power of the resources and to reduce the simulation time. Topology mapping is a partitioning technique that maps the simulated nodes to different physical nodes. In this assignment, we will use spectral clustering to partition a given network topology on the available physical nodes. The network topology is a graph of N nodes communicating with each other by sending data traffic through a set of edges. An edge in the topology is weighted by the traffic (Mbps) passing through it. Our clustering technique should find the cut that minimizes the traffic between different partitions

Dataset
a.The dataset contains 30 network topology with 3 topology sizes (10 simulated nodes, 50 simulated nodes, and 100 simulated nodes)
b. Each topology is described in a .txt file.
c. Each line in the file is an edge in the topology: <from, to, traffic (Mbps)>
d. Ground truth clustering is available for topologies with sizes 10 and 50. The <ground_truth.txt> file contains a line for each topology ordered by the topology name: t_10_0, t_10_1, ..., t_50_0, t_50_1, ..., t_50_9
e. The ground truth line consists of N values (number of nodes), where nodes having the same value are in the same cluster.
  
ALGORITHM EXPLAINED 
For topologies of sizes 10, the values of parameter k that we will try are are [2,4,6,8,10] which is stored in k_10_array. For topologies of size 50,100, the k values are [2,10,12,15,17,20,25] and are stored in the array k_50_array.
create_adjacency_matrix
  We first call function [create_adjacency_matrix]  with parameters num, path
Num: the size of the topology to be created (10,50 or 100)
Path: the name of the file to read in the topology
This function creates the needed matrices for the topology so that we can compute the laplacian matrix later on. It returns the matrix Total ;which is the adjacency matrix and the Degree matrix which are represented mathematically as A and  ∆ respectively. Note that this function will read in the 10 topologies and construct an adjanceny matrix and degree matrix for each individual topology, but all the matrices are saved in a multidimensional array that will be returned from the function. 

Visualize before clustering
   We then call the function “visualize before clustering” which takes in the Adjacency matrices for the 10 topologies and the number of nodes in each topology. This function will call the visualize topology function and each topology will be drawn as a graph. All the nodes are the same color now because we still did not perform the clustering.
Evaluate Spectral Clustering

   This method is called to start performing the clustering. It takes the number of nodes (num), the matricies A,L,D and the different K in addition to the ground truth if available. First, we compute the eigen vectors for the equation  [ inv(∆)L ].
After this step, we enter the for loop which will loop for every value of K. The method prepare_eigen_vectors takes the k value, the eigen vectors and values and return the eigenvector after it is reduced. Since this operation will be done on the 10 topologies, this method is a helper method to loop from 1 to 10, and each time it calls the cut_eigen method which takes only the eigenvectors of one topology.




Cut_Eigen 

   This method will loop k times, each time it checks if the corresponding eigen value is equal to zero. If it is zero, it will check if the corresponding eigenvector is equal to ones. If true, this eigenvector will be ignored, otherwise it will be taken.

After the eigenvectors are ready for each topology, the Spectral Clustering method is called. Spectral Clustering takes the k value, and the eigenvectors. 
It normalizes the eigenvectors, then it performs K-means algorithm on the data to partition it into k clusters. The K-means function returns the labels for the nodes. 
Finally, these labels are sent back to the function evaluate_spectral_clustering.
We now have the labels for each of the 10 topologies of whichever node size we chose. To keep track of this data, we created a dictionary. This dictionary uses the K value as the key, and the value is the labels for each of the 10 topologies that were produced from performing K-means with this particular K value. 

 At the end of the function evaluate_spectral_clustering, we call the visualize function that will draw all the topologies, but after the clustering, where nodes in the same cluster have the same color.

Evaluating the Clustering

After we perform the clustering, we check the number of nodes, for topologies of nodes 10 and 50, we have the ground truth. For topologies of size 100, we will perform internal measures. For the external measures, we calculate the F-measure and the conditional entropy. For both of these measures, we call the function create_class_nodes, this method takes the labeling output from the k means, and returns a dictionary, where the key is the symbol of a specific cluster (an integer in our condition) and the value is a list of the indices of the nodes that are in this specific cluster. This dictionary will be sent to the function calculate_total_f_measure and to a similar function called calculate_conditional_entropy.

Calculate  Total F measure

   This method loops on each cluster, and call calculate_f_measure for each cluster. The calculate_f_measure will calculate the purity and recall for a given cluster and return the f measure for that specific cluster. The returned value will be multiplied by it’s weight and added to the total f measure. At the end, the total f measure is returned for this clustering.

Calculate Conditional Entropy

    This is very similar to the F-measure calculation. We will loop over the dictionary which represents our cluster, and each cluster is sent to the function calculate_cluster_entropy which calculates the entropy for a specific cluster. The final conditional entropy is calculated and returned.

Normalized Cut measure

For topologies of size 100, we do not have the ground truth, therefore we will compute the evaluation with internal measures.

Get_normalized_cut
   
    We will construct the dictionary that holds all our clusters, then we will call the methods get_internal_weights and get_external_weights to return the intercluster and intracluster distances summed. We calculate the Total normalized cut and return the value.

Returning to the evaluate spectral clustering method, we have an array best_k that will hold the value of k for each topology that scored the best measure after evaluating the clustering. 

Every topology will be drawn as a graph after performing the clustering. Nodes in the same cluster will be drawn with the same colors. This will portray the different clusterings that arise from choosing different values for K.
