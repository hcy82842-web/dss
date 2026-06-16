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
- 页面按报告写作顺序组织为 4 个 Tab：数据集与模型概览、训练与验证结果、客户预测验证、LLM 画像与营销建议。
- 前端负责输入、触发、展示和报告截图；模型训练、验证和预测逻辑由后端/服务层提供。

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

`run_demo.bat` 是 Windows CMD 启动入口，文件内容故意保持英文/ASCII，以避免 CMD 对中文批处理编码解析不稳定。详细中文诊断信息由 `scripts/run_demo.ps1` 输出。

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

Windows 环境推荐直接运行：

```bash
train_model.bat
```

该脚本会自动完成：

- 检查 Python 3.10+；
- 创建或复用 `.venv` 虚拟环境；
- 安装 `requirements.txt` 依赖；
- 检查 `data/bank-additional-full.csv`；
- 清理旧运行缓存；
- 重新训练逻辑回归模型；
- 校验模型和验证集产物是否生成成功。

如果已经激活虚拟环境，也可以手动执行：

```bash
python scripts/train_logistic_regression.py
```

训练完成后生成：

- `artifacts/logistic_regression.joblib`
- `artifacts/model_metadata.json`
- `artifacts/validation_predictions.csv`
- `artifacts/evaluation_summary.json`

`model_metadata.json` 包含 AUC、Accuracy、Precision、Recall、F1、混淆矩阵、正类召回率和主要特征影响方向。`validation_predictions.csv` 保存 30% 验证集上的真实标签、预测概率、预测类别和营销优先级，供前端进行单客户案例验证。

## 训练与预测链路

系统运行逻辑如下：

```text
原始数据 -> 70/30 分层划分 -> 训练逻辑回归 -> 验证集评估 -> 保存模型与验证预测 -> 前端读取结果 -> LLM解释
```

具体说明：

- 原始数据来自 `data/bank-additional-full.csv`。
- 训练脚本在内存中按 `70%` 训练集、`30%` 验证集划分数据，并使用 `stratify=y` 保持购买/未购买比例一致。
- 系统不会额外保存 `train.csv` 和 `test.csv`，验证集预测结果统一保存为 `artifacts/validation_predictions.csv`。
- 前端 `数据集与模型概览` 和 `训练与验证结果` 读取 `artifacts/evaluation_summary.json`。
- 前端 `客户预测验证` 读取 `artifacts/validation_predictions.csv`，也可以加载 `artifacts/logistic_regression.joblib` 对手动输入客户即时预测。
- 前端 `LLM画像与营销建议` 基于当前客户的模型输出生成解释文本，不重新预测概率。

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
3. 打开 Streamlit 报告验证页面。
4. 在“客户预测验证”页选择验证集样本或手动输入客户。
5. 查看模型评分、真实标签、预测是否正确、优先级、推荐渠道、LLM 客户画像和营销建议。

## 页面结构

- `数据集与模型概览`：展示 UCI 数据来源、样本量、目标变量分布、训练/验证划分和建模边界。
- `训练与验证结果`：展示 AUC、Accuracy、Precision、Recall、F1、混淆矩阵和主要影响因素。
- `客户预测验证`：从验证集中选择真实客户，或手动输入客户，查看逻辑回归预测结果。
- `LLM画像与营销建议`：基于当前客户的模型输出生成客户画像、营销策略、风险提示和推荐话术。

## 测试

```bash
python -m pytest -q
```

测试覆盖数据加载、模型训练、推理、后端 API、LLM fallback、前端服务层筛选与单客户详情绑定。

## 常见问题

### `run_demo.bat` 闪退或出现一堆红色报错怎么办？

通常是旧的 FastAPI / Streamlit 服务还在运行，占用了演示端口 `8000` 或 `8501`。当前脚本会在失败时停住窗口，并显示占用端口的进程 PID 和进程名。

如果看到类似 `'xxx' is not recognized as an internal or external command`，可能是旧版 `run_demo.bat` 中的中文提示被 Windows CMD 误解析。请拉取最新代码后重新运行；新版 `run_demo.bat` 已保持纯 ASCII，中文诊断统一由 PowerShell 脚本输出。

可以用下面命令查看端口占用：

```powershell
Get-NetTCPConnection -LocalPort 8000,8501 -State Listen
```

处理方式：

1. 关闭旧的 FastAPI / Streamlit 命令行窗口。
2. 重新运行 `run_demo.bat`。
3. 如果仍失败，查看 `artifacts/run_demo.log`。

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

### 出现 `ImportError: cannot import name 'build_structured_llm_sections'` 怎么办？

这通常是旧 Streamlit 进程或 Python 缓存导致的。处理方式：

1. 关闭所有旧的 FastAPI / Streamlit 命令行窗口。
2. 运行缓存清理脚本：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\clean_runtime_cache.ps1
```

3. 运行 import 自检：

```powershell
.\.venv\Scripts\python.exe -c "from src.dss_frontend.llm_cards import build_structured_llm_sections; print('ok')"
```

4. 如果输出 `ok`，重新运行：

```bash
run_demo.bat
```

当前 `run_demo.bat` 已经会自动执行缓存清理和 import 自检。若仍失败，说明本地代码不是最新版本，需要先拉取 GitHub 最新代码。
