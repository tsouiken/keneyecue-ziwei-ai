# Agent Builder Exports

此目錄保存 KenEyeCue 正式 Agent Builder workflow 的原始 Agents SDK Python 匯出碼。

## 目錄格式

```text
agent-builder-exports/
├── README.md
├── WORKFLOW_INVENTORY.md
└── <workflow-slug>/
    ├── <version>.py
    └── METADATA.md
```

## 保存規則

1. 匯出碼視為原始證據，不直接改寫。
2. 若要修改，複製到正式 runtime 目錄後再處理。
3. 每次匯出必須保留版本，不覆蓋舊檔。
4. `METADATA.md` 必須記錄 workflow 名稱、ID、版本、匯出日期與匯出人。
5. 不得提交：
   - OpenAI API key
   - OAuth token
   - Webhook secret
   - MCP／連接器憑證
   - 客戶姓名、生辰、照片、私訊或其他真實個資
6. 需要敏感設定的欄位只記錄環境變數名稱，例如：

```text
OPENAI_API_KEY
LINE_CHANNEL_ACCESS_TOKEN
GOOGLE_SERVICE_ACCOUNT_JSON
```

不得記錄真實值。

## 匯出步驟

1. Agent Builder → 開啟 workflow。
2. `Code` → `Agents SDK` → `Python`。
3. 複製完整匯出碼。
4. 建立對應 workflow 資料夾。
5. 新增版本檔與 `METADATA.md`。
6. 更新 `WORKFLOW_INVENTORY.md`。
7. 開 PR 進行逐節點複審。

## 重要限制

在所有正式 workflow 尚未匯出並完成比對前，不得宣稱 Agents SDK 新版已完全取代 Agent Builder。
