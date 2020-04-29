import numpy as np
import pandas as pd
from scipy import interpolate


# Pre-determined input
Gross_Revenue=6960000/1000000
Baseline_Net_Medical_Cost=33100/10000
Pt_Cnt=1500 


Performance_assumption=pd.read_csv('data/performance_assumption.csv')
Performance_assumption.set_index(['Cohort','Measure'],inplace=True)
Recom_Measure_all=pd.read_csv('data/recom_measure.csv')
Recom_Measure_all.set_index(['Cohort','Measure'],inplace=True)
Pt_Info=pd.read_csv('data/patient_cohort_basic_info.csv')

def Contract_Calculation(Recom_Contract, UD_Measure,UD_Contract,UD_Pt_Cohort,Rebate_noVBC, Rebate_VBC):    
  
    import numpy as np
    import pandas as pd
    from scipy import interpolate

    Recom_Pt_cohort=UD_Pt_Cohort 
    Recom_Measure=Recom_Measure_all.loc[Recom_Pt_cohort]   
    
    Recom_Performance_assumption=[]
    UD_Performance_assumption=[]
    Recom_Merge=[]
    UD_Merge=[]
    Recom_Rebate_Adj_Perc=[]
    UD_Rebate_Adj_Perc=[]
    
    Type = ['Recom','UD']
    Pt_cohort={'Recom':Recom_Pt_cohort , 'UD': UD_Pt_Cohort} 
    Contract_name={'Recom':Recom_Contract,'UD':UD_Contract}    
    Performance_assumption_name={'Recom':Recom_Performance_assumption,'UD':UD_Performance_assumption}
    Merge_name={'Recom':Recom_Merge,'UD':UD_Merge}
    Measure_name={'Recom':Recom_Measure,'UD':UD_Measure}
    Rebate_Adj_Perc={'Recom':Recom_Rebate_Adj_Perc,'UD':UD_Rebate_Adj_Perc}
    Rebate = {'noVBC': Rebate_noVBC, 'VBC': Rebate_VBC} 
    
    Type = ['Recom','UD']   
    Scenario_list=['Worst','Worse','Mid','Better','Best']
    VBC_list=['noVBC','VBC']
    
    for i in Type:
        Performance_assumption_name[i]=Performance_assumption.loc[Pt_cohort[i]]
        
        for scenario in Scenario_list:
            for VBC in VBC_list:
                Performance_assumption_name[i]['total_'+scenario+'_'+VBC]=Performance_assumption_name[i]['Medical_'+scenario]+Performance_assumption_name[i]['Rx_Before_Rebate_'+scenario]*(1-Rebate[VBC])
                Performance_assumption_name[i]['total_'+scenario+'_'+VBC].fillna(Performance_assumption_name[i]['Medical_'+scenario],inplace=True)
        
        Merge_name[i]=Measure_name[i].merge(Performance_assumption_name[i],left_on='Measure', right_on='Measure', suffixes=(False, False))
        
        Merge_name[i]['Worse_Diff']= Merge_name[i]['total_Worse_VBC'].astype(float)- Merge_name[i]['Target'].astype(float)
        Merge_name[i]['Worse_Perc']=np.where( Merge_name[i]['Scoring Method']==1,1+ Merge_name[i]['Worse_Diff']/ Merge_name[i]['Target'],1- Merge_name[i]['Worse_Diff']/ Merge_name[i]['Target'])
        Merge_name[i]['Mid_Diff']= Merge_name[i]['total_Mid_VBC'].astype(float)- Merge_name[i]['Target'].astype(float)
        Merge_name[i]['Mid_Perc']=np.where( Merge_name[i]['Scoring Method']==1,1+ Merge_name[i]['Mid_Diff']/ Merge_name[i]['Target'],1- Merge_name[i]['Mid_Diff']/ Merge_name[i]['Target'])
        Merge_name[i]['Better_Diff']= Merge_name[i]['total_Better_VBC'].astype(float)- Merge_name[i]['Target'].astype(float)
        Merge_name[i]['Better_Perc']=np.where( Merge_name[i]['Scoring Method']==1,1+ Merge_name[i]['Better_Diff']/ Merge_name[i]['Target'],1- Merge_name[i]['Better_Diff']/ Merge_name[i]['Target'])
            
        Worse_Performance=Merge_name[i]['Weight'].dot(Merge_name[i]['Worse_Perc'])
        Mid_Performance=Merge_name[i]['Weight'].dot(Merge_name[i]['Mid_Perc'])
        Better_Performance=Merge_name[i]['Weight'].dot(Merge_name[i]['Better_Perc'])
        
        x=[0,Contract_name[i].iloc[0][4],Contract_name[i].iloc[0][3],Contract_name[i].iloc[0][0],Contract_name[i].iloc[0][1],999]
        y=[Contract_name[i].iloc[0][5],Contract_name[i].iloc[0][5],0,0,Contract_name[i].iloc[0][2],Contract_name[i].iloc[0][2]]
        f = interpolate.interp1d(x, y)
        Rebate_Adj_Perc[i]=[f(Mid_Performance),Contract_name[i].iloc[0][5],Contract_name[i].iloc[0][2],f(Worse_Performance),f(Better_Performance)]
    
    #Produce output table - Pharma's net revenue  
    
    data = {'Scenario': ['Best Estimate', 'Worst', 'Best', 'Lower End', 'Higher End'], 
                'NoVBC Gross Revenue': [Gross_Revenue, 'NA', 'NA','NA','NA'], 
                'NoVBC Base Rebate Payout': [Gross_Revenue*Rebate_noVBC, 'NA', 'NA','NA','NA'], 
                'NoVBC Outcome Based Rebate Adjustment': [0, 'NA', 'NA','NA','NA'], 
                'NoVBC Net Rebate Payout': [Gross_Revenue*Rebate_noVBC, 'NA', 'NA','NA','NA'], 
                'NoVBC Net Revenue': [Gross_Revenue-Gross_Revenue*Rebate_noVBC, 'NA', 'NA','NA','NA']} 
    Output_Pharma_Net_Revenue = pd.DataFrame(data) 
    
    for i in Type:
        Output_Pharma_Net_Revenue[i+ 'VBC Gross Revenue']=Gross_Revenue
        Output_Pharma_Net_Revenue[i+'VBC Base Rebate Payout']=Gross_Revenue*Rebate_VBC
        Output_Pharma_Net_Revenue[i+'VBC Outcome Based Rebate Adjustment']=Output_Pharma_Net_Revenue[i+'VBC Gross Revenue']*Rebate_Adj_Perc[i]
        Output_Pharma_Net_Revenue[i+'VBC Net Rebate Payout']=Output_Pharma_Net_Revenue[i+'VBC Base Rebate Payout']-Output_Pharma_Net_Revenue[i+'VBC Outcome Based Rebate Adjustment']
        Output_Pharma_Net_Revenue[i+'VBC Net Revenue']=Output_Pharma_Net_Revenue[i+'VBC Gross Revenue']-Output_Pharma_Net_Revenue[i+'VBC Net Rebate Payout']
    
    #Produce output table - Plan's medical cost
    
    Baseline=Pt_Info.loc[Pt_Info['Population'] == UD_Pt_Cohort]
    
    NoVBC_Cost=Merge_name['UD'][['total_Mid_noVBC', 'total_Worst_noVBC','total_Best_noVBC','total_Worse_noVBC','total_Better_noVBC']].iloc[0]
    
    RecomVBC_Cost=Merge_name['Recom'][['total_Mid_VBC', 'total_Worst_VBC','total_Best_VBC','total_Worse_VBC','total_Better_VBC']].iloc[0]
    UDVBC_Cost=Merge_name['UD'][['total_Mid_VBC', 'total_Worst_VBC','total_Best_VBC','total_Worse_VBC','total_Better_VBC']].iloc[0]
    
    data = {'Scenario': ['Best Estimate', 'Worst', 'Best', 'Lower End', 'Higher End'], 
                'Baseline Total Cost': [Baseline.iat[0,1]*Baseline.iat[0,2]/1000000, 'NA', 'NA','NA','NA'],
                'NoVBC Total Cost':[x * Baseline.iat[0,1]/1000000 for x in NoVBC_Cost],
                'NoVBC Rebate Adjustment':[0,0,0,0,0],
                'NoVBC Total Cost (After Rebate Adj)':[x * Baseline.iat[0,1]/1000000 for x in NoVBC_Cost],
                'RecomVBC Total Cost':[x * Baseline.iat[0,1]/1000000 for x in RecomVBC_Cost]}

    Output_Medical_Cost=pd.DataFrame(data) 

    Output_Medical_Cost['RecomVBC Rebate Adjustment']=Output_Pharma_Net_Revenue['RecomVBC Outcome Based Rebate Adjustment']
    Output_Medical_Cost['RecomVBC Total Cost (After Rebate Adj)']=Output_Medical_Cost['RecomVBC Total Cost']+Output_Medical_Cost['RecomVBC Rebate Adjustment']

    Output_Medical_Cost['UDVBC Total Cost']=[x * Baseline.iat[0,1]/1000000 for x in UDVBC_Cost]
    Output_Medical_Cost['UDVBC Rebate Adjustment']=Output_Pharma_Net_Revenue['UDVBC Outcome Based Rebate Adjustment']
    Output_Medical_Cost['UDVBC Total Cost (After Rebate Adj)']=Output_Medical_Cost['UDVBC Total Cost']+Output_Medical_Cost['UDVBC Rebate Adjustment']

    Output_Medical_Cost=Output_Medical_Cost.T
    header=Output_Medical_Cost.iloc[0]
    Output_Medical_Cost=Output_Medical_Cost[1:]
    Output_Medical_Cost.columns=header
    
    Output_Medical_Cost.insert(0, 'Contract Type',['Baseline']*1+ ['Contract w/o VBC Payout']*3+['Contract with VBC Payout (Recommended)']*3+['Contract with VBC Payout (Payor Contract)']*3)
    Output_Medical_Cost.insert(1, 'Item',['Total Cost']*1+ ['Total Cost','Rebate Adjustment','Total Cost (After Rebate Adj)']*3)
    
    Output_Medical_Cost.reset_index()  
    Output_Medical_Cost.set_index(['Contract Type'],inplace=True)
    
     #Transpose pharma net revenue table
    
    Output_Pharma_Net_Revenue=Output_Pharma_Net_Revenue.T
    header=Output_Pharma_Net_Revenue.iloc[0]
    Output_Pharma_Net_Revenue=Output_Pharma_Net_Revenue[1:]
    Output_Pharma_Net_Revenue.columns=header
    
    Output_Pharma_Net_Revenue.insert(0, 'Contract Type', ['Contract w/o VBC Payout']*5+['Contract with VBC Payout (Recommended)']*5+['Contract with VBC Payout (Payor Contract)']*5)
    Output_Pharma_Net_Revenue.insert(1, 'Item', ['Gross Revenue','Base Rebate Payout','Outcome Based Rebate Adjustment','Net Rebate Payout','Net Revenue']*3)
    
        
    #Produce output table - Pharma's rebate payout
    
    Output_Rebate = Output_Pharma_Net_Revenue[Output_Pharma_Net_Revenue['Item'].str.contains('Rebate')]
    Output_Pharma_Net_Revenue.reset_index()
    pos=[1,2,6,7,11,12]
    Output_Pharma_Net_Revenue.drop(Output_Pharma_Net_Revenue.index[pos], inplace=True)
    Output_Pharma_Net_Revenue.set_index(['Contract Type'],inplace=True)
    Output_Rebate.set_index(['Contract Type'],inplace=True)
 
    return Output_Pharma_Net_Revenue,Output_Rebate, Output_Medical_Cost