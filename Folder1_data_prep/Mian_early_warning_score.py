import pandas as pd
from collections import defaultdict

def calculate_ews(data):
    """
    Based on the paper rule.
    """
    score = 0
    
    # 1. Body Temperature
    if 'Body Temperature' in data.keys():
        if data['Body Temperature'] <= 35:
            score += 3
        elif 35 < data['Body Temperature'] <= 36:
            score += 1
        elif 36 < data['Body Temperature'] <= 38:
            score += 0
        elif 38 < data['Body Temperature'] <= 39:
            score += 1 
        else:
            score += 2

    # 2. Systolic blood pressure
    if 'Systolic blood pressure' in data.keys():
        if data['Systolic blood pressure'] <= 90:
            score += 3
        if 90 < data['Systolic blood pressure'] <= 100:
            score +=2
        if 100 < data['Systolic blood pressure'] <= 110:
            score +=1
        if 220 <= data['Systolic blood pressure']:
            score +=3
    
    # 3. Heart rate
    if 'Heart rate' in data.keys():
        if data['Heart rate'] <= 40:
            score += 3
        if 40 <data['Heart rate'] <= 50:
            score += 1
        if 90 <data['Heart rate'] <= 110:
            score += 1
        if 110 <data['Heart rate'] <= 130:
            score += 2
        if 130 <data['Heart rate']:
            score += 3

    return score

def cal_warning_score():
    file_path = 'database/Physiology.csv' 
    df = pd.read_csv(file_path)

    patient_records = defaultdict(list)

    for _, data in df.iterrows():
        patient_id = data['patient_id']
        record = data.drop('patient_id').to_dict()
        patient_records[patient_id].append(record)

    patient_records = dict(patient_records)

    NEWS2_dict = {}
    for key in patient_records.keys():
        NEWS2_dict[key] = {}

        df = pd.DataFrame(patient_records[key])

        df['date_only'] = pd.to_datetime(df['date']).dt.date

        result_dict = defaultdict(list)

        for (date, device_type), group in df.groupby(['date_only', 'device_type']):
            avg_value = group['value'].mean()
            unit = group['unit'].iloc[0]  
            
            result_dict[str(date)].append({
                device_type: round(avg_value, 2),
            })

        result_dict = dict(result_dict)
        # print(result_dict)
        score_dict = {}
        for date in result_dict.keys():
            score = 0
            # print(result_dict[date])

            data_dict = {key: value for item in result_dict[date] for key, value in item.items()}
            # print(data_dict)
            score += calculate_ews(data_dict)
            # for data in result_dict[date]:
            #     print(data)
                
            score_dict[date] = score
        # print(score_dict)
        NEWS2_dict[key] = score_dict

    # for key in NEWS2_dict:
    #     print(f"\npatient id : {key}")
    #     for i in NEWS2_dict[key].keys():
    #         print(f"Date: {i} || warning score: {NEWS2_dict[key][i]}")
        output = []
        for patient_id in NEWS2_dict.keys():
            for data in NEWS2_dict[patient_id].keys():
                output.append([patient_id,data,NEWS2_dict[patient_id][data]])
    return output


output =  cal_warning_score()
# for i in output:
#     print(i)
df = pd.DataFrame(output, columns=['patient_id', 'date', 'score'])

df.to_csv('warning_score.csv',index=False, encoding='utf-8')
# print(df)

# print(NEWS2_dict)
# output = []
# for patient_id in NEWS2_dict.keys():
#     for data in NEWS2_dict[patient_id].keys():
#         output.append([patient_id,data,NEWS2_dict[patient_id][data]])
# for i in output:
#     print(i)
        
