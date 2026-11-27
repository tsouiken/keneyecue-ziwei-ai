# KenEyeCue Agent Builder 全套盤點與遷移規格

> 狀態：Phase 1｜盤點與保存  
> 總追蹤：GitHub Issue #4  
> 原則：先匯出、再比對、後切換；未完成雙跑前不得停用舊流程。

## 1. 遷移目標

將所有依賴 OpenAI Agent Builder 的正式流程，遷移為：

- 可在 GitHub 版本控制
- 可測試、可稽核、可回滾
- 模型、工具與資料來源可替換
- 客戶敏感資料有明確邊界
- 所有正式寫入需人工核准

## 2. 現況邊界

目前已確認：KenEyeCue 有正式流程依賴 Agent Builder。

尚未取得：

- workflow 完整清單
- workflow ID 與版本
- Agents SDK Python export
- 節點、分支與 handoff
- 工具、MCP、File Search、連接器
- guardrail、approval、timeout、retry
- 觸發方式、使用量、成本與失敗紀錄

因此目前只能建立安全遷移骨架，不能宣稱與既有流程逐節點等價。

## 3. 全套盤點欄位

每一條 workflow 都必須填入 `agent-builder-exports/WORKFLOW_INVENTORY.md`：

1. 名稱
2. Workflow ID
3. 版本／最後更新日
4. 商業用途
5. 觸發方式
6. 輸入資料
7. 輸出格式
8. 節點與分支
9. Handoff
10. Tools／MCP／File Search／Connectors
11. Guardrails
12. Human approval
13. Timeout／Retry／Fallback
14. 認證與權限
15. 敏感資料類型
16. 正常案例
17. 邊界案例
18. 失敗案例
19. 平均延遲
20. 每次成本／月使用量
21. 負責人
22. Cutover 優先序

## 4. 官方匯出程序

每一條正式 workflow：

1. 開啟 Agent Builder workflow。
2. 選擇 `Code`。
3. 選擇 `Agents SDK`。
4. 選擇 `Python`。
5. 複製完整程式碼，不得只複製局部節點。
6. 存入：

```text
agent-builder-exports/<workflow-slug>/<version>.py
```

7. 同資料夾新增 `METADATA.md`，記錄：
   - Workflow 名稱與 ID
   - 匯出日期
   - 匯出人
   - Agent Builder 畫面版本
   - 是否含未匯出的 secrets／connector 設定
8. API key、OAuth token、Webhook secret、客戶資料不得寫入檔案。

## 5. 遷移目標架構

```text
Client / Admin / Webhook
        ↓
Input validation + privacy gate
        ↓
Manager / Router
   ├── Query agent
   ├── Ingest agent
   ├── Lint / Review agent
   └── 其他正式 workflow agent
        ↓
Read-only knowledge tools
        ↓
Human approval gate
        ↓
GitHub PR / approved external action
```

### 權限原則

- Query：唯讀。
- Ingest：只產生分類與變更計畫，不直接改正式資料。
- Lint：只回報風險，不自行修正正式版本。
- 對外發送、付款、預約、刪除與發布：必須經人工確認。
- 原始客戶照片、生辰、姓名、私訊預設為敏感資料。

## 6. Node-by-node 比對表

取得 export 後，每個節點逐項比較：

| 項目 | Agent Builder | Agents SDK | 差異 | 處理狀態 |
|---|---|---|---|---|
| Instructions |  |  |  |  |
| Model／設定 |  |  |  |  |
| Input schema |  |  |  |  |
| Output schema |  |  |  |  |
| Tools |  |  |  |  |
| Branch／condition |  |  |  |  |
| Handoff |  |  |  |  |
| Guardrail |  |  |  |  |
| Approval |  |  |  |  |
| Timeout／retry |  |  |  |  |
| Error handling |  |  |  |  |
| Logging／trace |  |  |  |  |

## 7. 測試標準

每條流程至少準備：

- 5 個正常案例
- 3 個資料不足案例
- 3 個矛盾資料案例
- 3 個敏感資料案例
- 2 個工具失敗案例
- 2 個 timeout／retry 案例

### Golden test 比對

記錄：

- 是否完成任務
- 事實／推論是否分開
- 是否出現品牌漂移
- 是否出現命理絕對化
- 是否洩漏或誤用敏感資料
- 延遲
- Token／成本
- 人工接受／退回原因

## 8. Shadow run

切換前，Agent Builder 與 Agents SDK 同時執行同一批輸入：

1. 不讓新版直接執行外部寫入。
2. 保存兩邊輸出與 trace。
3. 人工標記：通過、可接受差異、不可接受差異。
4. 重大差異歸因到 prompt、工具、資料、模型或流程。
5. 連續兩週穩定後，才進入正式切換。

## 9. Cutover 條件

必須全部符合：

- [ ] 所有正式 workflow 已盤點
- [ ] 所有 workflow 已保存 export
- [ ] Node-by-node 比對完成
- [ ] Golden tests 通過
- [ ] 敏感資料防護通過
- [ ] 外部寫入均有 approval
- [ ] 新版連續穩定兩週
- [ ] 成本與延遲在可接受範圍
- [ ] Rollback 已實測
- [ ] Ken 最終確認

## 10. Rollback

若新版發生重大錯誤：

1. 停止新版外部流量。
2. 切回最後可用 Agent Builder workflow 或上一個穩定 runtime tag。
3. 保存失敗輸入、trace 與工具回應。
4. 開立 GitHub Issue，標記根因與影響範圍。
5. 修復後重新執行 golden tests 與 shadow run。

## 11. 現階段下一步

1. 填寫 `agent-builder-exports/WORKFLOW_INVENTORY.md`。
2. 匯出第一條最重要的正式 workflow。
3. 保存 export 與 metadata。
4. 再依真實 export 建立 Agents SDK runtime；不憑空重建節點。
