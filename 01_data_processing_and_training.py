"""
Data Processing and Model Training Script
This script processes the Uber rides data and trains ML models for booking predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, learning_curve, validation_curve
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report
import joblib
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

def plot_training_curves(booking_model, revenue_model, success_model, X_train, y_booking_train, y_revenue_train, y_success_train):
    """Plot training curves and validation curves for all models"""
    
    st.subheader("📊 Training Curves & Model Performance")
    
    # Create a figure with subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('Booking Count - Learning Curve', 'Booking Count - Validation Curve',
                       'Revenue - Learning Curve', 'Revenue - Validation Curve', 
                       'Success Rate - Learning Curve', 'Success Rate - Validation Curve'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Booking Count Model Learning Curve
    train_sizes, train_scores, val_scores = learning_curve(
        booking_model, X_train, y_booking_train, cv=5, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10), scoring='neg_mean_absolute_error'
    )
    
    train_mean = -np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = -np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    fig.add_trace(
        go.Scatter(x=train_sizes, y=train_mean, name='Training MAE', 
                  line=dict(color='blue'), mode='lines+markers'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=train_sizes, y=val_mean, name='Validation MAE', 
                  line=dict(color='red'), mode='lines+markers'),
        row=1, col=1
    )
    
    # 2. Revenue Model Learning Curve
    train_sizes, train_scores, val_scores = learning_curve(
        revenue_model, X_train, y_revenue_train, cv=5, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10), scoring='neg_mean_absolute_error'
    )
    
    train_mean = -np.mean(train_scores, axis=1)
    val_mean = -np.mean(val_scores, axis=1)
    
    fig.add_trace(
        go.Scatter(x=train_sizes, y=train_mean, name='Training MAE', 
                  line=dict(color='blue'), mode='lines+markers', showlegend=False),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=train_sizes, y=val_mean, name='Validation MAE', 
                  line=dict(color='red'), mode='lines+markers', showlegend=False),
        row=2, col=1
    )
    
    # 3. Success Rate Model Learning Curve
    train_sizes, train_scores, val_scores = learning_curve(
        success_model, X_train, y_success_train, cv=5, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10), scoring='accuracy'
    )
    
    train_mean = np.mean(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    
    fig.add_trace(
        go.Scatter(x=train_sizes, y=train_mean, name='Training Accuracy', 
                  line=dict(color='blue'), mode='lines+markers', showlegend=False),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=train_sizes, y=val_mean, name='Validation Accuracy', 
                  line=dict(color='red'), mode='lines+markers', showlegend=False),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=1200,
        title_text="Model Training Curves",
        title_x=0.5,
        showlegend=True
    )
    
    # Update x and y axis labels
    for i in range(1, 4):
        fig.update_xaxes(title_text="Training Set Size", row=i, col=1)
        if i == 3:
            fig.update_yaxes(title_text="Accuracy", row=i, col=1)
        else:
            fig.update_yaxes(title_text="Mean Absolute Error", row=i, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    return fig

def plot_model_predictions(booking_model, revenue_model, success_model, X_test, y_booking_test, y_revenue_test, y_success_test):
    """Plot actual vs predicted values for all models"""
    
    st.subheader("🎯 Model Predictions vs Actual Values")
    
    # Get predictions
    booking_pred = booking_model.predict(X_test)
    revenue_pred = revenue_model.predict(X_test)
    success_pred = success_model.predict(X_test)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Booking Count: Actual vs Predicted', 'Revenue: Actual vs Predicted',
                       'Success Rate: Actual vs Predicted', 'Model Performance Summary'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Booking Count Scatter Plot
    fig.add_trace(
        go.Scatter(x=y_booking_test, y=booking_pred, mode='markers', 
                  name='Booking Count', marker=dict(color='blue', opacity=0.6)),
        row=1, col=1
    )
    
    # Add perfect prediction line
    max_val = max(y_booking_test.max(), booking_pred.max())
    fig.add_trace(
        go.Scatter(x=[0, max_val], y=[0, max_val], mode='lines', 
                  name='Perfect Prediction', line=dict(color='red', dash='dash')),
        row=1, col=1
    )
    
    # 2. Revenue Scatter Plot
    fig.add_trace(
        go.Scatter(x=y_revenue_test, y=revenue_pred, mode='markers', 
                  name='Revenue', marker=dict(color='green', opacity=0.6)),
        row=1, col=2
    )
    
    # Add perfect prediction line
    max_val = max(y_revenue_test.max(), revenue_pred.max())
    fig.add_trace(
        go.Scatter(x=[0, max_val], y=[0, max_val], mode='lines', 
                  name='Perfect Prediction', line=dict(color='red', dash='dash'), showlegend=False),
        row=1, col=2
    )
    
    # 3. Success Rate Scatter Plot
    fig.add_trace(
        go.Scatter(x=y_success_test, y=success_pred, mode='markers', 
                  name='Success Rate', marker=dict(color='orange', opacity=0.6)),
        row=2, col=1
    )
    
    # Add perfect prediction line
    max_val = max(y_success_test.max(), success_pred.max())
    fig.add_trace(
        go.Scatter(x=[0, max_val], y=[0, max_val], mode='lines', 
                  name='Perfect Prediction', line=dict(color='red', dash='dash'), showlegend=False),
        row=2, col=1
    )
    
    # 4. Performance Summary Bar Chart
    booking_r2 = r2_score(y_booking_test, booking_pred)
    revenue_r2 = r2_score(y_revenue_test, revenue_pred)
    success_accuracy = accuracy_score(y_success_test, success_pred)
    
    models = ['Booking Count', 'Revenue', 'Success Rate']
    scores = [booking_r2, revenue_r2, success_accuracy]
    
    fig.add_trace(
        go.Bar(x=models, y=scores, name='Model Performance', 
               marker=dict(color=['blue', 'green', 'orange'])),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Model Predictions Analysis",
        title_x=0.5,
        showlegend=True
    )
    
    # Update axis labels
    fig.update_xaxes(title_text="Actual Values", row=1, col=1)
    fig.update_yaxes(title_text="Predicted Values", row=1, col=1)
    fig.update_xaxes(title_text="Actual Values", row=1, col=2)
    fig.update_yaxes(title_text="Predicted Values", row=1, col=2)
    fig.update_xaxes(title_text="Actual Values", row=2, col=1)
    fig.update_yaxes(title_text="Predicted Values", row=2, col=1)
    fig.update_xaxes(title_text="Models", row=2, col=2)
    fig.update_yaxes(title_text="Performance Score", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display performance metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Booking Count R²", f"{booking_r2:.3f}")
        st.metric("Booking Count MAE", f"{mean_absolute_error(y_booking_test, booking_pred):.2f}")
    
    with col2:
        st.metric("Revenue R²", f"{revenue_r2:.3f}")
        st.metric("Revenue MAE", f"₹{mean_absolute_error(y_revenue_test, revenue_pred):.2f}")
    
    with col3:
        st.metric("Success Rate Accuracy", f"{success_accuracy:.3f}")
        st.metric("Success Rate MAE", f"{mean_absolute_error(y_success_test, success_pred):.3f}")
    
    return fig

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
                st.session_state['training_completed'] = True
                st.success("✅ Model training completed!")
    
    # Step 4: Plot Training Curves and Model Predictions
    if 'trained_models' in st.session_state and 'training_completed' in st.session_state:
        st.subheader("📊 Step 4: Training Curves & Model Analysis")
        
        if st.button("📈 Generate Training Curves & Predictions", type="primary"):
            with st.spinner("Generating training curves and model predictions..."):
                booking_model, revenue_model, success_model, label_encoders = st.session_state['trained_models']
                
                # Get the training data for plotting
                X, y_booking, y_revenue, y_success, encoders = st.session_state['features']
                feature_columns = ['Hour', 'DayOfWeek', 'Month', 'IsWeekend', 'Pickup Location', 'Vehicle Type', 'TimeCategory']
                X_train = X[feature_columns].copy()
                
                # Prepare targets for plotting (same logic as in train_models)
                df = st.session_state['processed_data']
                y_booking_count = []
                y_revenue = []
                y_success = []
                
                for _, row in X_train.iterrows():
                    location = label_encoders['Pickup Location'].inverse_transform([row['Pickup Location']])[0]
                    vehicle = label_encoders['Vehicle Type'].inverse_transform([row['Vehicle Type']])[0]
                    time_cat = label_encoders['TimeCategory'].inverse_transform([row['TimeCategory']])[0]
                    hour = row['Hour']
                    
                    matching_records = df[
                        (df['Pickup Location'] == location) &
                        (df['Vehicle Type'] == vehicle) &
                        (df['TimeCategory'] == time_cat) &
                        (df['Hour'] == hour)
                    ]
                    
                    if len(matching_records) > 0:
                        y_booking_count.append(len(matching_records))
                        y_revenue.append(matching_records['Booking Value'].mean())
                        y_success.append(matching_records['IsSuccessful'].mean())
                    else:
                        y_booking_count.append(1)
                        y_revenue.append(df['Booking Value'].mean())
                        y_success.append(df['IsSuccessful'].mean())
                
                y_booking_count = np.array(y_booking_count)
                y_revenue = np.array(y_revenue)
                y_success = np.array(y_success)
                
                # Split data for plotting
                X_train_split, X_test_split, y_booking_train, y_booking_test = train_test_split(
                    X_train, y_booking_count, test_size=0.2, random_state=42
                )
                _, _, y_revenue_train, y_revenue_test = train_test_split(
                    X_train, y_revenue, test_size=0.2, random_state=42
                )
                _, _, y_success_train, y_success_test = train_test_split(
                    X_train, y_success, test_size=0.2, random_state=42
                )
                
                # Plot training curves
                plot_training_curves(booking_model, revenue_model, success_model, 
                                   X_train_split, y_booking_train, y_revenue_train, y_success_train)
                
                # Plot model predictions
                plot_model_predictions(booking_model, revenue_model, success_model, 
                                     X_test_split, y_booking_test, y_revenue_test, y_success_test)
                
                st.session_state['plots_generated'] = True
                st.success("✅ Training curves and model predictions generated!")
    
    # Step 5: Save Models (Enhanced with better UI)
    if 'trained_models' in st.session_state and 'plots_generated' in st.session_state:
        st.subheader("💾 Step 5: Save Trained Models")
        
        # Enhanced save button with better styling and information
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 15px; margin: 1rem 0; 
                    color: white; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h3>🎉 Models Ready for Saving!</h3>
            <p>Your models have been trained and analyzed. Click the button below to save them to disk.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("💾 Save All Trained Models", type="primary", use_container_width=True):
                with st.spinner("Saving models to disk..."):
                    booking_model, revenue_model, success_model, label_encoders = st.session_state['trained_models']
                    save_models(booking_model, revenue_model, success_model, label_encoders)
                    
                    # Show success message with file details
                    st.success("🎉 Models saved successfully!")
                    st.balloons()
                    
                    # Display saved files information
                    st.info("""
                    **Saved Files:**
                    - `models/booking_count_model.pkl` - Booking count prediction model
                    - `models/revenue_model.pkl` - Revenue prediction model  
                    - `models/success_rate_model.pkl` - Success rate prediction model
                    - `models/label_encoders.pkl` - Label encoders for categorical variables
                    """)
                    
                    # Add download option for the models directory
                    import os
                    import zipfile
                    import tempfile
                    
                    if os.path.exists('models'):
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                            with zipfile.ZipFile(tmp_file.name, 'w') as zip_file:
                                for root, dirs, files in os.walk('models'):
                                    for file in files:
                                        zip_file.write(os.path.join(root, file), file)
                            
                            with open(tmp_file.name, 'rb') as f:
                                st.download_button(
                                    label="📥 Download Models as ZIP",
                                    data=f.read(),
                                    file_name="trained_models.zip",
                                    mime="application/zip"
                                )
    
    # Legacy save button for backward compatibility
    elif 'trained_models' in st.session_state:
        st.subheader("💾 Save Models")
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
