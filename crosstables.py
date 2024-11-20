
import pandas as pd
import numpy as np
from IPython.display import display, HTML, display_html 
import seaborn as sns
import matplotlib.pyplot as plt



def geomean(series,hour_to_minute_to_hour=False):
    ser = series.copy()
    from scipy.stats import gmean
    if hour_to_minute_to_hour:
        ser = ser.dropna()
        ser.loc[ser<=0]=0.001
        ser = np.ceil(ser*60)
        return gmean(ser)/60
    else:
        ser = ser.dropna()
        ser.loc[ser<=0]=0.001
        ser = np.ceil(ser)
        return gmean(ser)
    
geomean_aggfunc_hour = lambda x: geomean(x,hour_to_minute_to_hour=True)
geomean_aggfunc = lambda x: geomean(x,hour_to_minute_to_hour=False)

def Percentile(series, q=0.8):
    #perc=np.percentile(a=series, q=q)
    perc=series.quantile(q)
    return perc

percentile_aggfunc = lambda x: Percentile(x)

def string_shortener(s,max_len):
    s = str(s)
    if len(s)> max_len:
        return s[0:max_len] + '...'
    else:
        return s

def priocolor_legend_elements():
    import matplotlib.patches as mpatches
    legs = []
    data_key = mpatches.Patch(color='tomato', label='P1')
    legs.append(data_key)
    data_key = mpatches.Patch(color='orange', label='P2')
    legs.append(data_key)
    data_key = mpatches.Patch(color='yellow', label='P3')
    legs.append(data_key)
    data_key = mpatches.Patch(color='lightgreen', label='P4')
    legs.append(data_key)
    data_key = mpatches.Patch(color='lightsteelblue', label='P5')
    legs.append(data_key)
    return legs


def crosstable(df,                            # dataframe
            index_col=None,                     # List of columns to use for heatmap rows
            column_col=None,                    # List of columns to use for heatmap columns
            max_rows=30,                    # Int, max number of rows in the heatmap, skip the rest of the rows from the chart
            max_name_length=100,            # Int, max length of row labels, shortens the label if longer...
            #count_all_table=False,          # Bool, whether to make an overall count by the given column(s)
            count_table=True,               # Bool, whether to make the count heatmap
            percent_table_by_columns=False, # Bool, whether to make the percentage heatmap, calculated along columns
            percent_table_by_rows=False,    # Bool, whether to make the percentage heatmap, calculated along rows
            percent_table_by_overall=False, # Bool, whether to make the percentage heatmap, calculated overall
            #aggfunc_values_column_alias=None,
            title_colnames=True,            # Bool, whether to include the column name to tie title (... by xxx and yyy)
            aggfunc=None,
            values=None,
            index_colors=None,      # dict!
            cell_colors=None,       # dict!
            #order_by_columns=None,
            order_by_columns_ascending=False,
            reindex_0_by=None,
            reindex_1_by=None,
            dropna_row=False,
            dropna_col=False,
            title_suffix=None,
            all_name='ALL'):

    def string_shortener(s,max_len):
        s = str(s)
        if len(s)> max_len:
            return s[0:max_len] + '...'
        else:
            return s

    def color_background(cell):
        for value, color in index_colors.items():
            if value in cell:
                return "background-color: {}".format(color)
        return ""
    

    vc_top = df[index_col].astype('str').fillna('na').value_counts()

    def crosstab_chart_with_totals(table_type, cmap, fmt, percent_method=False, aggfunc=None, values=None):
        global count_html
        # full crosstab with totals
        if aggfunc!=None and values!=None:
            cross = pd.crosstab(df[index_col].astype('str').fillna('na'), df[column_col].astype('str').fillna('na'), margins=True, aggfunc=aggfunc, values=df[values], normalize=percent_method, margins_name=all_name)
        else:
            cross = pd.crosstab(df[index_col].astype('str').fillna('na'), df[column_col].astype('str').fillna('na'), margins=True, normalize=percent_method, margins_name=all_name)

            
        if percent_method == 'index':
            cross[all_name] = 1.0                      # adding rowtotal column as 100%
        if percent_method == 'columns':
            cross.loc[all_name] = 1.0         # adding coltotal row as 100%

        # reindexing rows
        # if reindex_0_by is not None:
        #     if type(reindex_0_by)!=list:
        #         cross = cross.reindex(list(reindex_0_by) + [all_name,], axis=0)
        #     else:
        #         cross = cross.reindex(reindex_0_by + [all_name,], axis=0)
        # else:
        cross = cross.reindex(vc_top.index.to_list() + [all_name,])
            
        # reindexing columns
        # if reindex_1_by is not None:
        #     if type(reindex_1_by)!=list:
        #         cross = cross.reindex(list(reindex_1_by) + [all_name,], axis=1)
        #     else:
        #cross = cross.reindex(reindex_1_by + [all_name,], axis=1)
        
        # custom order by cols
        #if order_by_columns != None:
        #    cross = pd.concat([ cross.iloc[:-1].sort_values(by=order_by_columns, ascending=order_by_columns_ascending) , cross.tail(1) ])
        
        # limit the number of rows if need
        topn = False
        if max_rows < cross.shape[0]:
            cross = pd.concat([cross[0:max_rows],cross.tail(1)])
            topn = True

        # shorter indexes to chart
        if index_colors is None:
            cross.index = cross.index.to_series().apply(lambda x: string_shortener(x,max_name_length))
    
        if percent_method==False:
            title = rf'Counts by "{index_col}" & "{column_col}"'
        if percent_method=='columns':
            title = rf'Distribution of "{column_col}" by "{index_col}"'
        if percent_method=='index':
            title = rf'Distribution of "{index_col}" by "{column_col}"'
        if percent_method=='all':
            title = rf'Distribution by "{index_col}" & "{column_col}"'
        #if title_colnames:
        #    title = title +  f' by "{col}" and "{tcol}"'
        if aggfunc=='mean':
            title = rf'AVG {values}'
        elif aggfunc=='median':
            title = rf'Median {values}'
        elif aggfunc=="sum":
            title = rf'SUM {values}'
        
        if title_suffix != None: title = title + f' {title_suffix}'         
        if topn: title = title + f' (top {len(cross)-1} {index_col})'

        # string_shortener(t,max_name_length)

        #cross.columns = cross.columns.str.replace(" ", "@@")
                    
        format = '{:' + fmt + '}'
        styled_cross = cross.style.set_caption(title).set_table_styles([{'selector':'caption', 'props': [("font-size", "110%"),("font-weight", "bold"),("background-color", "#ffffff"),("color", "black")]}, 
                                {'selector':'th', 'props': [("font-size", "85%")]},
                                {'selector':'td', 'props': [("font-size", "85%")]},
                                {"selector": "td,th", "props": "line-height: inherit; padding: 2px;"}
                                ]).background_gradient(subset=(cross.index[0:-1],cross.columns[-1]),cmap='Greys',axis=None,low=0,high=1).background_gradient(subset=(cross.index[-1],cross.columns[0:-1]),cmap='Greys',axis=None,low=0,high=1).background_gradient(subset=(cross.index[0:-1],cross.columns[0:-1]),cmap=cmap,axis=None).applymap(lambda x: 'background: #f3dcf7', subset=(cross.index[-1],cross.columns[-1])).applymap(lambda x: 'color: transparent' if pd.isnull(x) else '').applymap(lambda x: 'background: #eeeeee' if pd.isnull(x) else '').format(format).set_table_attributes("style='display:inline'")
        
        return styled_cross, title

    if count_table: 
        styled_cross, title=crosstab_chart_with_totals(table_type='count',percent_method=False, fmt='.0f', cmap='Blues')
        return styled_cross, title
    
    if percent_table_by_columns: 
        styled_cross, title=crosstab_chart_with_totals(table_type='column_%',percent_method='columns', fmt='.2%', cmap='Oranges')
        return styled_cross, title
    
    if percent_table_by_rows: 
        styled_cross, title=crosstab_chart_with_totals(table_type='row_%',percent_method='index', fmt='.2%', cmap='Oranges')
        return styled_cross, title
    
    if percent_table_by_overall: 
        styled_cross, title=crosstab_chart_with_totals(table_type='overall_%',percent_method='all', fmt='.2%', cmap='Oranges')
        return styled_cross, title
    
    if aggfunc!=None and values!=None: 
        styled_cross, title=crosstab_chart_with_totals(table_type=f'{aggfunc}_{values}',percent_method=False, fmt='.1f', cmap='Reds', aggfunc=aggfunc, values=values)
        return styled_cross, title



