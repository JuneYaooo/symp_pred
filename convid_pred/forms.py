from django import forms

class PatientForm(forms.Form):
    GENDER_CHOICES = [
        ('1', '男'),
        ('2', '女'),
    ]
    AGE_CHOICES = [(i, i) for i in range(0, 101)]
    SYMPTOMS_CHOICES = [
        ('fever', '发热'),
        ('cough_expectoration', '咳嗽咳痰'),
        ('headache', '头痛'),
        ('feel_sick_vomit', '恶心呕吐'),
        ('sore', '酸痛'),
        ('runny_nose', '鼻塞流涕'),
        ('chills', '畏寒'),
        ('dizziness', '头晕'),
        ('sore_throat', '咽痛'),
        ('chest_pain', '胸痛'),
        ('palpitations', '心悸'),
        ('poor_appetite', '纳差'),
        ('diarrhea', '腹泻'),
        ('rash', '皮疹'),
        ('chest_tightness', '胸闷'),
        ('fatigue', '乏力'),
        ('stomach_ache', '腹痛'),
        ('joint_pain', '关节疼痛'),
        ('drowsiness', '嗜睡'),
        ('dry_mouth', '口干'),
        ('insomnia', '失眠'),
        ('abdominal_bloating', '腹胀'),
        ('abdominal_discomfort', '腹部不适'),
        ('shortness_of_breath', '气促')
    ]

    gender = forms.ChoiceField(label='性别', choices=GENDER_CHOICES, required=True)
    # age = forms.IntegerField(label='年龄', required=True)
    age = forms.ChoiceField(choices=AGE_CHOICES, required=True)
    symptoms = forms.MultipleChoiceField(label='症状', choices=SYMPTOMS_CHOICES, required=True)