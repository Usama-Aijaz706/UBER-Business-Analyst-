#!/usr/bin/env python3
"""
🚗 Uber Ride Analytics 2024 - Professional Business Intelligence Dashboard
=======================================================================

A stunning, interactive dashboard with modern design, amazing color schemes,
and professional business intelligence capabilities.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="🚗 Uber Analytics Pro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for stunning design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        animation: fadeInUp 1s ease-out;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        animation: slideInLeft 0.8s ease-out;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.15);
    }
    
    .insight-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .insight-box:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .insight-box::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 0 20px 20px 0;
        border-color: transparent #667eea transparent transparent;
        transition: all 0.3s ease;
    }
    
    .insight-box:hover::after {
        border-width: 0 25px 25px 0;
    }
    
    .download-btn {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem;
    }
    
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(81, 207, 102, 0.4);
        color: white;
        text-decoration: none;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #ff6b6b;
        animation: pulse 2s infinite;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #51cf66;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px 20px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
        transform: scale(1.05);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { transform: rotate(0deg); opacity: 0.3; }
        50% { opacity: 0.6; }
        100% { transform: rotate(360deg); opacity: 0.3; }
    }
    
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); opacity: 0.3; }
        50% { transform: translateY(-10px) rotate(180deg); opacity: 0.6; }
        100% { transform: translateY(0px) rotate(360deg); opacity: 0.3; }
    }
    
    .metric-delta {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    
    .metric-delta.positive {
        color: #51cf66;
    }
    
    .metric-delta.negative {
        color: #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load the cleaned dataset."""
    try:
        file_paths = [
            'output/uber_rides_cleaned.pkl',
            'output/uber_rides_cleaned.parquet',
            'output/uber_rides_cleaned.csv'
        ]
        
        for file_path in file_paths:
            try:
                if file_path.endswith('.pkl'):
                    df = pd.read_pickle(file_path)
                elif file_path.endswith('.parquet'):
                    df = pd.read_parquet(file_path)
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    if 'Date' in df.columns and df['Date'].dtype == 'object':
                        df['Date'] = pd.to_datetime(df['Date'])
                else:
                    continue
                
                st.success(f"✅ Data loaded successfully from {file_path}")
                return df
            except:
                continue
        
        st.error("❌ No data files found. Please run the data cleaning script first.")
        return None
        
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None

def create_header():
    """Create stunning header with gradient background."""
    st.markdown("""
    <div class="main-header">
        <h1>🚗 UBER RIDE ANALYTICS 2024</h1>
        <h3>Professional Business Intelligence Dashboard</h3>
        <p>Transform your ride data into actionable business insights</p>
    </div>
    """, unsafe_allow_html=True)

def create_kpi_section(df):
    """Create beautiful KPI cards with gradients."""
    st.markdown('<div class="section-header"><h2>📊 KEY PERFORMANCE INDICATORS</h2></div>', unsafe_allow_html=True)
    
    # Calculate additional metrics
    total_bookings = len(df)
    success_rate = df['IsSuccessful'].mean() * 100
    total_revenue = df['Booking Value'].sum()
    avg_rating = df['Customer Rating'].mean()
    
    # Calculate deltas (comparing to industry benchmarks)
    industry_success_rate = 92.0  # Industry benchmark
    industry_rating = 4.2  # Industry benchmark
    industry_revenue_per_booking = 350.0  # Industry benchmark
    
    success_delta = success_rate - industry_success_rate
    rating_delta = avg_rating - industry_rating
    revenue_delta = (total_revenue / total_bookings) - industry_revenue_per_booking
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; text-align: center;
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); margin: 0.5rem;
                    border-left: 4px solid #4c1d95; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        animation: shimmer 3s ease-in-out infinite;"></div>
            <div style="position: relative; z-index: 2;">
                <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Total Bookings</div>
                <div style="font-size: 2.2rem; font-weight: bold; margin: 0.5rem 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.6); color: #ffffff;">{total_bookings:,}</div>
                <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Rides</div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem; color: #ffffff; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">📈 All Time High</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        delta_class = "positive" if success_delta >= 0 else "negative"
        delta_icon = "📈" if success_delta >= 0 else "📉"
        delta_color = "#51cf66" if success_delta >= 0 else "#ff6b6b"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; text-align: center;
                    box-shadow: 0 8px 25px rgba(79, 172, 254, 0.3); margin: 0.5rem;
                    border-left: 4px solid #1971c2; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        animation: pulse 2s ease-in-out infinite;"></div>
            <div style="position: relative; z-index: 2;">
                <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Success Rate</div>
                <div style="font-size: 2.2rem; font-weight: bold; margin: 0.5rem 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.6); color: #ffffff;">{success_rate:.1f}%</div>
                <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Completed</div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem; color: #ffffff; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{delta_icon} {success_delta:+.1f}% vs Industry</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        delta_class = "positive" if revenue_delta >= 0 else "negative"
        delta_icon = "📈" if revenue_delta >= 0 else "📉"
        delta_color = "#51cf66" if revenue_delta >= 0 else "#ff6b6b"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #51cf66 0%, #40c057 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; text-align: center;
                    box-shadow: 0 8px 25px rgba(81, 207, 102, 0.3); margin: 0.5rem;
                    border-left: 4px solid #2b8a3e; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        animation: float 2.5s ease-in-out infinite;"></div>
            <div style="position: relative; z-index: 2;">
                <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Total Revenue</div>
                <div style="font-size: 2.2rem; font-weight: bold; margin: 0.5rem 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.6); color: #ffffff;">₹{total_revenue:,.0f}</div>
                <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Generated</div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem; color: #ffffff; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{delta_icon} ₹{revenue_delta:+.0f} vs Industry</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        delta_class = "positive" if rating_delta >= 0 else "negative"
        delta_icon = "📈" if rating_delta >= 0 else "📉"
        delta_color = "#51cf66" if rating_delta >= 0 else "#ff6b6b"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; text-align: center;
                    box-shadow: 0 8px 25px rgba(255, 154, 158, 0.3); margin: 0.5rem;
                    border-left: 4px solid #e64980; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        animation: shimmer 3s ease-in-out infinite;"></div>
            <div style="position: relative; z-index: 2;">
                <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Customer Rating</div>
                <div style="font-size: 2.2rem; font-weight: bold; margin: 0.5rem 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.6); color: #ffffff;">{avg_rating:.1f}/5</div>
                <div style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Satisfaction</div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem; color: #ffffff; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{delta_icon} {rating_delta:+.1f} vs Industry</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add additional metrics row
    st.markdown('<div class="section-header"><h3>📈 ADDITIONAL METRICS</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_booking_value = df['Booking Value'].mean()
        st.metric(
            label="💰 Average Booking Value",
            value=f"₹{avg_booking_value:.0f}",
            delta=f"₹{avg_booking_value - 400:.0f}"
        )
    
    with col2:
        avg_ride_distance = df['Ride Distance'].mean()
        st.metric(
            label="🛣️ Average Ride Distance",
            value=f"{avg_ride_distance:.1f} km",
            delta=f"{avg_ride_distance - 20:.1f} km"
        )
    
    with col3:
        unique_customers = df['Customer ID'].nunique()
        st.metric(
            label="👥 Unique Customers",
            value=f"{unique_customers:,}",
            delta=f"{unique_customers - 140000:,}"
        )
    
    with col4:
        cancellation_rate = (1 - df['IsSuccessful'].mean()) * 100
        st.metric(
            label="❌ Cancellation Rate",
            value=f"{cancellation_rate:.1f}%",
            delta=f"{cancellation_rate - 8:.1f}%"
        )

def create_filters_sidebar(df):
    """Create beautiful sidebar filters."""
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 1rem;">
        <h3>🔍 FILTERS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Date range filter
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    
    date_range = st.sidebar.date_input(
        "📅 Select Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Vehicle type filter
    vehicle_types = st.sidebar.multiselect(
        "🚗 Select Vehicle Types:",
        options=df['Vehicle Type'].unique(),
        default=df['Vehicle Type'].unique()
    )
    
    # Time category filter
    time_categories = st.sidebar.multiselect(
        "🕒 Select Time Categories:",
        options=df['TimeCategory'].unique(),
        default=df['TimeCategory'].unique()
    )
    
    # Payment method filter
    payment_methods = st.sidebar.multiselect(
        "💳 Select Payment Methods:",
        options=df['Payment Method'].unique(),
        default=df['Payment Method'].unique()
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        # Convert date objects to datetime for comparison
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered_df = filtered_df[
            (filtered_df['Date'] >= start_date) & 
            (filtered_df['Date'] <= end_date)
        ]
    
    if vehicle_types:
        filtered_df = filtered_df[filtered_df['Vehicle Type'].isin(vehicle_types)]
    
    if time_categories:
        filtered_df = filtered_df[filtered_df['TimeCategory'].isin(time_categories)]
    
    if payment_methods:
        filtered_df = filtered_df[filtered_df['Payment Method'].isin(payment_methods)]
    
    # Filter summary
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
        <h4>📊 Filter Summary</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.metric("Filtered Records", f"{len(filtered_df):,}")
    st.sidebar.metric("Original Records", f"{len(df):,}")
    
    # Download section
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #51cf66 0%, #40c057 100%); padding: 1rem; border-radius: 10px; margin-top: 1rem; color: white;">
        <h4>💾 Download Data</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Download filtered data
    csv_data = filtered_df.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"uber_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # Download summary report
    summary_report = f"""
UBER RIDE ANALYTICS 2024 - SUMMARY REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FILTERED DATA SUMMARY:
- Total Records: {len(filtered_df):,}
- Date Range: {filtered_df['Date'].min()} to {filtered_df['Date'].max()}
- Success Rate: {filtered_df['IsSuccessful'].mean()*100:.1f}%
- Total Revenue: ₹{filtered_df['Booking Value'].sum():,.0f}
- Average Rating: {filtered_df['Customer Rating'].mean():.1f}/5

TOP INSIGHTS:
- Most Popular Vehicle: {filtered_df['Vehicle Type'].value_counts().index[0]}
- Peak Hour: {filtered_df['Hour'].value_counts().index[0]}:00
- Average Booking Value: ₹{filtered_df['Booking Value'].mean():.0f}
- Top Pickup Location: {filtered_df['Pickup Location'].value_counts().index[0]}
    """
    
    st.sidebar.download_button(
        label="📄 Download Report",
        data=summary_report,
        file_name=f"uber_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
    
    # Quick actions
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1rem; border-radius: 10px; margin-top: 1rem; color: white;">
        <h4>⚡ Quick Actions</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🔄 Reset Filters"):
        st.rerun()
    
    if st.sidebar.button("📊 Show Data Sample"):
        st.sidebar.dataframe(filtered_df.head(10))
    
    return filtered_df

def create_temporal_analysis(df):
    """Create stunning temporal analysis with beautiful charts and comprehensive insights."""
    st.markdown('<div class="section-header"><h2>🕒 TEMPORAL ANALYSIS</h2></div>', unsafe_allow_html=True)
    
    # Add interactive controls with perfect alignment
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("📊 Select Metric to Analyze:")
        time_metric = st.selectbox(
            "",
            ["Total Bookings", "Success Rate", "Average Revenue", "Customer Rating"],
            key="time_metric",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("🕒 Select Time Period:")
        time_period = st.selectbox(
            "",
            ["Hourly", "Daily", "Monthly", "Weekly"],
            key="time_period",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown("📈 Show Trend Lines:")
        show_trends = st.checkbox("", value=True, key="show_trends", label_visibility="collapsed")
    
    # Create comprehensive temporal analysis with different colors
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly patterns with enhanced colors
        hourly_stats = df.groupby('Hour').agg({
            'Booking ID': 'count',
            'IsSuccessful': 'mean',
            'Booking Value': 'mean',
            'Customer Rating': 'mean'
        }).reset_index()
        
        # Select metric based on user choice
        if time_metric == "Total Bookings":
            y_data = hourly_stats['Booking ID']
            y_title = "Number of Bookings"
            line_color = '#FF6B6B'  # Red
        elif time_metric == "Success Rate":
            y_data = hourly_stats['IsSuccessful'] * 100
            y_title = "Success Rate (%)"
            line_color = '#4ECDC4'  # Teal
        elif time_metric == "Average Revenue":
            y_data = hourly_stats['Booking Value']
            y_title = "Average Revenue (₹)"
            line_color = '#45B7D1'  # Blue
        else:  # Customer Rating
            y_data = hourly_stats['Customer Rating']
            y_title = "Customer Rating"
            line_color = '#96CEB4'  # Green
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_stats['Hour'],
            y=y_data,
            mode='lines+markers',
            name=time_metric,
            line=dict(color=line_color, width=4),
            marker=dict(size=10, color=line_color, line=dict(width=2, color='white'))
        ))
        
        if show_trends:
            # Add trend line
            z = np.polyfit(hourly_stats['Hour'], y_data, 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=hourly_stats['Hour'],
                y=p(hourly_stats['Hour']),
                mode='lines',
                name='Trend Line',
                line=dict(color='#FFA500', width=3, dash='dash')
            ))
        
        fig.update_layout(
            title=f'📊 Hourly {time_metric} Patterns',
            xaxis_title='Hour of Day',
            yaxis_title=y_title,
            template='plotly_white',
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced hourly insights with colors
        if time_metric == "Total Bookings":
            peak_hour = hourly_stats.loc[hourly_stats['Booking ID'] == hourly_stats['Booking ID'].max(), 'Hour'].iloc[0]
            peak_value = hourly_stats['Booking ID'].max()
            low_hour = hourly_stats.loc[hourly_stats['Booking ID'] == hourly_stats['Booking ID'].min(), 'Hour'].iloc[0]
            low_value = hourly_stats['Booking ID'].min()
        elif time_metric == "Success Rate":
            peak_hour = hourly_stats.loc[hourly_stats['IsSuccessful'] == hourly_stats['IsSuccessful'].max(), 'Hour'].iloc[0]
            peak_value = hourly_stats['IsSuccessful'].max() * 100
            low_hour = hourly_stats.loc[hourly_stats['IsSuccessful'] == hourly_stats['IsSuccessful'].min(), 'Hour'].iloc[0]
            low_value = hourly_stats['IsSuccessful'].min() * 100
        elif time_metric == "Average Revenue":
            peak_hour = hourly_stats.loc[hourly_stats['Booking Value'] == hourly_stats['Booking Value'].max(), 'Hour'].iloc[0]
            peak_value = hourly_stats['Booking Value'].max()
            low_hour = hourly_stats.loc[hourly_stats['Booking Value'] == hourly_stats['Booking Value'].min(), 'Hour'].iloc[0]
            low_value = hourly_stats['Booking Value'].min()
        else:  # Customer Rating
            peak_hour = hourly_stats.loc[hourly_stats['Customer Rating'] == hourly_stats['Customer Rating'].max(), 'Hour'].iloc[0]
            peak_value = hourly_stats['Customer Rating'].max()
            low_hour = hourly_stats.loc[hourly_stats['Customer Rating'] == hourly_stats['Customer Rating'].min(), 'Hour'].iloc[0]
            low_value = hourly_stats['Customer Rating'].min()
        
        # Display enhanced insights
        col_a, col_b = st.columns(2)
        with col_a:
            st.success(f"🎯 **Peak Hour**: {peak_hour}:00 ({peak_value:.1f})")
        with col_b:
            st.warning(f"📉 **Low Hour**: {low_hour}:00 ({low_value:.1f})")
    
    with col2:
        # Dynamic chart based on time_period selection
        if time_period == "Hourly":
            # Show daily patterns as second chart
            period_stats = df.groupby('DayOfWeek').agg({
                'Booking ID': 'count',
                'IsSuccessful': 'mean',
                'Booking Value': 'mean',
                'Customer Rating': 'mean'
            }).reset_index()
            # Reorder days
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            period_stats['DayOfWeek'] = pd.Categorical(period_stats['DayOfWeek'], categories=day_order, ordered=True)
            period_stats = period_stats.sort_values('DayOfWeek')
            x_col = 'DayOfWeek'
            x_title = 'Day of Week'
            chart_title = f'📅 Daily {time_metric} Patterns'
        elif time_period == "Daily":
            # Show hourly patterns as second chart
            period_stats = df.groupby('Hour').agg({
                'Booking ID': 'count',
                'IsSuccessful': 'mean',
                'Booking Value': 'mean',
                'Customer Rating': 'mean'
            }).reset_index()
            x_col = 'Hour'
            x_title = 'Hour of Day'
            chart_title = f'📊 Hourly {time_metric} Patterns'
        elif time_period == "Monthly":
            # Show monthly patterns
            period_stats = df.groupby('Month').agg({
                'Booking ID': 'count',
                'IsSuccessful': 'mean',
                'Booking Value': 'mean',
                'Customer Rating': 'mean'
            }).reset_index()
            # Add month names
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            period_stats['MonthName'] = period_stats['Month'].apply(lambda x: month_names[x-1])
            x_col = 'MonthName'
            x_title = 'Month'
            chart_title = f'📈 Monthly {time_metric} Patterns'
        else:  # Weekly
            # Show weekly patterns (using day of week as proxy)
            period_stats = df.groupby('DayOfWeek').agg({
                'Booking ID': 'count',
                'IsSuccessful': 'mean',
                'Booking Value': 'mean',
                'Customer Rating': 'mean'
            }).reset_index()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            period_stats['DayOfWeek'] = pd.Categorical(period_stats['DayOfWeek'], categories=day_order, ordered=True)
            period_stats = period_stats.sort_values('DayOfWeek')
            x_col = 'DayOfWeek'
            x_title = 'Day of Week'
            chart_title = f'📅 Weekly {time_metric} Patterns'
        
        # Select metric based on user choice
        if time_metric == "Total Bookings":
            y_data = period_stats['Booking ID']
            y_title = "Number of Bookings"
            bar_color = '#FF8C42'  # Orange
        elif time_metric == "Success Rate":
            y_data = period_stats['IsSuccessful'] * 100
            y_title = "Success Rate (%)"
            bar_color = '#FF6B9D'  # Pink
        elif time_metric == "Average Revenue":
            y_data = period_stats['Booking Value']
            y_title = "Average Revenue (₹)"
            bar_color = '#4ECDC4'  # Teal
        else:  # Customer Rating
            y_data = period_stats['Customer Rating']
            y_title = "Customer Rating"
            bar_color = '#96CEB4'  # Green
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=period_stats[x_col],
            y=y_data,
            marker_color=bar_color,
            name=time_metric,
            hovertemplate='<b>%{x}</b><br>' + time_metric + ': %{y:,.1f}<extra></extra>',
            marker=dict(
                line=dict(width=0),
                cornerradius=8  # Rounded corners on top
            ),
            text=y_data.round(1),  # Display values inside bars
            textposition='inside',  # Position text inside bars
            textfont=dict(
                size=12,
                color='white',
                weight='bold'
            )
        ))
        
        fig.update_layout(
            title=chart_title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            template='plotly_white',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title=dict(
                    text=x_title,
                    font=dict(size=14, color='#34495e'),
                    standoff=20
                ),
                tickfont=dict(size=12, color='#7f8c8d'),
                gridcolor='rgba(128, 128, 128, 0.15)',
                showline=True,
                linecolor='rgba(128, 128, 128, 0.4)',
                linewidth=1.5
            ),
            yaxis=dict(
                title=dict(
                    text=y_title,
                    font=dict(size=14, color='#34495e'),
                    standoff=30
                ),
                tickfont=dict(size=12, color='#7f8c8d'),
                gridcolor='rgba(128, 128, 128, 0.15)',
                showline=True,
                linecolor='rgba(128, 128, 128, 0.4)',
                linewidth=1.5,
                zeroline=True,
                zerolinecolor='rgba(128, 128, 128, 0.3)',
                zerolinewidth=1
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='rgba(128, 128, 128, 0.2)',
                borderwidth=1,
                font=dict(size=12, color='#34495e')
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced insights with colors (dynamic based on time period)
        if time_metric == "Total Bookings":
            peak_idx = period_stats['Booking ID'].idxmax()
            peak_value = period_stats.loc[peak_idx, 'Booking ID']
            low_idx = period_stats['Booking ID'].idxmin()
            low_value = period_stats.loc[low_idx, 'Booking ID']
        elif time_metric == "Success Rate":
            peak_idx = period_stats['IsSuccessful'].idxmax()
            peak_value = period_stats.loc[peak_idx, 'IsSuccessful'] * 100
            low_idx = period_stats['IsSuccessful'].idxmin()
            low_value = period_stats.loc[low_idx, 'IsSuccessful'] * 100
        elif time_metric == "Average Revenue":
            peak_idx = period_stats['Booking Value'].idxmax()
            peak_value = period_stats.loc[peak_idx, 'Booking Value']
            low_idx = period_stats['Booking Value'].idxmin()
            low_value = period_stats.loc[low_idx, 'Booking Value']
        else:  # Customer Rating
            peak_idx = period_stats['Customer Rating'].idxmax()
            peak_value = period_stats.loc[peak_idx, 'Customer Rating']
            low_idx = period_stats['Customer Rating'].idxmin()
            low_value = period_stats.loc[low_idx, 'Customer Rating']
        
        peak_period = period_stats.loc[peak_idx, x_col]
        low_period = period_stats.loc[low_idx, x_col]
        
        # Display enhanced insights
        col_c, col_d = st.columns(2)
        with col_c:
            if time_period == "Hourly":
                st.success(f"🏆 **Best Day**: {peak_period} ({peak_value:.1f})")
            elif time_period == "Daily":
                st.success(f"🎯 **Peak Hour**: {peak_period}:00 ({peak_value:.1f})")
            elif time_period == "Monthly":
                st.success(f"📊 **Peak Month**: {peak_period} ({peak_value:.1f})")
            else:  # Weekly
                st.success(f"🏆 **Best Day**: {peak_period} ({peak_value:.1f})")
        with col_d:
            if time_period == "Hourly":
                st.warning(f"📉 **Worst Day**: {low_period} ({low_value:.1f})")
            elif time_period == "Daily":
                st.warning(f"📉 **Low Hour**: {low_period}:00 ({low_value:.1f})")
            elif time_period == "Monthly":
                st.warning(f"📉 **Low Month**: {low_period} ({low_value:.1f})")
            else:  # Weekly
                st.warning(f"📉 **Worst Day**: {low_period} ({low_value:.1f})")
    
    # Enhanced monthly trends with professional combo chart and filter
    st.markdown("**🎯 Filter for Monthly Trends Chart:**")
    
    # Professional filter layout with enhanced styling
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 0.6rem; border-radius: 12px; color: white; text-align: center; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;
                    border-left: 4px solid #4c1d95; display: flex; align-items: center; justify-content: center;">
            <h5 style="margin: 0; font-weight: 600; font-size: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">📊</span> Filter Type
            </h5>
        </div>
        """, unsafe_allow_html=True)
        monthly_filter_type = st.selectbox(
            "",
            ["Overall", "Days", "Time", "Monthly"],
            key="monthly_filter_type",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 0.6rem; border-radius: 12px; color: white; text-align: center; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;
                    border-left: 4px solid #be185d; display: flex; align-items: center; justify-content: center;">
            <h5 style="margin: 0; font-weight: 600; font-size: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🎯</span> Filter Value
            </h5>
        </div>
        """, unsafe_allow_html=True)
        # Always show a consistent height element
        if monthly_filter_type == "Days":
            monthly_filter_value = st.selectbox(
                "",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                key="monthly_filter_day",
                label_visibility="collapsed"
            )
        elif monthly_filter_type == "Time":
            monthly_filter_value = st.selectbox(
                "",
                ["Morning", "Afternoon", "Evening", "Night"],
                key="monthly_filter_time",
                label_visibility="collapsed"
            )
        elif monthly_filter_type == "Monthly":
            monthly_filter_value = st.selectbox(
                "",
                ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                key="monthly_filter_month",
                label_visibility="collapsed"
            )
        else:
            monthly_filter_value = "Overall"
            st.selectbox(
                "",
                ["Overall Analysis"],
                key="overall_display",
                disabled=True,
                label_visibility="collapsed"
            )
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #51cf66 0%, #40c057 100%); 
                    padding: 0.6rem; border-radius: 12px; color: white; text-align: center; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1rem;
                    border-left: 4px solid #166534; display: flex; align-items: center; justify-content: center;">
            <h5 style="margin: 0; font-weight: 600; font-size: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">📈</span> Select Metric
            </h5>
        </div>
        """, unsafe_allow_html=True)
        monthly_metric = st.selectbox(
            "",
            ["All Metrics", "Bookings Only", "Revenue Only", "Rating Only"],
            key="monthly_metric",
            label_visibility="collapsed"
        )
    
    # Filter data based on user selection (auto-apply when selections change)
    filtered_monthly_df = df.copy()
    
    # Apply filter automatically based on current selections
    if monthly_filter_type != "Overall" and monthly_filter_value != "Overall":
        if monthly_filter_type == "Days":
            filtered_monthly_df = df[df['DayOfWeek'] == monthly_filter_value]
        elif monthly_filter_type == "Time":
            if monthly_filter_value == "Morning":
                filtered_monthly_df = df[df['Hour'].between(6, 11)]
            elif monthly_filter_value == "Afternoon":
                filtered_monthly_df = df[df['Hour'].between(12, 17)]
            elif monthly_filter_value == "Evening":
                filtered_monthly_df = df[df['Hour'].between(18, 21)]
            elif monthly_filter_value == "Night":
                filtered_monthly_df = df[(df['Hour'] >= 22) | (df['Hour'] <= 5)]
        elif monthly_filter_type == "Monthly":
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_num = month_names.index(monthly_filter_value) + 1
            filtered_monthly_df = df[df['Month'] == month_num]
    
    # Calculate monthly stats for filtered data
    monthly_stats = filtered_monthly_df.groupby('Month').agg({
        'Booking ID': 'count',
        'Booking Value': 'sum',
        'IsSuccessful': 'mean',
        'Customer Rating': 'mean'
    }).reset_index()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_stats['MonthName'] = monthly_stats['Month'].apply(lambda x: month_names[x-1])
    
    # Professional filter info display with detailed stats
    total_filtered_records = len(filtered_monthly_df)
    total_filtered_bookings = filtered_monthly_df['Booking ID'].count()
    total_filtered_revenue = filtered_monthly_df['Booking Value'].sum()
    avg_filtered_rating = filtered_monthly_df['Customer Rating'].mean()
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 1rem 0;">
        <h4>📊 Filter Applied: {} = {} | {} records</h4>
        <p>📈 Total Bookings: {:,} | 💰 Total Revenue: ₹{:,} | ⭐ Avg Rating: {:.2f}/5</p>
    </div>
    """.format(monthly_filter_type, monthly_filter_value, total_filtered_records, 
               total_filtered_bookings, total_filtered_revenue, avg_filtered_rating), unsafe_allow_html=True)
    
             # Create dynamic title based on filter selection
    if monthly_filter_type == "Overall":
        chart_title = "Monthly Trends Analysis - Overall"
    elif monthly_filter_type == "Days":
        chart_title = f"Monthly Trends Analysis - Days: {monthly_filter_value}"
    elif monthly_filter_type == "Time":
        chart_title = f"Monthly Trends Analysis - Time: {monthly_filter_value}"
    elif monthly_filter_type == "Monthly":
        chart_title = f"Monthly Trends Analysis - Month: {monthly_filter_value}"
    else:
        chart_title = "Monthly Trends Analysis"
    
    # Create beautiful bar combo chart with separate bars and rounded corners
    fig = go.Figure()
    
    # Add bar chart for bookings (primary metric - left Y-axis)
    if monthly_metric in ["All Metrics", "Bookings Only"]:
        fig.add_trace(go.Bar(
            x=monthly_stats['MonthName'],
            y=monthly_stats['Booking ID'],
            name='Total Bookings',
            marker_color='#E6B800',  # Darker yellow color
            opacity=0.95,
            yaxis='y',
            hovertemplate='<b>%{x}</b><br>Bookings: %{y:,.0f}<extra></extra>',
            marker=dict(
                line=dict(width=0),
                cornerradius=12  # Enhanced rounded corners
            ),
            offset=-0.3  # Offset to the left for better separation
        ))
    
    # Add line chart for revenue (secondary metric - left Y-axis)
    if monthly_metric in ["All Metrics", "Revenue Only"]:
        fig.add_trace(go.Scatter(
            x=monthly_stats['MonthName'],
            y=monthly_stats['Booking Value'] / 1000,
            mode='lines+markers',  # Changed to include markers/dots
            name='Revenue (₹K)',
            line=dict(color='#2E8B57', width=4),  # Darker green color, thick line
            marker=dict(
                size=10,  # Larger markers for better visibility
                color='#2E8B57',
                line=dict(width=2, color='white')  # White border around markers
            ),
            yaxis='y',
            hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:.0f}K<extra></extra>'
        ))
    
    # Add bar chart for customer rating (separate bars with enhanced rounded corners)
    if monthly_metric in ["All Metrics", "Rating Only"]:
        fig.add_trace(go.Bar(
            x=monthly_stats['MonthName'],
            y=monthly_stats['Customer Rating'],
            name='Customer Rating',
            marker_color='#FF4500',  # Darker orange color
            opacity=0.95,
            yaxis='y2',  # Use secondary Y-axis for proper scaling
            hovertemplate='<b>%{x}</b><br>Rating: %{y:.2f}/5<extra></extra>',
            marker=dict(
                line=dict(width=0),
                cornerradius=12  # Enhanced rounded corners
            ),
            offset=0.3  # Offset to the right for better separation
        ))
    
    # Professional layout configuration
    if monthly_filter_type == "Overall":
        yaxis_title = "Number of Bookings (Overall)"
        rating_title = "Customer Rating (Overall)"
        legend_title = "Metrics (Overall)"
    elif monthly_filter_type == "Days":
        yaxis_title = f"Number of Bookings ({monthly_filter_value})"
        rating_title = f"Customer Rating ({monthly_filter_value})"
        legend_title = f"Metrics ({monthly_filter_value})"
    elif monthly_filter_type == "Time":
        yaxis_title = f"Number of Bookings ({monthly_filter_value})"
        rating_title = f"Customer Rating ({monthly_filter_value})"
        legend_title = f"Metrics ({monthly_filter_value})"
    elif monthly_filter_type == "Monthly":
        yaxis_title = f"Number of Bookings ({monthly_filter_value})"
        rating_title = f"Customer Rating ({monthly_filter_value})"
        legend_title = f"Metrics ({monthly_filter_value})"
    else:
        yaxis_title = "Number of Bookings"
        rating_title = "Customer Rating"
        legend_title = "Metrics"
    
    if monthly_metric == "Revenue Only":
        yaxis_title = "Revenue (₹K)"
    elif monthly_metric == "Rating Only":
        yaxis_title = "Customer Rating"
    
    # Enhanced professional layout with proper bar separation and line positioning
    fig.update_layout(
        title=dict(
            text=f'📈 Monthly Trends Analysis - {monthly_filter_type}: {monthly_filter_value}',
            font=dict(size=18, color='#2c3e50'),
            x=0.5,
            xanchor='center',
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text='Month',
                font=dict(size=14, color='#34495e'),
                standoff=20
            ),
            tickfont=dict(size=12, color='#7f8c8d'),
            gridcolor='rgba(128, 128, 128, 0.15)',
            showline=True,
            linecolor='rgba(128, 128, 128, 0.4)',
            linewidth=1.5,
            tickangle=0,
            tickmode='array',
            tickvals=monthly_stats['MonthName'],
            ticktext=monthly_stats['MonthName']
        ),
        yaxis=dict(
            title=dict(
                text=yaxis_title,
                font=dict(size=14, color='#34495e'),
                standoff=30
            ),
            tickfont=dict(size=12, color='#7f8c8d'),
            gridcolor='rgba(128, 128, 128, 0.15)',
            showline=True,
            linecolor='rgba(128, 128, 128, 0.4)',
            linewidth=1.5,
            zeroline=True,
            zerolinecolor='rgba(128, 128, 128, 0.3)',
            zerolinewidth=1,
            side='left',
            # Set range to accommodate both bars and revenue line above with proper spacing
            range=[0, max(monthly_stats['Booking ID'].max() * 1.8, (monthly_stats['Booking Value'].max() / 1000) * 2.0)]
        ),
        yaxis2=dict(
            title=dict(
                text=rating_title,
                font=dict(size=14, color='#FF4500'),
                standoff=30
            ),
            tickfont=dict(size=12, color='#7f8c8d'),
            gridcolor='rgba(128, 128, 128, 0.05)',
            showline=True,
            linecolor='rgba(255, 69, 0, 0.6)',
            linewidth=1.5,
            zeroline=False,
            side='right',
            overlaying='y',
            range=[3.0, 5.0]  # Set appropriate range for ratings (3.0 to 5.0)
        ),
        template='plotly_white',
        height=500,
        width=900,
        hovermode='x unified',
        plot_bgcolor='rgba(248, 249, 250, 0.9)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
        margin=dict(l=100, r=100, t=120, b=100),
        barmode='group',  # Group bars side by side instead of overlaying
        bargap=0.5,  # Increased gap between bar groups for better separation
        bargroupgap=0.3,  # Increased gap between bars within groups for better separation
        legend=dict(
            title=dict(text=legend_title, font=dict(size=12, color='#34495e')),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(128, 128, 128, 0.2)',
            borderwidth=1,
            font=dict(size=12, color='#34495e')
        ),
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced monthly insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_month_idx = monthly_stats['Booking ID'].idxmax()
        best_month = month_names[monthly_stats.loc[best_month_idx, 'Month'] - 1]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #51cf66 0%, #40c057 100%); 
                    padding: 0.5rem; border-radius: 12px; color: white; text-align: center;
                    box-shadow: 0 6px 20px rgba(81, 207, 102, 0.3); margin: 0.3rem 0;
                    border-left: 4px solid #2b8a3e; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        animation: shimmer 3s ease-in-out infinite;"></div>
            <div style="position: relative; z-index: 2;">
                <div style="font-size: 1.4rem; margin-bottom: 0.2rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">📊</div>
                <div style="font-size: 0.8rem; font-weight: 600; margin-bottom: 0.1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Peak Month</div>
                <div style="font-size: 1rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{best_month}</div>
                <div style="font-size: 0.7rem; opacity: 0.9; margin-top: 0.1rem;">{monthly_stats.loc[best_month_idx, 'Booking ID']:,.0f} bookings</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        best_revenue_idx = monthly_stats['Booking Value'].idxmax()
        best_revenue_month = month_names[monthly_stats.loc[best_revenue_idx, 'Month'] - 1]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 0.5rem; border-radius: 12px; color: white; text-align: center;
                    box-shadow: 0 6px 20px rgba(79, 172, 254, 0.3); margin: 0.3rem 0;
                    border-left: 4px solid #1971c2; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        animation: pulse 2s ease-in-out infinite;"></div>
            <div style="position: relative; z-index: 2;">
                <div style="font-size: 1.4rem; margin-bottom: 0.2rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">💰</div>
                <div style="font-size: 0.8rem; font-weight: 600; margin-bottom: 0.1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Revenue Peak</div>
                <div style="font-size: 1rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{best_revenue_month}</div>
                <div style="font-size: 0.7rem; opacity: 0.9; margin-top: 0.1rem;">₹{monthly_stats.loc[best_revenue_idx, 'Booking Value']/1000:.0f}K</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        best_rating_idx = monthly_stats['Customer Rating'].idxmax()
        best_rating_month = month_names[monthly_stats.loc[best_rating_idx, 'Month'] - 1]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                    padding: 0.5rem; border-radius: 12px; color: white; text-align: center;
                    box-shadow: 0 6px 20px rgba(255, 154, 158, 0.3); margin: 0.3rem 0;
                    border-left: 4px solid #e64980; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        animation: float 2.5s ease-in-out infinite;"></div>
            <div style="position: relative; z-index: 2;">
                <div style="font-size: 1.4rem; margin-bottom: 0.2rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">⭐</div>
                <div style="font-size: 0.8rem; font-weight: 600; margin-bottom: 0.1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Rating Peak</div>
                <div style="font-size: 1rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{best_rating_month}</div>
                <div style="font-size: 0.7rem; opacity: 0.9; margin-top: 0.1rem;">{monthly_stats.loc[best_rating_idx, 'Customer Rating']:.2f}/5</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add minute-wise analysis if available
    if 'Minute' in df.columns:
        st.markdown('<div class="section-header"><h3>⏰ MINUTE-WISE ANALYSIS</h3></div>', unsafe_allow_html=True)
        
        minute_stats = df.groupby('Minute').agg({
            'Booking ID': 'count',
            'IsSuccessful': 'mean',
            'Booking Value': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=minute_stats['Minute'],
            y=minute_stats['Booking ID'],
            mode='lines+markers',
            name='Bookings by Minute',
            line=dict(color='#FF8C42', width=3),
            marker=dict(size=8, color='#FF8C42')
        ))
        
        fig.update_layout(
            title='⏰ Minute-wise Booking Patterns',
            xaxis_title='Minute of Hour',
            yaxis_title='Number of Bookings',
            template='plotly_white',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Minute insights
        peak_minute = minute_stats.loc[minute_stats['Booking ID'] == minute_stats['Booking ID'].max(), 'Minute'].iloc[0]
        st.info(f"⏰ **Peak Minute**: {peak_minute} minutes past the hour has highest bookings")
    
    # Enhanced temporal insights header with professional styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 0.7rem; border-radius: 15px; color: white; margin: 0.8rem 0;
                box-shadow: 0 8px 25px rgba(240, 147, 251, 0.4); text-align: center;
                position: relative; overflow: hidden; border: 2px solid rgba(255,255,255,0.2);">
        <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; 
                    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%); 
                    animation: shimmer 4s ease-in-out infinite;"></div>
        <div style="position: relative; z-index: 2;">
            <div style="font-size: 1.5rem; margin-bottom: 0.2rem; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));">📊</div>
            <h3 style="margin: 0; font-size: 1.2rem; font-weight: 800; text-shadow: 0 3px 6px rgba(0,0,0,0.4);
                       background: linear-gradient(45deg, #fff, #f0f8ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                TEMPORAL INSIGHTS & RECOMMENDATIONS
            </h3>
            <div style="font-size: 0.75rem; margin-top: 0.2rem; opacity: 0.9; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                Strategic Analysis for Business Optimization
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create professional insights cards with unified gradient
    col1, col2 = st.columns(2)
    
    with col1:
        # Peak Performance Insights
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; margin: 0.5rem 0;
                    box-shadow: 0 8px 25px rgba(255, 255, 0, 0.3); height: 380px; display: flex; flex-direction: column;">
            <h4 style="margin: 0 0 1.2rem 0; display: flex; align-items: center; font-size: 1.2rem; font-weight: bold;">
                🎯 Peak Performance Analysis
            </h4>
            <div style="background: rgba(255,255,255,0.18); padding: 0.9rem; border-radius: 10px; margin: 0.2rem 0.5rem; flex: 1; display: flex; flex-direction: column; justify-content: flex-start; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #ff6b6b;">
                <div style="font-weight: bold; margin-bottom: 0.6rem; font-size: 1.05rem; color: #fff;">Peak Hours:</div>
                <div style="font-size: 0.9rem; line-height: 1.5; color: rgba(255,255,255,0.95);">Focus resources during identified peak hours for optimal service delivery</div>
            </div>
            <div style="background: rgba(255,255,255,0.18); padding: 0.9rem; border-radius: 10px; margin: 0.2rem 0.5rem; flex: 1; display: flex; flex-direction: column; justify-content: flex-start; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #ff6b6b;">
                <div style="font-weight: bold; margin-bottom: 0.6rem; font-size: 1.05rem; color: #fff;">Best Days:</div>
                <div style="font-size: 0.9rem; line-height: 1.5; color: rgba(255,255,255,0.95);">Understand weekly demand variations for strategic staffing decisions</div>
            </div>
            <div style="background: rgba(255,255,255,0.18); padding: 0.9rem; border-radius: 10px; margin: 0.2rem 0.5rem; flex: 1; display: flex; flex-direction: column; justify-content: flex-start; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #ff6b6b;">
                <div style="font-weight: bold; margin-bottom: 0.6rem; font-size: 1.05rem; color: #fff;">Seasonal Patterns:</div>
                <div style="font-size: 0.9rem; line-height: 1.5; color: rgba(255,255,255,0.95);">Track monthly trends for long-term strategic planning</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Optimization Opportunities
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; margin: 0.5rem 0;
                    box-shadow: 0 8px 25px rgba(255, 255, 0, 0.3); height: 380px; display: flex; flex-direction: column;">
            <h4 style="margin: 0 0 1.2rem 0; display: flex; align-items: center; font-size: 1.2rem; font-weight: bold;">
                ⚡ Optimization Opportunities
            </h4>
            <div style="background: rgba(255,255,255,0.18); padding: 0.9rem; border-radius: 10px; margin: 0.2rem 0.5rem; flex: 1; display: flex; flex-direction: column; justify-content: flex-start; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #ff6b6b;">
                <div style="font-weight: bold; margin-bottom: 0.6rem; font-size: 1.05rem; color: #fff;">Low Hours:</div>
                <div style="font-size: 0.9rem; line-height: 1.5; color: rgba(255,255,255,0.95);">Implement promotional activities during low-demand periods</div>
            </div>
            <div style="background: rgba(255,255,255,0.18); padding: 0.9rem; border-radius: 10px; margin: 0.2rem 0.5rem; flex: 1; display: flex; flex-direction: column; justify-content: flex-start; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #ff6b6b;">
                <div style="font-weight: bold; margin-bottom: 0.6rem; font-size: 1.05rem; color: #fff;">Worst Days:</div>
                <div style="font-size: 0.9rem; line-height: 1.5; color: rgba(255,255,255,0.95);">Develop strategies to boost performance on slower days</div>
            </div>
            <div style="background: rgba(255,255,255,0.18); padding: 0.9rem; border-radius: 10px; margin: 0.2rem 0.5rem; flex: 1; display: flex; flex-direction: column; justify-content: flex-start; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #ff6b6b;">
                <div style="font-weight: bold; margin-bottom: 0.6rem; font-size: 1.05rem; color: #fff;">Revenue Cycles:</div>
                <div style="font-size: 0.9rem; line-height: 1.5; color: rgba(255,255,255,0.95);">Identify high-revenue months for investment decisions</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Key Metrics Summary with enhanced styling and optimized height
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                padding: 1.5rem; border-radius: 15px; color: white; margin: 0.5rem 0;
                box-shadow: 0 8px 25px rgba(255, 255, 0, 0.3); height: 200px;">
        <h4 style="margin: 0 0 1.2rem 0; text-align: center; font-size: 1.3rem; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">📈 Key Performance Indicators</h4>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; height: calc(100% - 4.5rem);">
            <div style="background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 12px; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: transform 0.2s ease; border-left: 4px solid #ff6b6b;">
                <div style="font-size: 1.6rem; font-weight: bold; margin-bottom: 0.3rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">🕒</div>
                <div style="font-weight: bold; margin-bottom: 0.2rem; font-size: 0.95rem; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Hourly Efficiency</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.9); line-height: 1.2;">Peak hour optimization</div>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 12px; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: transform 0.2s ease; border-left: 4px solid #ff6b6b;">
                <div style="font-size: 1.6rem; font-weight: bold; margin-bottom: 0.3rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">📅</div>
                <div style="font-weight: bold; margin-bottom: 0.2rem; font-size: 0.95rem; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Daily Performance</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.9); line-height: 1.2;">Weekly demand patterns</div>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 12px; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: transform 0.2s ease; border-left: 4px solid #ff6b6b;">
                <div style="font-size: 1.6rem; font-weight: bold; margin-bottom: 0.3rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">📊</div>
                <div style="font-weight: bold; margin-bottom: 0.2rem; font-size: 0.95rem; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Monthly Trends</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.9); line-height: 1.2;">Seasonal analysis</div>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.8rem; border-radius: 12px; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: transform 0.2s ease; border-left: 4px solid #ff6b6b;">
                <div style="font-size: 1.6rem; font-weight: bold; margin-bottom: 0.3rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">⏰</div>
                <div style="font-weight: bold; margin-bottom: 0.2rem; font-size: 0.95rem; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Precision Timing</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.9); line-height: 1.2;">Minute-level optimization</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_vehicle_analysis(df):
    """Create beautiful vehicle performance analysis."""
    st.markdown('<div class="section-header"><h2>🚗 VEHICLE PERFORMANCE ANALYSIS</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Vehicle popularity
        vehicle_popularity = df['Vehicle Type'].value_counts()
        
        # Define unique colors for each vehicle type
        vehicle_colors = {
            'Auto': '#FF6B6B',           # Red
            'Go Mini': '#4ECDC4',        # Teal
            'Go Sedan': '#45B7D1',       # Blue
            'eBike/Bike': '#96CEB4',     # Green
            'Premier Sedan': '#FFEAA7',  # Yellow
            'eBike': '#DDA0DD',          # Purple
            'UberXL': '#98D8C8'          # Light Green
        }
        
        fig = px.pie(
            values=vehicle_popularity.values,
            names=vehicle_popularity.index,
            title='🚗 Vehicle Type Distribution',
            color_discrete_map=vehicle_colors
        )
        fig.update_layout(
            height=500,  # Proper height for column layout
            title_font_size=18,
            title_font_color='#2c3e50',
            title_x=0.5,  # Center the title
            margin=dict(t=50, b=30, l=30, r=30),  # Balanced margins
            showlegend=True,
            legend=dict(
                font=dict(size=12),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#bdc3c7',
                borderwidth=1,
                x=1.02,
                y=1
            )
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=14,
            textfont_color='white',
            textfont_weight='bold',
            marker=dict(line=dict(width=2, color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Vehicle performance metrics
        vehicle_performance = df.groupby('Vehicle Type').agg({
            'IsSuccessful': 'mean',
            'Booking Value': 'mean',
            'Customer Rating': 'mean'
        }).reset_index()
        
        # Use the same color scheme for consistency
        colors = [vehicle_colors.get(vehicle, '#667eea') for vehicle in vehicle_performance['Vehicle Type']]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=vehicle_performance['Vehicle Type'],
            y=vehicle_performance['IsSuccessful'] * 100,
            name='Success Rate (%)',
            marker_color=colors,
            marker_line_width=0,
            marker=dict(
                cornerradius=12,  # Increased rounded corners from top
                line=dict(width=0)
            ),
            text=vehicle_performance['IsSuccessful'] * 100,
            texttemplate='%{text:.1f}%',
            textposition='inside',
            textfont=dict(
                size=12,
                color='white',
                weight='bold'
            )
        ))
        fig.update_layout(
            title='✅ Vehicle Success Rates',
            xaxis_title='Vehicle Type',
            yaxis_title='Success Rate (%)',
            template='plotly_white',
            height=500,  # Match pie chart height
            title_font_size=18,
            title_font_color='#2c3e50',
            title_x=0.5,  # Center the title
            margin=dict(t=50, b=30, l=30, r=30),  # Balanced margins to match pie chart
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                tickfont=dict(size=11),
                gridcolor='rgba(0,0,0,0.1)',
                range=[0, 100]  # Set y-axis scale to go from 0 to 100%
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Vehicle revenue analysis
    vehicle_revenue = df.groupby('Vehicle Type').agg({
        'Booking Value': ['sum', 'mean', 'count']
    }).round(2)
    vehicle_revenue.columns = ['Total_Revenue', 'Avg_Revenue', 'Total_Bookings']
    vehicle_revenue = vehicle_revenue.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=vehicle_revenue['Vehicle Type'],
        y=vehicle_revenue['Total_Revenue'],
        mode='lines+markers',
        name='Total Revenue',
        line=dict(color='#667eea', width=4),
        marker=dict(size=8, color='#667eea', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Total Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=vehicle_revenue['Vehicle Type'],
        y=vehicle_revenue['Avg_Revenue'],
        mode='lines+markers',
        name='Average Revenue',
        line=dict(color='#764ba2', width=4),
        marker=dict(size=8, color='#764ba2', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Average Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='💰 Vehicle Revenue Analysis',
        xaxis_title='Vehicle Type',
        yaxis_title='Revenue (₹)',
        template='plotly_white',
        height=500,
        title_font_size=18,
        title_font_color='#2c3e50',
        title_x=0.5,  # Center the title
        margin=dict(t=50, b=30, l=30, r=30),  # Consistent margins
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            font=dict(size=12),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#bdc3c7',
            borderwidth=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def create_revenue_analysis(df):
    """Create stunning revenue analysis visualizations."""
    st.markdown('<div class="section-header"><h2>💰 REVENUE ANALYSIS</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue distribution with enhanced styling
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 1rem;
                    border-left: 5px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.1rem; font-weight: bold;">
                💰 Revenue Distribution
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        fig = px.histogram(
            df, 
            x='Booking Value',
            nbins=100,  # Increased bins for better granularity
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            height=400,
            margin=dict(t=20, b=30, l=30, r=30),
            xaxis=dict(
                title='Booking Value (₹)',
                tickfont=dict(size=11),
                gridcolor='rgba(0,0,0,0.1)',
                range=[0, 1800]  # Limit x-axis to 2500 for better visuals
            ),
            yaxis=dict(
                title='Frequency',
                tickfont=dict(size=11),
                gridcolor='rgba(0,0,0,0.1)',
                range=[0, 60000]  # Increase y-axis to accommodate peak values
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_traces(
            marker=dict(
                line=dict(width=1, color='white'),
                opacity=0.8
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue by time category with enhanced styling
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 1rem;
                    border-left: 5px solid #764ba2; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.1rem; font-weight: bold;">
                🕒 Revenue by Time Category
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        revenue_by_time = df.groupby('TimeCategory')['Booking Value'].sum().reset_index()
        
        fig = px.bar(
            revenue_by_time,
            x='TimeCategory',
            y='Booking Value',
            color_discrete_sequence=['#764ba2']
        )
        fig.update_layout(
            height=400,
            margin=dict(t=20, b=30, l=30, r=30),
            xaxis=dict(
                title='Time Category',
                tickfont=dict(size=11),
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(
                title='Revenue (₹)',
                tickfont=dict(size=11),
                gridcolor='rgba(0,0,0,0.1)',
                range=[0, 25000000]  # Increase y-axis to accommodate peak values (25M)
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_traces(
            marker=dict(
                line=dict(width=1, color='white'),
                opacity=0.8
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Revenue trends over time with enhanced styling and filters
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 0.6rem; border-radius: 10px; margin-bottom: 1rem;
                border-left: 5px solid #f093fb; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h3 style="margin: 0; color: #2c3e50; font-size: 1.1rem; font-weight: bold;">
            📈 Revenue Trends Analysis
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Add filter controls
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        time_filter = st.selectbox(
            "Select Time Period:",
            ["Overall", "By Day", "By Week", "By Month"],
            help="Choose how to aggregate the revenue data"
        )
    
    with col_filter2:
        if time_filter == "By Day":
            selected_day = st.selectbox(
                "Select Day of Week:",
                ["All Days", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                help="Filter by specific day of the week"
            )
        elif time_filter == "By Month":
            selected_month = st.selectbox(
                "Select Month:",
                ["All Months"] + sorted(df['Date'].dt.month_name().unique().tolist()),
                help="Filter by specific month"
            )
        else:
            st.empty()  # Empty space for alignment
    
    # Prepare data based on filter selection
    if time_filter == "Overall":
        revenue_data = df.groupby('Date')['Booking Value'].sum().reset_index()
        title_suffix = "Daily Revenue Trends"
        x_title = "Date"
    elif time_filter == "By Day":
        if selected_day == "All Days":
            revenue_data = df.groupby(['Date', 'DayOfWeek'])['Booking Value'].sum().reset_index()
            revenue_data = revenue_data.groupby('Date')['Booking Value'].sum().reset_index()
            title_suffix = "Daily Revenue Trends (All Days)"
        else:
            day_mapping = {
                "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
                "Friday": 4, "Saturday": 5, "Sunday": 6
            }
            day_num = day_mapping[selected_day]
            filtered_df = df[df['Date'].dt.dayofweek == day_num]
            revenue_data = filtered_df.groupby('Date')['Booking Value'].sum().reset_index()
            title_suffix = f"Daily Revenue Trends ({selected_day}s)"
        x_title = "Date"
    elif time_filter == "By Week":
        df['Week'] = df['Date'].dt.isocalendar().week
        df['Year'] = df['Date'].dt.year
        df['Week_Year'] = df['Year'].astype(str) + '-W' + df['Week'].astype(str).str.zfill(2)
        revenue_data = df.groupby('Week_Year')['Booking Value'].sum().reset_index()
        revenue_data = revenue_data.rename(columns={'Week_Year': 'Date'})
        title_suffix = "Weekly Revenue Trends"
        x_title = "Week"
    elif time_filter == "By Month":
        if selected_month == "All Months":
            df['Month_Year'] = df['Date'].dt.to_period('M').astype(str)
            revenue_data = df.groupby('Month_Year')['Booking Value'].sum().reset_index()
            revenue_data = revenue_data.rename(columns={'Month_Year': 'Date'})
            title_suffix = "Monthly Revenue Trends"
        else:
            month_mapping = {
                "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }
            month_num = month_mapping[selected_month]
            filtered_df = df[df['Date'].dt.month == month_num]
            revenue_data = filtered_df.groupby('Date')['Booking Value'].sum().reset_index()
            title_suffix = f"Daily Revenue Trends ({selected_month})"
        x_title = "Month" if selected_month == "All Months" else "Date"
    
    # Define colors for different filters
    color_mapping = {
        "Overall": "#f093fb",
        "By Day": "#667eea",
        "By Week": "#4ecdc4", 
        "By Month": "#45b7d1"
    }
    
    # Get color based on filter
    chart_color = color_mapping.get(time_filter, "#f093fb")
    
    # Create the chart
    fig = go.Figure()
    
    # Add vertical lines for each data point using shapes
    for i, (date, value) in enumerate(zip(revenue_data['Date'], revenue_data['Booking Value'])):
        fig.add_shape(
            type="line",
            x0=date, x1=date,
            y0=0, y1=value,
            line=dict(
                color='rgba(0,0,0,0.1)',
                width=1
            )
        )
    
    # Add the main line chart
    fig.add_trace(go.Scatter(
        x=revenue_data['Date'],
        y=revenue_data['Booking Value'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color=chart_color, width=3),
        marker=dict(size=6, color=chart_color),
        fill='tonexty'
    ))
    
    # Calculate max revenue for proper y-axis scaling
    max_revenue = revenue_data['Booking Value'].max()
    y_axis_max = max_revenue * 1.15  # Add 15% padding to prevent cut-off
    
    # Configure x-axis based on filter type
    if time_filter == "By Week":
        xaxis_config = dict(
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.1)',
            tickmode='linear',
            dtick=1,
            tickangle=45
        )
    elif time_filter == "By Month" and selected_month == "All Months":
        xaxis_config = dict(
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.1)',
            tickmode='linear',
            dtick=1,
            tickangle=45
        )
    else:
        # For daily data, show all months
        xaxis_config = dict(
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.1)',
            tickmode='auto',
            nticks=12,  # Show more ticks for better month visibility
            tickangle=45
        )
    
    fig.update_layout(
        title=title_suffix,
        xaxis_title=x_title,
        yaxis_title='Revenue (₹)',
        template='plotly_white',
        height=500,
        margin=dict(t=20, b=30, l=30, r=30),
        xaxis=xaxis_config,
        yaxis=dict(
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.1)',
            range=[0, y_axis_max],  # Dynamic y-axis scaling
            showgrid=True
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Update axes with horizontal grid lines only
    fig.update_xaxes(
        showgrid=False,  # No x-axis grid since we have custom vertical lines
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0,0,0,0.1)',
        zeroline=False,
        range=[0, y_axis_max]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Add summary statistics
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric(
            label="Total Revenue",
            value=f"₹{revenue_data['Booking Value'].sum():,.0f}",
            help="Total revenue for the selected period"
        )
    
    with col_stat2:
        st.metric(
            label="Average Revenue",
            value=f"₹{revenue_data['Booking Value'].mean():,.0f}",
            help="Average revenue per period"
        )
    
    with col_stat3:
        st.metric(
            label="Peak Revenue",
            value=f"₹{revenue_data['Booking Value'].max():,.0f}",
            help="Highest revenue in the selected period"
        )
    
    with col_stat4:
        st.metric(
            label="Data Points",
            value=f"{len(revenue_data)}",
            help="Number of data points in the analysis"
        )

def create_cancellation_analysis(df):
    """Create insightful cancellation analysis."""
    st.markdown('<div class="section-header"><h2>🚫 CANCELLATION ANALYSIS</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cancellation reasons
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 0.6rem;
                    border-left: 5px solid #ff6b6b; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
                🚫 Booking Status Distribution
            </h3>
        </div>
        """, unsafe_allow_html=True)
        cancellation_reasons = df['Booking Status'].value_counts()
        
        fig = px.pie(
            values=cancellation_reasons.values,
            names=cancellation_reasons.index,
            title=None,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        # Add a bit more top/bottom margin so nothing is clipped
        fig.update_layout(height=400, margin=dict(t=40, b=40, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cancellation by vehicle type
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 0.6rem;
                    border-left: 5px solid #e64980; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
                ❌ Cancellation Rate by Vehicle Type
            </h3>
        </div>
        """, unsafe_allow_html=True)
        cancellation_by_vehicle = df.groupby('Vehicle Type')['IsSuccessful'].mean().reset_index()
        cancellation_by_vehicle['Cancellation_Rate'] = (1 - cancellation_by_vehicle['IsSuccessful']) * 100
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=cancellation_by_vehicle['Vehicle Type'],
            y=cancellation_by_vehicle['Cancellation_Rate'],
            name='Cancellation Rate (%)',
            marker_color='#ff6b6b'
        ))
        fig.update_layout(
            title='',
            xaxis_title='Vehicle Type',
            yaxis_title='Cancellation Rate (%)',
            template='plotly_white',
            height=400,
            margin=dict(t=40, b=40, l=10, r=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Lost revenue analysis
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 0.6rem; border-radius: 10px; margin: 0.6rem 0;
                border-left: 5px solid #ff6b6b; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
            💸 Lost Revenue by Booking Status
        </h3>
    </div>
    """, unsafe_allow_html=True)
    lost_revenue = df.groupby('Booking Status')['Booking Value'].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=lost_revenue['Booking Status'],
        y=lost_revenue['Booking Value'],
        marker_color='#ef5350'
    ))
    
    fig.update_layout(
        title='',
        xaxis_title='Booking Status',
        yaxis_title='Lost Revenue (₹)',
        template='plotly_white',
        height=500,
        margin=dict(t=40, b=40, l=10, r=10),
        yaxis=dict(range=[0, 50000000], tickformat='.0s')
    )
    st.plotly_chart(fig, use_container_width=True)

def create_customer_insights(df):
    """Create customer-focused insights."""
    st.markdown('<div class="section-header"><h2>👥 CUSTOMER INSIGHTS</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer ratings distribution
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 0.6rem;
                    border-left: 5px solid #51cf66; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
                ⭐ Customer Ratings Distribution
            </h3>
        </div>
        """, unsafe_allow_html=True)
        fig = px.histogram(
            df,
            x='Customer Rating',
            nbins=20,
            title=None,
            color_discrete_sequence=['#51cf66']
        )
        # Separate bars visually
        fig.update_traces(marker_line_width=1, marker_line_color='white')
        # Add some headroom to y-axis to avoid clipping
        try:
            y_vals = fig.data[0]['y'] if len(fig.data) > 0 else []
            if y_vals is not None and len(y_vals) > 0:
                y_max = max(y_vals)
                fig.update_layout(yaxis=dict(range=[0, y_max * 1.1]))
        except Exception:
            pass
        fig.update_layout(height=400, bargap=0.1, margin=dict(t=30, b=30, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Driver ratings vs Customer ratings - Changed to line graph with enhanced colors
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 0.6rem;
                    border-left: 5px solid #FF6B9D; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
                👨‍💼 Driver vs Customer Ratings Relationship
            </h3>
        </div>
        """, unsafe_allow_html=True)
        ratings_df = df.dropna(subset=['Driver Ratings', 'Customer Rating'])
        
        # Group by driver ratings and calculate average customer rating
        driver_customer_analysis = ratings_df.groupby('Driver Ratings')['Customer Rating'].agg(['mean', 'count']).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=driver_customer_analysis['Driver Ratings'],
            y=driver_customer_analysis['mean'],
            mode='lines+markers',
            name='Avg Customer Rating',
            line=dict(color='#FF6B9D', width=5),
            marker=dict(size=10, color='#FF6B9D', line=dict(width=2, color='white'))
        ))
        
        # Add trend line
        z = np.polyfit(driver_customer_analysis['Driver Ratings'], driver_customer_analysis['mean'], 1)
        p = np.poly1d(z)
        trend_vals = p(driver_customer_analysis['Driver Ratings'])
        fig.add_trace(go.Scatter(
            x=driver_customer_analysis['Driver Ratings'],
            y=trend_vals,
            mode='lines',
            name='Trend Line',
            line=dict(color='#FFA500', width=4, dash='dash')
        ))
        
        # Add y-axis padding so points/lines do not touch bounds
        y_all = list(driver_customer_analysis['mean'].values) + list(trend_vals)
        y_min = min(y_all) if len(y_all) else 0
        y_max = max(y_all) if len(y_all) else 5
        pad = max(0.02, (y_max - y_min) * 0.05)
        
        fig.update_layout(
            title='',
            xaxis_title='Driver Rating',
            yaxis_title='Average Customer Rating',
            template='plotly_white',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
            margin=dict(t=60, b=30, l=10, r=10),
            yaxis=dict(range=[y_min - pad, y_max + pad])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add correlation insight
        correlation = ratings_df['Driver Ratings'].corr(ratings_df['Customer Rating'])
        if correlation > 0.5:
            st.success(f"🔗 **Strong Positive Correlation**: Driver and Customer ratings are well aligned (r={correlation:.2f})")
        elif correlation > 0.2:
            st.info(f"🔗 **Moderate Correlation**: Some relationship between driver and customer ratings (r={correlation:.2f})")
        else:
            st.warning(f"🔗 **Weak Correlation**: Limited relationship between driver and customer ratings (r={correlation:.2f})")
    
    # Customer satisfaction trends with enhanced colors and insights
    st.markdown("""
    <div style=\"background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 0.6rem; border-radius: 10px; margin: 0.6rem 0;
                border-left: 5px solid #96CEB4; box-shadow: 0 2px 8px rgba(0,0,0,0.06);\">
        <h3 style=\"margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;\">
            📊 Daily Customer Satisfaction Trends with Moving Averages
        </h3>
    </div>
    """, unsafe_allow_html=True)

    daily_ratings = df.groupby('Date')['Customer Rating'].mean().reset_index()
    
    # Calculate moving averages for trend analysis
    daily_ratings['MA7'] = daily_ratings['Customer Rating'].rolling(window=7).mean()
    daily_ratings['MA30'] = daily_ratings['Customer Rating'].rolling(window=30).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_ratings['Date'],
        y=daily_ratings['Customer Rating'],
        mode='lines',
        name='Daily Average Rating',
        line=dict(color='#96CEB4', width=3.5)
    ))
    
    # Add moving averages
    fig.add_trace(go.Scatter(
        x=daily_ratings['Date'],
        y=daily_ratings['MA7'],
        mode='lines',
        name='7-Day Moving Average',
        line=dict(color='#FF8C42', width=3, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_ratings['Date'],
        y=daily_ratings['MA30'],
        mode='lines',
        name='30-Day Moving Average',
        line=dict(color='#FF6B6B', width=3, dash='dot')
    ))
    
    # Configure monthly ticks for 2024 to ensure all months are visible
    fig.update_xaxes(dtick='M1', tickformat='%b %Y')
    
    fig.update_layout(
        title='',
        xaxis_title='Date',
        yaxis_title='Average Rating',
        template='plotly_white',
        height=560,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        margin=dict(t=80, b=40, l=10, r=10)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced customer satisfaction insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_rating = daily_ratings['Customer Rating'].mean()
        st.metric(
            label="📊 Overall Average Rating",
            value=f"{avg_rating:.2f}/5",
            delta=f"{avg_rating - 4.5:.2f}"
        )
    
    with col2:
        best_day = daily_ratings.loc[daily_ratings['Customer Rating'].idxmax()]
        st.success(f"🏆 **Best Day**: {best_day['Date'].strftime('%Y-%m-%d')} ({best_day['Customer Rating']:.2f})")
    
    with col3:
        worst_day = daily_ratings.loc[daily_ratings['Customer Rating'].idxmin()]
        st.warning(f"📉 **Worst Day**: {worst_day['Date'].strftime('%Y-%m-%d')} ({worst_day['Customer Rating']:.2f})")
    
    # Trend analysis
    recent_trend = daily_ratings.tail(30)['Customer Rating'].mean() - daily_ratings.head(30)['Customer Rating'].mean()
    if recent_trend > 0.1:
        st.success(f"📈 **Improving Trend**: Customer satisfaction has improved by {recent_trend:.2f} points recently")
    elif recent_trend < -0.1:
        st.warning(f"📉 **Declining Trend**: Customer satisfaction has decreased by {abs(recent_trend):.2f} points recently")
    else:
        st.info(f"➡️ **Stable Trend**: Customer satisfaction has remained stable (change: {recent_trend:.2f} points)")

def create_geographic_analysis(df):
    """Create geographic insights."""
    st.markdown('<div class="section-header"><h2>📍 GEOGRAPHIC ANALYSIS</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top pickup locations
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 0.6rem;
                    border-left: 5px solid #764ba2; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
                📍 Top 10 Pickup Locations
            </h3>
        </div>
        """, unsafe_allow_html=True)

        top_pickup = df['Pickup Location'].value_counts().head(10)

        # Attach country flag (assuming India for this dataset)
        pickup_labels = [f"🇮🇳 {name}" for name in top_pickup.index]
        
        fig = px.bar(
            x=top_pickup.values,
            y=pickup_labels,
            orientation='h',
            title=None,
            color_discrete_sequence=['#764ba2']
        )
        fig.update_layout(height=400, margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top drop locations
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 0.6rem;
                    border-left: 5px solid #f093fb; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
                🎯 Top 10 Drop Locations
            </h3>
        </div>
        """, unsafe_allow_html=True)

        top_drop = df['Drop Location'].value_counts().head(10)

        drop_labels = [f"🇮🇳 {name}" for name in top_drop.index]
        
        fig = px.bar(
            x=top_drop.values,
            y=drop_labels,
            orientation='h',
            title=None,
            color_discrete_sequence=['#f093fb']
        )
        fig.update_layout(height=400, margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    
    # Location performance
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 0.6rem; border-radius: 10px; margin: 0.6rem 0;
                border-left: 5px solid #51cf66; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
            ✅ Top 15 Locations by Success Rate
        </h3>
    </div>
    """, unsafe_allow_html=True)

    location_performance = df.groupby('Pickup Location').agg({
        'IsSuccessful': 'mean',
        'Booking Value': 'mean',
        'Customer Rating': 'mean'
    }).reset_index()
    
    location_performance = location_performance.sort_values('IsSuccessful', ascending=False).head(15)
    
    # Add India flag to labels
    loc_labels = [f"🇮🇳 {name}" for name in location_performance['Pickup Location']]

    # Use different colors per city
    color_palette = px.colors.qualitative.Set3
    colors = [color_palette[i % len(color_palette)] for i in range(len(loc_labels))]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=loc_labels,
        y=location_performance['IsSuccessful'] * 100,
        marker_color=colors,
        name='Success Rate (%)'
    ))

    fig.update_layout(
        title='',
        xaxis_title='Pickup Location',
        yaxis_title='Success Rate (%)',
        template='plotly_white',
        height=520,
        margin=dict(t=20, b=80, l=10, r=10)
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

def create_advanced_analytics(df):
    """Create advanced analytics and insights."""
    st.markdown('<div class="section-header"><h2>🔬 ADVANCED ANALYTICS</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Relationship explorer header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 0.6rem;
                    border-left: 5px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
                🔗 Feature Relationship Explorer
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Horizontal Progress Bar Chart - Top Categories
        time_counts = df['TimeCategory'].value_counts()
        vehicle_counts = df['Vehicle Type'].value_counts()
        revenue_counts = df['RevenueCategory'].value_counts()
        
        # Get top 5 from each category and calculate percentages
        top_time = time_counts.head(5)
        top_vehicle = vehicle_counts.head(5)
        top_revenue = revenue_counts.head(5)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Colors for different categories
        colors = ['#9C27B0', '#E91E63', '#00BCD4', '#2196F3', '#4CAF50']
        
        # Combine all categories for display
        all_categories = []
        all_values = []
        all_percentages = []
        all_colors = []
        
        # Add Time Category data
        for i, (label, value) in enumerate(top_time.items()):
            percentage = (value / len(df)) * 100
            all_categories.append(f"Time: {label}")
            all_values.append(percentage)
            all_percentages.append(f"{percentage:.1f}%")
            all_colors.append(colors[i % len(colors)])
        
        # Add Vehicle Type data
        for i, (label, value) in enumerate(top_vehicle.items()):
            percentage = (value / len(df)) * 100
            all_categories.append(f"Vehicle: {label}")
            all_values.append(percentage)
            all_percentages.append(f"{percentage:.1f}%")
            all_colors.append(colors[i % len(colors)])
        
        # Add Revenue Category data
        for i, (label, value) in enumerate(top_revenue.items()):
            percentage = (value / len(df)) * 100
            all_categories.append(f"Revenue: {label}")
            all_values.append(percentage)
            all_percentages.append(f"{percentage:.1f}%")
            all_colors.append(colors[i % len(colors)])
        
        # Create horizontal bars with better visual styling
        fig.add_trace(go.Bar(
            y=all_categories,
            x=all_values,
            orientation='h',
            marker=dict(
                color=all_colors,
                line=dict(color='white', width=2),
                opacity=0.85
            ),
            text=all_percentages,
            textposition='inside',
            textfont=dict(
                color='white', 
                size=13,
                family='Arial'
            ),
            hovertemplate='<b>%{y}</b><br>Count: %{customdata:,}<br>Percentage: %{x:.1f}%<extra></extra>',
            customdata=[time_counts.get(cat.split(': ')[1], 0) if 'Time:' in cat 
                       else vehicle_counts.get(cat.split(': ')[1], 0) if 'Vehicle:' in cat
                       else revenue_counts.get(cat.split(': ')[1], 0) for cat in all_categories]
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Top Categories Distribution</b>",
                x=0.5,
                font=dict(size=16, color='#2c3e50'),
                pad=dict(t=10, b=20)
            ),
            xaxis=dict(
                title="Percentage (%)",
                range=[0, 100],
                tickfont=dict(size=11),
                gridcolor='rgba(0,0,0,0.1)',
                showgrid=True,
                tickmode='linear',
                tick0=0,
                dtick=20
            ),
            yaxis=dict(
                title="Categories",
                tickfont=dict(size=11),
                gridcolor='rgba(0,0,0,0.05)',
                showgrid=True
            ),
            height=650,
            margin=dict(t=60, b=50, l=200, r=50),
            showlegend=False,
            plot_bgcolor='rgba(248,249,250,0.5)',
            paper_bgcolor='white',
            font=dict(family='Arial', size=11),
            bargap=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue categories header
        st.markdown("""
        <div style=\"background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 0.6rem; border-radius: 10px; margin-bottom: 0.6rem;
                    border-left: 5px solid #f093fb; box-shadow: 0 2px 8px rgba(0,0,0,0.06);\">
            <h3 style=\"margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;\">
                💰 Revenue Category Distribution
            </h3>
        </div>
        """, unsafe_allow_html=True)

        revenue_categories = df['RevenueCategory'].value_counts()
        labels_with_counts = [f"{name} ({count})" for name, count in zip(revenue_categories.index, revenue_categories.values)]
        values = revenue_categories.values.tolist()
        total = sum(values) if len(values) else 1
        percents = [v / total * 100 for v in values]
        # Place labels outside if slice < 6%
        text_positions = ['outside' if p < 6 else 'inside' for p in percents]
        fig = go.Figure(go.Pie(
            labels=labels_with_counts,
            values=values,
            hole=0.55,
            textinfo='none',
            texttemplate='%{label}<br>%{percent}',
            textposition=text_positions,
            marker=dict(colors=['#ef5350','#4dabf7','#69db7c','#b197fc'], line=dict(color='white', width=1)),
            showlegend=True
        ))
        fig.update_layout(
            height=640,
            margin=dict(t=30, b=30, l=30, r=30),
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0)
        )
        fig.update_traces(automargin=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # Time series analysis header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 0.6rem; border-radius: 10px; margin: 0.6rem 0;
                border-left: 5px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <h3 style="margin: 0; color: #2c3e50; font-size: 1.05rem; font-weight: 700;">
            📈 Time Series Analysis with Moving Averages
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Month filter
    month_options = ['All Months'] + sorted(df['Date'].dt.strftime('%B').unique().tolist(), key=lambda m: datetime.strptime(m, '%B').month)
    selected_month = st.selectbox('Filter by Month', month_options, index=0)

    daily_bookings = df.groupby('Date')['Booking ID'].count().reset_index()
    daily_bookings = daily_bookings.set_index('Date').sort_index()
    if selected_month != 'All Months':
        month_num = datetime.strptime(selected_month, '%B').month
        daily_bookings = daily_bookings[daily_bookings.index.month == month_num]
    
    # Calculate moving averages (only used when viewing all months)
    if selected_month == 'All Months':
        daily_bookings['MA7'] = daily_bookings['Booking ID'].rolling(window=7).mean()
        daily_bookings['MA30'] = daily_bookings['Booking ID'].rolling(window=30).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_bookings.index,
        y=daily_bookings['Booking ID'],
        mode='lines',
        name='Daily Bookings',
        line=dict(color='#667eea', width=2)
    ))
    # Show moving averages only when not filtering to a single month
    if selected_month == 'All Months':
        fig.add_trace(go.Scatter(
            x=daily_bookings.index,
            y=daily_bookings['MA7'],
            mode='lines',
            name='7-Day Moving Average',
            line=dict(color='#ff4d4f', width=3, dash='dot')
        ))
        fig.add_trace(go.Scatter(
            x=daily_bookings.index,
            y=daily_bookings['MA30'],
            mode='lines',
            name='30-Day Moving Average',
            line=dict(color='#f093fb', width=3)
        ))
    
    fig.update_layout(
        title='',
        xaxis_title='Date',
        yaxis_title='Number of Bookings',
        template='plotly_white',
        height=520,
        margin=dict(t=20, b=40, l=10, r=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0)
    )
    fig.update_xaxes(dtick='M1', tickformat='%b %Y')
    st.plotly_chart(fig, use_container_width=True)
    
    # Business recommendations (simplified, remove extra decorative container)
    st.markdown("""
    **🚀 Strategic Recommendations:**
    
    1. **Peak Hour Optimization**: Focus resources during identified peak hours
    2. **Vehicle Allocation**: Optimize fleet distribution based on demand patterns
    3. **Pricing Strategy**: Implement dynamic pricing during high-demand periods
    4. **Customer Experience**: Address factors affecting customer ratings
    5. **Operational Efficiency**: Reduce cancellation rates through targeted improvements
    """)

def main():
    """Main function to run the stunning dashboard."""
    # Load data
    df = load_data()
    
    if df is None:
        st.error("❌ Unable to load data. Please ensure the data cleaning script has been run.")
        st.stop()
    
    # Create header
    create_header()
    
    # Create sidebar filterschange 
    filtered_df = create_filters_sidebar(df)
    
    # Create KPI section
    create_kpi_section(filtered_df)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🕒 Temporal Analysis", 
        "🚗 Vehicle Analysis", 
        "💰 Revenue Analysis", 
        "🚫 Cancellation Analysis",
        "👥 Customer Insights",
        "📍 Geographic Analysis",
        "🔬 Advanced Analytics"
    ])
    
    with tab1:
        create_temporal_analysis(filtered_df)
    
    with tab2:
        create_vehicle_analysis(filtered_df)
    
    with tab3:
        create_revenue_analysis(filtered_df)
    
    with tab4:
        create_cancellation_analysis(filtered_df)
    
    with tab5:
        create_customer_insights(filtered_df)
    
    with tab6:
        create_geographic_analysis(filtered_df)
    
    with tab7:
        create_advanced_analytics(filtered_df)
    
    # Performance monitoring section with enhanced unified styling
    st.markdown('<div class="section-header"><h2>📊 PERFORMANCE MONITORING</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Real-time metrics with enhanced styling and improved visibility
        current_success_rate = filtered_df['IsSuccessful'].mean() * 100
        target_success_rate = 95.0
        success_delta = current_success_rate - target_success_rate
        success_arrow = "↗️" if success_delta > 0 else "↘️"
        success_color = "#51cf66" if success_delta > 0 else "#ff6b6b"
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; text-align: center;
                    box-shadow: 0 8px 25px rgba(255, 255, 0, 0.3); height: 420px; display: flex; flex-direction: column;">
            <h4 style="margin: 0 0 1.2rem 0; font-size: 1.2rem; font-weight: bold; display: flex; align-items: center; justify-content: center; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                ⚡ Real-Time Performance
            </h4>
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.15) 100%); 
                        padding: 0.8rem; border-radius: 12px; margin: 0.1rem 0; height: 300px; display: flex; flex-direction: column; 
                        justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.3);
                        border: 1px solid rgba(255,255,255,0.25); border-left: 4px solid #51cf66; backdrop-filter: blur(6px); position: relative;">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 2.8rem; font-weight: 800; margin-bottom: 0.3rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4);
                               background: linear-gradient(45deg, #fff, #e6f3ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{:.1f}%</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Current Success Rate</div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.4rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0.6rem; 
                               background: rgba(255,255,255,0.1); border-radius: 8px; border-left: 3px solid rgba(255,255,255,0.4);">
                        <span style="font-size: 0.9rem; color: rgba(255,255,255,0.9);">Target</span>
                        <span style="font-size: 0.9rem; font-weight: 600; color: #fff;">95.0%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0.6rem; 
                               background: rgba(255,255,255,0.1); border-radius: 8px; border-left: 3px solid {};">
                        <span style="font-size: 0.9rem; color: rgba(255,255,255,0.9);">Variance</span>
                        <span style="font-size: 0.9rem; font-weight: 600; color: {};">{} {}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0.6rem; 
                               background: rgba(255,255,255,0.1); border-radius: 8px; border-left: 3px solid {};">
                        <span style="font-size: 0.9rem; color: rgba(255,255,255,0.9);">Status</span>
                        <span style="font-size: 0.9rem; font-weight: 600; color: {};">{}</span>
                    </div>
                </div>
            </div>
        </div>
        """.format(current_success_rate, success_color, success_color, success_arrow, f"{abs(success_delta):.1f}", 
                   success_color, success_color, "Above" if success_delta > 0 else "Below"), unsafe_allow_html=True)
    
    with col2:
        # Efficiency metrics with enhanced styling and improved visibility
        avg_vtat = filtered_df['Avg VTAT'].mean()
        avg_ctat = filtered_df['Avg CTAT'].mean()
        vtat_target = 8.0
        ctat_target = 25.0
        vtat_delta = avg_vtat - vtat_target
        ctat_delta = avg_ctat - ctat_target
        vtat_arrow = "↗️" if vtat_delta > 0 else "↘️"
        ctat_arrow = "↗️" if ctat_delta > 0 else "↘️"
        vtat_color = "#ff6b6b" if vtat_delta > 0 else "#51cf66"
        ctat_color = "#ff6b6b" if ctat_delta > 0 else "#51cf66"
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; text-align: center;
                    box-shadow: 0 8px 25px rgba(255, 255, 0, 0.3); height: 420px; display: flex; flex-direction: column;">
            <h4 style="margin: 0 0 1.2rem 0; font-size: 1.2rem; font-weight: bold; display: flex; align-items: center; justify-content: center; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                🎯 Efficiency Metrics
            </h4>
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.15) 100%); 
                        padding: 0.6rem; border-radius: 12px; margin: 0.1rem 0; height: 140px; display: flex; flex-direction: column; 
                        justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.3);
                        border: 1px solid rgba(255,255,255,0.25); border-left: 4px solid #51cf66; backdrop-filter: blur(6px);">
                <div style="text-align: center; margin-bottom: 0.6rem;">
                    <div style="font-size: 2.2rem; font-weight: 800; margin-bottom: 0.2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4);
                               background: linear-gradient(45deg, #fff, #e6f3ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{:.1f} min</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Avg VTAT</div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0.5rem; 
                           background: rgba(255,255,255,0.1); border-radius: 6px; border-left: 3px solid {};">
                    <span style="font-size: 0.8rem; color: rgba(255,255,255,0.9);">Variance</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: {};">{} {} min</span>
                </div>
            </div>
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.15) 100%); 
                        padding: 0.6rem; border-radius: 12px; margin: 0.1rem 0; height: 140px; display: flex; flex-direction: column; 
                        justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.3);
                        border: 1px solid rgba(255,255,255,0.25); border-left: 4px solid #51cf66; backdrop-filter: blur(6px);">
                <div style="text-align: center; margin-bottom: 0.6rem;">
                    <div style="font-size: 2.2rem; font-weight: 800; margin-bottom: 0.2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4);
                               background: linear-gradient(45deg, #fff, #e6f3ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{:.1f} min</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Avg CTAT</div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0.5rem; 
                           background: rgba(255,255,255,0.1); border-radius: 6px; border-left: 3px solid {};">
                    <span style="font-size: 0.8rem; color: rgba(255,255,255,0.9);">Variance</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: {};">{} {} min</span>
                </div>
            </div>
        </div>
        """.format(avg_vtat, vtat_color, vtat_color, vtat_arrow, f"{abs(vtat_delta):.1f}",
                   avg_ctat, ctat_color, ctat_color, ctat_arrow, f"{abs(ctat_delta):.1f}"), unsafe_allow_html=True)
    
    with col3:
        # Customer satisfaction with enhanced styling and improved visibility
        avg_customer_rating = filtered_df['Customer Rating'].mean()
        avg_driver_rating = filtered_df['Driver Ratings'].mean()
        customer_target = 4.5
        driver_target = 4.3
        customer_delta = avg_customer_rating - customer_target
        driver_delta = avg_driver_rating - driver_target
        customer_arrow = "↗️" if customer_delta > 0 else "↘️"
        driver_arrow = "↗️" if driver_delta > 0 else "↘️"
        customer_color = "#51cf66" if customer_delta > 0 else "#ff6b6b"
        driver_color = "#51cf66" if driver_delta > 0 else "#ff6b6b"
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.2rem; border-radius: 15px; color: white; text-align: center;
                    box-shadow: 0 8px 25px rgba(255, 255, 0, 0.3); height: 420px; display: flex; flex-direction: column;">
            <h4 style="margin: 0 0 1.2rem 0; font-size: 1.2rem; font-weight: bold; display: flex; align-items: center; justify-content: center; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                ⭐ Customer Satisfaction
            </h4>
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.15) 100%); 
                        padding: 0.6rem; border-radius: 12px; margin: 0.1rem 0; height: 140px; display: flex; flex-direction: column; 
                        justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.3);
                        border: 1px solid rgba(255,255,255,0.25); border-left: 4px solid #51cf66; backdrop-filter: blur(6px);">
                <div style="text-align: center; margin-bottom: 0.6rem;">
                    <div style="font-size: 2.2rem; font-weight: 800; margin-bottom: 0.2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4);
                               background: linear-gradient(45deg, #fff, #e6f3ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{:.1f}/5</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Customer Rating</div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0.5rem; 
                           background: rgba(255,255,255,0.1); border-radius: 6px; border-left: 3px solid {};">
                    <span style="font-size: 0.8rem; color: rgba(255,255,255,0.9);">Variance</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: {};">{} {}</span>
                </div>
            </div>
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.15) 100%); 
                        padding: 0.6rem; border-radius: 12px; margin: 0.1rem 0; height: 140px; display: flex; flex-direction: column; 
                        justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.3);
                        border: 1px solid rgba(255,255,255,0.25); border-left: 4px solid #51cf66; backdrop-filter: blur(6px);">
                <div style="text-align: center; margin-bottom: 0.6rem;">
                    <div style="font-size: 2.2rem; font-weight: 800; margin-bottom: 0.2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4);
                               background: linear-gradient(45deg, #fff, #e6f3ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{:.1f}/5</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Driver Rating</div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0.5rem; 
                           background: rgba(255,255,255,0.1); border-radius: 6px; border-left: 3px solid {};">
                    <span style="font-size: 0.8rem; color: rgba(255,255,255,0.9);">Variance</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: {};">{} {}</span>
                </div>
            </div>
        </div>
        """.format(avg_customer_rating, customer_color, customer_color, customer_arrow, f"{abs(customer_delta):.1f}",
                   avg_driver_rating, driver_color, driver_color, driver_arrow, f"{abs(driver_delta):.1f}"), unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
        <h3>🚗 Uber Ride Analytics 2024 Dashboard</h3>
        <p>Built with ❤️ using Streamlit | Professional Business Intelligence Solution</p>
        <p style="margin-top: 1rem; opacity: 0.8;">Last Updated: {}</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
