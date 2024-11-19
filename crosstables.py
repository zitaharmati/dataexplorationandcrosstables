
import pandas as pd
import numpy as np
from IPython.display import display, HTML, display_html 

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
        # elif aggfunc == percentile_aggfunc:
        #     title = rf'80 Percentile {values}'

        #if title_prefix != None: title = f'{title_prefix} ' + title
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





def crosstables(df,                            # dataframe
            index_cols: [],                     # List of columns to use for heatmap rows
            column_cols: [],                    # List of columns to use for heatmap columns
            max_rows=30,                    # Int, max number of rows in the heatmap, skip the rest of the rows from the chart
            max_name_length=100,            # Int, max length of row labels, shortens the label if longer...
            count_all_table=False,          # Bool, whether to make an overall count by the given column(s)
            count_table=True,               # Bool, whether to make the count heatmap
            percent_table_by_columns=False, # Bool, whether to make the percentage heatmap, calculated along columns
            percent_table_by_rows=False,    # Bool, whether to make the percentage heatmap, calculated along rows
            percent_table_by_overall=False, # Bool, whether to make the percentage heatmap, calculated overall
            excel_name=None,                # String, if given then the name of the xls file to export, in case of None won't export excels
            excel_sheet_names_index_alias=None,   # String, if given then the short name of the index column name
            excel_sheet_names_column_alias=None,   # String, if given then the short name of the column name
            aggfunc_values_column_alias=None,
            title_colnames=True,            # Bool, whether to include the column name to tie title (... by xxx and yyy)
            title_prefix=None,              # String, prefix to title
            title_suffix=None,              # String, suffix to title
            ylabels_to_highlight=None,      # List of strings, if given then these row labels will be red colored
            aggfunc=None,
            values=None,
            index_colors=None,      # dict!
            cell_colors=None,       # dict!
            priocolor_legend=False,
            order_by_columns=None,
            order_by_columns_ascending=False,
            reindex_0_by=None,
            reindex_1_by=None,
            dropna_row=False,
            dropna_col=False,
            all_name='ALL',
            count_table_at_right=False):



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

    for tcol in column_cols:

        # writer = None
        # if excel_name != None:
        #     writer = pd.ExcelWriter(f'{os.getcwd()}\{excel_name}_stats_by_{tcol}.xlsx',engine='xlsxwriter')   
        #     workbook=writer.book

        if count_all_table:
            # FULL COUNT...
            # cross table
            df[tcol] = df[tcol].astype('str')
            cross = pd.DataFrame(df[tcol].value_counts())
            cross = cross.sort_index()        
            cross.columns = (['',])
            cross = cross.T
            cross[all_name] = cross.sum(axis=1)
            # cross_total = cross[[all_name]]
            # cross = cross.iloc[:,0:-1]
            if tcol=='Opened DAY NAME': cross = cross.reindex(('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), axis=1)
            if tcol=='Opened HOUR': cross = cross.reindex(('0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23'), axis=1)

            # excel sheet
            if excel_name != None:
                worksheet=workbook.add_worksheet('Count All')
                writer.sheets['Count All'] = worksheet
                cross.to_excel(writer,sheet_name='Count All',startrow=0 , startcol=0)

            title = f'Count of all by {tcol}'
            if title_prefix != None: title = f'{title_prefix} ' + title
            if title_suffix != None: title = title + f' {title_suffix}'

            cross.columns = cross.columns.str.replace(" ", "@@@")
                            
            cross = (cross.style.set_caption(title)
                .set_table_styles([{'selector':'caption', 'props': [("font-size", "105%"),("background-color", "#aaaaaa"),("color", "white")]}, 
                                        {'selector':'th', 'props': [("font-size", "80%")]},
                                        {'selector':'td', 'props': [("font-size", "80%")]}
                                        ]) 
                .background_gradient(subset=(cross.index[:],cross.columns[0:-1]),cmap='Oranges',axis=None,low=0,high=1)
                # .format("{:.2%}")
                .applymap(lambda x: 'color: transparent' if pd.isnull(x) else '')
                .applymap(lambda x: 'background: #eeeeee' if pd.isnull(x) else '')
                .applymap(lambda x: 'background: #f3dcf7', subset=(cross.index[-1],cross.columns[-1])))
            
            display( HTML(cross.to_html().replace("@@@","<br>") ) )
    
        if priocolor_legend:
            prio_colors = {'P1':'tomato','P2':'orange','P3':'yellow','P4':'lightgreen','P5':'lightsteelblue'}
            leg = pd.DataFrame({'P1':('P1',),'P2':('P2',),'P3':('P3',),'P4':('P4',),'P5':('P5',)})
            leg = leg.set_index(pd.Index(['Priority of the incident type (average priority) :',]))
            leg = leg.style.applymap(lambda x: f'background-color: {prio_colors[x]}' if x in prio_colors else '')
            display(leg.hide_columns())

        for col in index_cols:
          
            vc_top = df[col].astype('str').fillna('na').value_counts()

            def crosstab_chart_with_totals(table_type, cmap, fmt, percent_method=False, aggfunc=None, values=None):
                global count_html
                # full crosstab with totals
                if aggfunc!=None and values!=None:
                    cross = pd.crosstab(df[col].astype('str').fillna('na'), df[tcol].astype('str').fillna('na'), margins=True, aggfunc=aggfunc, values=df[values], normalize=percent_method, margins_name=all_name)
                    #cross = pd.crosstab(df[col], df[tcol], margins=True, aggfunc=aggfunc, values=df[values], normalize=percent_method)
                else:
                    cross = pd.crosstab(df[col].astype('str').fillna('na'), df[tcol].astype('str').fillna('na'), margins=True, normalize=percent_method, margins_name=all_name)
                    #cross = pd.crosstab(df[col], df[tcol], margins=True, normalize=percent_method)
                    
                if percent_method == 'index':
                    cross[all_name] = 1.0                      # adding rowtotal column as 100%
                if percent_method == 'columns':
                    cross.loc[all_name] = 1.0         # adding coltotal row as 100%

                # reindexing rows
                if reindex_0_by is not None:
                    if type(reindex_0_by)!=list:
                        cross = cross.reindex(list(reindex_0_by) + [all_name,], axis=0)
                    else:
                        cross = cross.reindex(reindex_0_by + [all_name,], axis=0)
                else:
                    if col == 'Impact':
                        # cross = cross.reindex(SNOW_IMPACTS_REV + SM9_IMPACT)
                        cross = cross.reindex(SNOW_IMPACTS_REV + [all_name,])
                    elif col == 'Priority':
                        cross = cross.reindex(['1','2','3','4','5'] + [all_name,])
                    elif col=="Opened YEAR MONTH":
                        cross=cross.reindex(sorted(df["Opened YEAR MONTH"].unique()) + [all_name,])
                    else:
                        cross = cross.reindex(vc_top.index.to_list() + [all_name,])
                    
                # reindexing columns
                if reindex_1_by is not None:
                    if type(reindex_1_by)!=list:
                        cross = cross.reindex(list(reindex_1_by) + [all_name,], axis=1)
                    else:
                        cross = cross.reindex(reindex_1_by + [all_name,], axis=1)
                else:
                    if tcol=='Opened DAY NAME' or tcol =='DateCreated DAY NAME':
                        cross = cross.reindex(('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',all_name), axis=1)
                    if tcol=='Opened DAY':
                        cross = cross.reindex(('0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23', '24', '25', '26', '27', '28', '29', '30', '31',all_name), axis=1)
                    if tcol=='Opened HOUR' or tcol =='DateCreated HOUR':
                        cross = cross.reindex(('0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23',all_name), axis=1)
                    if tcol== "Priority":
                        cross = cross.reindex(('1','2','3','4','5',all_name), axis=1)
                    if tcol== "Impact":
                        cross = cross.reindex(('Outage or Degradation beyond usability', 'Significant Degradation', 'Moderate Degradation', 'Minor to No Degradation',all_name), axis=1)
                    if tcol== "Urgency":
                        cross = cross.reindex(('Very urgent', 'Urgent', 'Moderate', 'Less urgent',all_name), axis=1)

                # # excel sheet
                # if excel_name != None:
                #     sheet_name = None
                #     if (excel_sheet_names_column_alias != None) & (excel_sheet_names_index_alias != None) & (aggfunc_values_column_alias != None):
                #         sheet_name = excel_sheet_names_index_alias + '-' + excel_sheet_names_column_alias + '-' + table_type
                #     else:
                #         sheet_name = col.replace('[','').replace(']','') + '_' + table_type
                #     worksheet=workbook.add_worksheet(sheet_name)
                #     writer.sheets[sheet_name] = worksheet
                #     cross.to_excel(writer,sheet_name=sheet_name,startrow=0 , startcol=0)
           
                # custom order by cols
                if order_by_columns != None:
                    cross = pd.concat([ cross.iloc[:-1].sort_values(by=order_by_columns, ascending=order_by_columns_ascending) , cross.tail(1) ])
                
                # limit the number of rows if need
                topn = False
                if max_rows < cross.shape[0]:
                    cross = pd.concat([cross[0:max_rows],cross.tail(1)])
                    topn = True

                # shorter indexes to chart
                if index_colors is None:
                    cross.index = cross.index.to_series().apply(lambda x: string_shortener(x,max_name_length))
           
                if percent_method==False:
                    title = rf'counts by "{col}" & "{tcol}"'
                if percent_method=='columns':
                    title = rf'Distribution of "{tcol}" by "{col}"'
                if percent_method=='index':
                    title = rf'Distribution of "{col}" by "{tcol}"'
                if percent_method=='all':
                    title = rf'Distribution by "{col}" & "{tcol}"'
                #if title_colnames:
                #    title = title +  f' by "{col}" and "{tcol}"'
                if aggfunc=='mean':
                    title = rf'AVG {values}'
                elif aggfunc=='median':
                    title = rf'Median {values}'
                elif aggfunc in (geomean_aggfunc_hour, geomean_aggfunc):
                    title = rf'MEAN {values}'
                elif aggfunc == percentile_aggfunc:
                    title = rf'80 Percentile {values}'

                if title_prefix != None: title = f'{title_prefix} ' + title
                if title_suffix != None: title = title + f' {title_suffix}'         
                if topn: title = title + f' (top {len(cross)-1} {col})'

                # string_shortener(t,max_name_length)

                cross.columns = cross.columns.str.replace(" ", "@@")
                           
                format = '{:' + fmt + '}'
                cross = (cross.style.set_caption(title)
                    .set_table_styles([{'selector':'caption', 'props': [("font-size", "110%"),("font-weight", "bold"),("background-color", "#ffffff"),("color", "black")]}, 
                                        {'selector':'th', 'props': [("font-size", "85%")]},
                                        {'selector':'td', 'props': [("font-size", "85%")]},
                                        {"selector": "td,th", "props": "line-height: inherit; padding: 2px;"}
                                        ]) 
                    .background_gradient(subset=(cross.index[0:-1],cross.columns[-1]),cmap='Greys',axis=None,low=0,high=1)
                    .background_gradient(subset=(cross.index[-1],cross.columns[0:-1]),cmap='Greys',axis=None,low=0,high=1)
                    .background_gradient(subset=(cross.index[0:-1],cross.columns[0:-1]),cmap=cmap,axis=None)
                    #.background_gradient(subset=(cross.index[0:-1],cross.columns[-1]),cmap='Greys',axis=None)
                    #.background_gradient(subset=(cross.index[-1],cross.columns[0:-1]),cmap='Greys',axis=None)
                    .applymap(lambda x: 'background: #f3dcf7', subset=(cross.index[-1],cross.columns[-1]))
                    .applymap(lambda x: 'color: transparent' if pd.isnull(x) else '')
                    .applymap(lambda x: 'background: #eeeeee' if pd.isnull(x) else '')
                    .format(format)
                    .set_table_attributes("style='display:inline'"))
                    #.set_table_attributes("align='left'"))
                
                if index_colors is not None:
                    cross = cross.applymap_index(lambda x: f'background-color: {index_colors[x]}' if x in index_colors else '')
                    # cross = cross.applymap(color_background)
                
                # "\xa0\xa0\xa0"
                
                if count_table_at_right:
                    if percent_method==False:
                        count_html = HTML(cross.to_html().replace("@@","<br>") )
                    else:
                        display_html(HTML(cross.to_html().replace("@@","<br>") )._repr_html_()+"\xa0\xa0\xa0"+count_html._repr_html_(), raw=True)
                else:                
                    display( HTML(cross.to_html().replace("@@","<br>") ) )

            if count_table: crosstab_chart_with_totals(table_type='count',percent_method=False, fmt='.0f', cmap='Blues')
            if percent_table_by_columns: crosstab_chart_with_totals(table_type='column_%',percent_method='columns', fmt='.2%', cmap='Oranges')
            if percent_table_by_rows: crosstab_chart_with_totals(table_type='row_%',percent_method='index', fmt='.2%', cmap='Oranges')
            if percent_table_by_overall: crosstab_chart_with_totals(table_type='overall_%',percent_method='all', fmt='.2%', cmap='Oranges')
            if aggfunc!=None and values!=None: crosstab_chart_with_totals(table_type=f'{aggfunc}_{values}',percent_method=False, fmt='.1f', cmap='Reds', aggfunc=aggfunc, values=values)
    
            
    
        # if excel_name != None:
        #     writer.save()
    
            