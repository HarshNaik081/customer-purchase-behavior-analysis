import pandas as pd
import numpy as np

print("=" * 60)
print("STEP 3: COHORT ANALYSIS (RETENTION TRACKING)")
print("=" * 60)

# Load cleaned data
df = pd.read_csv('data/OnlineRetail_Clean.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Create year-month periods
df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')

# Get first purchase month per customer
first_purchase = df.groupby('CustomerID')['InvoiceDate'].min()
df['CohortMonth'] = df['CustomerID'].map(first_purchase).dt.to_period('M')

# Calculate months between first purchase and current purchase
df['CohortIndex'] = (df['InvoiceMonth'] - df['CohortMonth']).apply(lambda x: x.n if pd.notna(x) else None)

# Remove any NaN CohortIndex
df = df.dropna(subset=['CohortIndex'])
df['CohortIndex'] = df['CohortIndex'].astype(int)

print(f"\n✓ Date Range: {df['InvoiceDate'].min().date()} to {df['InvoiceDate'].max().date()}")

# -------- BUILD COHORT TABLE --------
cohort_data = df.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
cohort_data.columns = ['CohortMonth', 'MonthIndex', 'Customers']

# Pivot to matrix
cohort_pivot = cohort_data.pivot(index='CohortMonth', columns='MonthIndex', values='Customers')

# Calculate retention rates (%)
cohort_size = cohort_pivot.iloc[:, 0]
retention = cohort_pivot.divide(cohort_size, axis=0) * 100

# Save outputs
cohort_pivot.to_csv('cohort_counts.csv')
retention.round(1).to_csv('cohort_retention.csv')

print(f"\n📊 COHORT SIZES (First Month):")
print(cohort_size.head(10))

print(f"\n📈 RETENTION RATES (%):")
print(retention.round(1).iloc[:, :6])  # Show first 6 months

# Calculate average retention by month index
avg_retention = retention.mean()
print(f"\n💡 AVERAGE RETENTION BY MONTH:")
for month in range(min(6, len(avg_retention))):
    print(f"   Month {month}: {avg_retention.iloc[month]:.1f}%")

# Find repeat purchase rate
month_1_retention = retention.iloc[:, 1].mean() if retention.shape[1] > 1 else None
if month_1_retention:
    print(f"\n💡 KEY INSIGHT:")
    print(f"   Repeat purchase rate (Month 1): {month_1_retention:.1f}%")
    print(f"   (% of customers who buy again within 1 month)")

print(f"\n✓ Saved outputs:")
print(f"   - cohort_counts.csv (raw customer counts)")
print(f"   - cohort_retention.csv (retention %)")
print("=" * 60)
