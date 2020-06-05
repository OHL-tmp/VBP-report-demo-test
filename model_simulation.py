import numpy as np
import pandas as pd

result=pd.read_csv('data/pharma_simulate.csv')
setup_template=pd.read_csv('data/setup_1.csv')

hr_ori=0.1
probnp_ori=-0.25
lvef_ori=0.03

CHF_Pt=150000*0.136
Cost_per_Script_Gross=580





#input
'''cost_trend=0
util_trend=0

hr_input=0.1
probnp_input=-0.25
lvef_input=0.03

Entresto_Utilizer_Perc=0.07

Script_PMPM=0.08

Rebate_VBC_flat=0.4

data={'Marketshare_L':[0,0.05,0.1,0.15],
     'Marketshare_H':[0.05,0.1,0.15,0.20],
     'Rebate':[0.3,0.35,0.35,0.45]}

Rebate_VBC_table=pd.DataFrame(data, columns = ['Marketshare_L', 'Marketshare_H', 'Rebate']) 

data={'Month':[1,2,3,4,5,6,7,8,9,10,11,12],
      'MarketShare':[0.02,0.03,0.04,0.05,0.06,0.06,0.06,0.06,0.06,0.06,0.06,0.06]}
MarketShare_table=pd.DataFrame(data, columns = ['Month','MarketShare'])
'''
def simulate_input(cost_trend,util_trend,hr_input,probnp_input,lvef_input,Entresto_Utilizer_Perc,Script_PMPM,Rebate_VBC_flat,Rebate_VBC_table,MarketShare_table):

    
    #Calculate Total Script and Gross Revenue

    Entresto_Utilizer=CHF_Pt*Entresto_Utilizer_Perc
    Ultimate_MarketShare=MarketShare_table['MarketShare'].max()
    MarketShare_table['MM']=MarketShare_table['MarketShare']/Ultimate_MarketShare*Entresto_Utilizer
    Total_MM=MarketShare_table['MM'].sum()
    Total_Script=Total_MM*Script_PMPM
    Gross_Revenue=Cost_per_Script_Gross*Total_Script/1000000

    if Rebate_VBC_table.shape[0]==0:
        Rebate_VBC=Rebate_VBC_flat
    else:
        for i in range(4):        
            if Ultimate_MarketShare>=Rebate_VBC_table.iat[i,0] and Ultimate_MarketShare<Rebate_VBC_table.iat[i,1]:
                row_num=i
        Rebate_VBC=Rebate_VBC_table.iat[row_num,2]
    
    drugcost=4640*(1-Rebate_VBC)#Rebate_VBC

    df_drugcost=pd.DataFrame(
    {"Cohort":['CHF+AF']*4+['All CHF Patients']*4,
     "Measure":['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate','NT-proBNP Change %','LVEF LS Mean Change %']*2,
     "Rx_Before_Rebate_Worst":[drugcost,0,0,0]*2,
     "Rx_Before_Rebate_Worse":[drugcost,0,0,0]*2,
     "Rx_Before_Rebate_Mid":[drugcost,0,0,0]*2,
     "Rx_Before_Rebate_Better":[drugcost,0,0,0]*2,
     "Rx_Before_Rebate_Best":[drugcost,0,0,0]*2,
     "Scoring Method":[-1,-1,1,1]*2        
    }
    )
    

    
    base_cost=[23906.382007,31474.460332]
    base_hr=[910.218,1180.037]
    base_probnp=[0,0]
    base_lvef=[0,0]
    
    base_cost=[i*(1+cost_trend) for i in base_cost]
    base_hr=[i*(1+util_trend) for i in base_hr]

    df_base=pd.DataFrame(
    {"Cohort":['All CHF Patients','CHF+AF']*4,
     "Measure":['CHF Related Average Cost per Patient']*2+['CHF Related Hospitalization Rate']*2+['NT-proBNP Change %']*2+['LVEF LS Mean Change %']*2,
     "Weight default":[0.3]*2+[0.3]*2+[0.4]*2+[0.4]*2,
     "Baseline":base_cost+base_hr+base_probnp+base_lvef,
     "Likelihood":['High']*8,     
    }
    )

    result['Hospitalization Rate Reduct %']=result['Hospitalization Rate Reduct %']*(hr_input/hr_ori)
    result['CHF Related Hospitalization Rate']=result[' hospitalization rate ']*(1+util_trend)*(1-result['Hospitalization Rate Reduct %']*(hr_input/hr_ori))*1000

    result['CHF Related Average Cost per Patient']=result['cost']*(1+cost_trend)-result['Inpatient Cost Reduct']*(hr_input/hr_ori)*(1+util_trend)+drugcost

    result['NT-proBNP Change %']=result['NT-proBNP Change %']*(probnp_input/probnp_ori)
    result['LVEF LS Mean Change %']=result['LVEF LS Mean Change %']*(lvef_input/lvef_ori)
    
    better=pd.melt(pd.concat([result.groupby('Cohort')['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate'].quantile(0.125) 
    ,result.groupby('Cohort')['NT-proBNP Change %','LVEF LS Mean Change %'].quantile(0.875)],axis=1).reset_index(),id_vars='Cohort',var_name='Measure',value_name='Medical_Better')

    best=pd.melt(pd.concat([result.groupby('Cohort')['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate'].quantile(0.05) 
    ,result.groupby('Cohort')['NT-proBNP Change %','LVEF LS Mean Change %'].quantile(0.95)],axis=1).reset_index(),id_vars='Cohort',var_name='Measure',value_name='Medical_Best')

    worst=pd.melt(pd.concat([result.groupby('Cohort')['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate'].quantile(0.95) 
    ,result.groupby('Cohort')['NT-proBNP Change %','LVEF LS Mean Change %'].quantile(0.05)],axis=1).reset_index(),id_vars='Cohort',var_name='Measure',value_name='Medical_Worst')

    mid=pd.melt(result.groupby('Cohort')['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate','NT-proBNP Change %','LVEF LS Mean Change %'].quantile(0.5).reset_index(),id_vars='Cohort',var_name='Measure',value_name='Medical_Mid')

    worse=pd.melt(pd.concat([result.groupby('Cohort')['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate'].quantile(0.875) 
    ,result.groupby('Cohort')['NT-proBNP Change %','LVEF LS Mean Change %'].quantile(0.125)],axis=1).reset_index(),id_vars='Cohort',var_name='Measure',value_name='Medical_Worse')

    df_perfom_assump=worst.merge(worse,how='left',on=['Cohort','Measure']).merge(mid,how='left',on=['Cohort','Measure']).merge(better,how='left',on=['Cohort','Measure']).merge(best,how='left',on=['Cohort','Measure']).merge(df_drugcost,how='left',on=['Cohort','Measure'])

    df_recom_measure=mid.merge(df_base,how='left',on=['Cohort','Measure']).rename(columns={'Medical_Mid':'Target'})

    df_recom_measure['Weight']=df_recom_measure.apply(lambda x: 0 if ((x['Measure'] in ['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate','NT-proBNP Change %']) 
                                                            and (x['Target']>x['Baseline'])) or
                                                            ((x['Measure'] in ['LVEF LS Mean Change %']) 
                                                            and (x['Target']<x['Baseline']))
                                                            else x['Weight default'],axis=1)

    if df_recom_measure.iloc[4,6]+df_recom_measure.iloc[6,6]==0.8:
        df_recom_measure.iloc[4,6]=0

    if df_recom_measure.iloc[5,6]+df_recom_measure.iloc[7,6]==0.8:
        df_recom_measure.iloc[5,6]=0

    df_recom_measure.iloc[[0,2,4,6],6]=df_recom_measure.iloc[[0,2,4,6],6]/(df_recom_measure.iloc[[0,2,4,6],6].sum())
    df_recom_measure.iloc[[1,3,5,7],6]=df_recom_measure.iloc[[1,3,5,7],6]/(df_recom_measure.iloc[[1,3,5,7],6].sum())

    df_recom_measure=df_recom_measure.drop(columns=['Weight default'])


    if df_recom_measure.iloc[0,5]>0:
        recom_cohort='All CHF Patients'
    else:
        if df_recom_measure.iloc[1,5]>0:
            recom_cohort='CHF+AF'
        else:
            recom_cohort='All CHF Patients'
    
    meas_recom_all=df_recom_measure[(df_recom_measure['Weight']>0) & (df_recom_measure['Cohort']=='All CHF Patients') ]['Measure'].tolist()
    meas_recom_af=df_recom_measure[(df_recom_measure['Weight']>0) & (df_recom_measure['Cohort']=='CHF+AF') ]['Measure'].tolist()
#    meas_recom_all_row=[]

#    if len(set(meas_recom_all).intersection( set(['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate'])))>0:
#        meas_recom_all_row.append(0)
#        if 'CHF Related Average Cost per Patient' in meas_recom_all:
#            meas_recom_all_row.append(1)
#        if 'CHF Related Hospitalization Rate' in meas_recom_all:
#            meas_recom_all_row.append(2)
#    if len(set(meas_recom_all).intersection( set(['NT-proBNP Change %','LVEF LS Mean Change %'])))>0:
#        meas_recom_all_row.append(9)  
#        if 'NT-proBNP Change %' in meas_recom_all:
#            meas_recom_all_row.append(10)
#        if 'LVEF LS Mean Change %' in meas_recom_all:
#            meas_recom_all_row.append(11)

#    meas_recom_af_row=[]

#    if len(set(meas_recom_af).intersection( set(['CHF Related Average Cost per Patient','CHF Related Hospitalization Rate'])))>0:
#        meas_recom_af_row.append(0)
#        if 'CHF Related Average Cost per Patient' in meas_recom_af:
#            meas_recom_af_row.append(1)
#        if 'CHF Related Hospitalization Rate' in meas_recom_af:
#            meas_recom_af_row.append(2)
#    if len(set(meas_recom_af).intersection( set(['NT-proBNP Change %','LVEF LS Mean Change %'])))>0:
#        meas_recom_af_row.append(9)  
#        if 'NT-proBNP Change %' in meas_recom_af:
#            meas_recom_af_row.append(10)
#        if 'LVEF LS Mean Change %' in meas_recom_af:
#            meas_recom_af_row.append(11)
    
    setup_all=setup_template.copy()
    
    setup_all.iloc[0,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[[0,2],5].sum())
    setup_all.iloc[1,[1,2,3]]=['${:,.0f}'.format(i) for i in df_recom_measure.iloc[0,[3,2,2]].tolist()]
    setup_all.iloc[1,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[0,5])
    setup_all.iloc[1,[10,11]]= [df_recom_measure.iloc[0,2],df_recom_measure.iloc[0,2]*0.95]

    setup_all.iloc[2,[1,2,3]]=['{:.0f}'.format(i) for i in df_recom_measure.iloc[2,[3,2,2]].tolist()]
    setup_all.iloc[2,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[2,5])
    setup_all.iloc[2,[10,11]]= [df_recom_measure.iloc[2,2],df_recom_measure.iloc[2,2]*0.95]

    setup_all.iloc[9,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[[4,6],5].sum())

    setup_all.iloc[10,[1,2,3]]=['{:.0%}'.format(i) for i in df_recom_measure.iloc[4,[3,2,2]].tolist()]
    setup_all.iloc[10,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[4,5])
    setup_all.iloc[10,[10,11]]= [round(df_recom_measure.iloc[4,2]*100,0),round(df_recom_measure.iloc[4,2]*100,2)*1.1]

    setup_all.iloc[11,[1,2,3]]=['{:.0%}'.format(i) for i in df_recom_measure.iloc[6,[3,2,2]].tolist()]
    setup_all.iloc[11,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[6,5])
    setup_all.iloc[11,[10,11]]= [round(df_recom_measure.iloc[6,2]*100,0),round(df_recom_measure.iloc[6,2]*100,2)*1.1]

#    setup_all['Cohort']='All CHF Patients'

    setup_af=setup_template.copy()
    setup_af.iloc[0,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[[1,3],5].sum())
    setup_af.iloc[1,[1,2,3]]=['${:,.0f}'.format(i) for i in df_recom_measure.iloc[1,[3,2,2]].tolist()]
    setup_af.iloc[1,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[1,5])
    setup_af.iloc[1,[10,11]]= [df_recom_measure.iloc[0,2],df_recom_measure.iloc[1,2]*0.95]

    setup_af.iloc[2,[1,2,3]]=['{:.0f}'.format(i) for i in df_recom_measure.iloc[3,[3,2,2]].tolist()]
    setup_af.iloc[2,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[3,5])
    setup_af.iloc[2,[10,11]]= [df_recom_measure.iloc[2,2],df_recom_measure.iloc[3,2]*0.95]

    setup_af.iloc[9,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[[5,7],5].sum())

    setup_af.iloc[10,[1,2,3]]=['{:.0%}'.format(i) for i in df_recom_measure.iloc[5,[3,2,2]].tolist()]
    setup_af.iloc[10,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[5,5])
    setup_af.iloc[10,[10,11]]= [round(df_recom_measure.iloc[5,2]*100,0),round(df_recom_measure.iloc[5,2]*100,2)*1.1]

    setup_af.iloc[11,[1,2,3]]=['{:.0%}'.format(i) for i in df_recom_measure.iloc[7,[3,2,2]].tolist()]
    setup_af.iloc[11,[6,7]]='{:.0%}'.format(df_recom_measure.iloc[7,5])
    setup_af.iloc[11,[10,11]]= [round(df_recom_measure.iloc[7,2]*100,0),round(df_recom_measure.iloc[7,2]*100,2)*1.1]

#    setup_af['Cohort']='CHF+AF'

#    setup=pd.concat([setup_all,setup_af])
    
    df_recom_measure=df_recom_measure.iloc[:,[0,1,2,5,3,4]]
    df_perfom_assump.iloc[[2,3,4,5,6,7],[2,6]]=0
    df_perfom_assump.iloc[[0,1],[2,3,4,5,6]]=df_perfom_assump.iloc[[0,1],[2,3,4,5,6]]-drugcost

    if recom_cohort=='CHF+AF':
        meas_recom=meas_recom_af
        meas_recom_not=meas_recom_all
    else:
        meas_recom=meas_recom_all
        meas_recom_not=meas_recom_af

    return df_perfom_assump,df_recom_measure,recom_cohort,meas_recom,meas_recom_not,setup_all,setup_af
