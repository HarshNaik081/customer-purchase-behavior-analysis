import pandas as pd

print("=" * 60)
print("STEP 2: RFM SEGMENTATION ANALYSIS")
print("=" * 60)

# Load cleaned data
df = pd.read_csv('data/OnlineRetail_Clean.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Set snapshot date for Recency calculation
snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

print(f"\nAnalysis Date: {snapshot_date.date()}")
print(f"Data Range: {df['InvoiceDate'].min().date()} to {df['InvoiceDate'].max().date()}")

# -------- CALCULATE RFM --------
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,  # Recency
    'InvoiceNo': 'nunique',  # Frequency
    'TotalPrice': 'sum'  # Monetary
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

print(f"\n📊 RFM METRICS:")
print(f"   Recency (days): min={rfm['Recency'].min()}, max={rfm['Recency'].max()}, avg={rfm['Recency'].mean():.0f}")
print(f"   Frequency: min={rfm['Frequency'].min()}, max={rfm['Frequency'].max()}, avg={rfm['Frequency'].mean():.1f}")
print(f"   Monetary: min=${rfm['Monetary'].min():.2f}, max=${rfm['Monetary'].max():.2f}, avg=${rfm['Monetary'].mean():.2f}")

# -------- RFM SCORING (1-4 scale) --------
rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1], duplicates='drop')
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4], duplicates='drop')
rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 4, labels=[1, 2, 3, 4], duplicates='drop')

# Convert to numeric
rfm['R_Score'] = rfm['R_Score'].astype(int)
rfm['F_Score'] = rfm['F_Score'].astype(int)
rfm['M_Score'] = rfm['M_Score'].astype(int)

# -------- SEGMENTATION LOGIC --------
def segment_customers(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
    
    if r >= 3 and f >= 3 and m >= 3:
        return 'Champions'
    elif r >= 3 and f < 3:
        return 'New Customers'
    elif r < 2 and f >= 3 and m >= 3:
        return 'Cannot Lose Them'
    elif r < 2 and f >= 3 and m < 3:
        return 'At Risk'
    elif r < 2 and f < 2:
        return 'Lost'
    else:
        return 'Potential Loyalists'

rfm['Segment'] = rfm.apply(segment_customers, axis=1)

# Save results
rfm.to_csv('rfm_segments.csv', index=False)

print(f"\n✓ RFM SEGMENTATION COMPLETE")
print(f"\n📈 SEGMENT DISTRIBUTION:")
segment_stats = rfm.groupby('Segment').agg({
    'CustomerID': 'count',
    'Monetary': ['sum', 'mean'],
    'Frequency': 'mean'
}).round(2)

segment_stats.columns = ['Count', 'Total Revenue', 'Avg Revenue', 'Avg Orders']
print(segment_stats)

# Revenue concentration
total_revenue = rfm['Monetary'].sum()
rfm_sorted = rfm.sort_values('Monetary', ascending=False)
top_20_pct = rfm_sorted.head(int(len(rfm) * 0.2))
revenue_from_top_20 = (top_20_pct['Monetary'].sum() / total_revenue) * 100

print(f"\n💡 KEY INSIGHT:")
print(f"   Top 20% of customers drive {revenue_from_top_20:.1f}% of revenue")

print(f"\n✓ Saved to: rfm_segments.csv")
print("=" * 60)
