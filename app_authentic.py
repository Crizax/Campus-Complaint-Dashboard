import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION & PREMIUM THEMING
# ==========================================
st.set_page_config(
    page_title="University Complaints Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enlarge text, improve typography, and remove generic styling
st.markdown("""
<style>
    /* Global Base Font scaling */
    html, body, [class*="css"] {
        font-size: 16px !important;
    }
    
    /* Sidebar text sizes */
    .css-1d391kg p, .sidebar .sidebar-content {
        font-size: 1.1rem !important;
    }
    div[data-baseweb="select"] {
        font-size: 1.05rem !important;
    }

    /* ADAPTIVE Floating Cards for KPIs */
    div[data-testid="metric-container"] {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--faded-text-10);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        border-color: #2563eb;
    }

    /* ADAPTIVE KPI Label and Value Font Boost */
    div[data-testid="metric-container"] label {
        font-size: 1.1rem !important;
        color: var(--text-color) !important;
        opacity: 0.8;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        color: var(--text-color) !important;
    }

    /* Web-app Tab Styling */
    button[data-baseweb="tab"] {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🎓 University Complaints & Reports Analysis Dashboard")
st.markdown("Real dataset analysis with 1,005 student complaints • Data-driven insights for institutional improvement")
st.markdown("---")

# ==========================================
# 2. DATA LOADING ENGINE
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv('university_complaints_real.csv')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['Month'] = df['Timestamp'].dt.strftime('%B')
    df['Day of Week'] = df['Timestamp'].dt.day_name()
    df['Hour'] = df['Timestamp'].dt.hour
    return df

df = load_data()

# ==========================================
# 3. GLOBAL FILTERS (8 DIMENSIONS)
# ==========================================
st.sidebar.header("🎛️ Advanced Filtering")

# Original + derived category filters
all_genres = ["All Complaint Types"] + sorted(list(df['Genre'].unique()))
selected_genre = st.sidebar.selectbox("Complaint Category (Original)", all_genres)

all_campuses = ["All Campuses"] + sorted(list(df['Campus'].unique()))
selected_campus = st.sidebar.selectbox("Campus Location", all_campuses)

all_depts = ["All Departments"] + sorted(list(df['Department'].unique()))
selected_dept = st.sidebar.selectbox("Academic Department", all_depts)

all_severities = ["All Severities"] + sorted(list(df['Severity'].unique()))
selected_severity = st.sidebar.selectbox("Issue Severity", all_severities)

all_statuses = ["All Statuses"] + sorted(list(df['Status'].unique()))
selected_status = st.sidebar.selectbox("Resolution Status", all_statuses)

all_resp_depts = ["All Departments"] + sorted(list(df['Responsible_Department'].unique()))
selected_resp_dept = st.sidebar.selectbox("Handling Department", all_resp_depts)

# Demographic filters
min_age = st.sidebar.slider("Student Age Range", int(df['Age'].min()), int(df['Age'].max()), 
                             (int(df['Age'].min()), int(df['Age'].max())))
min_gpa = st.sidebar.slider("GPA Range", float(df['Gpa'].min()), float(df['Gpa'].max()), 
                            (float(df['Gpa'].min()), float(df['Gpa'].max())), 0.1)

min_date, max_date = df['Date'].min(), df['Date'].max()
selected_date_range = st.sidebar.date_input("Time Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# ==========================================
# 4. FILTERING LOGIC
# ==========================================
filtered_df = df.copy()

if selected_genre != "All Complaint Types": 
    filtered_df = filtered_df[filtered_df['Genre'] == selected_genre]
if selected_campus != "All Campuses": 
    filtered_df = filtered_df[filtered_df['Campus'] == selected_campus]
if selected_dept != "All Departments": 
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
if selected_severity != "All Severities": 
    filtered_df = filtered_df[filtered_df['Severity'] == selected_severity]
if selected_status != "All Statuses": 
    filtered_df = filtered_df[filtered_df['Status'] == selected_status]
if selected_resp_dept != "All Departments": 
    filtered_df = filtered_df[filtered_df['Responsible_Department'] == selected_resp_dept]

# Age and GPA filters
filtered_df = filtered_df[(filtered_df['Age'] >= min_age[0]) & (filtered_df['Age'] <= min_age[1])]
filtered_df = filtered_df[(filtered_df['Gpa'] >= min_gpa[0]) & (filtered_df['Gpa'] <= min_gpa[1])]

# Date range filter
if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]

# ==========================================
# 5. BANNER EXECUTIVE METRICS (KPIs)
# ==========================================
total_complaints = len(filtered_df)
resolved_count = len(filtered_df[filtered_df['Status'] == 'Resolved'])
resolution_rate = (resolved_count / total_complaints * 100) if total_complaints > 0 else 0.0
critical_issues = len(filtered_df[filtered_df['Severity'].isin(['Critical', 'High'])])
avg_gpa = filtered_df['Gpa'].mean() if len(filtered_df) > 0 else 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="📊 Total Complaints", value=f"{total_complaints:,}")
kpi2.metric(label="✅ Resolution Rate", value=f"{resolution_rate:.1f}%")
kpi3.metric(label="⚠️ Critical Issues", value=f"{critical_issues:,}")
kpi4.metric(label="📈 Avg Student GPA", value=f"{avg_gpa:.2f}")

st.markdown("---")

# ==========================================
# 6. TAB ARCHITECTURE
# ==========================================
tab_overview, tab_demographics, tab_trends, tab_raw_data = st.tabs([
    "📊 Complaint Analysis", 
    "👥 Student Demographics", 
    "📈 Temporal Trends",
    "📋 Raw Data Explorer"
])

# ------------------------------------------
# TAB 1: COMPLAINT ANALYSIS
# ------------------------------------------
with tab_overview:
    chart_font = dict(family="sans-serif", size=13, color="#1e293b")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Complaints by Category")
        if len(filtered_df) > 0:
            genre_df = filtered_df['Genre'].value_counts().reset_index()
            genre_df.columns = ['Category', 'Count']
            fig_genre = px.bar(genre_df, x='Count', y='Category', orientation='h', 
                              color='Count', color_continuous_scale='Viridis', text_auto=True)
            fig_genre.update_layout(showlegend=False, height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font)
            st.plotly_chart(fig_genre, use_container_width=True)

    with col2:
        st.subheader("Severity Distribution")
        if len(filtered_df) > 0:
            severity_df = filtered_df['Severity'].value_counts().reset_index()
            severity_df.columns = ['Severity', 'Count']
            severity_order = ['Critical', 'High', 'Medium', 'Low']
            severity_df['Severity'] = pd.Categorical(severity_df['Severity'], categories=severity_order, ordered=True)
            severity_df = severity_df.sort_values('Severity')
            fig_sev = px.pie(severity_df, values='Count', names='Severity', 
                            color_discrete_map={'Critical': '#dc2626', 'High': '#f97316', 
                                               'Medium': '#eab308', 'Low': '#22c55e'})
            fig_sev.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font)
            st.plotly_chart(fig_sev, use_container_width=True)

    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Status Breakdown")
        if len(filtered_df) > 0:
            status_df = filtered_df['Status'].value_counts().reset_index()
            status_df.columns = ['Status', 'Count']
            fig_status = px.bar(status_df, x='Status', y='Count', color='Status',
                               color_discrete_sequence=['#ef4444', '#f59e0b', '#10b981', '#6366f1'])
            fig_status.update_layout(showlegend=False, height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font)
            st.plotly_chart(fig_status, use_container_width=True)

    with col4:
        st.subheader("Handling Department")
        if len(filtered_df) > 0:
            dept_df = filtered_df['Responsible_Department'].value_counts().reset_index()
            dept_df.columns = ['Department', 'Count']
            fig_dept = px.pie(dept_df, values='Count', names='Department')
            fig_dept.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font)
            st.plotly_chart(fig_dept, use_container_width=True)

# ------------------------------------------
# TAB 2: STUDENT DEMOGRAPHICS
# ------------------------------------------
with tab_demographics:
    chart_font = dict(family="sans-serif", size=13, color="#1e293b")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Gender Distribution")
        if len(filtered_df) > 0:
            gender_df = filtered_df['Gender'].value_counts().reset_index()
            gender_df.columns = ['Gender', 'Count']
            gender_map = {'M': 'Male', 'F': 'Female'}
            gender_df['Gender'] = gender_df['Gender'].map(gender_map)
            fig_gender = px.pie(gender_df, values='Count', names='Gender', 
                               color_discrete_sequence=['#3b82f6', '#ec4899'])
            fig_gender.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font)
            st.plotly_chart(fig_gender, use_container_width=True)
    
    with col2:
        st.subheader("Academic Year Distribution")
        if len(filtered_df) > 0:
            year_df = filtered_df['Year'].value_counts().sort_index().reset_index()
            year_df.columns = ['Year', 'Count']
            fig_year = px.bar(year_df, x='Year', y='Count', color='Year', text_auto=True,
                             color_continuous_scale='Blues')
            fig_year.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font, showlegend=False)
            st.plotly_chart(fig_year, use_container_width=True)
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Age Distribution")
        if len(filtered_df) > 0:
            fig_age = px.histogram(filtered_df, x='Age', nbins=12, color_discrete_sequence=['#06b6d4'],
                                  title="Student Age Range")
            fig_age.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font, 
                                 showlegend=False, xaxis_title="Age", yaxis_title="Count")
            st.plotly_chart(fig_age, use_container_width=True)
    
    with col4:
        st.subheader("GPA Distribution")
        if len(filtered_df) > 0:
            fig_gpa = px.histogram(filtered_df, x='Gpa', nbins=20, color_discrete_sequence=['#8b5cf6'],
                                  title="Student GPA Range")
            fig_gpa.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font,
                                 showlegend=False, xaxis_title="GPA", yaxis_title="Count")
            st.plotly_chart(fig_gpa, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Complaint Severity by Student Demographics")
    if len(filtered_df) > 0:
        col5, col6 = st.columns(2)
        with col5:
            fig_gpa_sev = px.box(filtered_df, x='Severity', y='Gpa',
                                category_orders={"Severity": ["Critical", "High", "Medium", "Low"]},
                                title="GPA vs Complaint Severity")
            fig_gpa_sev.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font)
            st.plotly_chart(fig_gpa_sev, use_container_width=True)
        
        with col6:
            fig_age_sev = px.box(filtered_df, x='Severity', y='Age',
                                category_orders={"Severity": ["Critical", "High", "Medium", "Low"]},
                                title="Age vs Complaint Severity")
            fig_age_sev.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), font=chart_font)
            st.plotly_chart(fig_age_sev, use_container_width=True)

# ==========================================
# PASTE THIS INTO app_authentic.py 
# Replace the existing tab_trends section
# ==========================================

# ------------------------------------------
# TAB 3: TEMPORAL TRENDS
# ------------------------------------------
with tab_trends:
    st.subheader("📅 Temporal Analysis & Patterns")
    chart_font = dict(family="sans-serif", size=13, color="#1e293b")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Monthly Complaint Trends")
        st.write("Complaints by month with severity breakdown")
        if len(filtered_df) > 0:
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            trend_df = filtered_df.groupby(['Month', 'Severity']).size().reset_index(name='Count')
            trend_df['Month'] = pd.Categorical(trend_df['Month'], categories=month_order, ordered=True)
            trend_df = trend_df.sort_values('Month')
            
            fig_trend = px.line(
                trend_df, 
                x='Month', 
                y='Count', 
                color='Severity',
                markers=True,
                title="Complaints Over Academic Year",
                color_discrete_map={
                    'Critical': '#dc2626',
                    'High': '#f97316',
                    'Medium': '#eab308',
                    'Low': '#22c55e'
                }
            )
            fig_trend.update_layout(
                height=400, 
                margin=dict(l=0, r=0, t=40, b=0), 
                font=chart_font,
                hovermode='x unified'
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No data available for this filter combination")
    
    with col2:
        st.subheader("📊 Day of Week Patterns")
        st.write("Complaint volume by day of the week")
        if len(filtered_df) > 0:
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_df = filtered_df.groupby('Day of Week').size().reset_index(name='Count')
            day_df['Day of Week'] = pd.Categorical(day_df['Day of Week'], categories=day_order, ordered=True)
            day_df = day_df.sort_values('Day of Week')
            
            fig_day = px.bar(
                day_df, 
                x='Day of Week', 
                y='Count', 
                color='Count',
                color_continuous_scale='Blues',
                text_auto=True,
                title="Peak Complaint Days"
            )
            fig_day.update_layout(
                height=400, 
                margin=dict(l=0, r=0, t=40, b=0), 
                font=chart_font,
                showlegend=False
            )
            st.plotly_chart(fig_day, use_container_width=True)
        else:
            st.info("No data available for this filter combination")
    
    st.markdown("---")
    
    st.subheader("🔥 Heatmap: Complaint Patterns by Day & Hour")
    st.write("When do students submit complaints most? Analyze patterns by day and time of day.")
    
    if len(filtered_df) > 0:
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = filtered_df.groupby(['Day of Week', 'Hour']).size().unstack(fill_value=0)
        heatmap_data = heatmap_data.reindex(days_order, fill_value=0).reindex(columns=range(0, 24), fill_value=0)
        
        fig_heatmap = px.imshow(
            heatmap_data, 
            labels=dict(x="Hour of Day (24h)", y="Day of Week", color="# Complaints"),
            x=list(range(0, 24)), 
            y=days_order, 
            color_continuous_scale="YlOrRd",
            title="Complaint Density Heatmap - Identify Peak Times",
            aspect='auto'
        )
        fig_heatmap.update_layout(
            height=450, 
            margin=dict(l=0, r=0, t=50, b=0), 
            font=chart_font,
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week"
        )
        fig_heatmap.update_xaxes(tickangle=0)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Add insights
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            busiest_day = heatmap_data.sum(axis=1).idxmax()
            max_day_complaints = heatmap_data.sum(axis=1).max()
            st.metric("Busiest Day", f"{busiest_day}", f"{int(max_day_complaints)} complaints")
        
        with col_b:
            busiest_hour = heatmap_data.sum(axis=0).idxmax()
            max_hour_complaints = heatmap_data.sum(axis=0).max()
            st.metric("Peak Hour", f"{busiest_hour}:00", f"{int(max_hour_complaints)} complaints")
        
        with col_c:
            total_complaints_heatmap = heatmap_data.sum().sum()
            avg_per_slot = total_complaints_heatmap / (7 * 24)
            st.metric("Avg per Slot", f"{avg_per_slot:.1f}", "complaints/hour/day")
    else:
        st.info("No data available for this filter combination")

# ==========================================
# END OF TRENDS SECTION
# ==========================================
# ------------------------------------------
# TAB 4: RAW DATA EXPLORER
# ------------------------------------------
with tab_raw_data:
    st.subheader("🔍 Explore Complaint Details")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_text = st.text_input("Search complaint descriptions", "")
    with col2:
        show_count = st.selectbox("Show rows", [10, 25, 50, 100])
    
    # Filter by search text
    display_df = filtered_df.copy()
    if search_text:
        display_df = display_df[display_df['Reports'].str.contains(search_text, case=False, na=False)]
    
    # Select relevant columns for display
    display_columns = ['Date', 'Genre', 'Reports', 'Severity', 'Status', 'Age', 'Gpa', 'Year', 'Gender']
    display_df = display_df[display_columns].head(show_count)
    
    st.dataframe(display_df, use_container_width=True, height=500)
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Dataset Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", len(filtered_df))
    col2.metric("Unique Complaint Types", filtered_df['Genre'].nunique())
    col3.metric("Avg Student Age", f"{filtered_df['Age'].mean():.1f}")
    col4.metric("Avg GPA", f"{filtered_df['Gpa'].mean():.2f}")
