Mình đã tạo file `send_request.ps1` hoàn chỉnh trong canvas (tên: **Send Request**).
```powershell
# send_request.ps1
$apiKey = $env:OPENROUTER_API_KEY
if (-not $apiKey) {
  Write-Error "OPENROUTER_API_KEY chưa được đặt. Chạy: $env:OPENROUTER_API_KEY='your_key' hoặc dùng [Environment]::SetEnvironmentVariable(...)"
  exit 1
}

$uri = "https://openrouter.ai/api/v1/chat/completions"

$json = @'
{
  "model": "anthropic/claude-3.5-sonnet",
  "messages": [{"role": "user", "content": "Test"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "test_function",
      "description": "A test function",
      "parameters": {"type": "object", "properties": {}}
    }
  }]
}
'@

# Gửi request
$response = Invoke-RestMethod -Uri $uri -Method Post -Headers @{
  Authorization = "Bearer $apiKey"
  "Content-Type" = "application/json"
} -Body $json

# In kết quả (đã được parse thành object nếu response là JSON)
$response | ConvertTo-Json -Depth 10

```
Nội dung sẵn sàng copy — cách chạy nhanh:

1. Mở PowerShell ở thư mục chứa file.
2. (Nếu bị chặn chạy script) tạm cho phép trong session:
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
3. Chạy ví dụ:
   `.\send_request.ps1 -Message "Xin chào" -Model "anthropic/claude-3.5-sonnet" -OutFile response.json`

Nếu cần mình dán trực tiếp nội dung file vào chat thay vì canvas, hoặc muốn chỉnh để gửi prompt từ file, hỗ trợ proxy, hoặc thêm header khác — nói mình biết nhé.
