import pandas as pd
import numpy as np

print("=" * 60)
print("STEP 1: DATA QUALITY CHECK & CLEANING")
print("=" * 60)

# Load data with proper encoding
df = pd.read_csv('data/OnlineRetail.csv', encoding='ISO-8859-1')

print(f"\n📊 Original dataset: {len(df)} rows, {df.shape[1]} columns")
print(f"Columns: {list(df.columns)}")

# -------- STEP 1: Check for issues --------
print("\n" + "=" * 60)
print("DATA QUALITY ISSUES:")
print("=" * 60)

print(f"\n1. Missing values:")
print(df.isnull().sum())

print(f"\n2. Duplicate rows: {df.duplicated().sum()}")

print(f"\n3. Rows with negative Quantity (returns): {(df['Quantity'] < 0).sum()}")

print(f"\n4. Rows with zero/negative UnitPrice: {(df['UnitPrice'] <= 0).sum()}")

print(f"\n5. Missing InvoiceDate or CustomerID:")
print(f"   - Missing InvoiceDate: {df['InvoiceDate'].isnull().sum()}")
print(f"   - Missing CustomerID: {df['CustomerID'].isnull().sum()}")

print(f"\n6. Unique InvoiceNo: {df['InvoiceNo'].nunique()}")
print(f"   Unique CustomerID: {df['CustomerID'].nunique()}")

# -------- STEP 2: CLEAN DATA --------
print("\n" + "=" * 60)
print("CLEANING DATA...")
print("=" * 60)

df_clean = df.copy()

# Remove rows with missing essential fields
df_clean = df_clean.dropna(subset=['InvoiceDate', 'CustomerID'])
print(f"✓ After removing null CustomerID/InvoiceDate: {len(df_clean)} rows")

# Remove duplicate rows
df_clean = df_clean.drop_duplicates()
print(f"✓ After removing exact duplicates: {len(df_clean)} rows")

# Remove negative quantities (returns)
df_clean = df_clean[df_clean['Quantity'] > 0]
print(f"✓ After removing returns (negative Qty): {len(df_clean)} rows")

# Remove zero or negative prices
df_clean = df_clean[df_clean['UnitPrice'] > 0]
print(f"✓ After removing invalid prices: {len(df_clean)} rows")

# Remove outliers (extremely high prices/quantities)
df_clean = df_clean[df_clean['Quantity'] <= df_clean['Quantity'].quantile(0.99)]
df_clean = df_clean[df_clean['UnitPrice'] <= df_clean['UnitPrice'].quantile(0.99)]
print(f"✓ After removing 1% outliers: {len(df_clean)} rows")

# Convert types
df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
df_clean['CustomerID'] = df_clean['CustomerID'].astype(int)
df_clean['TotalPrice'] = df_clean['Quantity'] * df_clean['UnitPrice']

print(f"\n✓ Final cleaned dataset: {len(df_clean)} rows")
print(f"   Unique Customers: {df_clean['CustomerID'].nunique()}")
print(f"   Date Range: {df_clean['InvoiceDate'].min()} to {df_clean['InvoiceDate'].max()}")
print(f"   Total Revenue: ${df_clean['TotalPrice'].sum():,.2f}")

# Save cleaned data
df_clean.to_csv('data/OnlineRetail_Clean.csv', index=False)
print(f"\n✓ Saved cleaned data to: data/OnlineRetail_Clean.csv")

print("\n" + "=" * 60)
print("✓ DATA CLEANING COMPLETE - Run rfm_analysis.py next")
print("=" * 60)
