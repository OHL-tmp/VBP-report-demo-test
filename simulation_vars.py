#!/usr/bin/env python3

Domain_options ={
"checklist-domain-measures-lv1-1" : {
    "Average Cost per Patient" : ["All Causes Average Cost per Patient", "CHF Related Average Cost per Patient"],
    "Average IP Cost per Patient" : ["All Causes Average IP Cost per Patient", "CHF Related Average IP Cost per Patient"  ],
    "Hospitalization Rate" : ["All Causes Hospitalization Rate", "CHF Related Hospitalization Rate"],
    "ER Rate" : ["All Causes ER Rate", "CHF Related ER Rate"  ],
    "Readmission Rate" : [],
    "Incidence Rate of Medical Procedures" : []
},

"checklist-domain-measures-lv1-2" : {
    "Improvement in Clinical Measures" : ["NT-proBNP Change %", "LVEF LS Mean Change %", "LAVi LS Mean Change",
                                         "LVEDVi LS Mean Change", "LVESVi LS Mean Change", "E/e' LS Mean Change"],
    "Functional Outcomes" : ["Change in Self-Care Score", "Change in Mobility Score"  ],
    "Life Expectancy" : ["CV Mortality Rate"],
    "Disease Progression" : ["Rate of CHF Progression for 24 months"],
    "Clinical Measures Adherence Level" : [],
    "Depressive Symptom Measures" : [],
    "Psychosocial Outcome" : []
},

"checklist-domain-measures-lv1-3" : {
    "Benefit Coverage Parity" : [],
    "Screening Rate" : []
},

"checklist-domain-measures-lv1-4" : {
    "Occurrence of Side Effects" : ["Emergent care rate for medication side effect", "Hospitalization rate for medication side effect"],
    "Occurrence of Adverse Event" : [],
    "Occurrence of Complications" : [],
    "Inappropriate Use" :[]
},

"checklist-domain-measures-lv1-5" : {
    "Medication Adherence" : ["DOT", "PDC", "MPR"],
    "Healthcare-Associated Infections" : [],
    "Patient-reported Care quality outcome" : []
},

"checklist-domain-measures-lv1-6" : {
    "Symptom management" : ["Patient Reported SOB changes", "Patient Reported Fatigue and Tiredness Changes",
                           "Patient Reported Peripheral Oedema Changes", "Patient Reported Disturbed Sleep Changes"],
    "Patient Satisfaction" : []
}}


domain_set = ["Cost & Utilization  Reduction", "Improving Disease Outcome",
                 "Decreasing Health Disparities", "Increasing Patient Safety",
                 "Enhancing Care Quality", "Better Patient Experience"]
domain_measure = {"Cost & Utilization  Reduction" : 8, "Improving Disease Outcome" : 10,
                 "Decreasing Health Disparities" : 0, "Increasing Patient Safety" : 2,
                 "Enhancing Care Quality" : 3, "Better Patient Experience" : 4}

Triple_Aim_set =["Reducing Cost","Improving Health", "Improving Health","Improving Patient Care",
                "Improving Patient Care","Improving Patient Care"]
Triple_Aim_color = ["#1db954", "#ffa319","#ffa319", "#6147d6", "#6147d6", "#6147d6"]



dollar_input = ["All Causes Average Cost per Patient", "CHF Related Average Cost per Patient", "All Causes Average IP Cost per Patient", "CHF Related Average IP Cost per Patient"]

percent_input = ["All Causes Hospitalization Rate", "CHF Related Hospitalization Rate", "All Causes ER Rate", "CHF Related ER Rate",
"NT-proBNP Change %", "LVEF LS Mean Change %",
"CV Mortality Rate", "Rate of CHF Progression for 24 months", "Emergent care rate for medication side effect", "Hospitalization rate for medication side effect"]
