# Agent Builder Export Metadata

- **Workflow 名稱：** ⚠️ 待確認
- **Workflow ID：** ⚠️ 待確認
- **Workflow 版本／最後更新日：** ⚠️ 待確認
- **匯出日期：** YYYY-MM-DD
- **匯出人：** ⚠️ 待確認
- **匯出方式：** Agent Builder → Code → Agents SDK → Python
- **原始 export 檔名：** `<version>.py`
- **用途：** ⚠️ 待確認
- **正式／測試／已停用：** ⚠️ 待確認

## 未包含在 export 內的設定

只記錄設定名稱與取得位置，不填真實值。

| 類型 | 名稱 | 取得位置 | 是否必要 |
|---|---|---|---|
| Environment variable | `OPENAI_API_KEY` | Secret manager | 是 |
| Connector／OAuth | ⚠️ 待確認 | ⚠️ 待確認 | ⚠️ 待確認 |
| Vector store／File Search | ⚠️ 待確認 | ⚠️ 待確認 | ⚠️ 待確認 |

## 安全複審

- [ ] 未包含 API key
- [ ] 未包含 OAuth token
- [ ] 未包含 Webhook secret
- [ ] 未包含真實客戶姓名、生辰、照片或私訊
- [ ] 已記錄工具與連接器權限
- [ ] 已記錄 guardrail 與 human approval

## 比對狀態

- [ ] 已和 Agent Builder 畫面逐節點比對
- [ ] 已建立正常案例
- [ ] 已建立邊界與失敗案例
- [ ] 已完成 shadow run
- [ ] 已取得 Ken 最終確認
