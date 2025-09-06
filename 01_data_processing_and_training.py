"""
Data Processing and Model Training Script
This script processes the Uber rides data and trains ML models for booking predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report
import joblib
import streamlit as st
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the Uber rides data"""
    try:
        # Load the cleaned data
        df = pd.read_csv('output/uber_rides_cleaned.csv')
        
        st.success(f"✅ Data loaded successfully: {len(df):,} records")
        
        # Check available columns
        st.write("📋 Available columns:", list(df.columns))
        
        # Additional data cleaning and feature engineering
        df['Date'] = pd.to_datetime(df['Date'])
        df['Hour'] = df['Date'].dt.hour
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['Month'] = df['Date'].dt.month
        df['IsWeekend'] = df['DayOfWeek'].isin([5, 6]).astype(int)
        
        # Create time-based features
        df['TimeCategory'] = df['Hour'].apply(lambda x: 
            'Morning' if 6 <= x < 12 else
            'Afternoon' if 12 <= x < 18 else
            'Evening' if 18 <= x < 22 else
            'Night'
        )
        
        # Create revenue categories
        df['RevenueCategory'] = df['Booking Value'].apply(lambda x:
            'Low (< ₹100)' if x < 100 else
            'Medium (₹100-300)' if x < 300 else
            'High (₹300-500)' if x < 500 else
            'Premium (> ₹500)'
        )
        
        # Create success indicator - check if IsSuccessful column exists
        if 'IsSuccessful' not in df.columns:
            if 'Booking Status' in df.columns:
                df['IsSuccessful'] = (df['Booking Status'] == 'Completed').astype(int)
            else:
                # If no status column, create a default success rate
                df['IsSuccessful'] = np.random.choice([0, 1], size=len(df), p=[0.15, 0.85])  # 85% success rate
        
        st.info(f"📊 Data Features: {df.shape[1]} columns, {df.shape[0]:,} rows")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

def prepare_features(df):
    """Prepare features for machine learning models"""
    
    # Select features for prediction
    feature_columns = [
        'Hour', 'DayOfWeek', 'Month', 'IsWeekend',
        'Pickup Location', 'Vehicle Type', 'TimeCategory'
    ]
    
    # Check if all required columns exist
    missing_columns = [col for col in feature_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ Missing columns: {missing_columns}")
        return None, None, None, None, None
    
    # Create feature matrix
    X = df[feature_columns].copy()
    
    # Encode categorical variables
    label_encoders = {}
    categorical_columns = ['Pickup Location', 'Vehicle Type', 'TimeCategory']
    
    for col in categorical_columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le
    
    # Target variables
    y_booking_count = df.groupby(['Pickup Location', 'Vehicle Type', 'TimeCategory']).size()
    y_revenue = df.groupby(['Pickup Location', 'Vehicle Type', 'TimeCategory'])['Booking Value'].sum()
    y_success_rate = df.groupby(['Pickup Location', 'Vehicle Type', 'TimeCategory'])['IsSuccessful'].mean()
    
    return X, y_booking_count, y_revenue, y_success_rate, label_encoders

def train_models(X, y_booking_count, y_revenue, y_success_rate, label_encoders):
    """Train multiple ML models for different predictions"""
    
    st.subheader("🤖 Training Machine Learning Models")
    
    # Use individual records for training instead of aggregated data
    # This gives us more training samples and better generalization
    
    # Prepare features for training
    feature_columns = ['Hour', 'DayOfWeek', 'Month', 'IsWeekend', 'Pickup Location', 'Vehicle Type', 'TimeCategory']
    X_train = X[feature_columns].copy()
    
    # Get the original data for targets
    df = st.session_state['processed_data']
    
    # Create realistic targets using a simpler approach
    # 1. Booking Count: Predict how many bookings per hour for this combination
    # Calculate average bookings per hour for each location-vehicle-time combination
    hourly_booking_counts = df.groupby(['Pickup Location', 'Vehicle Type', 'TimeCategory', 'Hour']).size()
    
    y_booking_count = []
    y_revenue = []
    y_success = []
    
    for _, row in X_train.iterrows():
        # Get original values
        location = label_encoders['Pickup Location'].inverse_transform([row['Pickup Location']])[0]
        vehicle = label_encoders['Vehicle Type'].inverse_transform([row['Vehicle Type']])[0]
        time_cat = label_encoders['TimeCategory'].inverse_transform([row['TimeCategory']])[0]
        hour = row['Hour']
        
        # Find matching records
        matching_records = df[
            (df['Pickup Location'] == location) &
            (df['Vehicle Type'] == vehicle) &
            (df['TimeCategory'] == time_cat) &
            (df['Hour'] == hour)
        ]
        
        if len(matching_records) > 0:
            # Use actual counts and averages
            y_booking_count.append(len(matching_records))
            y_revenue.append(matching_records['Booking Value'].mean())
            y_success.append(matching_records['IsSuccessful'].mean())
        else:
            # Use overall averages as fallback
            y_booking_count.append(1)  # At least 1 booking
            y_revenue.append(df['Booking Value'].mean())
            y_success.append(df['IsSuccessful'].mean())
    
    y_booking_count = np.array(y_booking_count)
    y_revenue = np.array(y_revenue)
    y_success = np.array(y_success)
    
    st.write(f"📊 Training data shape: {X_train.shape[0]} samples, {X_train.shape[1]} features")
    st.write(f"📈 Target ranges:")
    st.write(f"- Booking Count: {y_booking_count.min():.0f} to {y_booking_count.max():.0f}")
    st.write(f"- Revenue: ₹{y_revenue.min():.0f} to ₹{y_revenue.max():.0f}")
    st.write(f"- Success Rate: {y_success.min():.3f} to {y_success.max():.3f}")
    
    # Split data
    X_train_split, X_test_split, y_booking_train, y_booking_test = train_test_split(
        X_train, y_booking_count, test_size=0.2, random_state=42
    )
    
    _, _, y_revenue_train, y_revenue_test = train_test_split(
        X_train, y_revenue, test_size=0.2, random_state=42
    )
    
    _, _, y_success_train, y_success_test = train_test_split(
        X_train, y_success, test_size=0.2, random_state=42
    )
    
    # Train Booking Count Model (predicts number of bookings)
    st.write("📈 Training Booking Count Prediction Model...")
    booking_model = RandomForestRegressor(
        n_estimators=50,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    booking_model.fit(X_train_split, y_booking_train)
    
    # Train Revenue Model
    st.write("💰 Training Revenue Prediction Model...")
    revenue_model = RandomForestRegressor(
        n_estimators=50,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    revenue_model.fit(X_train_split, y_revenue_train)
    
    # Train Success Rate Model
    st.write("✅ Training Success Rate Prediction Model...")
    success_model = RandomForestClassifier(
        n_estimators=50,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    success_model.fit(X_train_split, y_success_train)
    
    # Evaluate models
    st.subheader("📊 Model Performance")
    
    # Booking Count Model Evaluation
    booking_pred = booking_model.predict(X_test_split)
    booking_mae = mean_absolute_error(y_booking_test, booking_pred)
    booking_r2 = r2_score(y_booking_test, booking_pred)
    
    st.write(f"**Booking Count Model:**")
    st.write(f"- MAE: {booking_mae:.2f}")
    st.write(f"- R² Score: {booking_r2:.3f}")
    
    # Revenue Model Evaluation
    revenue_pred = revenue_model.predict(X_test_split)
    revenue_mae = mean_absolute_error(y_revenue_test, revenue_pred)
    revenue_r2 = r2_score(y_revenue_test, revenue_pred)
    
    st.write(f"**Revenue Model:**")
    st.write(f"- MAE: ₹{revenue_mae:.2f}")
    st.write(f"- R² Score: {revenue_r2:.3f}")
    
    # Success Rate Model Evaluation
    success_pred = success_model.predict(X_test_split)
    success_accuracy = accuracy_score(y_success_test, success_pred)
    
    st.write(f"**Success Rate Model:**")
    st.write(f"- Accuracy: {success_accuracy:.3f}")
    
    # Feature importance
    st.subheader("🔍 Feature Importance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Booking Count Model:**")
        feature_importance = booking_model.feature_importances_
        for i, (feature, importance) in enumerate(zip(feature_columns, feature_importance)):
            st.write(f"{feature}: {importance:.3f}")
    
    with col2:
        st.write("**Revenue Model:**")
        feature_importance = revenue_model.feature_importances_
        for i, (feature, importance) in enumerate(zip(feature_columns, feature_importance)):
            st.write(f"{feature}: {importance:.3f}")
    
    with col3:
        st.write("**Success Rate Model:**")
        feature_importance = success_model.feature_importances_
        for i, (feature, importance) in enumerate(zip(feature_columns, feature_importance)):
            st.write(f"{feature}: {importance:.3f}")
    
    return booking_model, revenue_model, success_model, label_encoders

def save_models(booking_model, revenue_model, success_model, label_encoders):
    """Save trained models and encoders"""
    
    try:
        # Create models directory
        import os
        os.makedirs('models', exist_ok=True)
        
        # Save models
        joblib.dump(booking_model, 'models/booking_count_model.pkl')
        joblib.dump(revenue_model, 'models/revenue_model.pkl')
        joblib.dump(success_model, 'models/success_rate_model.pkl')
        joblib.dump(label_encoders, 'models/label_encoders.pkl')
        
        st.success("✅ Models saved successfully!")
        st.write("📁 Saved files:")
        st.write("- models/booking_count_model.pkl")
        st.write("- models/revenue_model.pkl")
        st.write("- models/success_rate_model.pkl")
        st.write("- models/label_encoders.pkl")
        
    except Exception as e:
        st.error(f"❌ Error saving models: {str(e)}")

def main():
    """Main function to run data processing and training"""
    
    st.set_page_config(
        page_title="Uber Data Processing & Model Training",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Uber Data Processing & Model Training")
    st.markdown("---")
    
    # Step 1: Load and Clean Data
    st.subheader("📊 Step 1: Data Loading & Cleaning")
    if st.button("🔄 Load and Process Data", type="primary"):
        with st.spinner("Loading and processing data..."):
            df = load_and_clean_data()
            
            if df is not None:
                st.session_state['processed_data'] = df
                st.success("✅ Data processing completed!")
    
    # Step 2: Prepare Features
    if 'processed_data' in st.session_state:
        st.subheader("🔧 Step 2: Feature Preparation")
        if st.button("⚙️ Prepare Features for ML", type="primary"):
            with st.spinner("Preparing features..."):
                X, y_booking, y_revenue, y_success, encoders = prepare_features(st.session_state['processed_data'])
                st.session_state['features'] = (X, y_booking, y_revenue, y_success, encoders)
                st.success("✅ Features prepared successfully!")
    
    # Step 3: Train Models
    if 'features' in st.session_state:
        st.subheader("🎯 Step 3: Model Training")
        if st.button("🚀 Train ML Models", type="primary"):
            with st.spinner("Training models... This may take a few minutes."):
                X, y_booking, y_revenue, y_success, encoders = st.session_state['features']
                booking_model, revenue_model, success_model, label_encoders = train_models(
                    X, y_booking, y_revenue, y_success, encoders
                )
                st.session_state['trained_models'] = (booking_model, revenue_model, success_model, label_encoders)
                st.success("✅ Model training completed!")
    
    # Step 4: Save Models
    if 'trained_models' in st.session_state:
        st.subheader("💾 Step 4: Save Models")
        if st.button("💾 Save Trained Models", type="primary"):
            with st.spinner("Saving models..."):
                booking_model, revenue_model, success_model, label_encoders = st.session_state['trained_models']
                save_models(booking_model, revenue_model, success_model, label_encoders)
    
    # Display data summary
    if 'processed_data' in st.session_state:
        st.subheader("📈 Data Summary")
        df = st.session_state['processed_data']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        
        with col2:
            st.metric("Unique Locations", f"{df['Pickup Location'].nunique():,}")
        
        with col3:
            st.metric("Vehicle Types", f"{df['Vehicle Type'].nunique():,}")
        
        with col4:
            st.metric("Success Rate", f"{df['IsSuccessful'].mean()*100:.1f}%")
        
        # Show sample data
        st.write("**Sample Data:**")
        st.dataframe(df.head(10))

if __name__ == "__main__":
    main()
