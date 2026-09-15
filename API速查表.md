# PETsARD API 速查表

這份文件是 PETsARD 的精簡版 API 速查表，重點保留最常用的公開接口與典型用法，方便快速查閱。

---

## 1. 最常用流程

PETsARD 的典型使用順序大致如下：

1. `Loader`：載入資料
2. `Synthesizer`：建立與訓練合成資料模型
3. `Evaluator` / `Describer`：評估與描述資料結果
4. `Reporter`：輸出報告、schema、資料結果
5. `Executor`：透過 YAML 驅動整個工作流

---

## 2. 入口類別與核心用法

### 2.1 `Executor`

```python
from petsard.executor import Executor

executor = Executor(config="workflow.yaml")
executor.run()
```

用途：
- 直接透過 YAML 設定執行整套 pipeline
- 適合正式工作流、重複實驗與批次執行

常見參數：
- `config`: YAML 檔路徑或 YAML 字串

注意：
- 這是最適合做完整流程控制的入口

---

### 2.2 `Loader`

```python
from petsard.loader import Loader

loader = Loader(
    filepath="data.csv",
    nrows=1000,
    schema={...},
)
```

主要方法/參數：
- `filepath`: 資料檔路徑
- `nrows`: 僅讀取前 N 筆（測試用）
- `schema`: schema 或 schema 路徑
- `column_types`, `header_names`, `na_values`: 多為 legacy 相容參數

用途：
- 載入原始資料
- 可搭配 `schema` 做欄位型別與資料結構定義

---

### 2.3 `Synthesizer`

```python
from petsard.synthesizer import Synthesizer

synth = Synthesizer(method="default", sample_num_rows=1000)
synth.create(metadata=metadata)
synth.fit(data=train_df)
result_df = synth.sample()
```

主要方法：
- `Synthesizer(method: str, sample_num_rows: int = None, **kwargs)`
- `create(metadata=None)`
- `fit(data=None)`
- `sample() -> pd.DataFrame`

用途：
- 建立合成資料模型
- 使用 train data 訓練
- 輸出合成後資料

常見方法名稱：
- `default`
- `petsard-gaussian_copula`
- `sdv`
- `custom`

---

### 2.4 `Evaluator`

```python
from petsard.evaluator import Evaluator

evaluator = Evaluator(method="sdmetrics")
evaluator.create()

result = evaluator.eval({
    "ori": ori_df,
    "syn": syn_df,
    "control": control_df,
})
```

主要方法：
- `Evaluator(method: str, **kwargs)`
- `create()`
- `eval(data: dict[str, pd.DataFrame])`

用途：
- 對合成資料進行效用、fidelity、隱私相關評估

常見方法：
- `sdmetrics`
- `mlutility`
- `anonymeter`
- `mpuccs`
- `custom`

---

### 2.5 `Describer`

```python
from petsard.evaluator import Describer

describer = Describer(method="describe", mode="describe")
describer.create()
summary = describer.eval({"data": data_df})
```

主要方法：
- `Describer(method: str, mode: str = "describe", **kwargs)`
- `create()`
- `eval(data: dict)`

模式：
- `describe`: 單一資料集統計摘要
- `compare`: 比較兩份資料集差異

用途：
- 快速產生資料描述與比較結果
- 例如資料分布、統計量、差異分析

---

### 2.6 `Reporter`

```python
from petsard.reporter import Reporter

reporter = Reporter(method="save_report", output_path="./output")
reporter.create(data={...})
```

主要方法：
- `Reporter(**kwargs)`
- `create(data: dict)`

常見 `method`：
- `save_data`
- `save_report`
- `save_schema`
- `save_timing`
- `save_validation`

用途：
- 輸出資料、schema、分析報告與執行時間資訊

---

## 3. 常見使用模式

### 模式 A：YAML 驅動整體流程

```python
from petsard.executor import Executor

executor = Executor(config="workflow.yaml")
executor.run()
```

最適合：
- 重複實驗
- 可追蹤流程
- 需大量設定參數時

### 模式 B：Python 程式化分步執行

```python
from petsard.loader import Loader
from petsard.synthesizer import Synthesizer
from petsard.evaluator import Evaluator

loader = Loader(filepath="data.csv")
ori_df = loader.load()  # 依實際 API 版本而定

synth = Synthesizer(method="default")
synth.create(metadata=None)
synth.fit(data=ori_df)
syn_df = synth.sample()

evaluator = Evaluator(method="sdmetrics")
evaluator.create()
result = evaluator.eval({"ori": ori_df, "syn": syn_df})
```

最適合：
- 做原型
- 自定義流程
- 研究與比對不同設定

---

## 4. 重要說明

### 4.1 `schema` 很重要

PETsARD 很重視 metadata / schema。若資料結構複雜，建議在 `Loader` 或流程中提供 schema，這樣能提升後續處理、約束與評估穩定性。

### 4.2 `Synthesizer` 需要先 `create()` 再 `fit()`

合成流程通常遵循：

```python
synth = Synthesizer(...)
synth.create(metadata=metadata)
synth.fit(data=train_df)
```

先建立實作，再進行訓練。

### 4.3 `Evaluator` / `Describer` 輸入格式要注意

- `Evaluator.eval()` 通常接收 `ori`、`syn`、`control` 等資料字典
- `Describer.eval()` 則依模式不同，可能接收 `data` 或 `base` / `target`

### 4.4 `Reporter` 主要負責匯出

`Reporter` 不負責做分析，重點是把結果輸出成資料、報告、schema 或時間資訊。

### 4.5 可選依賴要分開安裝

PETsARD 的功能分層較明確，某些方法需要額外套件，例如：
- `sdv`
- 其他評估或處理依賴

建議依需求安裝對應 extras 或可選套件。

---

## 5. 簡短版使用口訣

如果只記住一句話：

> 先用 `Loader` 載入資料，再用 `Synthesizer` 產生合成資料，接著用 `Evaluator` / `Describer` 評估，最後用 `Reporter` 輸出結果；若要做完整工作流，直接用 `Executor` + YAML。

---

## 6. 建議閱讀順序

如果你是第一次使用 PETsARD，建議依序閱讀：

1. `README.md`
2. `使用筆記.md`
3. `API速查表.md`
4. `demo/` 目錄中的範例 YAML / Notebook

這樣能最快建立整體概念。
