REQUIRED_COLUMNS = [
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "y",
]

BUSINESS_INPUT_COLUMNS = [
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
]

MODEL_FEATURE_COLUMNS = [
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
]

MODEL_EXCLUDED_COLUMNS = {
    "duration": "通话时长属于营销接触发生后的结果变量，本系统将其用于复盘展示，不参与前置客户筛选预测。",
}

DISPLAY_LABELS = {
    "age": "年龄",
    "job": "职业",
    "marital": "婚姻",
    "education": "教育",
    "default": "违约",
    "housing": "房贷",
    "loan": "个人贷",
    "contact": "联系渠道",
    "month": "月份",
    "duration": "通话时长",
    "campaign": "本次联系次数",
    "pdays": "历史联系间隔",
    "previous": "历史联系次数",
    "poutcome": "历史结果",
    "y": "目标结果",
}

FIELD_DESCRIPTIONS = {
    "age": "客户年龄，作为基础人口统计特征进入模型。",
    "job": "客户职业类别，用于刻画客群差异。",
    "marital": "婚姻状态，用于辅助判断客户生命周期阶段。",
    "education": "教育水平，用于辅助刻画客户背景。",
    "default": "是否存在信用违约记录。",
    "housing": "是否有住房贷款。",
    "loan": "是否有个人贷款。",
    "contact": "本次营销使用的联系渠道。",
    "month": "最近一次营销联系月份。",
    "duration": "通话时长，接触后才知道，只用于复盘，不参与前置预测模型。",
    "campaign": "本轮营销中对该客户的联系次数。",
    "pdays": "距上一次营销联系的天数，999 表示此前未联系。",
    "previous": "本轮营销前的历史联系次数。",
    "poutcome": "上一次营销活动结果。",
    "y": "客户是否订购定期存款，是模型预测目标。",
}

VALUE_LABELS = {
    "job": {
        "admin.": "行政/文员",
        "blue-collar": "蓝领",
        "entrepreneur": "企业主",
        "housemaid": "家政",
        "management": "管理人员",
        "retired": "退休",
        "self-employed": "自雇",
        "services": "服务业",
        "student": "学生",
        "technician": "技术人员",
        "unemployed": "失业",
        "unknown": "未知职业",
    },
    "marital": {
        "divorced": "离异",
        "married": "已婚",
        "single": "单身",
        "unknown": "未知婚姻状态",
    },
    "education": {
        "basic.4y": "基础教育4年",
        "basic.6y": "基础教育6年",
        "basic.9y": "基础教育9年",
        "high.school": "高中",
        "illiterate": "未受教育",
        "professional.course": "职业课程",
        "university.degree": "大学学历",
        "unknown": "未知教育水平",
    },
    "default": {"no": "无违约", "yes": "有违约", "unknown": "未知违约状态"},
    "housing": {"no": "无住房贷款", "yes": "有住房贷款", "unknown": "未知住房贷款状态"},
    "loan": {"no": "无个人贷款", "yes": "有个人贷款", "unknown": "未知个人贷款状态"},
    "contact": {"cellular": "手机联系", "telephone": "固定电话联系"},
    "month": {
        "mar": "3月",
        "apr": "4月",
        "may": "5月",
        "jun": "6月",
        "jul": "7月",
        "aug": "8月",
        "sep": "9月",
        "oct": "10月",
        "nov": "11月",
        "dec": "12月",
    },
    "poutcome": {
        "failure": "上次失败",
        "nonexistent": "此前无营销记录",
        "success": "上次成功",
        "unknown": "未知历史结果",
    },
    "y": {"no": "未购买", "yes": "购买"},
}

AGE_GROUP_LABELS = ["35及以下", "36-50", "51+"]
PRIORITY_LEVELS = [
    "高价值客户",
    "中价值客户",
    "低响应客户",
]
CHANNEL_LABELS = ["电话", "短信", "邮件"]
MONTH_ORDER = ["mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
