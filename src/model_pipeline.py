import logging

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)


def optimal_clusternum(df,min_clust,max_clust,cluster_cols,init_type,n_init,max_iter,random_state,SSEpath,silpath):
    """
    Run K-means clustering for different numbers of total clusters and calculate SSE and Silhouette scores for each fit
    Args:
        df: (Pandas DataFrame), Required: Data features based on player statistics to be used in clustering
        min_clust (int), Required: Minimum number of clusters to try in K-means
        max_clust (int), Required: Maximum number of clusters to try in K-means
        cluster_cols (list of Strings), Required: Columns used as features in K-means
        init_type (String), Required: Initialization method for K-means
        n_init (int), Required: Number of times K-means is run with different starting seeds
        max_iter (int), Required: Maximum number of iterationsfor K-means in one run
        random_state (int), Required: Random seed for K-means
        SSEpath (String), Required: Filepath to save SSE plot
        silpath (String), Required: Filepath to save Silhouette score plot
    Returns:
        None
    """
    # Ensure df is a DataFrame
    if not isinstance(df, pd.DataFrame):
        logger.error('Provided argument `df` is not a Pandas DataFrame object')
        raise TypeError('Provided argument `df` is not a Pandas DataFrame object')

    # Isolate columns to be used as features in clustering
    features = df[cluster_cols]
    # Scale columns prior to clustering to weight all features equally
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Find the optimal number of clusters by looping through different cluster numbers and fitting K-means on each
    logger.debug('Attempting to run K-Means on several cluster numbers.')
    sse = []
    silhouette_scores = []
    for k in range(min_clust, max_clust):
        kmeans = KMeans(init=init_type,n_clusters=k,n_init=n_init,max_iter=max_iter,random_state=random_state)
        kmeans.fit(scaled_features)
        # Record within cluster SSE for each number of clusters
        sse.append(kmeans.inertia_)
        # Record Silhouette Score for each number of clusters
        score = silhouette_score(scaled_features, kmeans.labels_)
        silhouette_scores.append(score)

    logger.info('Trained K-means on %i to %i number of clusters and calculated within-cluster SSE and Silhouette score for each.', 2, 11)

    # Call functions to generate SSE and Silhouette score plots
    generate_SSEplot(sse,SSEpath,min_clust,max_clust)
    generate_silplot(silhouette_scores,silpath,min_clust,max_clust)


def generate_SSEplot(sse,SSEpath,min_clust,max_clust):
    """
    Plot number of clusters vs. within-cluster SSE for K-means fits
    Args:
        sse: (list), Required: Within cluster SSE values for K-means clustering fits for different numbers of clusters
        SSEpath (String), Required: Filepath to save SSE plot
        min_clust (int), Required: Minimum number of clusters to try in K-means
        max_clust (int), Required: Maximum number of clusters to try in K-means
    Returns:
        None
    """
    # Generate and save SSE plot to model folder
    plt.plot(range(min_clust, max_clust), sse)
    plt.xticks(range(min_clust, max_clust))
    plt.xlabel('Number of Clusters')
    plt.ylabel('SSE')

    try:
        plt.savefig(SSEpath)
    except OSError:
        logger.warning('The filepath %s could not be found or accessed to save the SSE plot.',SSEpath)
    else:
        logger.info('Number of clusters vs. within cluster SSE plot saved to %s',SSEpath)
    plt.close()


def generate_silplot(silhouette_scores,silpath,min_clust,max_clust):
    """
    Plot number of clusters vs. Silhouette score for K-means fits
    Args:
        silhouette_scores: (list), Required: Silhouette scores for K-means clustering fits for different numbers of clusters
        silpath (String), Required: Filepath to save Silhouette score plot
        min_clust (int), Required: Minimum number of clusters to try in K-means
        max_clust (int), Required: Maximum number of clusters to try in K-means
    Returns:
        None
    """
    # Generate and save Silhouette plot to model folder
    plt.plot(range(min_clust, max_clust), silhouette_scores)
    plt.xticks(range(min_clust, max_clust))
    plt.xlabel('Number of Clusters')
    plt.ylabel('Silhouette Coefficient')

    try:
        plt.savefig(silpath)
    except OSError:
        logger.warning('The filepath %s could not be found or accessed to save the Silhouette plot.',silpath)
    else:
        logger.info('Number of clusters vs. Silhouette scores plot saved to %s',silpath)
    plt.close()


def test_cluster_stability(df,cluster_cols,init_type,n_init,max_iter,random_state,n_clusters,random_state_comp,cluster_map,cluster_col1,cluster_col2,round_digits,savepath):
    """
    Run K-means clustering twice with different seeds and see how many of the cluster assignments change for a
    measure of stability of the cluster fit
    Args:
        df: (Pandas DataFrame), Required: Data features based on player statistics to be used in clustering
        cluster_cols (list of Strings), Required: Columns used as features in K-means
        init_type (String), Required: Initialization method for K-means
        n_init (int), Required: Number of times K-means is run with different starting seeds
        max_iter (int), Required: Maximum number of iterationsfor K-means in one run
        random_state (int), Required: Random seed for K-means
        n_clusters (int), Required: Number of clusters to be used in K-means
        random_state_comp (int), Required: Random seed for K-means being used as a comparison run for stability
        cluster_map (dict), Required: The mapping of similar cluster between the two runs
        cluster_col1 (String), Required: Column name for the newly created cluster labels column
        cluster_col2 (String), Required: Column name for the newly created cluster labels column for the second clustering run
        round_digits (int), Required: Number of digits to round outputs to
        savepath (String), Required: Path to save percent difference between the two clustering fits
    Returns:
        None
    """
    # Ensure df is a DataFrame
    if not isinstance(df, pd.DataFrame):
        logger.error('Provided argument `df` is not a Pandas DataFrame object')
        raise TypeError('Provided argument `df` is not a Pandas DataFrame object')

    # Isolate columns to be used as features in clustering
    features = df[cluster_cols]
    # Scale columns prior to clustering to weight all features equally
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    # Fit kmeans with optimal number of clusters
    kmeans = KMeans(init=init_type,n_clusters=n_clusters,n_init=n_init,max_iter=max_iter,random_state=random_state)
    kmeans.fit(scaled_features)
    # Append cluster assignments to the features DataFrame
    df[cluster_col1] = kmeans.labels_
    # Check the stability of the clusters by fitting Kmeans again with a different seed
    kmeans_compared = KMeans(init=init_type,n_clusters=n_clusters,n_init=n_init,max_iter=max_iter,random_state=random_state_comp)
    kmeans_compared.fit(scaled_features)
    df[cluster_col2] = kmeans_compared.labels_
    # Align cluster labels between the two fits
    df[cluster_col2] = df[cluster_col2].map(cluster_map)

    # Count the percentage of classification differences between the two cluster fits
    num_diff = sum(i != j for i, j in zip(df[cluster_col1],df[cluster_col2]))
    perc_diff = round(100*(1-num_diff/len(df)),round_digits)
    perc_diff_df = pd.DataFrame(columns=['perc_similar'])
    perc_diff_df.loc[0] = perc_diff

    try:
        perc_diff_df.to_csv(savepath,index=False)
    except OSError:
        logger.warning('The filepath %s could not be found or accessed to save the cluster stability metric.',savepath)
    else:
        logger.info('The similarity in cluster assignments between two runs with different seeds is %s percent.',str(perc_diff))


def final_cluster_fit(df,cluster_cols,init_type,n_init,max_iter,random_state,n_clusters,label_col,label_col2,label_map,player_type_col,scatterx_col,scattery_col,palette,clust_title,clust_plot):
    """
    Run K-means clustering and assign a cluster label to each player
    Args:
        df: (Pandas DataFrame), Required: Data features based on player statistics to be used in clustering
        cluster_cols (list of Strings), Required: Columns used as features in K-means
        init_type (String), Required: Initialization method for K-means
        n_init (int), Required: Number of times K-means is run with different starting seeds
        max_iter (int), Required: Maximum number of iterationsfor K-means in one run
        random_state (int), Required: Random seed for K-means
        n_clusters (int), Required: Number of clusters to be used in K-means
        label_col (String), Required: Column name for cluster labels
        label_col2 (String), Required: Column name for cluster labels of second clustering run
        label_map (dict), Required: Mapping of cluster labels to descriptive player types
        player_type_col (String), Required: Column for newly created player type labels
        scatterx_col (String), Required: Column used as X-axis in scatterplot
        scattery_col (String), Required: Column used as Y-axis in scatterplot
        palette (String), Required: Color palette used in plots
        clust_title (String), Required: Title for cluster visualization plot
        clust_plot (String), Required: Path to save cluster visualization
    Returns:
        cluster_assignments: (Pandas DataFrame): Features and new column designating cluster labels for each player
    """
    logger.debug('Attempting to run final K-means fit.')
    # Ensure df is a DataFrame
    if not isinstance(df, pd.DataFrame):
        logger.error('Provided argument `df` is not a Pandas DataFrame object')
        raise TypeError('Provided argument `df` is not a Pandas DataFrame object')

    # Isolate columns to be used as features in clustering
    features = df[cluster_cols]
    # Scale columns prior to clustering to weight all features equally
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    # Fit final kmeans with optimal number of clusters
    kmeans = KMeans(init=init_type,n_clusters=n_clusters,n_init=n_init,max_iter=max_iter,random_state=random_state)
    kmeans.fit(scaled_features)
    # Append cluster assignments to the features DataFrame
    df[label_col] = kmeans.labels_
    # Label the clusters with appropriate descriptive names
    df[player_type_col] = df[label_col].map(label_map)

    # Generate a scatterplot that shows the separation between clusters
    sns.scatterplot(data=df, hue=player_type_col, x=scatterx_col, y=scattery_col, palette=palette)
    plt.title(clust_title)
    plt.legend(loc=1)

    try:
        plt.savefig(clust_plot)
    except OSError:
        logger.warning('The filepath %s could not be found or accessed to save the clustering visualization.',clust_plot)
    else:
        logger.info('Clustering visualizaion saved to %s',clust_plot)

    # Drop unneeded column
    cluster_assignments = df.drop([label_col,label_col2],axis=1)
    logger.info('Cluster assignments DataFrame generated.')
    return cluster_assignments
