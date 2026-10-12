import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import timedelta
from pathlib import Path

# configure page with title and page_icon
st.set_page_config(page_title= 'Healthcare Dashboard',
                   layout='wide',
                   page_icon='🏥')


# load the CSS + HTML from the separate 'style.html' file and apply it to the page
def load_style(file_name):
    file_path = Path(__file__).parent / file_name
    return file_path.read_text(encoding='utf-8')

st.markdown(load_style('style.html'), unsafe_allow_html=True)


# colors variable
# PALETTE = [ '#fb7185', '#38dbf8' , '#fbbf24','#00d4aa', '#a78bfa', '#fb923c']
PALETTE =  ["#067B54","#93215A", "#61469F","#9D6B14", "#8E96A3","#dc4d5b"]

# chart theme for all charts
CHART_THEME = dict(
    plot_bgcolor = 'rgba(0,0,0,0)',
    paper_bgcolor = 'rgba(0,0,0,0)',
    font = dict(color = 'rgba(255,255,255,.07)', size = 12 , family = 'DM Sans'),
    xaxis = dict(gridcolor = 'rgba(255,255,255,.06)', showline = False , zeroline = False),
    yaxis = dict(gridcolor = 'rgba(255,255,255,.06)', showline = False , zeroline = False),
    margin = dict(l = 10 ,r = 10, t = 40 , b = 10),
    legend = dict(bgcolor = 'rgba(0,0,0,0)'),
    colorway = PALETTE,
)

## LOAD DATA

# Loading csv data
@st.cache_data  #decorator
def laod_data() :
    csv_path = Path(__file__).resolve().parent / 'Healthcare report.csv'
    df = pd.read_csv(csv_path)
    return df

df = laod_data()

# print(df.head(5))
# print(df.to_string())

base_df = df.copy()

## DATA CLEANING

# change the 'Date of Admission' to date datatype
base_df['Date of Admission'] = pd.to_datetime(base_df['Date of Admission'],format= '%d-%m-%Y')

# change the 'Discharge Date' to date datatype
base_df['Discharge Date'] = pd.to_datetime(base_df['Discharge Date'], format='%d-%m-%Y')

# to create a 'Stay Days' column to find how many days patient stay in hospital
base_df['Stay Days'] = (base_df['Discharge Date']- base_df['Date of Admission']).dt.days

# to create the "Age Group" column that content 0-18 age range is 'Kids', 18-30 age range is 'Adult', 30-45 age range is 'Mid', 45-60 age range is 'Senior', and 60-120 age range is 'Old'.
# cut => it is used to convert numerical column to categorical column
base_df['Age Group'] = pd.cut(
    base_df['Age'],
    bins=[0, 18, 30, 45, 60, 120],
    labels=['Kids','Adult','Mid','Senior','Old']
)

# convert 'Name' column to title like: hello -> Hello
base_df['Name'] = base_df['Name'].str.title()

## SIDEBAR AND FILTERS

# define title of sidebar
st.sidebar.title('🏥 Filters')

# create a 'Basic Filter' sidebar expander with expanded True that means expander bydefault expended.
with st.sidebar.expander(label="Basic Filter", expanded=True):
    # calculate min and max date from 'Date of Admission'
    min_date = base_df['Date of Admission'].min().date()
    max_date = base_df['Date of Admission'].max().date()

    # create a date range with min_date and max_date
    date_range = st.date_input(label="Date Range", value=(min_date,max_date), min_value=min_date, max_value=max_date)

    # it ensure that range is either list or tuple and length of date_range is 2.
    if isinstance(date_range,(list,tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # create a medical_condition with multiselect filter in sidebar
    medical_condition = st.multiselect(label='Medical Condition',
                                       options=sorted(base_df['Medical Condition'].unique()),
                                       default=sorted(base_df['Medical Condition'].unique())
    )

    # create an admission_type with multiselect filter in sidebar
    admission_type = st.multiselect(label='Admission Type',
                                    options=sorted(base_df['Admission Type'].unique()),
                                    default=sorted(base_df['Admission Type'].unique())
    )

# create a 'Basic Filter' sidebar expander with expanded True that means expander bydefault expended.
with st.sidebar.expander(label='Advanced Filters'):

    # create an insurance_provider with multiselect filter in sidebar
    insurance_provider = st.multiselect(
        label="Insurance Providers",
        options=sorted(base_df['Insurance Provider'].unique()),
        default=sorted(base_df['Insurance Provider'].unique())
    )

    # create a gender with multiselect filter in sidebar
    gender = st.multiselect(
        label='Gender',
        options=sorted(base_df['Gender'].unique()),
        default=sorted(base_df['Gender'].unique())
    )

    # create a age_group with multiselect filter in sidebar
    age_group = st.multiselect(
        label='Age Group',
        options=['Kids','Adult','Mid','Senior','Old'],
        default=['Kids','Adult','Mid','Senior','Old']
    )

## FILTERS IMPLEMANTION WITH LOGIC

# build logic to apply filters for start_date, end_date, and all reamaining filters
df = base_df[
    (base_df['Date of Admission'] >= pd.to_datetime(start_date)) &
    (base_df['Date of Admission'] <= pd.to_datetime(end_date)) &
    (base_df['Medical Condition'].isin(medical_condition)) &
    (base_df['Admission Type'].isin(admission_type)) &

    (base_df['Insurance Provider'].isin(insurance_provider)) &
    (base_df['Gender'].isin(gender)) &
    (base_df['Age Group'].isin(age_group))
]

# calculate total_date and +1 for inclusive both start and end dates.
total_date = (end_date-start_date).days + 1

# it give you start date of the previous period. prev -> Previous
prev_start = start_date - timedelta(days=total_date)

# it give you the end date of the previous period.
prev_end = start_date - timedelta(days=1)

# # build logic to apply filters for prev_start, prev_end, and all reamaining filters
prev_df = base_df[
    (base_df['Date of Admission'] >= pd.to_datetime(prev_start)) &
    (base_df['Date of Admission'] <= pd.to_datetime(prev_end)) &
    (base_df['Medical Condition'].isin(medical_condition)) &
    (base_df['Admission Type'].isin(admission_type)) &

    (base_df['Insurance Provider'].isin(insurance_provider)) &
    (base_df['Gender'].isin(gender)) &
    (base_df['Age Group'].isin(age_group))
]

# 'get_delta' function calculates the percentage change b/w current value and previous value. It is designed to safely handle missing or zero values also.
def get_delta(current, previous):
    if previous == 0 or pd.isna(previous) or pd.isna(current):
        return 'N/A (no prev data)'

    change = ((current-previous)/previous)*100

    return f"{change:.1f}% vs prev"

## KPIs

# find total Billing Amount in 'df' dataframe
current_bill = df['Billing Amount'].sum()
# find total Billing Amount in 'prev_df' dataframe
prev_bill = prev_df['Billing Amount'].sum()


# find total admission in 'df' dataframe
current_admission = len(df)
# find total admission in 'prev_df' dataframe
prev_addmission = len(prev_df)


# find average Billing Amount in 'df' dataframe
current_avg = df['Billing Amount'].mean() if len(df) else 0
# find average Billing Amount in 'prev_df' dataframe
prev_avg = prev_df['Billing Amount'].mean() if len(prev_df) else 0


# find average Stay Days in 'df' dataframe
current_stay = df['Stay Days'].mean() if len(df) else 0
# find average Stay Days in 'prev_df' dataframe
prev_stay = df['Stay Days'].mean() if len(prev_df) else 0

st.caption(f"Previous: {prev_start}  ->  {prev_end}   | Current: {start_date}  ->  {end_date}")

col1, col2, col3, col4 = st.columns(4)

# 1. KPI -> Total Billing
col1.metric(
    'Total Billing',
    f'₹{current_bill:,.0f}',
    get_delta(current_bill,prev_bill)
)

# 2. KPI -> Total Admission
col2.metric(
    'Total Admission',
    f'{current_admission}',
    get_delta(current_admission,prev_addmission)
)

# 3. KPI -> AVG Billing / Admission
col3.metric(
    'AVG Billing / Admission',
    f'₹{current_avg:,.1f}',
    get_delta(current_avg,prev_avg)
)

# 4. KPI -> AVG Stay Days
col4.metric(
    'AVG Stay Days',
    f'{current_stay:,.1f}',
    get_delta(current_stay,prev_stay)
)

st.divider()
# define 3-tabs with there correnspoding names
tab1, tab2, tab3 = st.tabs(['🧠 Patient Intelligence','💰 Financial Intelligence','🗎 Raw Data'])

# write code for tab1
with tab1:
    # create 4-columns for Sub-KPIs
    col1, col2, col3, col4 = st.columns(4)

    # a. KPI -> Total Unique Patient
    col1.metric(
        label="Unique Patient(by Name)", 
        value=f'{df['Name'].nunique()}'
    )

    # b. KPI -> Average Age of patients
    col2.metric(
        label="Average Age",
        value=f"{df['Age'].mean():.0f} yrs"
    )

    # c. KPI -> Average Stay Days
    col3.metric(
        label='AVG Stay',
        value=f'{df["Stay Days"].mean():.1f} days'
    )

    # d. KPI -> Average Emergency Rate in percentage(%)
    col4.metric(
        label='Emergency Rate',
        value=f'{(df['Admission Type']=='Emergency').mean()*100:.1f}%'
    )

    st.divider()
    # define sub-header in tab1
    st.subheader('Demographics')

    # define 3-columns for different charts
    col1, col2 = st.columns(2)

    # With col1
    with col2:
        # counts each unique age group in series then convert it into a dataframe
        age_data = df['Age Group'].value_counts().reset_index()
        # renames the 'age_data' columns
        age_data.columns = ['Age Group','Count']

        # create a bar-chart is 'Age Group Distribution'.
        fig = px.bar(age_data,x='Age Group', y='Count',
                    text='Count',title='Age Group Distribution', color='Age Group',
                    color_discrete_sequence=PALETTE
        )

        # textposition is above the bars and remove the dark border around each bar
        fig.update_traces(
            textposition = 'outside',
            marker_line_width = 0,
            textfont=dict(
                    color="#AAA6A6",         
                    size=12,             
                    family="sans-serif"
            ),
            cliponaxis=False
        )

        # unpacks a pre-configured dict of design styles and hide the color legends.
        fig.update_layout(
            **CHART_THEME, showlegend=False
        )

        # it is used to show the chart on streamlit and ensure chart is resposive.
        st.plotly_chart(fig, use_container_width=True)

    with col1:
        ## counts each unique gender in series then convert it into a dataframe
        gender_data = df['Gender'].value_counts().reset_index()
        # renames the 'gender_data' columns
        gender_data.columns = ['Gender','Count']

        # create a pie-chart is 'Gender Distribution'.
        fig = px.pie(gender_data, names='Gender',
                     values='Count', title='Gender Distribution',
                     color_discrete_sequence=PALETTE, hole=0.3
        )

        # unpacks a pre-configured dict of design styles and hide the color legends.
        fig.update_layout(
            **CHART_THEME
        )

        # it is used to show the chart on streamlit and ensure chart is resposive.
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)

    with col2:
        # # counts each unique medical condition in series then convert it into a dataframe
        medical_data = df['Medical Condition'].value_counts().reset_index()
        # renames the 'medical_data' columns
        medical_data.columns=['Medical Condition','Count']

        # create a tree map  is 'Medical Condition Distribution'.
        fig = px.treemap(
            medical_data,
            path=['Medical Condition'],  # Note: 'path' usually expects a list/tuple in newer Plotly versions
            values='Count',
            title='Medical Condition Distribution', 
            color='Medical Condition',
            color_discrete_sequence=PALETTE,
            custom_data=['Count']
        )

        # add label+count in each tree and remove the dark border around each bar
        fig.update_traces(
            textinfo='label+text',
            text=medical_data['Count'],
            marker_line_width = 0,
            textfont=dict(
                color="#E1DEDE",         
                size=13,             
                family="sans-serif"
            ),
            
        )

        # unpacks a pre-configured dict of design styles and hide the color legends. also tilde x-axis 20 degree
        fig.update_layout(
                    **CHART_THEME, showlegend=False
        )

        # it is used to show the chart on streamlit and ensure chart is resposive.
        st.plotly_chart(fig, use_container_width=True)

    with col1: 
        # # counts each unique blood type in series then convert it into a dataframe
        blood_data = df['Blood Type'].value_counts().sort_values().reset_index()
        # renames the 'blood_data' columns
        blood_data.columns=['Blood Type','Count']
    
        blood_data['percentage'] = (blood_data['Count']/blood_data['Count'].sum()*100).round(1)

        # create a bar-chart is 'Blood Type Distribution'.
        fig = px.bar(
            blood_data, x='Count', y='Blood Type', orientation='h',
            text=blood_data['percentage'].astype(str) + '%',
            title= 'Blood Type Distribution',
            color='Blood Type',
            color_discrete_sequence = PALETTE
        )    

        # textposition is above the bars and remove the dark border around each bar
        fig.update_traces(
            textposition = 'outside',
            marker_line_width=0,
            textfont=dict(
                color="#AAA6A6",         
                size=12,             
                family="sans-serif"
            ),
            cliponaxis=False
        )

        # unpacks a pre-configured dict of design styles and hide the color legends.
        fig.update_layout(
            **CHART_THEME,showlegend=False
        )

        # it is used to show the chart on streamlit and ensure chart is resposive.
        st.plotly_chart(fig, use_container_width=True)

# with tab2 : 'Financial Intelligence'
with tab2:
    # define 4-columns for KIPs
    col1, col2, col3, col4 = st.columns(4)

    # a. KPI -> Total Revenue
    col1.metric(
        label='Total Revenue',
        value=f'₹{df['Billing Amount'].sum():,.0f}'
    )

    # b. KPI -> Average Billing
    col2.metric(
        label='Avg Billing',
        value=f'₹{df['Billing Amount'].mean():,.1f}'
    )

    # c. KPI -> Max Bill
    col3.metric(
        label='Max Bill',
        value=f'₹{df['Billing Amount'].max():,.0f}'
    )

    # d. KPI -> Min Bill
    col4.metric(
        label='Min Bill',
        value=f'₹{df['Billing Amount'].min():,.0f}'
    )

    st.divider()

    st.subheader("Demographics")


    # group by 'Medical Condition' with 'Billing Amount' in series then convert it into a dataframe
    medical_revenue = df.groupby('Medical Condition')['Billing Amount'].sum().reset_index()
    # renames the 'medical revenue' columns
    medical_revenue.columns = ['Medical Condition','Revenue']
    # sort the 'medical_reveue' by 'Revenue' in ascendign order
    medical_revenue=medical_revenue.sort_values('Revenue', ascending=False)

    # create a bar-chart is 'Revenue by Medical Condition'.
    fig = px.bar(
            medical_revenue,
            x = 'Revenue', y='Medical Condition',
            orientation='h',
            title = 'Revenue by Medical Condition',
            color='Medical Condition', color_discrete_sequence=PALETTE,
            text='Revenue'
    )

    # textposition is above the bars and remove the dark border around each bar
    fig.update_traces(
            texttemplate = '₹%{text:,.0f}', 
            textposition = 'outside',
            marker_line_width=0,
            textfont=dict(
                color="#9A9696",         
                size=12,             
                family="sans-serif"
            ),
            cliponaxis=False

        )
    # unpacks a pre-configured dict of design styles and hide the color legends.
    fig.update_layout(**CHART_THEME,showlegend = False)

    # it is used to show the chart on streamlit and ensure chart is resposive.
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col2:
        # group by 'Insurance Provider' with 'Billing Amount' in series then convert it into a dataframe
        insurance_revenue = df.groupby('Insurance Provider')['Billing Amount'].sum().reset_index()
        # rename the 'isurance_revenue' columns
        insurance_revenue.columns = ['Insurance Provider','Revenue']

        # create a pie-chart is 'Revenue by Insurance Provider'.
        fig = px.pie(
            insurance_revenue,
            names='Insurance Provider',
            values= 'Revenue',
            title='Revenue by Insurance Provider',
            color_discrete_sequence=PALETTE,
            hole=0.2
        )

        # unpacks a pre-configured dict of design styles and hide the color legends.
        fig.update_layout(
            **CHART_THEME, showlegend=True
            )

        # it is used to show the chart on streamlit and ensure chart is resposive.
        st.plotly_chart(fig, use_container_width=True)

    

    with col1:
        # group by 'Insurance Provider' with 'Billing Amount' in series then convert it into a dataframe
        admission_type_revenue = df.groupby('Admission Type')['Billing Amount'].sum().reset_index()
        # rename the 'isurance_revenue' columns
        admission_type_revenue.columns = ['Admission Type','Revenue']
        
        # create a pie-chart is 'Revenue by Insurance Provider'.
        fig = px.pie(
            admission_type_revenue,
            names='Admission Type',
            values= 'Revenue',
            title='Revenue by Admission Type',
            color_discrete_sequence=PALETTE,
            hole=0.2
        )
        
        # unpacks a pre-configured dict of design styles and hide the color legends.
        fig.update_layout(**CHART_THEME)
        
        # it is used to show the chart on streamlit and ensure chart is resposive.
        st.plotly_chart(fig, use_container_width=True)

# With tab3
with tab3:
    # subheader : for showing total records
    st.subheader(f'{len(df)} Records')

    # display the raw data
    st.dataframe(
        # df.sort_values('Date of Admission',ascending=False),
        df,
        use_container_width=True,
        height=500
    )

