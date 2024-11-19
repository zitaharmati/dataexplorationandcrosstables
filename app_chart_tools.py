import pandas as pd
import numpy as np


def custom_describe(df):
    timestamp_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime']).columns
    other_cols = df.columns.difference(timestamp_cols)
    custom_summary = {}
    for col in timestamp_cols:
        custom_summary[col] = {
            'count': df[col].count(),
            'mean': np.nan,
            'min': np.nan,
            'max': np.nan,
            '25%': np.nan, 
            '50%': np.nan,
            '75%': np.nan,
            'max': np.nan,
            'std': np.nan,
        }
    custom_summary_df = pd.DataFrame(custom_summary).T

    describe_df = df[other_cols].describe().T

    combined_summary = pd.concat([describe_df, custom_summary_df], axis=0)
    return combined_summary

def nan_map(df):

    other = (~(df.isnull()) & (df!='') & (df!=True) & (df!=False))
    na = df.isnull()
    emptystring = df==''
    true = df==True
    false = df==False

    other_rep = 0
    na_rep = 1
    emptystring_rep = 2
    true_rep = 4
    false_rep = 5

    df = pd.DataFrame(np.select([other, na, emptystring, true, false],  [other_rep, na_rep, emptystring_rep, true_rep, false_rep],  default=df),columns=df.columns).astype('int8')

    other_color = '#cccccc'
    na_color = '#000000'
    emptystring_color = '#0000ff'
    true_color = '#22ff22'
    false_color = '#ff2222'

    import matplotlib
    from matplotlib.patches import Patch
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [other_color, na_color, emptystring_color, true_color, false_color])
    
    fig = plt.figure(figsize=(df.shape[1]*0.25,7))
    c = sns.heatmap(df, cbar=False, cmap=cmap)
    c.xaxis.set_label_position('top')
    c.xaxis.set_ticks_position('top')
    c.tick_params(length=0)
    c.tick_params(axis='x', rotation=87, labelsize=10)
    legend_elements = [ Patch([0], [0], color=na_color, lw=0, label='nan'),
                        Patch([0], [0], color=emptystring_color, lw=0, label='empty string'),
                        Patch([0], [0], color=true_color, lw=0, label='True / 1'),
                        Patch([0], [0], color=false_color, lw=0, label='False / 0')]
    fig.legend(handles=legend_elements, loc='outside lower center', ncol=5)
    fig.show()



def vc_all_columns(df, count_to=10, skip_na=False):
    
    vcall = pd.DataFrame()
    for i,c in enumerate(df.columns):
        t = df[c].value_counts(dropna=False).reset_index(name='count')[0:count_to]
        t['index'] = '( ' + t['count'].astype(int).astype(str) + ' ) @@@' + t['index'].astype(str)
        if len(t) < count_to:
            empty_df = pd.DataFrame({'index': [np.nan] * (count_to - len(t)), 'count': [np.nan] * (count_to - len(t))})
            t = pd.concat([t, empty_df], ignore_index=True)
        t.index = ['top '+ str(x) for x in range(1,count_to+1)]
        vc = t[['index']].T
        vcall = pd.concat([vcall,vc],axis=0)        
    vcall = vcall.replace('nan | nan','').reset_index()
    return vcall

def column_tops(df, count_to=10, skip_na=False):
    vc = vc_all_columns(df,count_to=count_to,skip_na=skip_na)
    vc['column'] = df.columns
    vc = pd.concat([ vc[['column']], vc.iloc[:,1:-1] ],axis=1)
    return(vc)

def column_profiler(df,formatting=True, count_to=10, skip_na=False):    
    from IPython.display import display, HTML
    
    # base counts and %
    not_na_counts = df.count().reset_index(name='filled')
    not_na_counts['filled %'] = not_na_counts['filled'] / len(df)
    
    na_counts = df.isna().sum().reset_index(name='nan')
    na_counts['nan %'] = na_counts['nan'] / len(df)
    col_stats = pd.concat([not_na_counts,na_counts.iloc[:,-2:]],axis=1)
    
    empty_strings = df.apply(lambda x: (x=='').sum(), axis=0).reset_index(name='empty_str')
    empty_strings['empty_str %'] = empty_strings['empty_str'] / len(df)
    col_stats = pd.concat([col_stats,empty_strings.iloc[:,-2:]],axis=1)
        
    zeros = df.apply(lambda x: (x==0).sum(), axis=0).reset_index(name='zero')
    zeros['zero %'] = zeros['zero'] / len(df)
    col_stats = pd.concat([col_stats,zeros.iloc[:,-2:]],axis=1)
    
    distinct = df.nunique().reset_index(name='distinct')
    col_stats = pd.concat([col_stats,distinct.iloc[:,-1:]],axis=1)
    
    #col_stats.set_index('index', inplace=True)
    try:
#        desc = df.describe().T[['min','max','mean']]
#        col_stats = pd.concat([col_stats,desc],axis=1)
        desc = custom_describe(df)
        col_stats.set_index('index', inplace=True)
        col_stats = pd.concat([col_stats,desc],axis=1)
    
    except:
        col_stats['min'],col_stats['max'],col_stats['mean'] = [np.nan,np.nan,np.nan]
        col_stats = col_stats.reset_index().rename(columns={'index':'COLUMN' })

    # top n values
    tops = vc_all_columns(df,count_to=count_to,skip_na=skip_na)
    del tops['index']
    col_stats = pd.concat([col_stats,tops],axis=1)

    # formatting
    #
    if formatting:
        # format = '{:' + fmt + '}'
        col_stats = (col_stats.style.set_caption('')
            .set_table_styles([{'selector':'caption', 'props': [("font-size", "110%"),("font-weight", "bold"),("background-color", "#ffffff"),("color", "black")]}, 
                                {'selector':'th', 'props': [("font-size", "85%")]},
                                {'selector':'td', 'props': [("font-size", "85%")]},
                                {"selector": "td,th", "props": "line-height: inherit; padding: 2px;"}
                                ]) 
            .background_gradient(subset='filled',cmap='summer_r',axis=None).format('{:.0f}',subset='filled')
            .background_gradient(subset='filled %',cmap='summer_r',axis=None).format('{:.2%}',subset='filled %')

            .background_gradient(subset='nan',cmap='Greys',axis=None).format('{:.0f}',subset='nan')
            .background_gradient(subset='nan %',cmap='Greys',axis=None).format('{:.2%}',subset='nan %')

            .background_gradient(subset='empty_str',cmap='Greys',axis=None).format('{:.0f}',subset='empty_str')
            .background_gradient(subset='empty_str %',cmap='Greys',axis=None).format('{:.2%}',subset='empty_str %')

            .background_gradient(subset='zero',cmap='Greys',axis=None).format('{:.0f}',subset='zero')
            .background_gradient(subset='zero %',cmap='Greys',axis=None).format('{:.2%}',subset='zero %')

            .background_gradient(subset='distinct',cmap='Blues',axis=None).format('{:.0f}',subset='distinct')
            
            .format('{:.2f}',subset='min').format('{:.2f}',subset='max').format('{:.2f}',subset='mean')
            # .applymap(lambda x: 'background: #f3dcf7', subset=(cross.index[-1],cross.columns[-1]))
            # .applymap(lambda x: 'color: transparent' if pd.isnull(x) else '')
            # .applymap(lambda x: 'background: #eeeeee' if pd.isnull(x) else '')
            )
        
        display( HTML(col_stats.to_html().replace('@@@',"<br>") ) )

    # else:
    #     display(col_stats)
    # return col_stats

    
def Stats_All_Columns(df):
    print('\nStats_All_Columns()')
    
    not_na_counts = df.count().reset_index(name='FILLED')
    not_na_counts['FILLED %'] = not_na_counts['FILLED'] / len(df)
    
    na_counts = df.isna().sum().reset_index(name='NA')
    na_counts['NA %'] = na_counts['NA'] / len(df)
    col_stats = pd.concat([not_na_counts,na_counts.iloc[:,-2:]],axis=1)
    
    empty_strings = df.apply(lambda x: (x=='').sum(), axis=0).reset_index(name='EMPTY_STR')
    empty_strings['EMPTY_STR %'] = empty_strings['EMPTY_STR'] / len(df)
    col_stats = pd.concat([col_stats,empty_strings.iloc[:,-2:]],axis=1)
        
    zeros = df.apply(lambda x: (x==0).sum(), axis=0).reset_index(name='0')
    zeros['0 %'] = zeros['0'] / len(df)
    col_stats = pd.concat([col_stats,zeros.iloc[:,-2:]],axis=1)
    
    distinct = df.nunique().reset_index(name='DISTINCT')
    col_stats = pd.concat([col_stats,distinct.iloc[:,-1:]],axis=1)
    
    desc = custom_describe(df)
    col_stats.set_index('index', inplace=True)
    col_stats = pd.concat([col_stats,desc.iloc[:,1:]],axis=1)
    col_stats = col_stats.reset_index().rename(columns={'index':'COLUMN' })
    col_stats=round(col_stats,2)
    try:
        cstat = col_stats.copy()
        cstat.set_index('COLUMN', inplace=True)
        norm_cstat = (cstat - cstat.min(0)) / (cstat.max(0) - cstat.min(0))

        plt.figure(figsize=(23, norm_cstat.shape[0]/3.3))
        sns.set(font_scale = 1)
        c = sns.heatmap(norm_cstat, annot=cstat, cmap="Blues", fmt='g', cbar=False)
        c.xaxis.set_label_position('top')
        c.xaxis.set_ticks_position('top')
        c.tick_params(length=0)
    except:
        c = None

    return col_stats, c
    
# make a stat table (dataframe) which contains statistics for each columns:
# - nan count and %
# - not nan count and %
# - empty string count and %
# - zero (0) count and %
# - count
# - mean
# - standard deviaton
# - min value, value at 25%, value at	50%, value at 75%, 	max value
# usage examples:
# >>> cstat, chart = Stats_All_Columns(df)
