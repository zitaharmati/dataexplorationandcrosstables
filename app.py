import streamlit as st
import pandas as pd
import numpy as np
from IPython.display import display, HTML, display_html 
import os
import streamlit as st
from io import StringIO
from app_chart_tools import *
from crosstables import *
from io import BytesIO
import openpyxl
import xlsxwriter
import openpyxl.cell._writer
import seaborn as sns

def Corr_Map(df):
    nums = df.select_dtypes(include=np.number)
    if len(nums.columns) > 1:
        fig, ax = plt.subplots(figsize=(nums.shape[1]*0.5, nums.shape[1]*0.4))
        sns.set(font_scale=0.8)
        sns.heatmap(nums.corr(), cmap='vlag', annot=True, fmt='.2f', vmin=-1, vmax=1, ax=ax)
        ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize=13)
        ax.set_yticklabels(ax.get_ymajorticklabels(), fontsize=13)
        st.session_state['fig'] = fig  # Store the figure in session state
        st.pyplot(fig)
    else:
        st.write(f'Not enough numerical columns ({len(nums.columns)}) to make a correlation plot!')
    del nums

def get_info_df(df):
    buffer = StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()

    # Process the captured output
    lines = info_str.split('\n')
    rows = []
    for line in lines[5:-2]:  # Adjust these indexes based on your DataFrame structure
        parts = line.split()
        row = [parts[0], parts[1], " ".join(parts[2:])]
        rows.append(row)

    info_df = pd.DataFrame(rows, columns=["Index", "Non-Null Count", "Dtype"])
    return info_df

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=True, sheet_name='Sheet1')
        writer._save()
    processed_data = output.getvalue()
    return processed_data

def convert_dfs_to_excel(dfs_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in dfs_dict.items():
            df.to_excel(writer, index=True, sheet_name=sheet_name)
        writer._save()
    processed_data = output.getvalue()
    return processed_data

def check_session_state(key):
    return st.session_state.get(key, False)

@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
 
st.title("Exploratory Data Analysis and Crosstable Generation")

uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])



if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        
        try:
            df = load_data(uploaded_file)
        except:
            st.write("Could not read your file! The file contains unknown characters.")
            st.stop()

    elif uploaded_file.name.endswith('.xlsx'):
        try:
            df = load_data(uploaded_file)
        except:
            st.write("Could not read your file! The file contains unknown characters.")
            st.stop()

    st.subheader("Column Names:")
    st.write(df.columns.tolist())

    
    num_rows = st.slider("Select number of rows to display - max 50", min_value=1, max_value=50, value=5)
    st.subheader(f"Displaying the first {num_rows} rows:")
    st.dataframe(df.head(num_rows))

    st.subheader("Descriptive statistics of variables")

    stats, c = Stats_All_Columns(df)
    styled_stats = stats.style.background_gradient(subset='FILLED',cmap='summer_r',axis=None).format('{:.0f}',subset='FILLED').background_gradient(subset='FILLED %',cmap='summer_r',axis=None).format('{:.2%}',subset='FILLED %').background_gradient(subset='NA',cmap='Greys',axis=None).format('{:.0f}',subset='NA').background_gradient(subset='NA %',cmap='Greys',axis=None).format('{:.2%}',subset='NA %').background_gradient(subset='EMPTY_STR',cmap='Greys',axis=None).format('{:.0f}',subset='EMPTY_STR').background_gradient(subset='EMPTY_STR %',cmap='Greys',axis=None).format('{:.2%}',subset='EMPTY_STR %').background_gradient(subset='0',cmap='Greys',axis=None).format('{:.0f}',subset='0').background_gradient(subset='0 %',cmap='Greys',axis=None).format('{:.2%}',subset='0 %').background_gradient(subset='DISTINCT',cmap='Blues',axis=None).applymap(lambda x: 'color: transparent' if pd.isnull(x) else '').format('{:.0f}',subset=['mean', 'std', 'min','25%', '50%', '75%', 'max'])
    st.dataframe(styled_stats, height=600)
 
    excel = convert_df_to_excel(styled_stats)
    st.download_button(
    label="Download stats as Excel",
    data=excel,
    file_name='general_stats.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
   

    # Initialize session state for tables, titles, and errors
    for key in ['count_table', 'titlecount', 'count_table_generated', 'normalized_table_row', 'titlenormrow', 'normalized_table_row_generated', 'normalized_table_column', 'titlenormcol', 'normalized_table_column_generated', 'normalized_table_overall', 'titlenormoverall', 'normalized_table_overall_generated', 'value_table', 'title_with_value', 'value_table_generated', 'error', 'corrmap', 'corrmap_generated']:
        if key not in st.session_state:
            st.session_state[key] = None if 'table' in key or 'title' in key or key == 'error' else False
    
    if 'fig' not in st.session_state:
        st.session_state['fig'] = None
    if 'fig_generated' not in st.session_state:
        st.session_state['fig_generated'] = None

    st.subheader("Generate Corrmap")
    if st.button('Generate Correlation Map'):
        st.session_state['fig_generated']=True
    
    if st.session_state['fig_generated']==True:
        try:
            Corr_Map(df)
        except:
            print("Failed to generate Corrmap!")

    st.subheader("Create crosstables")
    cols=df.columns
    xvar = st.selectbox("Select X variable", cols)
    yvar = st.selectbox("Select Y variable", cols)
    num_Xrows = st.slider("Select number of maximum rows to display - max 100", min_value=1, max_value=100, value=30)

    # Custom CSS for buttons
    button_style = """
    <style>
    .stButton > button {
        border-radius: 10px;
        padding: 10px;
    }
    .stButton > button:nth-child(1) {
        background-color: #4CAF50;
        color: white;
    }
    .stButton > button:nth-child(2) {
        background-color: #008CBA;
        color: white;
    }
    .stButton > button:nth-child(3) {
        background-color: #f44336;
        color: white;
    }
    .stButton > button:nth-child(4) {
        background-color: #ff9800;
        color: white;
    }
    .stButton > button:nth-child(5) {
        background-color: #9c27b0;
        color: white;
    }
    </style>
    """



    st.markdown(button_style, unsafe_allow_html=True)
    
    if st.button('Generate Crosstables'):
        st.session_state['count_table'], st.session_state['titlecount'] = crosstable(df, xvar, yvar, max_rows=num_Xrows)
        st.session_state['count_table_generated'] = True
        st.write(st.session_state['titlecount'])
        st.dataframe(st.session_state['count_table'])

        st.session_state['normalized_table_row'], st.session_state['titlenormrow'] = crosstable(df, xvar, yvar, count_table=False, percent_table_by_rows=True, max_rows=num_Xrows)
        st.session_state['normalized_table_row_generated'] = True
        st.write(st.session_state['titlenormrow'])
        st.dataframe(st.session_state['normalized_table_row'])
  
        st.session_state['normalized_table_column'], st.session_state['titlenormcol'] = crosstable(df, xvar, yvar, count_table=False, percent_table_by_columns=True, max_rows=num_Xrows)
        st.session_state['normalized_table_column_generated'] = True
        st.write(st.session_state['titlenormcol'])
        st.dataframe(st.session_state['normalized_table_column'])

        st.session_state['normalized_table_overall'], st.session_state['titlenormoverall'] = crosstable(df, xvar, yvar, count_table=False, percent_table_by_overall=True, max_rows=num_Xrows)
        st.session_state['normalized_table_overall_generated'] = True
        st.write(st.session_state['titlenormoverall'])
        st.dataframe(st.session_state['normalized_table_overall'])   

    # Display Crosstables if generated
    if check_session_state('count_table_generated'):
        st.write(st.session_state['titlecount'])
        st.dataframe(st.session_state['count_table'])
    if check_session_state('normalized_table_row_generated'):
        st.write(st.session_state['titlenormrow'])
        st.dataframe(st.session_state['normalized_table_row'])
    if check_session_state('normalized_table_column_generated'):
        st.write(st.session_state['titlenormcol'])
        st.dataframe(st.session_state['normalized_table_column'])
    if check_session_state('normalized_table_overall_generated'):
        st.write(st.session_state['titlenormoverall'])
        st.dataframe(st.session_state['normalized_table_overall'])

    if check_session_state('count_table_generated'):
        dfs = {
            'Count_table': st.session_state['count_table'],
            'Normalized_by_row': st.session_state['normalized_table_row'],
            'Normalized_by_column': st.session_state['normalized_table_column'],
            'Normalized_by_overall': st.session_state['normalized_table_overall']}
        crosstables_excel = convert_dfs_to_excel(dfs)
        st.download_button(label="Download Crosstables as Excel",
        data=crosstables_excel,
        file_name=f'crosstabales_{xvar}_by_{yvar}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    st.subheader("Create pivot table")
    xvarpivot = st.selectbox("Select X variable for pivot table", cols)
    yvarpivot = st.selectbox("Select Y variable for pivot table", cols)
    valvar=st.selectbox("Select Continuos variable", cols)
    aggfunc=st.selectbox("Select aggregation function", ["sum", "mean", "median"])
    num_Xrows_pivot = st.slider("Select number of maximum rows to display on pivot - max 100", min_value=1, max_value=100, value=30)

    if st.button('Generate pivot table'):
        try:
            st.session_state['value_table'], st.session_state['title_with_value'] = crosstable(df, xvarpivot, yvarpivot, count_table=False, values=valvar, aggfunc=aggfunc, max_rows=num_Xrows_pivot, title_suffix=f"{xvarpivot} by {yvarpivot}")
            st.session_state['value_table_generated'] = True
            st.write(st.session_state['title_with_value'])
            st.dataframe(st.session_state['value_table'])
        
        except:
            st.session_state['value_table_generated'] = False
            st.write("You should select continous variable!")
    
    if check_session_state('value_table_generated'):
        st.write(st.session_state['title_with_value'])
        st.dataframe(st.session_state['value_table'])

    if st.session_state['value_table_generated']:
        pivot_excel = convert_df_to_excel(st.session_state['value_table'])
        st.download_button(label="Download Pivot as Excel",
        data=pivot_excel,
        file_name=f'pivot_{xvarpivot}_by_{yvarpivot}_and_{valvar}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

else:
    st.info("Please upload a CSV or Excel file.")

