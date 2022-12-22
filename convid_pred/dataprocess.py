import pickle
from xgboost import XGBClassifier
import os

def model_predict(data):
    sym_feature = ['fever',
                 'cough_expectoration',
                 'headache',
                 'feel_sick_vomit',
                 'sore',
                 'runny_nose',
                 'chills',
                 'dizziness',
                 'sore_throat',
                 'chest_pain',
                 'palpitations',
                 'poor_appetite',
                 'diarrhea',
                 'rash',
                 'chest_tightness',
                 'fatigue',
                 'stomach_ache',
                 'joint_pain',
                 'drowsiness',
                 'dry_mouth',
                 'insomnia',
                 'abdominal_bloating',
                 'abdominal_discomfort',
                 'shortness_of_breath']
    x_data = [int(data["age"]), int(data["gender"])]
    for sym in sym_feature:
        if sym in data["symptoms"]:
            x_data.append(1)
        else:
            x_data.append(0)
    cur_path = os.getcwd() #.replace('\\', '/')    # 获取当前路径
    model_path = os.path.join(cur_path, "convid_pred/models/xgb.dat")
    ml_model = pickle.load(open(model_path, "rb"))
    y_pred = ml_model.predict([x_data])
    return y_pred[0]