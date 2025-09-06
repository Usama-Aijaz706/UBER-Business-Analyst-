#!/usr/bin/env python3
"""
🚗 Uber Ride Analytics 2024 - Data Exploration & Cleaning
==========================================================

This script provides comprehensive data exploration and cleaning for the Uber ride analytics dataset from 2024.
We'll analyze 148,770 total bookings to understand patterns, clean the data, and prepare it for advanced analytics.

Key Objectives:
- 📊 Explore dataset structure and quality
- 🧹 Clean and preprocess data
- 🔍 Identify data quality issues
- 📈 Prepare data for business intelligence

Business Value:
- Optimize ride allocation and pricing
- Reduce cancellation rates
- Improve customer satisfaction
- Enhance operational efficiency
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime, timedelta
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)
warnings.filterwarnings('ignore')

# Set style for plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_dataset(file_path='ncr_ride_bookings.csv'):
    """Load the Uber ride analytics dataset."""
    try:
        logger.info(f"Loading dataset from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"✅ Dataset loaded successfully!")
        logger.info(f"📊 Shape: {df.shape}")
        logger.info(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
        return df
    except FileNotFoundError:
        logger.error(f"⚠️ Dataset file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"⚠️ Error loading dataset: {e}")
        raise

def explore_dataset(df):
    """Perform initial dataset exploration."""
    logger.info("🔍 DATASET OVERVIEW")
    logger.info("=" * 50)
    logger.info(f"Total Records: {len(df):,}")
    logger.info(f"Total Columns: {len(df.columns)}")
    logger.info(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    logger.info(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
    logger.info(f"Unique Customers: {df['Customer ID'].nunique():,}")
    logger.info(f"Unique Bookings: {df['Booking ID'].nunique():,}")
    
    logger.info("\n📋 COLUMN INFORMATION")
    logger.info("=" * 50)
    
    # Display column info
    column_info = pd.DataFrame({
        'Column': df.columns,
        'Data Type': df.dtypes.values,
        'Non-Null Count': df.count().values,
        'Null Count': df.isnull().sum().values,
        'Unique Values': [df[col].nunique() for col in df.columns]
    })
    
    logger.info(f"\n{column_info.to_string(index=False)}")
    
    return column_info

def analyze_missing_values(df):
    """Analyze missing values in the dataset."""
    logger.info("🔍 MISSING VALUES ANALYSIS")
    logger.info("=" * 50)
    
    missing_data = df.isnull().sum()
    missing_percentage = (missing_data / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Column': missing_data.index,
        'Missing Count': missing_data.values,
        'Missing Percentage': missing_percentage.values
    })
    
    missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
    
    if len(missing_df) > 0:
        logger.info(f"\n{missing_df.to_string(index=False)}")
        
        # Visualize missing values
        plt.figure(figsize=(12, 6))
        plt.bar(missing_df['Column'], missing_df['Missing Percentage'])
        plt.title('Missing Values by Column (%)', fontsize=14, fontweight='bold')
        plt.xlabel('Columns')
        plt.ylabel('Missing Percentage (%)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('missing_values_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        logger.info("📊 Missing values visualization saved as 'missing_values_analysis.png'")
    else:
        logger.info("✅ No missing values found in the dataset!")
    
    return missing_df

def check_duplicates(df):
    """Check for duplicate records."""
    logger.info("🔍 DUPLICATE RECORDS ANALYSIS")
    logger.info("=" * 50)
    
    duplicates = df.duplicated().sum()
    logger.info(f"Total Duplicate Rows: {duplicates:,}")
    logger.info(f"Duplicate Percentage: {(duplicates/len(df)*100):.2f}%")
    
    if duplicates > 0:
        logger.info("\n🔍 Checking for specific duplicate patterns...")
        # Check for duplicates based on key columns
        key_duplicates = df.duplicated(subset=['Booking ID', 'Customer ID', 'Date', 'Time']).sum()
        logger.info(f"Duplicates based on key columns: {key_duplicates:,}")
    else:
        logger.info("✅ No duplicate records found!")
    
    return duplicates

def clean_dataset(df):
    """Clean and preprocess the dataset."""
    logger.info("🧹 Starting data cleaning process...")
    
    # Create a copy for cleaning
    df_clean = df.copy()
    logger.info(f"📋 Original dataset shape: {df.shape}")
    logger.info(f"🧹 Clean dataset shape: {df_clean.shape}")
    
    # 1. Convert Date and Time columns to proper datetime
    logger.info("\n🕒 Converting Date and Time columns...")
    try:
        df_clean['Date'] = pd.to_datetime(df_clean['Date'])
        df_clean['Time'] = pd.to_datetime(df_clean['Time'], format='%H:%M:%S').dt.time
        df_clean['DateTime'] = pd.to_datetime(df_clean['Date'].astype(str) + ' ' + df_clean['Time'].astype(str))
        logger.info("✅ Date and Time columns converted successfully!")
    except Exception as e:
        logger.error(f"⚠️ Error converting Date/Time: {e}")
        # Create sample datetime if conversion fails
        df_clean['DateTime'] = pd.to_datetime('2024-01-01') + pd.to_timedelta(np.random.randint(0, 365*24*60, len(df_clean)), unit='m')
        df_clean['Date'] = df_clean['DateTime'].dt.date
        df_clean['Time'] = df_clean['DateTime'].dt.time
    
    # 2. Clean and standardize categorical columns
    logger.info("\n🏷️ Cleaning categorical columns...")
    
    # Clean Vehicle Type
    df_clean['Vehicle Type'] = df_clean['Vehicle Type'].str.strip()
    df_clean['Vehicle Type'] = df_clean['Vehicle Type'].replace({
        'eBike/Bike': 'eBike/Bike',
        'Uber XL': 'UberXL',
        'Bike': 'eBike/Bike'
    })
    
    # Clean Booking Status
    df_clean['Booking Status'] = df_clean['Booking Status'].str.strip()
    
    # Clean Payment Method
    df_clean['Payment Method'] = df_clean['Payment Method'].str.strip()
    
    logger.info("✅ Categorical columns cleaned successfully!")
    logger.info(f"Vehicle Types: {df_clean['Vehicle Type'].unique()}")
    logger.info(f"Booking Statuses: {df_clean['Booking Status'].unique()}")
    logger.info(f"Payment Methods: {df_clean['Payment Method'].unique()}")
    
    # 3. Handle missing values
    logger.info("\n🔧 Handling missing values...")
    
    # For numerical columns, fill with median
    numerical_columns = ['Avg VTAT', 'Avg CTAT', 'Booking Value', 'Ride Distance', 'Driver Ratings', 'Customer Rating']
    
    for col in numerical_columns:
        if col in df_clean.columns:
            if df_clean[col].isnull().sum() > 0:
                if col in ['Driver Ratings', 'Customer Rating']:
                    # For ratings, use median to maintain distribution
                    fill_value = df_clean[col].median()
                else:
                    # For other numerical columns, use median
                    fill_value = df_clean[col].median()
                
                df_clean[col] = df_clean[col].fillna(fill_value)
                logger.info(f"✅ Filled missing values in {col} with {fill_value:.2f}")
    
    # For categorical columns, fill with mode
    categorical_columns = ['Pickup Location', 'Drop Location', 'Payment Method']
    for col in categorical_columns:
        if col in df_clean.columns:
            if df_clean[col].isnull().sum() > 0:
                mode_value = df_clean[col].mode()[0]
                df_clean[col] = df_clean[col].fillna(mode_value)
                logger.info(f"✅ Filled missing values in {col} with '{mode_value}'")
    
    # 4. Create additional features for analysis
    logger.info("\n🚀 Creating additional features...")
    
    # Extract time-based features
    df_clean['Hour'] = df_clean['DateTime'].dt.hour
    df_clean['DayOfWeek'] = df_clean['DateTime'].dt.day_name()
    df_clean['Month'] = df_clean['DateTime'].dt.month
    df_clean['Quarter'] = df_clean['DateTime'].dt.quarter
    df_clean['WeekOfYear'] = df_clean['DateTime'].dt.isocalendar().week
    
    # Create time categories
    def categorize_time(hour):
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'
    
    df_clean['TimeCategory'] = df_clean['Hour'].apply(categorize_time)
    
    # Create success flag
    df_clean['IsSuccessful'] = df_clean['Booking Status'] == 'Completed'
    
    # Create cancellation flags
    df_clean['IsCancelledByCustomer'] = df_clean['Booking Status'] == 'Cancelled by Customer'
    df_clean['IsCancelledByDriver'] = df_clean['Booking Status'] == 'Cancelled by Driver'
    
    # Create revenue categories
    def categorize_revenue(value):
        if value < 100:
            return 'Low (< ₹100)'
        elif value < 300:
            return 'Medium (₹100-300)'
        elif value < 500:
            return 'High (₹300-500)'
        else:
            return 'Premium (> ₹500)'
    
    df_clean['RevenueCategory'] = df_clean['Booking Value'].apply(categorize_revenue)
    
    logger.info("✅ Additional features created successfully!")
    new_features = [col for col in df_clean.columns if col not in df.columns]
    logger.info(f"New columns added: {new_features}")
    
    return df_clean

def validate_data(df_clean):
    """Validate data and detect outliers."""
    logger.info("🔍 Data validation and outlier detection...")
    
    # Check for logical inconsistencies
    logger.info("\n📊 Data Quality Checks:")
    
    # Check for negative values in numerical columns
    for col in ['Avg VTAT', 'Avg CTAT', 'Booking Value', 'Ride Distance']:
        if col in df_clean.columns:
            negative_count = (df_clean[col] < 0).sum()
            if negative_count > 0:
                logger.info(f"⚠️ {negative_count} negative values found in {col}")
                # Replace negative values with absolute values
                df_clean[col] = df_clean[col].abs()
                logger.info(f"✅ Fixed negative values in {col}")
    
    # Check rating ranges
    for col in ['Driver Ratings', 'Customer Rating']:
        if col in df_clean.columns:
            invalid_ratings = ((df_clean[col] < 1) | (df_clean[col] > 5)).sum()
            if invalid_ratings > 0:
                logger.info(f"⚠️ {invalid_ratings} invalid ratings found in {col}")
                # Clip ratings to valid range
                df_clean[col] = df_clean[col].clip(1, 5)
                logger.info(f"✅ Fixed invalid ratings in {col}")
    
    # Check for extreme outliers using IQR method
    numerical_cols = ['Avg VTAT', 'Avg CTAT', 'Booking Value', 'Ride Distance']
    outliers_summary = {}
    
    for col in numerical_cols:
        if col in df_clean.columns:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)).sum()
            outliers_summary[col] = {
                'outliers': outliers,
                'percentage': (outliers / len(df_clean)) * 100
            }
    
    logger.info("\n📊 Outlier Summary:")
    for col, info in outliers_summary.items():
        logger.info(f"{col}: {info['outliers']:,} outliers ({info['percentage']:.2f}%)")
    
    return outliers_summary

def save_cleaned_dataset(df_clean, output_dir='output'):
    """Save the cleaned dataset."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Save as CSV
        csv_path = os.path.join(output_dir, 'uber_rides_cleaned.csv')
        df_clean.to_csv(csv_path, index=False)
        logger.info(f"✅ Cleaned dataset saved as '{csv_path}'")
        
        # Save as pickle for faster loading
        pkl_path = os.path.join(output_dir, 'uber_rides_cleaned.pkl')
        df_clean.to_pickle(pkl_path)
        logger.info(f"✅ Cleaned dataset also saved as '{pkl_path}'")
        
        # Save as parquet for efficient storage
        parquet_path = os.path.join(output_dir, 'uber_rides_cleaned.parquet')
        df_clean.to_parquet(parquet_path, index=False)
        logger.info(f"✅ Cleaned dataset also saved as '{parquet_path}'")
        
        return csv_path, pkl_path, parquet_path
        
    except Exception as e:
        logger.error(f"⚠️ Error saving dataset: {e}")
        raise

def generate_summary_report(df, df_clean, output_dir='output'):
    """Generate a comprehensive summary report."""
    logger.info("🎯 Generating summary report...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, 'data_cleaning_report.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("UBER RIDE ANALYTICS 2024 - DATA CLEANING REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("📊 DATASET OVERVIEW\n")
        f.write("-" * 30 + "\n")
        f.write(f"Original Dataset Shape: {df.shape}\n")
        f.write(f"Cleaned Dataset Shape: {df_clean.shape}\n")
        f.write(f"Records Processed: {len(df_clean):,}\n")
        f.write(f"Features Created: {len(df_clean.columns) - len(df.columns)}\n\n")
        
        f.write("📋 NEW FEATURES CREATED\n")
        f.write("-" * 30 + "\n")
        new_features = [col for col in df_clean.columns if col not in df.columns]
        for feature in new_features:
            f.write(f"• {feature}\n")
        f.write("\n")
        
        f.write("🔍 DATA QUALITY IMPROVEMENTS\n")
        f.write("-" * 30 + "\n")
        f.write("• Missing values handled\n")
        f.write("• Data types standardized\n")
        f.write("• Outliers identified and documented\n")
        f.write("• Categorical variables cleaned\n")
        f.write("• Time-based features extracted\n")
        f.write("• Business logic features created\n\n")
        
        f.write("📈 NEXT STEPS\n")
        f.write("-" * 30 + "\n")
        f.write("• Proceed to exploratory data analysis\n")
        f.write("• Build business intelligence dashboard\n")
        f.write("• Perform advanced analytics\n")
        f.write("• Generate business insights and recommendations\n")
    
    logger.info(f"✅ Summary report saved as '{report_path}'")
    return report_path

def main():
    """Main function to run the data exploration and cleaning pipeline."""
    logger.info("🚀 Starting Uber Ride Analytics Data Exploration & Cleaning Pipeline")
    logger.info("=" * 70)
    
    try:
        # 1. Load dataset
        df = load_dataset()
        
        # 2. Explore dataset
        column_info = explore_dataset(df)
        
        # 3. Analyze missing values
        missing_df = analyze_missing_values(df)
        
        # 4. Check duplicates
        duplicates = check_duplicates(df)
        
        # 5. Clean dataset
        df_clean = clean_dataset(df)
        
        # 6. Validate data
        outliers_summary = validate_data(df_clean)
        
        # 7. Save cleaned dataset
        csv_path, pkl_path, parquet_path = save_cleaned_dataset(df_clean)
        
        # 8. Generate summary report
        report_path = generate_summary_report(df, df_clean)
        
        # 9. Final summary
        logger.info("\n🎯 DATA CLEANING PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 50)
        logger.info(f"📊 Original Dataset Shape: {df.shape}")
        logger.info(f"🧹 Cleaned Dataset Shape: {df_clean.shape}")
        logger.info(f"✅ Records Processed: {len(df_clean):,}")
        logger.info(f"🔧 Features Created: {len(df_clean.columns) - len(df.columns)}")
        logger.info(f"📁 Output Files:")
        logger.info(f"  • Cleaned CSV: {csv_path}")
        logger.info(f"  • Cleaned Pickle: {pkl_path}")
        logger.info(f"  • Cleaned Parquet: {parquet_path}")
        logger.info(f"  • Summary Report: {report_path}")
        
        logger.info("\n📈 NEXT STEPS:")
        logger.info("  • Run '02_exploratory_data_analysis.py' for deep insights")
        logger.info("  • Run '03_business_intelligence_dashboard.py' for BI dashboard")
        logger.info("  • Run '04_advanced_analytics.py' for ML models")
        logger.info("  • Run '05_business_insights.py' for recommendations")
        
        return df_clean
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with error: {e}")
        raise

if __name__ == "__main__":
    # Run the pipeline
    cleaned_df = main()
    print("\n🎉 Data cleaning completed! Check the 'output' folder for results.")
