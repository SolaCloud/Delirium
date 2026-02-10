import numpy as np
import pandas as pd
from scipy.optimize import nnls
import seaborn as sns
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def acls_nmf(X, r, max_iter=100, tol=1e-4, random_state=None):
    np.random.seed(random_state)
    n_samples, n_features = X.shape
    W = np.abs(np.random.rand(n_samples, r))
    H = np.abs(np.random.rand(r, n_features))
    
    for _ in range(max_iter):
        for j in range(n_features):
            H[:, j] = nnls(W, X[:, j])[0]
        
        for i in range(n_samples):
            W[i, :] = nnls(H.T, X[i, :])[0]
        
        error = np.linalg.norm(X - W @ H, 'fro')
        if error < tol:
            break
    
    return W, H

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def find_outliers_with_kmeans(data, n_clusters=5, contamination=0.05):
    X = np.array(data)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    
    distances = []
    for i in range(len(X_scaled)):
        cluster_center = kmeans.cluster_centers_[labels[i]]
        distance = np.linalg.norm(X_scaled[i] - cluster_center)
        distances.append(distance)
    
    n_outliers = int(contamination * len(distances))
    outlier_indices = np.argsort(distances)[-n_outliers:]
    
    return outlier_indices.tolist()

df = pd.read_csv('database/Activity.csv')
df['date'] = pd.to_datetime(df['date'])
df['dateonly'] = df['date'].dt.date
grouped = df.groupby(['patient_id', 'dateonly'])

# print(grouped.key())
activity_patterns = []
index_list = []
all_hours = range(18, 24) 

for group_key, group_data in grouped:
    patient_id, date = group_key
    # print(f"===== 病人 ID: {patient_id}, 日期: {date} =====")
    
    reset_group = group_data.reset_index(drop=True)
    reset_group['hour'] = reset_group['date'].dt.hour
    
    test_data = reset_group[['location_name', 'hour']]
    
    period_df = test_data[
        (test_data['hour'] >= 18) & (test_data['hour'] < 24) & 
        (test_data['location_name'] != "Hallway") & 
        (test_data['location_name'] != "Lounge")
    ]
    
    heatmap_data = period_df.groupby(['hour', 'location_name']).size().unstack(fill_value=0)
    
    heatmap_data = heatmap_data.reindex(all_hours, fill_value=0)
    
    all_locations = df['location_name'].unique()
    all_locations = [loc for loc in all_locations if loc not in ["Hallway", "Lounge"]]
    heatmap_data = heatmap_data.reindex(columns=all_locations, fill_value=0)
    
    # print("补全后的heatmap数据：")
    # print(heatmap_data)
    # print("\n" + "-"*50 + "\n")

    r = 2
    W, H = acls_nmf(heatmap_data.values, r, random_state=42)
    h_flat_row = H.flatten(order='C') 
    h_list = []
    for i in h_flat_row:
        h_list.append(i)
    activity_patterns.append(h_list)
    index_list.append((patient_id,date))


outliers = find_outliers_with_kmeans(activity_patterns, n_clusters=2, contamination=0.005)

# print(f"异常值的索引: {outliers}")
# print("异常值数据:")
# for idx in outliers:
#     print(f"索引 {idx}: {activity_patterns[idx]}")

#     print(f"索引 {idx}: {index_list[idx]}")
