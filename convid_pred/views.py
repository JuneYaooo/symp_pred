from django.shortcuts import render
from .forms import PatientForm
# -*- coding:utf-8 -*-
from .dataprocess import model_predict
# Get an instance of a logger

def diagnose(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        print('~~~form.is_valid', form.is_valid())
        print('~~~form.cleaned_data', form.cleaned_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            # gender = form.cleaned_data["gender"]
            # age = form.cleaned_data["age"]
            # symptoms = form.cleaned_data["symptoms"]
            # 这里你可以根据症状判断病人是正常还是异常，并将结果保存在变量result中
            res = model_predict(cleaned_data)
            result = '您有很大概率已感染新冠，愿您早日恢复健康' if res == 1 else '您有90%的概率没有感染，请好好休息~'
            return render(request, "convid_pred/diagnose.html", {"form": form, "result": result})
        else:
            return render(request, "convid_pred/diagnose.html", {"form": form, "result": "信息未填完，请重新输入！"})
    else:
        form = PatientForm()
    return render(request, "convid_pred/diagnose.html", {"form": form,"result": ""})
