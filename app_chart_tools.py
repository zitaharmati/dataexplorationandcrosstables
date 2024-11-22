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

