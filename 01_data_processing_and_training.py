"""
Data Processing and Model Training Script
This script processes the Uber rides data and trains ML models for booking predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import ShuffleSplit, learning_curve
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, roc_curve, auc
import joblib
import streamlit as st
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@st.cache_data(show_spinner=False)
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

@st.cache_data(show_spinner=False)
def prepare_features(df):
    """Prepare features and target for success classification model"""
    
    feature_columns = [
        'Hour', 'DayOfWeek', 'Month', 'IsWeekend',
        'Pickup Location', 'Vehicle Type', 'TimeCategory'
    ]
    
    missing_columns = [col for col in feature_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ Missing columns: {missing_columns}")
        return None, None, None
    
    X = df[feature_columns].copy()
    y = df['IsSuccessful'].astype(int).values
    
    # Encode categorical variables
    label_encoders = {}
    categorical_columns = ['Pickup Location', 'Vehicle Type', 'TimeCategory']
    for col in categorical_columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le
    
    return X, y, label_encoders

def train_model(X, y, encoders):
    """Train a single RandomForest classifier to predict ride success"""
    
    st.subheader("🤖 Training Success Classification Model")
    feature_columns = ['Hour', 'DayOfWeek', 'Month', 'IsWeekend', 'Pickup Location', 'Vehicle Type', 'TimeCategory']
    X_train_full = X[feature_columns].copy()
    
    X_train_split, X_test_split, y_train, y_test = train_test_split(
        X_train_full, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Fast, robust defaults
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=None,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    with st.spinner("Training RandomForest (success classifier)..."):
        model.fit(X_train_split, y_train)
    
    st.subheader("📊 Model Performance")
    y_pred = model.predict(X_test_split)
    acc = accuracy_score(y_test, y_pred)
    st.write(f"**Accuracy:** {acc:.3f}")
    st.text("Classification Report:\n" + classification_report(y_test, y_pred, digits=3))
    
    # Learning curve (training vs validation accuracy)
    st.subheader("📈 Learning Curve")
    cv = ShuffleSplit(n_splits=3, test_size=0.2, random_state=42)
    train_sizes, train_scores, val_scores = learning_curve(
        model,
        X_train_full,
        y,
        cv=cv,
        scoring='accuracy',
        n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 5)
    )
    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)
    import matplotlib.pyplot as plt
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(train_sizes, train_mean, 'o-', label='Training score')
    ax1.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.2)
    ax1.plot(train_sizes, val_mean, 'o-', label='Validation score')
    ax1.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.2)
    ax1.set_xlabel('Training examples')
    ax1.set_ylabel('Accuracy')
    ax1.set_title('Learning Curve')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)
    plt.close(fig1)
    
    # ROC curve (prediction curve)
    st.subheader("📉 ROC Curve")
    if hasattr(model, 'predict_proba'):
        y_proba = model.predict_proba(X_test_split)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
        ax2.plot([0, 1], [0, 1], color='navy', lw=1, linestyle='--')
        ax2.set_xlim([0.0, 1.0])
        ax2.set_ylim([0.0, 1.05])
        ax2.set_xlabel('False Positive Rate')
        ax2.set_ylabel('True Positive Rate')
        ax2.set_title('Receiver Operating Characteristic')
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
        plt.close(fig2)
    
    st.subheader("🔍 Feature Importance")
    for feature, importance in zip(feature_columns, model.feature_importances_):
        st.write(f"{feature}: {importance:.3f}")
    
    st.markdown("---")
    if st.button("💾 Save Trained Model Now", type="primary"):
        save_model(model, encoders)
    
    return model

def save_model(model, label_encoders):
    """Save trained success model and encoders"""
    try:
        import os
        os.makedirs('models', exist_ok=True)
        model_path = 'models/success_model.pkl'
        enc_path = 'models/label_encoders.pkl'
        joblib.dump(model, model_path)
        joblib.dump(label_encoders, enc_path)
        st.success("✅ Model saved successfully!")
        st.write("📁 Saved files:")
        st.write(f"- {os.path.abspath(model_path)}")
        st.write(f"- {os.path.abspath(enc_path)}")
    except Exception as e:
        st.error(f"❌ Error saving model: {str(e)}")

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
                X, y, encoders = prepare_features(st.session_state['processed_data'])
                st.session_state['features'] = (X, y, encoders)
                st.success("✅ Features prepared successfully!")
    
    # Step 3: Train Success Model
    if 'features' in st.session_state:
        st.subheader("🎯 Step 3: Train Success Model")
        if st.button("🚀 Train Success Model", type="primary"):
            X, y, encoders = st.session_state['features']
            model = train_model(X, y, encoders)
            st.session_state['trained_model'] = (model, encoders)
            st.success("✅ Success model training completed!")
    
    # Step 4: Save Model
    if 'trained_model' in st.session_state:
        st.subheader("💾 Step 4: Save Model")
        if st.button("💾 Save Trained Model", type="primary"):
            with st.spinner("Saving model..."):
                model, label_encoders = st.session_state['trained_model']
                save_model(model, label_encoders)
    
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
