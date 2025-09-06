#!/usr/bin/env python3
"""
🤖 Uber Ride Analytics 2024 - Advanced Analytics & Machine Learning
====================================================================

This script performs advanced analytics and machine learning on the cleaned Uber ride analytics dataset.
We'll build predictive models, perform clustering analysis, and generate actionable business insights.

Key Features:
- 🎯 Predictive modeling for ride success
- 🔍 Customer segmentation and clustering
- 📊 Demand forecasting and time series analysis
- 💰 Revenue optimization models
- 🚗 Vehicle allocation optimization
- ⭐ Customer satisfaction prediction

Business Value:
- Predict ride success probability
- Identify high-value customer segments
- Optimize vehicle fleet allocation
- Forecast demand patterns
- Improve revenue optimization
- Enhance customer experience
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import logging
from datetime import datetime, timedelta
import argparse

# Machine Learning Libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
import xgboost as xgb
import lightgbm as lgb

# Time Series Analysis
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA

# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')

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

def prepare_features_for_ml(df):
    """Prepare features for machine learning models."""
    logger.info("🔧 Preparing features for machine learning...")
    
    # Create a copy for feature engineering
    df_ml = df.copy()
    
    # 1. Encode categorical variables
    categorical_columns = ['Vehicle Type', 'Payment Method', 'TimeCategory', 'DayOfWeek', 'RevenueCategory']
    
    for col in categorical_columns:
        if col in df_ml.columns:
            le = LabelEncoder()
            df_ml[f'{col}_encoded'] = le.fit_transform(df_ml[col].astype(str))
    
    # 2. Create numerical features
    df_ml['Hour_sin'] = np.sin(2 * np.pi * df_ml['Hour'] / 24)
    df_ml['Hour_cos'] = np.cos(2 * np.pi * df_ml['Hour'] / 24)
    df_ml['Month_sin'] = np.sin(2 * np.pi * df_ml['Month'] / 12)
    df_ml['Month_cos'] = np.cos(2 * np.pi * df_ml['Month'] / 12)
    
    # 3. Create interaction features
    df_ml['Distance_Time_Ratio'] = df_ml['Ride Distance'] / (df_ml['Avg CTAT'] + 1)
    df_ml['Revenue_Distance_Ratio'] = df_ml['Booking Value'] / (df_ml['Ride Distance'] + 1)
    
    # 4. Create aggregated features
    # Average booking value by vehicle type
    vehicle_avg_revenue = df_ml.groupby('Vehicle Type')['Booking Value'].transform('mean')
    df_ml['Vehicle_Avg_Revenue'] = vehicle_avg_revenue
    
    # Average success rate by vehicle type
    vehicle_success_rate = df_ml.groupby('Vehicle Type')['IsSuccessful'].transform('mean')
    df_ml['Vehicle_Success_Rate'] = vehicle_success_rate
    
    # 5. Select features for ML
    feature_columns = [
        'Hour_sin', 'Hour_cos', 'Month_sin', 'Month_cos',
        'Avg VTAT', 'Avg CTAT', 'Booking Value', 'Ride Distance',
        'Driver Ratings', 'Customer Rating',
        'Distance_Time_Ratio', 'Revenue_Distance_Ratio',
        'Vehicle_Avg_Revenue', 'Vehicle_Success_Rate'
    ]
    
    # Add encoded categorical features
    for col in categorical_columns:
        if f'{col}_encoded' in df_ml.columns:
            feature_columns.append(f'{col}_encoded')
    
    # Remove rows with missing values
    df_ml_clean = df_ml[feature_columns + ['IsSuccessful']].dropna()
    
    logger.info(f"✅ Features prepared successfully!")
    logger.info(f"📊 Final dataset shape: {df_ml_clean.shape}")
    logger.info(f"🔧 Number of features: {len(feature_columns)}")
    
    return df_ml_clean, feature_columns

def build_ride_success_prediction_model(df_ml, feature_columns):
    """Build a model to predict ride success probability."""
    logger.info("🎯 Building ride success prediction model...")
    
    # Prepare data
    X = df_ml[feature_columns]
    y = df_ml['IsSuccessful']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Initialize models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42),
        'XGBoost': xgb.XGBClassifier(random_state=42),
        'LightGBM': lgb.LGBMClassifier(random_state=42)
    }
    
    # Train and evaluate models
    results = {}
    best_model = None
    best_score = 0
    
    for name, model in models.items():
        logger.info(f"Training {name}...")
        
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = model.score(X_test_scaled, y_test)
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'auc_score': auc_score,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
        
        logger.info(f"✅ {name} - Accuracy: {accuracy:.4f}, AUC: {auc_score:.4f}")
        
        # Track best model
        if auc_score > best_score:
            best_score = auc_score
            best_model = name
    
    logger.info(f"🏆 Best model: {best_model} (AUC: {best_score:.4f})")
    
    # Feature importance for best model
    best_model_obj = results[best_model]['model']
    if hasattr(best_model_obj, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'Feature': feature_columns,
            'Importance': best_model_obj.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        logger.info("📊 Top 10 Most Important Features:")
        logger.info(feature_importance.head(10).to_string(index=False))
    
    return results, best_model, scaler

def perform_customer_segmentation(df):
    """Perform customer segmentation using clustering."""
    logger.info("👥 Performing customer segmentation...")
    
    # Prepare customer data
    customer_data = df.groupby('Customer ID').agg({
        'Booking ID': 'count',
        'Booking Value': ['sum', 'mean'],
        'IsSuccessful': 'mean',
        'Customer Rating': 'mean',
        'Ride Distance': 'mean'
    }).round(3)
    
    # Flatten column names
    customer_data.columns = ['_'.join(col).strip() for col in customer_data.columns.values]
    customer_data = customer_data.reset_index()
    
    # Remove customers with missing values
    customer_data = customer_data.dropna()
    
    # Select features for clustering
    clustering_features = [
        'Booking ID_count', 'Booking Value_sum', 'Booking Value_mean',
        'IsSuccessful_mean', 'Customer Rating_mean', 'Ride Distance_mean'
    ]
    
    X_clustering = customer_data[clustering_features]
    
    # Scale features
    scaler_clustering = StandardScaler()
    X_scaled = scaler_clustering.fit_transform(X_clustering)
    
    # Determine optimal number of clusters using elbow method
    inertias = []
    K_range = range(2, 11)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
    
    # Plot elbow curve
    plt.figure(figsize=(10, 6))
    plt.plot(K_range, inertias, 'bo-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.title('Elbow Method for Optimal k')
    plt.grid(True)
    plt.savefig('output/ml/customer_segmentation_elbow.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Perform K-means clustering with optimal k (let's use 4 for now)
    optimal_k = 4
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    customer_data['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analyze clusters
    cluster_analysis = customer_data.groupby('Cluster').agg({
        'Booking ID_count': 'mean',
        'Booking Value_sum': 'mean',
        'Booking Value_mean': 'mean',
        'IsSuccessful_mean': 'mean',
        'Customer Rating_mean': 'mean',
        'Customer ID': 'count'
    }).round(3)
    
    cluster_analysis.columns = [
        'Avg_Bookings', 'Avg_Total_Revenue', 'Avg_Booking_Value',
        'Avg_Success_Rate', 'Avg_Customer_Rating', 'Cluster_Size'
    ]
    
    logger.info("📊 Customer Segmentation Results:")
    logger.info(f"\n{cluster_analysis.to_string()}")
    
    # Create output directory
    os.makedirs('output/ml', exist_ok=True)
    
    # Save results
    customer_data.to_csv('output/ml/customer_segments.csv', index=False)
    cluster_analysis.to_csv('output/ml/cluster_analysis.csv')
    
    logger.info("✅ Customer segmentation completed!")
    return customer_data, cluster_analysis

def perform_demand_forecasting(df):
    """Perform demand forecasting using time series analysis."""
    logger.info("📈 Performing demand forecasting...")
    
    # Prepare time series data
    daily_demand = df.groupby('Date')['Booking ID'].count().reset_index()
    daily_demand['Date'] = pd.to_datetime(daily_demand['Date'])
    daily_demand = daily_demand.set_index('Date')
    daily_demand = daily_demand.sort_index()
    
    # Fill missing dates with 0
    date_range = pd.date_range(start=daily_demand.index.min(), end=daily_demand.index.max(), freq='D')
    daily_demand = daily_demand.reindex(date_range, fill_value=0)
    
    # Resample to weekly data for better forecasting
    weekly_demand = daily_demand.resample('W').sum()
    
    # Time series decomposition
    decomposition = seasonal_decompose(weekly_demand, period=4)  # 4 weeks = 1 month
    
    # Plot decomposition
    fig, axes = plt.subplots(4, 1, figsize=(15, 12))
    
    decomposition.observed.plot(ax=axes[0], title='Observed')
    decomposition.trend.plot(ax=axes[1], title='Trend')
    decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
    decomposition.resid.plot(ax=axes[3], title='Residual')
    
    plt.tight_layout()
    plt.savefig('output/ml/time_series_decomposition.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Check stationarity
    adf_result = adfuller(weekly_demand['Booking ID'])
    logger.info(f"📊 Augmented Dickey-Fuller Test:")
    logger.info(f"ADF Statistic: {adf_result[0]:.4f}")
    logger.info(f"p-value: {adf_result[1]:.4f}")
    
    # Simple forecasting using moving average
    weekly_demand['MA_4'] = weekly_demand['Booking ID'].rolling(window=4).mean()
    weekly_demand['MA_8'] = weekly_demand['Booking ID'].rolling(window=8).mean()
    
    # Plot forecasting
    plt.figure(figsize=(15, 6))
    weekly_demand['Booking ID'].plot(label='Actual Demand', alpha=0.7)
    weekly_demand['MA_4'].plot(label='4-Week Moving Average', alpha=0.8)
    weekly_demand['MA_8'].plot(label='8-Week Moving Average', alpha=0.8)
    
    plt.title('Demand Forecasting using Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Number of Bookings')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('output/ml/demand_forecasting.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save results
    weekly_demand.to_csv('output/ml/weekly_demand_forecast.csv')
    
    logger.info("✅ Demand forecasting completed!")
    return weekly_demand

def build_revenue_optimization_model(df):
    """Build a model for revenue optimization."""
    logger.info("💰 Building revenue optimization model...")
    
    # Prepare data for revenue prediction
    revenue_features = [
        'Hour', 'Month', 'Vehicle Type', 'Ride Distance',
        'Avg VTAT', 'Avg CTAT', 'Driver Ratings'
    ]
    
    # Filter for successful rides only
    successful_rides = df[df['IsSuccessful'] == True].copy()
    
    # Encode categorical variables
    le_vehicle = LabelEncoder()
    successful_rides['Vehicle_Type_Encoded'] = le_vehicle.fit_transform(successful_rides['Vehicle Type'])
    
    # Select features
    X_revenue = successful_rides[revenue_features + ['Vehicle_Type_Encoded']].copy()
    y_revenue = successful_rides['Booking Value']
    
    # Remove rows with missing values
    mask = ~(X_revenue.isnull().any(axis=1) | y_revenue.isnull())
    X_revenue = X_revenue[mask]
    y_revenue = y_revenue[mask]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_revenue, y_revenue, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler_revenue = StandardScaler()
    X_train_scaled = scaler_revenue.fit_transform(X_train)
    X_test_scaled = scaler_revenue.transform(X_test)
    
    # Train multiple regression models
    models_revenue = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': xgb.XGBRegressor(random_state=42),
        'LightGBM': lgb.LGBMRegressor(random_state=42)
    }
    
    revenue_results = {}
    best_revenue_model = None
    best_r2 = -np.inf
    
    for name, model in models_revenue.items():
        logger.info(f"Training {name} for revenue prediction...")
        
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        revenue_results[name] = {
            'model': model,
            'r2_score': r2,
            'mse': mse,
            'mae': mae,
            'predictions': y_pred
        }
        
        logger.info(f"✅ {name} - R²: {r2:.4f}, MSE: {mse:.2f}, MAE: {mae:.2f}")
        
        # Track best model
        if r2 > best_r2:
            best_r2 = r2
            best_revenue_model = name
    
    logger.info(f"🏆 Best revenue model: {best_revenue_model} (R²: {best_r2:.4f})")
    
    # Feature importance for best model
    best_revenue_model_obj = revenue_results[best_revenue_model]['model']
    if hasattr(best_revenue_model_obj, 'feature_importances_'):
        feature_importance_revenue = pd.DataFrame({
            'Feature': revenue_features + ['Vehicle_Type_Encoded'],
            'Importance': best_revenue_model_obj.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        logger.info("📊 Top Revenue Prediction Features:")
        logger.info(feature_importance_revenue.head(10).to_string(index=False))
    
    return revenue_results, best_revenue_model, scaler_revenue

def perform_vehicle_allocation_optimization(df):
    """Perform vehicle allocation optimization analysis."""
    logger.info("🚗 Performing vehicle allocation optimization...")
    
    # Analyze vehicle performance by time and location
    vehicle_performance = df.groupby(['Vehicle Type', 'Hour', 'TimeCategory']).agg({
        'Booking ID': 'count',
        'IsSuccessful': 'mean',
        'Booking Value': 'mean',
        'Ride Distance': 'mean'
    }).reset_index()
    
    # Calculate efficiency score
    vehicle_performance['Efficiency_Score'] = (
        vehicle_performance['IsSuccessful'] * 
        vehicle_performance['Booking Value'] / 
        (vehicle_performance['Ride Distance'] + 1)
    )
    
    # Find optimal vehicle allocation by time
    optimal_allocation = vehicle_performance.groupby(['Hour', 'TimeCategory']).apply(
        lambda x: x.loc[x['Efficiency_Score'].idxmax()]
    ).reset_index(drop=True)
    
    # Create heatmap of optimal vehicle allocation
    pivot_optimal = optimal_allocation.pivot_table(
        values='Vehicle Type',
        index='TimeCategory',
        columns='Hour',
        aggfunc='first'
    )
    
    # Plot optimal allocation heatmap
    plt.figure(figsize=(15, 8))
    sns.heatmap(
        pivot_optimal.apply(lambda x: pd.Categorical(x).codes),
        annot=pivot_optimal,
        fmt='',
        cmap='viridis',
        cbar_kws={'label': 'Vehicle Type Index'}
    )
    plt.title('Optimal Vehicle Allocation by Time and Category')
    plt.xlabel('Hour of Day')
    plt.ylabel('Time Category')
    plt.tight_layout()
    plt.savefig('output/ml/optimal_vehicle_allocation.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save results
    optimal_allocation.to_csv('output/ml/optimal_vehicle_allocation.csv', index=False)
    
    logger.info("✅ Vehicle allocation optimization completed!")
    return optimal_allocation

def generate_business_insights(df, results, customer_segments, demand_forecast, revenue_results):
    """Generate comprehensive business insights and recommendations."""
    logger.info("💡 Generating business insights and recommendations...")
    
    # Create output directory
    os.makedirs('output/ml', exist_ok=True)
    
    # Generate insights report
    insights_report = []
    insights_report.append("🚗 UBER RIDE ANALYTICS 2024 - BUSINESS INSIGHTS REPORT")
    insights_report.append("=" * 70)
    insights_report.append("")
    
    # 1. Model Performance Insights
    insights_report.append("📊 MODEL PERFORMANCE INSIGHTS")
    insights_report.append("-" * 40)
    
    best_model = max(results.keys(), key=lambda x: results[x]['auc_score'])
    best_auc = results[best_model]['auc_score']
    insights_report.append(f"• Best Ride Success Prediction Model: {best_model}")
    insights_report.append(f"• Model Accuracy: {results[best_model]['accuracy']:.2%}")
    insights_report.append(f"• AUC Score: {best_auc:.2%}")
    
    if best_auc > 0.8:
        insights_report.append("  → Excellent model performance for ride success prediction")
    elif best_auc > 0.7:
        insights_report.append("  → Good model performance for ride success prediction")
    else:
        insights_report.append("  → Model needs improvement for better predictions")
    
    insights_report.append("")
    
    # 2. Customer Segmentation Insights
    insights_report.append("👥 CUSTOMER SEGMENTATION INSIGHTS")
    insights_report.append("-" * 40)
    
    # Find high-value customers
    high_value_cluster = customer_segments.groupby('Cluster')['Booking Value_sum'].mean().idxmax()
    high_value_avg = customer_segments.groupby('Cluster')['Booking Value_sum'].mean().max()
    
    insights_report.append(f"• High-Value Customer Cluster: {high_value_cluster}")
    insights_report.append(f"• Average Revenue per High-Value Customer: ₹{high_value_avg:,.0f}")
    
    # Find most loyal customers
    loyal_cluster = customer_segments.groupby('Cluster')['Booking ID_count'].mean().idxmax()
    loyal_avg_bookings = customer_segments.groupby('Cluster')['Booking ID_count'].mean().max()
    
    insights_report.append(f"• Most Loyal Customer Cluster: {loyal_cluster}")
    insights_report.append(f"• Average Bookings per Loyal Customer: {loyal_avg_bookings:.1f}")
    
    insights_report.append("")
    
    # 3. Demand Forecasting Insights
    insights_report.append("📈 DEMAND FORECASTING INSIGHTS")
    insights_report.append("-" * 40)
    
    # Calculate demand trends
    recent_demand = demand_forecast['Booking ID'].tail(8).mean()
    earlier_demand = demand_forecast['Booking ID'].head(8).mean()
    demand_change = ((recent_demand - earlier_demand) / earlier_demand) * 100
    
    insights_report.append(f"• Recent Average Weekly Demand: {recent_demand:.0f} bookings")
    insights_report.append(f"• Earlier Average Weekly Demand: {earlier_demand:.0f} bookings")
    insights_report.append(f"• Demand Change: {demand_change:+.1f}%")
    
    if demand_change > 10:
        insights_report.append("  → Strong demand growth - consider expanding fleet")
    elif demand_change < -10:
        insights_report.append("  → Declining demand - investigate causes and optimize operations")
    else:
        insights_report.append("  → Stable demand - maintain current operations")
    
    insights_report.append("")
    
    # 4. Revenue Optimization Insights
    insights_report.append("💰 REVENUE OPTIMIZATION INSIGHTS")
    insights_report.append("-" * 40)
    
    best_revenue_model = max(revenue_results.keys(), key=lambda x: revenue_results[x]['r2_score'])
    best_r2 = revenue_results[best_revenue_model]['r2_score']
    
    insights_report.append(f"• Best Revenue Prediction Model: {best_revenue_model}")
    insights_report.append(f"• Model R² Score: {best_r2:.2%}")
    
    if best_r2 > 0.7:
        insights_report.append("  → Excellent revenue prediction capability")
    elif best_r2 > 0.5:
        insights_report.append("  → Good revenue prediction capability")
    else:
        insights_report.append("  → Revenue prediction needs improvement")
    
    insights_report.append("")
    
    # 5. Strategic Recommendations
    insights_report.append("🎯 STRATEGIC RECOMMENDATIONS")
    insights_report.append("-" * 40)
    
    # Success rate recommendations
    overall_success_rate = df['IsSuccessful'].mean() * 100
    if overall_success_rate < 70:
        insights_report.append("• CRITICAL: Overall success rate below 70%")
        insights_report.append("  → Implement driver training programs")
        insights_report.append("  → Optimize vehicle allocation during peak hours")
        insights_report.append("  → Improve customer communication systems")
    else:
        insights_report.append(f"• SUCCESS: Overall success rate at {overall_success_rate:.1f}%")
        insights_report.append("  → Maintain current operational excellence")
        insights_report.append("  → Focus on revenue optimization")
    
    # Vehicle optimization recommendations
    vehicle_performance = df.groupby('Vehicle Type')['IsSuccessful'].mean().sort_values(ascending=False)
    best_vehicle = vehicle_performance.index[0]
    worst_vehicle = vehicle_performance.index[-1]
    
    insights_report.append(f"• VEHICLE OPTIMIZATION:")
    insights_report.append(f"  → Increase {best_vehicle} fleet during peak hours")
    insights_report.append(f"  → Investigate {worst_vehicle} performance issues")
    
    # Revenue optimization recommendations
    avg_booking_value = df['Booking Value'].mean()
    insights_report.append(f"• REVENUE OPTIMIZATION:")
    insights_report.append(f"  → Current average booking: ₹{avg_booking_value:.0f}")
    insights_report.append("  → Implement dynamic pricing during high-demand periods")
    insights_report.append("  → Focus on premium vehicle categories")
    
    # Customer experience recommendations
    avg_customer_rating = df['Customer Rating'].mean()
    insights_report.append(f"• CUSTOMER EXPERIENCE:")
    insights_report.append(f"  → Current average rating: {avg_customer_rating:.2f}/5")
    if avg_customer_rating < 4.0:
        insights_report.append("  → Implement customer feedback improvement programs")
        insights_report.append("  → Focus on driver quality and training")
    else:
        insights_report.append("  → Excellent customer satisfaction - maintain standards")
    
    insights_report.append("")
    insights_report.append("📅 Report Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Save insights report
    report_path = 'output/ml/business_insights_report.txt'
    with open(report_path, 'w') as f:
        f.write('\n'.join(insights_report))
    
    logger.info(f"✅ Business insights report saved to {report_path}")
    
    # Display key insights
    print("\n" + "="*70)
    print("🎯 KEY BUSINESS INSIGHTS")
    print("="*70)
    
    for line in insights_report:
        if line.startswith('•') or line.startswith('  →'):
            print(line)
    
    return insights_report

def main():
    """Main function to run the advanced analytics pipeline."""
    logger.info("🚀 Starting Uber Ride Analytics Advanced Analytics Pipeline")
    logger.info("=" * 70)
    
    try:
        # 1. Load cleaned data
        df = load_cleaned_data()
        
        # 2. Prepare features for ML
        df_ml, feature_columns = prepare_features_for_ml(df)
        
        # 3. Build ride success prediction model
        results, best_model, scaler = build_ride_success_prediction_model(df_ml, feature_columns)
        
        # 4. Perform customer segmentation
        customer_segments, cluster_analysis = perform_customer_segmentation(df)
        
        # 5. Perform demand forecasting
        demand_forecast = perform_demand_forecasting(df)
        
        # 6. Build revenue optimization model
        revenue_results, best_revenue_model, scaler_revenue = build_revenue_optimization_model(df)
        
        # 7. Perform vehicle allocation optimization
        optimal_allocation = perform_vehicle_allocation_optimization(df)
        
        # 8. Generate business insights
        insights_report = generate_business_insights(
            df, results, customer_segments, demand_forecast, revenue_results
        )
        
        # 9. Final summary
        logger.info("\n🎯 ADVANCED ANALYTICS PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"📊 Dataset analyzed: {len(df):,} records")
        logger.info(f"🤖 ML models trained: {len(results)}")
        logger.info(f"👥 Customer segments: {len(customer_segments['Cluster'].unique())}")
        logger.info(f"📈 Demand forecast: {len(demand_forecast)} weeks")
        logger.info(f"💰 Revenue models: {len(revenue_results)}")
        logger.info(f"📁 Output files saved in 'output/ml/' directory")
        
        logger.info("\n📈 NEXT STEPS:")
        logger.info("  • Deploy models to production using '05_model_deployment.py'")
        logger.info("  • Set up automated monitoring and retraining")
        logger.info("  • Integrate insights into business operations")
        logger.info("  • Implement A/B testing for optimization strategies")
        
        return df, results, customer_segments, demand_forecast, revenue_results
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with error: {e}")
        raise

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Uber Ride Analytics Advanced Analytics')
    parser.add_argument('--task', default='all', choices=['all', 'train_models', 'segmentation', 'forecasting', 'optimization'],
                       help='Specific task to run')
    
    args = parser.parse_args()
    
    # Run the pipeline
    if args.task == 'all':
        results = main()
    else:
        logger.info(f"Running specific task: {args.task}")
        # Implement specific task execution here
        pass
    
    print("\n🎉 Advanced analytics completed! Check the 'output/ml' folder for results.")
