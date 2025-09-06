#!/usr/bin/env python3
"""
📊 Uber Ride Analytics 2024 - Exploratory Data Analysis
========================================================

This script performs comprehensive exploratory data analysis on the cleaned Uber ride analytics dataset.
We'll uncover patterns, trends, and insights to drive business decisions.

Key Objectives:
- 📈 Analyze temporal patterns and trends
- 🚗 Understand vehicle performance and preferences
- 💰 Explore revenue and pricing insights
- 📍 Analyze geographic patterns
- ⭐ Investigate customer satisfaction and ratings
- 🚫 Understand cancellation patterns

Business Value:
- Identify peak hours and demand patterns
- Optimize vehicle fleet allocation
- Improve pricing strategies
- Reduce operational inefficiencies
- Enhance customer experience
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
import logging
from datetime import datetime, timedelta

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

def load_cleaned_data(file_path='output/uber_rides_cleaned.pkl'):
    """Load the cleaned dataset."""
    try:
        logger.info(f"Loading cleaned dataset from {file_path}")
        if file_path.endswith('.pkl'):
            df = pd.read_pickle(file_path)
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        logger.info(f"✅ Cleaned dataset loaded successfully!")
        logger.info(f"📊 Shape: {df.shape}")
        return df
    except FileNotFoundError:
        logger.error(f"⚠️ Cleaned dataset file not found: {file_path}")
        logger.info("💡 Please run '01_data_exploration_cleaning.py' first to generate cleaned data")
        raise
    except Exception as e:
        logger.error(f"⚠️ Error loading cleaned dataset: {e}")
        raise

def analyze_temporal_patterns(df):
    """Analyze temporal patterns in the data."""
    logger.info("🕒 Analyzing temporal patterns...")
    
    # Create output directory
    os.makedirs('output/eda', exist_ok=True)
    
    # 1. Hourly patterns
    logger.info("📊 Analyzing hourly patterns...")
    hourly_stats = df.groupby('Hour').agg({
        'Booking ID': 'count',
        'IsSuccessful': 'mean',
        'Booking Value': 'mean',
        'Ride Distance': 'mean'
    }).rename(columns={
        'Booking ID': 'Total_Bookings',
        'IsSuccessful': 'Success_Rate',
        'Booking Value': 'Avg_Booking_Value',
        'Ride Distance': 'Avg_Ride_Distance'
    })
    
    # Plot hourly patterns
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Total bookings by hour
    axes[0, 0].bar(hourly_stats.index, hourly_stats['Total_Bookings'])
    axes[0, 0].set_title('Total Bookings by Hour', fontweight='bold')
    axes[0, 0].set_xlabel('Hour of Day')
    axes[0, 0].set_ylabel('Number of Bookings')
    
    # Success rate by hour
    axes[0, 1].plot(hourly_stats.index, hourly_stats['Success_Rate'] * 100, marker='o')
    axes[0, 1].set_title('Success Rate by Hour', fontweight='bold')
    axes[0, 1].set_xlabel('Hour of Day')
    axes[0, 1].set_ylabel('Success Rate (%)')
    axes[0, 1].grid(True)
    
    # Average booking value by hour
    axes[1, 0].plot(hourly_stats.index, hourly_stats['Avg_Booking_Value'], marker='s', color='green')
    axes[1, 0].set_title('Average Booking Value by Hour', fontweight='bold')
    axes[1, 0].set_xlabel('Hour of Day')
    axes[1, 0].set_ylabel('Average Booking Value (₹)')
    axes[1, 0].grid(True)
    
    # Average ride distance by hour
    axes[1, 1].plot(hourly_stats.index, hourly_stats['Avg_Ride_Distance'], marker='^', color='orange')
    axes[1, 1].set_title('Average Ride Distance by Hour', fontweight='bold')
    axes[1, 1].set_xlabel('Hour of Day')
    axes[1, 1].set_ylabel('Average Ride Distance (km)')
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('output/eda/hourly_patterns.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Daily patterns
    logger.info("📅 Analyzing daily patterns...")
    daily_stats = df.groupby('DayOfWeek').agg({
        'Booking ID': 'count',
        'IsSuccessful': 'mean',
        'Booking Value': 'mean'
    }).rename(columns={
        'Booking ID': 'Total_Bookings',
        'IsSuccessful': 'Success_Rate',
        'Booking Value': 'Avg_Booking_Value'
    })
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats = daily_stats.reindex(day_order)
    
    # Plot daily patterns
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    axes[0].bar(daily_stats.index, daily_stats['Total_Bookings'])
    axes[0].set_title('Total Bookings by Day of Week', fontweight='bold')
    axes[0].set_xlabel('Day of Week')
    axes[0].set_ylabel('Number of Bookings')
    axes[0].tick_params(axis='x', rotation=45)
    
    axes[1].bar(daily_stats.index, daily_stats['Success_Rate'] * 100)
    axes[1].set_title('Success Rate by Day of Week', fontweight='bold')
    axes[1].set_xlabel('Day of Week')
    axes[1].set_ylabel('Success Rate (%)')
    axes[1].tick_params(axis='x', rotation=45)
    
    axes[2].bar(daily_stats.index, daily_stats['Avg_Booking_Value'])
    axes[2].set_title('Average Booking Value by Day of Week', fontweight='bold')
    axes[2].set_xlabel('Day of Week')
    axes[2].set_ylabel('Average Booking Value (₹)')
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('output/eda/daily_patterns.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. Monthly patterns
    logger.info("📆 Analyzing monthly patterns...")
    monthly_stats = df.groupby('Month').agg({
        'Booking ID': 'count',
        'IsSuccessful': 'mean',
        'Booking Value': 'mean'
    }).rename(columns={
        'Booking ID': 'Total_Bookings',
        'IsSuccessful': 'Success_Rate',
        'Booking Value': 'Avg_Booking_Value'
    })
    
    # Plot monthly patterns
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    axes[0].bar(month_names, monthly_stats['Total_Bookings'])
    axes[0].set_title('Total Bookings by Month', fontweight='bold')
    axes[0].set_xlabel('Month')
    axes[0].set_ylabel('Number of Bookings')
    
    axes[1].plot(month_names, monthly_stats['Success_Rate'] * 100, marker='o')
    axes[1].set_title('Success Rate by Month', fontweight='bold')
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('Success Rate (%)')
    axes[1].grid(True)
    
    axes[2].plot(month_names, monthly_stats['Avg_Booking_Value'], marker='s', color='green')
    axes[2].set_title('Average Booking Value by Month', fontweight='bold')
    axes[2].set_xlabel('Month')
    axes[2].set_ylabel('Average Booking Value (₹)')
    axes[2].grid(True)
    
    plt.tight_layout()
    plt.savefig('output/eda/monthly_patterns.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    logger.info("✅ Temporal patterns analysis completed!")
    return hourly_stats, daily_stats, monthly_stats

def analyze_vehicle_performance(df):
    """Analyze vehicle performance and preferences."""
    logger.info("🚗 Analyzing vehicle performance...")
    
    # Vehicle performance analysis
    vehicle_stats = df.groupby('Vehicle Type').agg({
        'Booking ID': 'count',
        'IsSuccessful': 'mean',
        'Booking Value': 'mean',
        'Ride Distance': 'mean',
        'Avg VTAT': 'mean',
        'Avg CTAT': 'mean',
        'Driver Ratings': 'mean',
        'Customer Rating': 'mean'
    }).rename(columns={
        'Booking ID': 'Total_Bookings',
        'IsSuccessful': 'Success_Rate',
        'Booking Value': 'Avg_Booking_Value',
        'Ride Distance': 'Avg_Ride_Distance',
        'Avg VTAT': 'Avg_VTAT',
        'Avg CTAT': 'Avg_CTAT',
        'Driver Ratings': 'Avg_Driver_Rating',
        'Customer Rating': 'Avg_Customer_Rating'
    })
    
    # Sort by total bookings
    vehicle_stats = vehicle_stats.sort_values('Total_Bookings', ascending=False)
    
    # Plot vehicle performance
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Total bookings by vehicle type
    axes[0, 0].bar(vehicle_stats.index, vehicle_stats['Total_Bookings'])
    axes[0, 0].set_title('Total Bookings by Vehicle Type', fontweight='bold')
    axes[0, 0].set_xlabel('Vehicle Type')
    axes[0, 0].set_ylabel('Number of Bookings')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Success rate by vehicle type
    axes[0, 1].bar(vehicle_stats.index, vehicle_stats['Success_Rate'] * 100)
    axes[0, 1].set_title('Success Rate by Vehicle Type', fontweight='bold')
    axes[0, 1].set_xlabel('Vehicle Type')
    axes[0, 1].set_ylabel('Success Rate (%)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Average booking value by vehicle type
    axes[0, 2].bar(vehicle_stats.index, vehicle_stats['Avg_Booking_Value'])
    axes[0, 2].set_title('Average Booking Value by Vehicle Type', fontweight='bold')
    axes[0, 2].set_xlabel('Vehicle Type')
    axes[0, 2].set_ylabel('Average Booking Value (₹)')
    axes[0, 2].tick_params(axis='x', rotation=45)
    
    # Average ride distance by vehicle type
    axes[1, 0].bar(vehicle_stats.index, vehicle_stats['Avg_Ride_Distance'])
    axes[1, 0].set_title('Average Ride Distance by Vehicle Type', fontweight='bold')
    axes[1, 0].set_xlabel('Vehicle Type')
    axes[1, 0].set_ylabel('Average Ride Distance (km)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Average driver rating by vehicle type
    axes[1, 1].bar(vehicle_stats.index, vehicle_stats['Avg_Driver_Rating'])
    axes[1, 1].set_title('Average Driver Rating by Vehicle Type', fontweight='bold')
    axes[1, 1].set_xlabel('Vehicle Type')
    axes[1, 1].set_ylabel('Average Driver Rating')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # Average customer rating by vehicle type
    axes[1, 2].bar(vehicle_stats.index, vehicle_stats['Avg_Customer_Rating'])
    axes[1, 2].set_title('Average Customer Rating by Vehicle Type', fontweight='bold')
    axes[1, 2].set_xlabel('Vehicle Type')
    axes[1, 2].set_ylabel('Average Customer Rating')
    axes[1, 2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('output/eda/vehicle_performance.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    logger.info("✅ Vehicle performance analysis completed!")
    return vehicle_stats

def analyze_revenue_patterns(df):
    """Analyze revenue and pricing patterns."""
    logger.info("💰 Analyzing revenue patterns...")
    
    # Revenue analysis by various dimensions
    revenue_by_time = df.groupby('TimeCategory').agg({
        'Booking Value': ['sum', 'mean', 'count']
    }).round(2)
    revenue_by_time.columns = ['Total_Revenue', 'Avg_Revenue', 'Total_Bookings']
    
    revenue_by_vehicle = df.groupby('Vehicle Type').agg({
        'Booking Value': ['sum', 'mean', 'count']
    }).round(2)
    revenue_by_vehicle.columns = ['Total_Revenue', 'Avg_Revenue', 'Total_Bookings']
    
    revenue_by_payment = df.groupby('Payment Method').agg({
        'Booking Value': ['sum', 'mean', 'count']
    }).round(2)
    revenue_by_payment.columns = ['Total_Revenue', 'Avg_Revenue', 'Total_Bookings']
    
    # Plot revenue patterns
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Revenue by time category
    axes[0, 0].bar(revenue_by_time.index, revenue_by_time['Total_Revenue'])
    axes[0, 0].set_title('Total Revenue by Time Category', fontweight='bold')
    axes[0, 0].set_xlabel('Time Category')
    axes[0, 0].set_ylabel('Total Revenue (₹)')
    
    # Revenue by vehicle type
    axes[0, 1].bar(revenue_by_vehicle.index, revenue_by_vehicle['Total_Revenue'])
    axes[0, 1].set_title('Total Revenue by Vehicle Type', fontweight='bold')
    axes[0, 1].set_xlabel('Vehicle Type')
    axes[0, 1].set_ylabel('Total Revenue (₹)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Revenue by payment method
    axes[1, 0].bar(revenue_by_payment.index, revenue_by_payment['Total_Revenue'])
    axes[1, 0].set_title('Total Revenue by Payment Method', fontweight='bold')
    axes[1, 0].set_xlabel('Payment Method')
    axes[1, 0].set_ylabel('Total Revenue (₹)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Revenue distribution histogram
    axes[1, 1].hist(df['Booking Value'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    axes[1, 1].set_title('Revenue Distribution', fontweight='bold')
    axes[1, 1].set_xlabel('Booking Value (₹)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/eda/revenue_patterns.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    logger.info("✅ Revenue patterns analysis completed!")
    return revenue_by_time, revenue_by_vehicle, revenue_by_payment

def analyze_cancellation_patterns(df):
    """Analyze cancellation patterns and reasons."""
    logger.info("🚫 Analyzing cancellation patterns...")
    
    # Cancellation analysis
    cancellation_stats = df.groupby('Booking Status').agg({
        'Booking ID': 'count',
        'Booking Value': 'sum'
    }).rename(columns={
        'Booking ID': 'Count',
        'Booking Value': 'Lost_Revenue'
    })
    
    cancellation_stats['Percentage'] = (cancellation_stats['Count'] / len(df)) * 100
    cancellation_stats = cancellation_stats.sort_values('Count', ascending=False)
    
    # Plot cancellation patterns
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Cancellation count by status
    axes[0].bar(cancellation_stats.index, cancellation_stats['Count'])
    axes[0].set_title('Bookings by Status', fontweight='bold')
    axes[0].set_xlabel('Booking Status')
    axes[0].set_ylabel('Number of Bookings')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Cancellation percentage by status
    axes[1].pie(cancellation_stats['Count'], labels=cancellation_stats.index, autopct='%1.1f%%')
    axes[1].set_title('Booking Status Distribution', fontweight='bold')
    
    # Lost revenue by status
    axes[2].bar(cancellation_stats.index, cancellation_stats['Lost_Revenue'])
    axes[2].set_title('Lost Revenue by Status', fontweight='bold')
    axes[2].set_xlabel('Booking Status')
    axes[2].set_ylabel('Lost Revenue (₹)')
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('output/eda/cancellation_patterns.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    logger.info("✅ Cancellation patterns analysis completed!")
    return cancellation_stats

def analyze_ratings_and_satisfaction(df):
    """Analyze customer and driver ratings."""
    logger.info("⭐ Analyzing ratings and satisfaction...")
    
    # Ratings analysis
    ratings_stats = df.groupby('Vehicle Type').agg({
        'Driver Ratings': ['mean', 'std', 'count'],
        'Customer Rating': ['mean', 'std', 'count']
    }).round(3)
    
    # Flatten column names
    ratings_stats.columns = ['_'.join(col).strip() for col in ratings_stats.columns.values]
    
    # Plot ratings
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Driver ratings by vehicle type
    vehicle_types = ratings_stats.index
    driver_ratings = ratings_stats['Driver Ratings_mean']
    driver_std = ratings_stats['Driver Ratings_std']
    
    axes[0].bar(vehicle_types, driver_ratings, yerr=driver_std, capsize=5)
    axes[0].set_title('Average Driver Ratings by Vehicle Type', fontweight='bold')
    axes[0].set_xlabel('Vehicle Type')
    axes[0].set_ylabel('Average Driver Rating')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].set_ylim(0, 5)
    
    # Customer ratings by vehicle type
    customer_ratings = ratings_stats['Customer Rating_mean']
    customer_std = ratings_stats['Customer Rating_std']
    
    axes[1].bar(vehicle_types, customer_ratings, yerr=customer_std, capsize=5)
    axes[1].set_title('Average Customer Ratings by Vehicle Type', fontweight='bold')
    axes[1].set_xlabel('Vehicle Type')
    axes[1].set_ylabel('Average Customer Rating')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].set_ylim(0, 5)
    
    plt.tight_layout()
    plt.savefig('output/eda/ratings_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Ratings distribution
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    axes[0].hist(df['Driver Ratings'].dropna(), bins=20, alpha=0.7, color='lightblue', edgecolor='black')
    axes[0].set_title('Driver Ratings Distribution', fontweight='bold')
    axes[0].set_xlabel('Driver Rating')
    axes[0].set_ylabel('Frequency')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].hist(df['Customer Rating'].dropna(), bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[1].set_title('Customer Ratings Distribution', fontweight='bold')
    axes[1].set_xlabel('Customer Rating')
    axes[1].set_ylabel('Frequency')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/eda/ratings_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    logger.info("✅ Ratings analysis completed!")
    return ratings_stats

def generate_eda_report(df, output_dir='output/eda'):
    """Generate comprehensive EDA report."""
    logger.info("📊 Generating EDA report...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, 'eda_report.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("UBER RIDE ANALYTICS 2024 - EXPLORATORY DATA ANALYSIS REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("📊 DATASET OVERVIEW\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total Records: {len(df):,}\n")
        f.write(f"Date Range: {df['Date'].min()} to {df['Date'].max()}\n")
        f.write(f"Vehicle Types: {len(df['Vehicle Type'].unique())}\n")
        f.write(f"Unique Customers: {df['Customer ID'].nunique():,}\n")
        f.write(f"Total Revenue: ₹{df['Booking Value'].sum():,.2f}\n\n")
        
        f.write("🔍 KEY INSIGHTS\n")
        f.write("-" * 30 + "\n")
        
        # Success rate
        success_rate = df['IsSuccessful'].mean() * 100
        f.write(f"• Overall Success Rate: {success_rate:.2f}%\n")
        
        # Top vehicle type
        top_vehicle = df['Vehicle Type'].value_counts().index[0]
        top_vehicle_count = df['Vehicle Type'].value_counts().iloc[0]
        f.write(f"• Most Popular Vehicle: {top_vehicle} ({top_vehicle_count:,} bookings)\n")
        
        # Peak hour
        peak_hour = df['Hour'].value_counts().index[0]
        peak_hour_count = df['Hour'].value_counts().iloc[0]
        f.write(f"• Peak Hour: {peak_hour}:00 ({peak_hour_count:,} bookings)\n")
        
        # Average booking value
        avg_booking = df['Booking Value'].mean()
        f.write(f"• Average Booking Value: ₹{avg_booking:.2f}\n")
        
        # Average customer rating
        avg_customer_rating = df['Customer Rating'].mean()
        f.write(f"• Average Customer Rating: {avg_customer_rating:.2f}/5\n")
        
        f.write("\n📈 BUSINESS RECOMMENDATIONS\n")
        f.write("-" * 30 + "\n")
        f.write("• Optimize vehicle allocation during peak hours\n")
        f.write("• Focus on improving success rates for underperforming vehicle types\n")
        f.write("• Implement dynamic pricing during high-demand periods\n")
        f.write("• Address cancellation reasons to reduce lost revenue\n")
        f.write("• Monitor and improve driver and customer satisfaction\n")
    
    logger.info(f"✅ EDA report saved as '{report_path}'")
    return report_path

def main():
    """Main function to run the exploratory data analysis pipeline."""
    logger.info("🚀 Starting Uber Ride Analytics Exploratory Data Analysis Pipeline")
    logger.info("=" * 70)
    
    try:
        # 1. Load cleaned data
        df = load_cleaned_data()
        
        # 2. Analyze temporal patterns
        hourly_stats, daily_stats, monthly_stats = analyze_temporal_patterns(df)
        
        # 3. Analyze vehicle performance
        vehicle_stats = analyze_vehicle_performance(df)
        
        # 4. Analyze revenue patterns
        revenue_by_time, revenue_by_vehicle, revenue_by_payment = analyze_revenue_patterns(df)
        
        # 5. Analyze cancellation patterns
        cancellation_stats = analyze_cancellation_patterns(df)
        
        # 6. Analyze ratings and satisfaction
        ratings_stats = analyze_ratings_and_satisfaction(df)
        
        # 7. Generate EDA report
        report_path = generate_eda_report(df)
        
        # 8. Final summary
        logger.info("\n🎯 EXPLORATORY DATA ANALYSIS PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"📊 Dataset analyzed: {len(df):,} records")
        logger.info(f"📁 Output files saved in 'output/eda/' directory")
        logger.info(f"📋 EDA Report: {report_path}")
        
        logger.info("\n📈 NEXT STEPS:")
        logger.info("  • Run '03_business_intelligence_dashboard.py' for interactive BI dashboard")
        logger.info("  • Run '04_advanced_analytics.py' for ML models and predictions")
        logger.info("  • Run '05_business_insights.py' for actionable recommendations")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with error: {e}")
        raise

if __name__ == "__main__":
    # Run the pipeline
    analyzed_df = main()
    print("\n🎉 Exploratory data analysis completed! Check the 'output/eda' folder for results.")
