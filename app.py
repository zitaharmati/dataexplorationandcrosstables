import streamlit as st
import pandas as pd
import numpy as np
from IPython.display import display
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
        writer.save()
    processed_data = output.getvalue()
    return processed_data

@st.cache
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
 
st.title("Exploratory Data Analysis and Crosstable Generation")

uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])



if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = load_data(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = load_data(uploaded_file)
    
    # Create DataFrame from info() output
    info_df = get_info_df(df)

    #st.write("Data Types and Non-Null Counts:")
    #st.dataframe(info_df)

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
    file_name='data.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    # Initialize session state for tables, titles, and errors
    for key in ['count_table', 'titlecount', 'count_table_generated', 'normalized_table_row', 'titlenormrow', 'normalized_table_row_generated', 'normalized_table_column', 'titlenormcol', 'normalized_table_column_generated', 'normalized_table_overall', 'titlenormoverall', 'normalized_table_overall_generated', 'value_table', 'title_with_value', 'value_table_generated', 'error']:
        if key not in st.session_state:
            st.session_state[key] = None if 'table' in key or 'title' in key or key == 'error' else False

    # # Initialize session state for tables and titles
    # if 'count_table' not in st.session_state:
    #     st.session_state['count_table'] = None
    # if 'titlecount' not in st.session_state:
    #     st.session_state['titlecount'] = ""
    # if 'count_table_generated' not in st.session_state:
    #     st.session_state['count_table_generated'] = False

    # if 'normalized_table_row' not in st.session_state:
    #     st.session_state['normalized_table_row'] = None
    # if 'titlenormrow' not in st.session_state:
    #     st.session_state['titlenormrow'] = ""
    # if 'normalized_table_row_generated' not in st.session_state:
    #     st.session_state['normalized_table_row_generated'] = False

    # if 'normalized_table_column' not in st.session_state:
    #     st.session_state['normalized_table_column'] = None
    # if 'titlenormcol' not in st.session_state:
    #     st.session_state['titlenormcol'] = ""
    # if 'normalized_table_column_generated' not in st.session_state:
    #     st.session_state['normalized_table_column_generated'] = False

    # if 'normalized_table_overall' not in st.session_state:
    #     st.session_state['normalized_table_overall'] = None
    # if 'titlenormoverall' not in st.session_state:
    #     st.session_state['titlenormoverall'] = ""
    # if 'normalized_table_overall_generated' not in st.session_state:
    #     st.session_state['normalized_table_overall_generated'] = False

    # if 'value_table' not in st.session_state:
    #     st.session_state['value_table'] = None
    # if 'title_with_value' not in st.session_state:
    #     st.session_state['title_with_value'] = ""
    # if 'value_table_generated' not in st.session_state:
    #     st.session_state['value_table_generated'] = False  

    st.subheader("Create crosstables")
    cols=df.columns
    xvar = st.selectbox("Select X variable", cols)
    yvar = st.selectbox("Select Y variable", cols)
    valvar=st.selectbox("Select Continuos variable", cols)
    aggfunc=st.selectbox("Select aggregation function", ["sum", "mean", "median"])
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
    
    # Count table
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button('Generate Count Table'):
            st.session_state['count_table'], st.session_state['titlecount'] = crosstable(df, xvar, yvar, max_rows=num_Xrows)
            st.session_state['count_table_generated'] = True
        else:
            st.session_state['count_table_generated'] = False
    
    if st.session_state['count_table_generated']:
        with col2:
            count_excel = convert_df_to_excel(st.session_state['count_table'])
            st.download_button(label="Download Count table as Excel",
            data=count_excel,
            file_name=f'count_table_{xvar}_{yvar}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    if st.session_state['count_table'] is not None:
        st.write(st.session_state['titlecount'])
        st.dataframe(st.session_state['count_table'])

    # Normalized by row
    col3, col4 = st.columns([3, 1])
    with col3:
        if st.button('Generate Normalized Table by Row'):
            st.session_state['normalized_table_row'], st.session_state['titlenormrow'] = crosstable(df, xvar, yvar, count_table=False, percent_table_by_rows=True, max_rows=num_Xrows)
            st.session_state['normalized_table_row_generated'] = True
        else:
            st.session_state['normalized_table_row_generated'] = False
    
    if st.session_state['normalized_table_row_generated']:
        with col4:
            ratio_by_row_excel = convert_df_to_excel(st.session_state['normalized_table_row'])
            st.download_button(label="Download normalized by row table as Excel",
            data=ratio_by_row_excel,
            file_name=f'distribution_of_{xvar}_by_{yvar}_normalized_by_row.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if st.session_state['normalized_table_row'] is not None:
        st.write(st.session_state['titlenormrow'])
        st.dataframe(st.session_state['normalized_table_row'])

    # Normalized by column
    col5, col6 = st.columns([3, 1])
    with col5:
        if st.button('Generate Normalized Table by Column'):
            st.session_state['normalized_table_column'], st.session_state['titlenormcol'] = crosstable(df, xvar, yvar, count_table=False, percent_table_by_columns=True, max_rows=num_Xrows)
            st.session_state['normalized_table_column_generated'] = True
        else:
            st.session_state['normalized_table_column_generated'] = False
    if st.session_state['normalized_table_column_generated']:
        with col6:            
            ratio_by_col_excel = convert_df_to_excel(st.session_state['normalized_table_column'])
            st.download_button(label="Download normalized by column table as Excel",
            data=ratio_by_col_excel,
            file_name=f'distribution_of_{xvar}_by_{yvar}_normalized_by_column.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if st.session_state['normalized_table_column'] is not None:
        st.write(st.session_state['titlenormcol'])
        st.dataframe(st.session_state['normalized_table_column'])

    # Normalized by overall
    col7, col8 = st.columns([3, 1])
    with col7:
        if st.button('Generate Overall Normalized Table'):
            st.session_state['normalized_table_overall'], st.session_state['titlenormoverall'] = crosstable(df, xvar, yvar, count_table=False, percent_table_by_overall=True, max_rows=num_Xrows)
            st.session_state['normalized_table_overall_generated'] = True
        else:
            st.session_state['normalized_table_overall_generated'] = False
    if st.session_state['normalized_table_overall_generated']:
        with col8:
           ratio_by_overall_excel = convert_df_to_excel(st.session_state['normalized_table_overall'])
           st.download_button(label="Download normalized overall table as Excel",
           data=ratio_by_overall_excel,
           file_name=f'distribution_of_{xvar}_by_{yvar}_normalized_overall.xlsx',
           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 
    if st.session_state['normalized_table_overall'] is not None:
        st.write(st.session_state['titlenormoverall'])
        st.dataframe(st.session_state['normalized_table_overall'])

    col9, col10 = st.columns([3, 1])
    with col9:
        if st.button('Generate Table with additional continous variable'):
            try:
                st.session_state['value_table'], st.session_state['title_with_value'] = crosstable(df, xvar, yvar, count_table=False, values=valvar, aggfunc=aggfunc, max_rows=num_Xrows, title_suffix=f"{xvar} by {yvar}")
                st.session_state['value_table_generated'] = True
            except ValueError as e:
                st.error(f"Could not generate table with additional continuous variable: {e}")
                st.session_state['value_table_generated'] = False
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.session_state['value_table_generated'] = False

    if st.session_state['value_table_generated']:
        with col10:
           values_excel = convert_df_to_excel(st.session_state['value_table'])
           st.download_button(label="Download table with continous variable as Excel",
           data=values_excel,
           file_name=f'{aggfunc}_{valvar}_by_{xvar}_and_{yvar}.xlsx',
           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')        

    if st.session_state['value_table'] is not None:
        st.write(st.session_state['title_with_value'])
        st.dataframe(st.session_state['value_table'])


else:
    st.info("Please upload a CSV or Excel file.")

