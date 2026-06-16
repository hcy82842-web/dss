# 银行零售业务智能营销资源配置决策支持系统

## 项目定位

本项目是《决策支持系统》课程作业原型。系统要解决的不是单纯的“客户会不会购买定期存款”，而是：

- 如何在有限营销资源下识别高响应客户；
- 如何把模型概率转化为高/中/低营销优先级；
- 如何为单个客户生成可解释的触达渠道、推荐动作和营销话术。

系统采用“逻辑回归预测 + 规则化决策转化 + LLM 解释增强”的混合决策引擎。LLM 不参与概率预测，也不改变模型输出，只负责解释和话术生成。

## 数据与建模边界

- 数据集：UCI Bank Marketing `bank-additional-full.csv`
- 数据规模：41,188 条样本，21 个原始字段
- 目标变量：`y`，表示客户是否订购定期存款
- 主模型：逻辑回归
- 模型输入特征：`age/job/marital/education/default/housing/loan/contact/month/campaign/pdays/previous/poutcome`
- 排除字段：`duration`

`duration` 是通话发生后才知道的结果变量。为了让系统用于“营销前客户筛选和资源配置”，模型训练与推理不使用 `duration`，该字段仅用于历史复盘和页面展示。

## 当前架构

### 1. Streamlit 展示层

- 入口：`app.py`
- 负责训练数据概览、业务客户录入、批量导入、客户筛选、单客户决策详情展示。
- 页面优先加载 `artifacts/logistic_regression.joblib` 进行模型评分；模型不可用时才回退到离线规则演示。

### 2. FastAPI 后端

- 入口：`src/dss_backend/main.py`
- 负责业务客户入库、模型评分、DeepSeek 解释生成、评分结果保存。

### 3. 数据库层

课程演示默认使用 SQLite，降低部署和答辩环境依赖：

```env
DSS_DATABASE_URL=sqlite:///artifacts/backend-demo.db
```

MySQL 作为可选扩展，适合正式部署：

```env
DSS_DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/dss_demo?charset=utf8mb4
```

核心表：

- `business_customers`：业务客户池，不直接复用训练集；
- `scoring_results`：模型评分、优先级、渠道建议、LLM 文本和生成状态。

### 4. LLM 解释层

- 集成位置：`src/dss_backend/integrations/deepseek_client.py`
- 输出字段：`customer_explanation`、`marketing_script`
- 失败策略：无 API Key 或调用失败时使用模板解释，评分不中断，并记录 `llm_status=failed_fallback`。

## 环境准备

项目需要 Python 3.10+。Windows 上不要直接使用系统默认 `python`，因为本机可能指向 Python 3.6。

## 一键运行

Windows 环境推荐直接运行：

```bash
run_demo.bat
```

该脚本会自动完成：

- 检查 Python 3.10+；
- 创建 `.venv` 虚拟环境；
- 安装 `requirements.txt` 依赖；
- 检查数据文件；
- 缺少模型产物时自动训练逻辑回归模型；
- 启动 FastAPI 后端；
- 启动 Streamlit 前端；
- 自动打开前端工作台。

启动完成后访问：

- 前端工作台：http://127.0.0.1:8501
- 后端健康检查：http://127.0.0.1:8000/api/health

端口说明：

- `8501` 是系统主页面，答辩和演示时打开这个地址。
- `8000` 是后端 API 服务，不是主页面。
- 如果打开 `http://127.0.0.1:8000/`，只会看到后端提示信息。

关闭演示时，关闭脚本打开的两个命令行窗口即可。

## 手动环境准备

推荐：

```bash
py -3.10 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

如果使用 Python 3.12：

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 数据文件位置

将 `bank-additional-full.csv` 放在：

- `data/bank-additional-full.csv`

## 模型训练

首次运行或调整特征后执行：

```bash
python scripts/train_logistic_regression.py
```

训练完成后生成：

- `artifacts/logistic_regression.joblib`
- `artifacts/model_metadata.json`

`model_metadata.json` 包含 AUC、Accuracy、Precision、Recall、F1、混淆矩阵、正类召回率和主要特征影响方向。

## 手动启动方式

### 启动前端

```bash
streamlit run app.py
```

### 启动后端

```bash
uvicorn src.dss_backend.main:create_default_app --factory --reload
```

默认接口前缀为 `/api`。

## 后端接口

- `GET /api/health`
- `POST /api/business-customers`
- `POST /api/business-customers/import`
- `GET /api/business-customers`
- `POST /api/scoring/run/{customer_id}`
- `POST /api/scoring/run-batch`
- `GET /api/scoring-results`
- `GET /api/scoring-results/{customer_id}`

## 演示闭环

1. 放置 `data/bank-additional-full.csv`。
2. 运行 `run_demo.bat`。
3. 打开 Streamlit 工作台。
4. 导入或录入业务客户。
5. 查看模型评分、优先级、推荐渠道、LLM 解释和营销话术。

## 测试

```bash
python -m pytest -q
```

测试覆盖数据加载、模型训练、推理、后端 API、LLM fallback、前端服务层筛选与单客户详情绑定。

## 常见问题

### 页面显示 `{"detail":"Not Found"}` 是不是报错？

通常不是。这个现象一般是因为打开了后端地址 `http://127.0.0.1:8000/`。系统主页面是：

```text
http://127.0.0.1:8501
```

### 如何判断后端是否正常？

打开：

```text
http://127.0.0.1:8000/api/health
```

如果返回 `{"status":"ok"}`，说明后端正常。

### `8501` 打不开怎么办？

检查是否有 Streamlit 命令行窗口，窗口里应出现类似：

```text
Local URL: http://127.0.0.1:8501
```

如果没有这个窗口，说明前端没有启动成功，需要查看一键脚本主窗口或重新运行 `run_demo.bat`。

### 提示端口被占用怎么办？

关闭之前打开的 FastAPI / Streamlit 命令行窗口，然后重新运行：

```bash
run_demo.bat
```
