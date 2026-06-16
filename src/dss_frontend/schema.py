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

AGE_GROUP_LABELS = ["35及以下", "36-50", "51+"]
PRIORITY_LEVELS = [
    "高价值客户",
    "中价值客户",
    "低响应客户",
]
CHANNEL_LABELS = ["电话", "短信", "邮件"]
MONTH_ORDER = ["mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
