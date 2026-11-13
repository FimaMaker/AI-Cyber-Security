# Laboratory Work: AI-Enhanced Cybersecurity — Anomaly Detection

## 📋 Project Overview
This project demonstrates the implementation of an AI-enhanced physical security monitoring system for a bank branch. Instead of simple threshold rules, we use Machine Learning (**Isolation Forest**) to analyze human foot traffic and detect contextual security violations (e.g., unauthorized entries when the bank is closed).

---

## 🏛️ Business Logic & Scenario
We monitor the main entrance of a bank during a 12-hour observation window **from 4:00 AM to 4:00 PM** across a 30-day period. 

The system understands the time context based on the following operating hours:
1. **Client Hours (7:00 – 13:59):** Bank is open. High traffic is expected (15–40+ people/hour).
2. **Staff Hours (6:00, 14:00):** Only authorized personnel, cleaners, or cash-in-transit (low traffic: 2–8 people/hour).
3. **Closed Hours (4:00–5:59, 15:00):** Bank is fully closed. Traffic should be zero.

---

## 🔬 Methodology & Algorithm
* **Features Used:** `hour` of the day and `people_count`.
* **Model:** **Isolation Forest** (from `scikit-learn`). It isolates observations by randomly selecting features and split values. Rare/anomalous events require fewer splits to isolate, yielding a higher anomaly score.
* **Concept:** This addresses **Contextual Anomalies** (Lecture 3, Slide 07). A low count of people (e.g., 3 people) is completely normal during the day, but highly suspicious at 5:00 AM.

---

## ⚙️ How to Run

1. Make sure you have the required libraries installed:
   ```bash
   pip install -r requirements.txt
