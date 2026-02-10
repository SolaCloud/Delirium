import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

df = pd.read_csv('database/Activity.csv')

df['datetime'] = pd.to_datetime(df['date'])
df['hour'] = df['datetime'].dt.hour
df['date_only'] = df['datetime'].dt.date

patient_id = '0697d'  
df_patient = df[df['patient_id'] == patient_id]

all_dates = df_patient['date_only'].unique()
all_hours = range(24)  
full_index = pd.MultiIndex.from_product([all_dates, all_hours], names=['date_only', 'hour'])

bathroom_visits = (df_patient[df_patient['location_name'] == 'Bathroom']
                  .groupby(['date_only', 'hour'])
                  .size()
                  .reindex(full_index, fill_value=0)
                  .reset_index(name='visit_count'))

if len(bathroom_visits) == 0:
    raise ValueError(f"patient {patient_id} no activity record")

visit_counts = bathroom_visits['visit_count']
mu, std = norm.fit(visit_counts)  

threshold = mu + std

plt.figure(figsize=(12, 6))

sns.histplot(visit_counts, kde=False, stat="density",
            bins=np.arange(visit_counts.max()+2)-0.5, 
            color='skyblue', alpha=0.7,
            discrete=True) 

plt.xticks(range(int(visit_counts.max())+1))

xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'r-', linewidth=2,
        label=f'Parameter (μ={mu:.2f}, σ={std:.2f})')

plt.title(f"Diagram of the normal distribution of patient 0697d's hourly visits to the bathroom", fontsize=14)
plt.xlabel("Count", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.xticks(range(int(visit_counts.max())+1))
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'patient_{patient_id}_bathroom_visit_distribution_with_zeros.png')
plt.show()