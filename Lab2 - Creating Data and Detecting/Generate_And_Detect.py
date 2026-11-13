import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import IsolationForest

# Set visual style and random seed for reproducibility
sns.set_theme(style='whitegrid')
np.random.seed(42)

# Create output directory for datasets and charts
OUTDIR = 'results'
os.makedirs(OUTDIR, exist_ok=True)

print('Step 1: Generating synthetic bank traffic data...')
days = 30
hours = list(range(4, 17))  # Observation window from 4:00 AM to 4:00 PM

data = []
for day in range(1, days + 1):
  for h in hours:
    # Define operating rules and traffic expectations based on time
    if 7 <= h <= 13:  # Client hours (normal peak traffic)
      count = int(np.random.normal(25, 6))
      zone = 'Client Hours'
    elif h in [6, 14]:  # Staff hours (low traffic)
      count = int(np.random.normal(5, 2))
      zone = 'Staff Hours'
    else:  # Closed hours (night / late afternoon)
      count = int(np.random.exponential(0.5))
      zone = 'Closed Hours'

    # Inject intentional security anomalies for testing the model
    if day == 5 and h == 4:  # Early morning break-in attempt
      count = 12
    elif day == 12 and h == 15:  # Door left unlocked after closing
      count = 18
    elif day == 20 and h == 5:  # Predawn suspicious activity
      count = 5

    data.append({
        'day': day,
        'hour': h,
        'people_count': max(0, count),
        'zone': zone,
    })

df = pd.DataFrame(data)

print('Step 2: Training Isolation Forest model...')
X = df[['hour', 'people_count']]
# Isolation Forest for unsupervised contextual anomaly detection
model = IsolationForest(contamination=0.03, random_state=42)
df['anomaly_score'] = model.fit_predict(X)
df['is_anomaly'] = df['anomaly_score'] == -1

# Save datasets to CSV files inside the results folder
df.to_csv(f'{OUTDIR}/raw_bank_traffic.csv', index=False)
anomalies = df[df['is_anomaly']]
anomalies.to_csv(f'{OUTDIR}/detected_security_anomalies.csv', index=False)

print(
    f'Processed {len(df)} records. Detected {len(anomalies)} security'
    ' anomalies.'
)

print('Step 3: Generating analytical charts...')

# Chart 1: Daily traffic trend across operating zones
plt.figure(figsize=(10, 5))
sns.lineplot(
    data=df,
    x='hour',
    y='people_count',
    hue='zone',
    marker='o',
    palette='Set2',
    linewidth=2.5,
)
plt.title('Bank Traffic Trend Across Operating Zones', fontsize=14, weight='bold')
plt.xlabel('Hour of Day (4 AM - 4 PM)', fontsize=12)
plt.ylabel('Average People Count', fontsize=12)
plt.legend(title='Zone Type')
plt.tight_layout()
plt.savefig(f'{OUTDIR}/chart_1_traffic_trend.png', dpi=300)
plt.close()

# Chart 2: Statistical distribution of traffic per security zone
plt.figure(figsize=(9, 5))
sns.boxplot(
    data=df,
    x='zone',
    y='people_count',
    palette='Pastel1',
    hue='zone',
    legend=False,
)
plt.title('Traffic Distribution per Security Zone', fontsize=14, weight='bold')
plt.xlabel('Security Zone', fontsize=12)
plt.ylabel('People Count', fontsize=12)
plt.tight_layout()
plt.savefig(f'{OUTDIR}/chart_2_distribution.png', dpi=300)
plt.close()

# Chart 3: Isolation Forest model decisions (Scatter plot with anomalies highlighted)
plt.figure(figsize=(11, 6))
normal = df[~df['is_anomaly']]
anom = df[df['is_anomaly']]

plt.scatter(
    normal['hour'],
    normal['people_count'],
    c='#3498db',
    label='Normal Traffic',
    alpha=0.6,
    s=40,
)
plt.scatter(
    anom['hour'],
    anom['people_count'],
    c='#e74c3c',
    label='Detected Anomaly',
    marker='X',
    s=140,
    edgecolors='black',
)

plt.title(
    'Isolation Forest: Contextual Security Anomalies Detection',
    fontsize=14,
    weight='bold',
)
plt.xlabel('Hour of Day (4 AM - 4 PM)', fontsize=12)
plt.ylabel('Number of People Entered', fontsize=12)

# Highlight operational time zones on the plot
plt.axvspan(7, 13.5, color='green', alpha=0.08, label='Client Hours (Open)')
plt.axvspan(5.5, 6.5, color='orange', alpha=0.08, label='Staff Hours')
plt.axvspan(13.5, 14.5, color='orange', alpha=0.08)

plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig(f'{OUTDIR}/chart_3_isolation_forest.png', dpi=300)
plt.close()

print('All files and 3 charts successfully generated inside the "results/" folder!')
