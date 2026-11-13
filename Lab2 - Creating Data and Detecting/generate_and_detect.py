import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.patches as patches
from matplotlib.lines import Line2D

N_DAYS = 30
OUTDIR = "results"
np.random.seed(42)

if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)

print("Starting Lab 3: Bank Traffic Anomaly Detection...")
print("Step 1: Generating synthetic bank traffic data (4AM - 4PM)...")

data = []
working_hours = range(7, 14)
staff_hours = [6, 14]
closed_hours = [4, 5, 15]

for day in range(N_DAYS):
    for hour in range(4, 16):
        
        people_count = 0
        
        if hour in working_hours:
            if hour in [11, 12, 13]:
                people_count = np.random.poisson(35)
            else:
                people_count = np.random.poisson(20)
                
        elif hour in staff_hours:
            people_count = np.random.poisson(5)
            
        elif hour in closed_hours:
            if np.random.rand() < 0.1:
                people_count = 1
            else:
                people_count = 0
                
        data.append([day, hour, people_count])

df = pd.DataFrame(data, columns=["day", "hour", "people_count"])

print("Step 2: Injecting security anomalies in closed hours...")

injected_anom1 = [5, 4, 8]
injected_anom2 = [12, 15, 15]
injected_anom3 = [20, 5, 3]

df_anom = pd.DataFrame([injected_anom1, injected_anom2, injected_anom3], columns=df.columns)
df = pd.concat([df, df_anom], ignore_index=True)
df = df.sort_values(["day", "hour"]).reset_index(drop=True)

df.to_csv(f"{OUTDIR}/raw_bank_traffic.csv", index=False)

print("Step 3: Preparing data for ML...")

cols_for_model = ["hour", "people_count"]
X = df[cols_for_model]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("Step 4: Running Isolation Forest...")

model = IsolationForest(n_estimators=200, contamination=0.015, random_state=42)
model.fit(X_scaled)

df['decision'] = model.predict(X_scaled)
df['score'] = model.score_samples(X_scaled)

print(f"Detected {len(df[df['decision'] == -1])} potential anomalies.")
df[df['decision'] == -1].to_csv(f"{OUTDIR}/detected_security_anomalies.csv", index=False)

print("Step 5: Generating visual explanation...")

plt.figure(figsize=(14, 8))
sns.set_style("whitegrid")

sns.scatterplot(
    data=df,
    x='hour',
    y='people_count',
    hue='decision',
    palette={1: '#3498db', -1: '#e74c3c'},
    alpha=0.5,
    s=80,
    x_jitter=0.2
)

ax = plt.gca()
rect_work = patches.Rectangle((7, 0), 7, df['people_count'].max()+5, linewidth=0, facecolor='#2ecc71', alpha=0.1, label='Client Hours')
ax.add_patch(rect_work)

rect_staff1 = patches.Rectangle((6, 0), 1, df['people_count'].max()+5, linewidth=0, facecolor='#f1c40f', alpha=0.1, label='Staff Only')
rect_staff2 = patches.Rectangle((14, 0), 1, df['people_count'].max()+5, linewidth=0, facecolor='#f1c40f', alpha=0.1)
ax.add_patch(rect_staff1)
ax.add_patch(rect_staff2)

injected_anomalies = df[df.apply(lambda row: [row['day'], row['hour'], row['people_count']] in [injected_anom1, injected_anom2, injected_anom3], axis=1)]

for i, row in injected_anomalies.iterrows():
    plt.annotate(f"Day {int(row['day'])}\n({int(row['people_count'])} ppl)", 
                 xy=(row['hour'], row['people_count']),
                 xytext=(15, 10), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', color='black'))
    
detected_anoms = df[df['decision'] == -1]
plt.scatter(detected_anoms['hour'], detected_anoms['people_count'], s=150, linewidth=2, facecolors='none', edgecolors='#c0392b')

plt.title("Bank Physical Security: Human Traffic Anomaly Detection\nIsolation Forest detects violations of operating hours context", fontsize=16)
plt.xlabel("Hour of Day (4AM - 4PM)", fontsize=12)
plt.ylabel("Number of People Entered", fontsize=12)
plt.xticks(range(4, 16))

handles, labels = ax.get_legend_handles_labels()
custom_lines = [Line2D([0], [0], color='#3498db', marker='o', linestyle=''),
                Line2D([0], [0], color='#e74c3c', marker='o', linestyle=''),
                Line2D([0], [0], color='#c0392b', marker='o', linestyle='', markersize=12, markeredgewidth=2, markerfacecolor='none')]
plt.legend(custom_lines + handles[0:2], ['Normal', 'Detected Anomaly', 'Anomaly Cluster Highlight', 'Client Hours (7-14)', 'Staff Hours (6, 14)'], loc='upper left')

plt.tight_layout()
plt.savefig(f"{OUTDIR}/bank_traffic_chart.png")
print(f"Graph saved to {OUTDIR}/bank_traffic_chart.png")
print("Process complete.")