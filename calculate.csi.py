import pandas as pd
import feather
import time
from datetime import datetime

start_time = time.time()


def cu_csimvalue(mdate, mopcls_df):

    cindex_df = mopcls_df.loc[(mopcls_df['tdate']==mdate)&(mopcls_df['stkcd']=='000905.SH')]
    csiprice0 = csi_df.loc[csi_df['trade_dt'] == mdate, ['s_con_windcode', 'closevalue', 'shr_calculation', 'weightfactor', 'weight']].reset_index(drop=True)
 
    clsprice = mopcls_df[mopcls_df['tdate'] == mdate].set_index('stkcd')['oprc'].to_dict()
    csiprice0['closevalue'] = csiprice0['s_con_windcode'].map(clsprice).fillna(csiprice0['closevalue'])
    csiprice0['closevalue'] = csiprice0['closevalue'].astype(float)

    csiprice0['mv_calculation'] = csiprice0['shr_calculation']*csiprice0['closevalue']*csiprice0['weightfactor']*csiprice0['weight']        
    mvalue0 = csiprice0['mv_calculation'].sum()

    mdivisor = mvalue0*10/float(cindex_df.oprc.iloc[0])
    #print(mdivisor)
    #input()
    cutrd_df = trd_df.loc[(trd_df['tdate'] == mdate) & (trd_df['S1'] > 0), ['stkcd', 'ttime', 'S1']].reset_index(drop=True)

    #prc_df = cutrd_df.copy()
    csiprice = csi_df.loc[csi_df['trade_dt'] == mdate, ['s_con_windcode', 'closevalue', 'shr_calculation', 'weightfactor', 'weight']].reset_index(drop=True)
    #out_df = pd.DataFrame(columns=['ttime', 'mvalue'])
    out_df = pd.DataFrame()

    gpcutrd_df = cutrd_df.groupby('ttime').count()
    for index in gpcutrd_df.index:
        #print(csiprice)
        newprice = cutrd_df[cutrd_df['ttime'] == index].set_index('stkcd')['S1'].to_dict()
        #print(newprice)
        csiprice['closevalue'] = csiprice['s_con_windcode'].map(newprice).fillna(csiprice['closevalue'])
        csiprice['closevalue'] = csiprice['closevalue'].astype(float)
        
        csiprice['mvalue'] = csiprice['shr_calculation']*csiprice['closevalue']*csiprice['weightfactor']*csiprice['weight']
        mv_index = csiprice['mvalue'].sum()*10/mdivisor
        out_df = out_df._append({'tdate': mdate, 'ttime': index, 'mvalue': mv_index}, ignore_index=True)
        #print(csiprice)
        
        #input()
    #for row in out_df.itertuples():
    #    print(row.ttime, row.mvalue)
    #input()

    return out_df




csi_df = pd.read_feather('csi500.2023120405.feather')

mmdate = '202312'
trd_file = 'mytrade.'+mmdate+'0405.feather'
opcls_file = 'myopcls.'+mmdate+'0405.feather'
trd_df = pd.read_feather(trd_file)
opcls_df = pd.read_feather(opcls_file)

fflg = 0
gpopcls_df = opcls_df.groupby('tdate').count()
for index in gpopcls_df.index:
    
    mmopcls_df = opcls_df.loc[opcls_df['tdate'] == index, ['tdate', 'stkcd', 'oprc', 'clpc']]
    #devisior0 = cu_divisor(index, mmopcls_df, 0)

    mvcsi_df = cu_csimvalue(index, mmopcls_df)

    if fflg == 0:
        fflg = 1
        rst_df = mvcsi_df
    else: 
        rst_df = pd.concat([rst_df, mvcsi_df], ignore_index=True)
        
    
    #pd.merge(df1, df2, on='共同字段', how='inner')
    #print(index, devisior0-devisior1)

# 将更新后的数据写回Feather文件
mpath = 'mvcsi.' +mmdate+'0405.feather'
feather.write_dataframe(rst_df, mpath)    
#input()


end_time = time.time()
runtime = end_time-start_time
print('运行时间： ', runtime)