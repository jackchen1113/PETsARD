<p align="center"><img width=75% src="https://raw.githubusercontent.com/nics-dp/petsard/main/.github/assets/PETsARD-logo.png"></p>

![Python 3.10](https://img.shields.io/badge/python-v3.10-blue.svg)
![Python 3.11](https://img.shields.io/badge/python-v3.11-blue.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
![PyPI - Status](https://img.shields.io/pypi/status/petsard)

`PETsARD` (Privacy Enhancing Technologies Analysis, Research, and Development, /pəˈtɑrd/) is a Python library for facilitating synthetic data generation and evaluation processes.

`PETsARD`（隱私強化技術分析、研究與開發）是一套為了促進合成資料生成與評估過程而設計的 Python 程式庫。

---

## **✨ Features 主要功能**

- 🔄 **Data Generation 資料生成**: Multiple synthetic data generation algorithms 多種合成資料生成演算法
- 🔒 **Privacy Evaluation 隱私評估**: Comprehensive privacy risk assessment 全面的隱私風險評估
- 📊 **Utility Metrics 效用指標**: Data quality and utility measurements 資料品質與效用測量
- 🎯 **Flexible Configuration 靈活配置**: YAML-based workflow configuration 基於 YAML 的工作流程配置
- 📦 **Benchmark Datasets 基準資料集**: Built-in benchmark dataset support 內建基準資料集支援

---

## **📚 Documentation 文件**

**Website 網站**: https://nics-dp.github.io/petsard/

### [**📦 Installation 安裝**](https://nics-dp.github.io/petsard/docs/installation/)
- PyPI installation PyPI 安裝
- Docker deployment Docker 部署
- Offline setup 離線設置

### [**🚀 Getting Started 入門指南**](https://nics-dp.github.io/petsard/docs/getting-started/)
- Default synthesis workflow 預設合成流程
- Using external synthetic data 使用外部合成資料

### [**🎯 Evaluation Purpose 評估目的**](https://nics-dp.github.io/petsard/docs/evaluation-purpose/)
- Experiment design 實驗設計
- Fidelity vs. utility 保真度與效用
- Privacy risk estimation 隱私風險估計

### [**⚙️ Data Property Adjustment 資料屬性調整**](https://nics-dp.github.io/petsard/docs/data-property-adjustment/)
- Long-tail distribution handling 長尾分佈處理
- Time anchoring 時間錨定
- Uniform encoding 統一編碼

### [**📝 YAML Configuration YAML 配置**](https://nics-dp.github.io/petsard/docs/petsard-yaml/)
- Executor, Loader, Splitter 執行器、載入器、分割器
- Preprocessor, Synthesizer, Postprocessor 前處理器、合成器、後處理器
- Evaluator, Constrainer, Reporter 評估器、約束器、報告器

### [**📋 Schema YAML 綱要配置**](https://nics-dp.github.io/petsard/docs/schema-yaml/)
- Data types and logical types 資料型別與邏輯型別
- Attribute parameters 屬性參數
- Statistics configuration 統計配置

### [**🐍 Python API**](https://nics-dp.github.io/petsard/docs/python-api/)
- Programmatic usage API 參考 API reference

### [**👨‍💻 Developer Guide 開發者指南**](https://nics-dp.github.io/petsard/docs/developer-guide/)
- Development setup 開發環境設置
- Test coverage 測試覆蓋率

### [**📚 Glossary 詞彙表**](https://nics-dp.github.io/petsard/docs/glossary/)
- Key terminology 關鍵術語

### [**⚠️ Error Handling 錯誤處理**](https://nics-dp.github.io/petsard/docs/error-handling/)
- Common errors and solutions 常見錯誤與解決方案

---

## **🛠️ Development 開發**

### Requirements 需求

- Python 3.10 or 3.11 Python 3.10 或 3.11

### Quick Start 快速開始

#### Install from PyPI / 從 PyPI 安裝

```bash
pip install petsard
```

#### Local development / 本地開發

```bash
# Create an isolated environment / 建立隔離環境
conda create -n petsard python=3.11 -y
conda activate petsard

# Install PETsARD and development tools / 安裝 PETsARD 與開發工具
python -m pip install --upgrade pip
pip install -e ".[dev]"

# Run tests / 執行測試
pytest
```

#### Optional extras / 可選額外功能

```bash
# Include Jupyter / notebook support / 包含 Jupyter / notebook 支援
pip install -e ".[all]"
```

### Notes / 注意事項

- PETsARD officially supports Python 3.10 and 3.11. Please avoid Python 3.12+ for now. / 本專案官方支援 Python 3.10 與 3.11，暫時請避免使用 Python 3.12+。
- For local development, run `pip install -e ".[dev]"` in the project root so PETsARD and its development tools are installed together. / 本地開發時，請在專案根目錄執行 `pip install -e ".[dev]"`，讓 PETsARD 與開發工具一起安裝。
- On Windows, if the repository path contains non-ASCII characters such as `OneDrive/文件`, some conda environments may fail to import `site` during Python startup. A practical workaround is to place the project in an ASCII-only path such as `C:\PETsARD`. / 在 Windows 上，如果專案路徑包含非 ASCII 字元（例如 `OneDrive/文件`），部分 conda 環境可能會在 Python 啟動時發生 `site` 匯入錯誤。實務上可將專案放到 `C:\PETsARD` 這類純 ASCII 路徑。
- After activation, verify the environment with `python -c "import petsard; print('PETsARD ready')"`. / 啟用環境後，可用 `python -c "import petsard; print('PETsARD ready')"` 驗證 PETsARD 是否已成功載入。

---

## **📄 License 授權**

This project is licensed under MIT License. See [LICENSE](LICENSE) for details.

本專案採用 MIT License 授權。詳見 [LICENSE](LICENSE)。

---

## **🔗 Links 連結**

- **GitHub**: https://github.com/nics-dp/petsard
- **Documentation 文件**: https://nics-dp.github.io/petsard/
- **PyPI**: https://pypi.org/project/petsard/
- **Issues 問題追蹤**: https://github.com/nics-dp/petsard/issues

---

## **📧 Contact 聯絡**

For questions or support: 如有問題或需要支援：
- Open an issue on GitHub 在 GitHub 開啟 issue
- Check the documentation 查看文件