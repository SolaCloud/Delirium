import csv
from datetime import datetime
from collections import defaultdict
import pandas as pd

def find_common_dates(dict1, dict2):
    common_dates_dict = defaultdict(list)
    
    common_ids = set(dict1.keys()) & set(dict2.keys())
    
    for patient_id in common_ids:
        dates_in_dict1 = set(dict1[patient_id])
        dates_in_dict2 = set(dict2[patient_id])
        common_dates = dates_in_dict1 & dates_in_dict2
        
        if common_dates:  
            common_dates_dict[patient_id] = sorted(common_dates) 
    
    return dict(common_dates_dict) 


def uti_detect():
    uti_list = []

    cases_dir = {
        "case_1": 0 , 
        # case_1 : Max temp > 38
        "case_2": 1 ,
        # case_2 : Min temp < 36
        "case_3": 0
        # case_3 : Max temp > 38 or Min temp < 36
    }

    with open('database/Physiology.csv', mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  
        
        for row in reader:
            flag = False
            if row[2] == 'Body Temperature':
                if cases_dir["case_1"]:
                    if(float(row[3]) > 38):
                        flag = True
                        
                if cases_dir["case_2"]:
                    if(float(row[3]) < 36):
                        flag = True
                if cases_dir["case_3"]:
                    if (float(row[3]) > 38) or (float(row[3]) < 36):
                        flag = True
                if(flag):
                    if [row[0],row[1][:10],row[2]] not in uti_list:
                        uti_list.append([row[0],row[1][:10],row[2]])


    temp_dict = {}
    for i in uti_list:
        if i[0] not in temp_dict.keys():
            temp_dict[i[0]] = []
            date_obj = datetime.strptime(i[1], "%Y-%m-%d").date()
            temp_dict[i[0]].append(date_obj)
        else:
            date_obj = datetime.strptime(i[1], "%Y-%m-%d").date()
            temp_dict[i[0]].append(date_obj)


    df = pd.read_csv('database/Activity.csv')

    df['datetime'] = pd.to_datetime(df['date'])
    df['hour'] = df['datetime'].dt.hour
    df['date_only'] = df['datetime'].dt.date

    id_list = []

    for i in df['patient_id']:
        if i not in id_list:
            id_list.append(i)


    uti_list_freq = []

    uti_dict = defaultdict(list) 

    for patient_id in id_list:
        df_patient = df[df['patient_id'] == patient_id]
        
        all_dates = df_patient['date_only'].unique()
        full_index = pd.Index(all_dates, name='date_only')
        
        bathroom_visits = (
            df_patient[df_patient['location_name'] == 'Bathroom']
            .groupby('date_only')
            .size()
            .reindex(full_index, fill_value=0)
            .reset_index(name='daily_visit_count')
        )
        
        high_freq_dates = bathroom_visits[bathroom_visits['daily_visit_count'] > 10]['date_only'].tolist()
        if high_freq_dates:  
            uti_dict[patient_id] = high_freq_dates

    uti_dict = dict(uti_dict)
    common_dates_dict = find_common_dates(temp_dict,uti_dict)
    output_dict = {}
    count = 0
    for key in common_dates_dict.keys():
        for j in common_dates_dict[key]:
            count += 1
            if (key,j) not in output_dict.keys():
                output_dict[(key,j)] = 1
    return output_dict

output_dict = uti_detect()
# print(output_dict)
out = []
for key in output_dict.keys():
    out.append(key)
for j in out:
    print(j)

out_df = pd.DataFrame(out, columns=['patient_id', 'date'])
out_df.to_csv('uti_m1.csv')





 
          