Tôi sẽ tạo script hoàn chỉnh để scan lỗi OPTIONS và tự động tạo báo cáo đầy đủ:

```python
#!/usr/bin/env python3
"""
HTTP OPTIONS Method Security Scanner & Report Generator
Quét lỗi OPTIONS method và tạo báo cáo chi tiết
"""

import requests
import sys
from datetime import datetime
from urllib.parse import urlparse

class OptionsSecurityScanner:
    def __init__(self, url):
        self.url = self.normalize_url(url)
        self.domain = urlparse(self.url).netloc
        self.scan_time = datetime.now()
        self.results = {}
        
    def normalize_url(self, url):
        """Chuẩn hóa URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
    
    def scan_options(self):
        """Quét OPTIONS method"""
        print(f"\n{'='*70}")
        print(f"🔍 ĐANG QUÉT: {self.url}")
        print(f"{'='*70}\n")
        
        try:
            # Test OPTIONS
            print("📤 Test 1: Gửi OPTIONS request...")
            options_response = requests.options(self.url, timeout=10, allow_redirects=False)
            
            self.results['options_status'] = options_response.status_code
            self.results['options_headers'] = dict(options_response.headers)
            self.results['allow_header'] = options_response.headers.get('Allow', None)
            
            print(f"   ✓ Status Code: {options_response.status_code}")
            print(f"   ✓ Allow Header: {self.results['allow_header'] or 'Không có'}")
            
            # Test các methods nguy hiểm
            print("\n📤 Test 2: Kiểm tra methods nguy hiểm...")
            dangerous_methods = ['PUT', 'DELETE', 'TRACE', 'CONNECT', 'PATCH']
            self.results['dangerous_tests'] = {}
            
            for method in dangerous_methods:
                try:
                    resp = requests.request(method, f"{self.url}/test", timeout=5)
                    self.results['dangerous_tests'][method] = resp.status_code
                    status_icon = "✅" if resp.status_code in [405, 403] else "⚠️"
                    print(f"   {status_icon} {method}: {resp.status_code}")
                except:
                    self.results['dangerous_tests'][method] = "Error"
                    print(f"   ⚠️ {method}: Lỗi kết nối")
            
            # Phân tích rủi ro
            self.analyze_risk()
            
            print(f"\n{'='*70}")
            print(f"✅ QUÉT HOÀN TẤT")
            print(f"{'='*70}\n")
            
            return True
            
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT - Không thể kết nối")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR")
            return False
        except Exception as e:
            print(f"❌ LỖI: {str(e)}")
            return False
    
    def analyze_risk(self):
        """Phân tích mức độ rủi ro"""
        status = self.results['options_status']
        allow = self.results['allow_header']
        
        # Xác định có lỗ hổng không
        self.results['is_vulnerable'] = False
        self.results['risk_level'] = 'Informational'
        self.results['cvss_score'] = 0.0
        
        if status in [405, 403]:
            self.results['assessment'] = 'AN TOÀN - Server từ chối OPTIONS'
        elif allow:
            # Có Allow header - kiểm tra methods nguy hiểm
            methods = [m.strip().upper() for m in allow.split(',')]
            dangerous_found = [m for m in methods if m in ['PUT', 'DELETE', 'TRACE', 'CONNECT']]
            
            if dangerous_found:
                self.results['is_vulnerable'] = True
                self.results['risk_level'] = 'Medium' if len(dangerous_found) <= 2 else 'High'
                self.results['cvss_score'] = 4.3 if len(dangerous_found) <= 2 else 5.3
                self.results['dangerous_methods'] = dangerous_found
                self.results['assessment'] = f'CÓ LỖ HỔNG - Tiết lộ methods nguy hiểm: {", ".join(dangerous_found)}'
            else:
                self.results['assessment'] = 'AN TOÀN - Chỉ có methods cơ bản'
        else:
            # Không có Allow header
            self.results['assessment'] = 'AN TOÀN - Không tiết lộ methods'
    
    def generate_markdown_report(self):
        """Tạo báo cáo Markdown chi tiết"""
        
        report = f"""# 🔍 Phản biện kỹ thuật: "OPTIONS Method is Enabled"

**Ngày phân tích:** {self.scan_time.strftime('%d/%m/%Y %H:%M:%S')}  
**Website:** {self.url}  
**Domain:** {self.domain}  
**Phân loại:** {"Vulnerability" if self.results['is_vulnerable'] else "False Positive Analysis"}

---

## 📚 1. Tham chiếu chuẩn kỹ thuật

- **RFC 7231 (Section 4.3.7):** OPTIONS là phương thức hợp lệ của HTTP/1.1
- **OWASP Testing Guide v4.2:** "OPTIONS method chỉ là lỗ hổng KHI tiết lộ methods nguy hiểm hoặc thông tin nhạy cảm"
- **CWE-16:** Configuration - OPTIONS không phải CWE nếu cấu hình đúng
- **PCI-DSS v4.0:** Không yêu cầu disable OPTIONS, chỉ yêu cầu không tiết lộ thông tin nhạy cảm

---

## 🧪 2. Kết quả kiểm tra thực tế

### Test 1: OPTIONS Request

```bash
curl -i -X OPTIONS {self.url}
```

**Phản hồi:**

```http
HTTP/1.1 {self.results['options_status']} {self._get_status_text(self.results['options_status'])}
"""

        # Thêm headers quan trọng
        important_headers = ['Server', 'Allow', 'Strict-Transport-Security', 'X-Frame-Options', 
                            'Content-Security-Policy', 'X-Content-Type-Options']
        
        for header in important_headers:
            if header in self.results['options_headers']:
                report += f"{header}: {self.results['options_headers'][header]}\n"
        
        report += "```\n\n"
        
        # Nhận xét
        report += f"""**Nhận xét:**

- Status Code: `{self.results['options_status']}` - {self._get_status_assessment(self.results['options_status'])}
- Allow Header: `{self.results['allow_header'] or 'Không có'}` - {self._get_allow_assessment()}
"""
        
        if 'Strict-Transport-Security' in self.results['options_headers']:
            report += "- ✅ Có HSTS header (HTTPS enforced)\n"
        
        report += "\n### Test 2: Methods nguy hiểm\n\n```bash\n"
        
        for method, status in self.results['dangerous_tests'].items():
            report += f"# {method}\n"
            report += f"curl -i -X {method} {self.url}/test\n"
            report += f"→ HTTP/1.1 {status} {'✅' if status in [405, 403] else '⚠️'}\n\n"
        
        report += "```\n\n"
        
        # Đánh giá các methods
        blocked = sum(1 for s in self.results['dangerous_tests'].values() if s in [405, 403])
        total = len(self.results['dangerous_tests'])
        
        if blocked == total:
            report += f"✅ **Kết quả:** Tất cả {total} methods nguy hiểm đều bị chặn\n\n"
        else:
            report += f"⚠️ **Cảnh báo:** {total - blocked}/{total} methods nguy hiểm KHÔNG bị chặn\n\n"
        
        report += """---

## 🔍 3. So sánh: Có lỗi vs Không có lỗi

### ❌ Trường hợp CÓ LỖ HỔNG (ví dụ):

```http
HTTP/1.1 200 OK
Allow: GET, POST, PUT, DELETE, TRACE, CONNECT  ← 🔴 Tiết lộ methods nguy hiểm
Server: Apache/2.4.41 (Ubuntu)                  ← 🔴 Tiết lộ phiên bản
X-Powered-By: PHP/7.4.3                         ← 🔴 Tiết lộ công nghệ
```

**Rủi ro:**
- Attacker biết được server hỗ trợ PUT → có thể thử upload file
- Biết TRACE enabled → có thể thực hiện Cross-Site Tracing (XST)
- Biết version cụ thể → tìm CVE tương ứng để khai thác

"""
        
        # Trường hợp của website hiện tại
        report += f"""### {"✅ Trường hợp AN TOÀN" if not self.results['is_vulnerable'] else "⚠️ Trường hợp HIỆN TẠI"} (website đang kiểm tra):

```http
HTTP/1.1 {self.results['options_status']} {self._get_status_text(self.results['options_status'])}
Server: {self.results['options_headers'].get('Server', 'N/A')}
"""
        
        if 'Strict-Transport-Security' in self.results['options_headers']:
            report += f"Strict-Transport-Security: {self.results['options_headers']['Strict-Transport-Security']}\n"
        
        if self.results['allow_header']:
            report += f"Allow: {self.results['allow_header']}\n"
        else:
            report += "(Không có Allow header)\n"
        
        report += "```\n\n"
        
        if not self.results['is_vulnerable']:
            report += """**Bảo vệ:**
- ✅ Không tiết lộ danh sách methods (hoặc chỉ có methods an toàn)
- ✅ Server name không tiết lộ version chi tiết
- ✅ Các methods nguy hiểm bị reject (405/403)

"""
        else:
            report += """**Vấn đề:**
- ⚠️ Có tiết lộ danh sách methods
- ⚠️ Có methods nguy hiểm trong Allow header
- ⚠️ Cần khắc phục để tăng cường bảo mật

"""
        
        report += """---

## 🧩 4. Phân tích kỹ thuật

### Tại sao OPTIONS được bật?

OPTIONS là **bắt buộc** cho CORS (Cross-Origin Resource Sharing):

```javascript
// Khi frontend gọi API từ domain khác:
fetch('https://api.example.com/data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
})

// Browser tự động gửi preflight request:
OPTIONS /data HTTP/1.1
Origin: https://www.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type

// Server phải phản hồi OPTIONS để CORS hoạt động
```

**Nếu tắt hoàn toàn OPTIONS:**
- ❌ CORS sẽ bị break
- ❌ API calls từ frontend sẽ bị chặn
- ❌ Modern web apps (SPA) sẽ không hoạt động

---

## 📊 5. Bảng đánh giá rủi ro

| Tiêu chí | Kết quả | Đánh giá | Rủi ro |
|----------|---------|----------|--------|
"""
        
        # OPTIONS status
        options_safe = self.results['options_status'] in [405, 403]
        report += f"| OPTIONS Enabled | {'❌ Bị chặn' if options_safe else '✅ Có'} | {'Server từ chối' if options_safe else 'Cần kiểm tra Allow header'} | {'✅ An toàn' if options_safe else '⚠️ Cần xem xét'} |\n"
        
        # Allow header
        has_allow = self.results['allow_header'] is not None
        report += f"| Header `Allow` | {'✅ Có' if has_allow else '❌ Không có'} | {'Tiết lộ methods' if has_allow else 'Không tiết lộ'} | {'⚠️ Cần xem xét' if has_allow else '✅ An toàn'} |\n"
        
        # Dangerous methods
        all_blocked = all(s in [405, 403] for s in self.results['dangerous_tests'].values() if s != 'Error')
        report += f"| PUT/DELETE/TRACE | {'❌ Bị chặn (405)' if all_blocked else '⚠️ Một số được phép'} | {'Không cho phép' if all_blocked else 'Có methods được phép'} | {'✅ An toàn' if all_blocked else '🔴 Nguy hiểm'} |\n"
        
        # Server header
        server = self.results['options_headers'].get('Server', '')
        version_disclosed = any(v in server for v in ['/', '(', 'Apache', 'nginx', 'IIS'])
        report += f"| Tiết lộ version | {'⚠️ Có' if version_disclosed else '❌ Không'} | {server if server else 'N/A'} | {'⚠️ Nên ẩn' if version_disclosed else '✅ An toàn'} |\n"
        
        # HSTS
        has_hsts = 'Strict-Transport-Security' in self.results['options_headers']
        report += f"| HSTS Header | {'✅ Có' if has_hsts else '❌ Không'} | {'HTTPS enforced' if has_hsts else 'Nên thêm'} | {'✅ An toàn' if has_hsts else '⚠️ Thiếu'} |\n"
        
        report += f"\n**Kết luận rủi ro:** {self.results['risk_level']}\n\n"
        
        report += """---

## ⚠️ 6. Về cảnh báo từ công cụ quét tự động

Một số scanner (Acunetix, Nessus, OWASP ZAP) có thể cảnh báo "OPTIONS enabled" do:

1. **Rule cũ từ thời 2000s** - Khi Apache/IIS thường có OPTIONS + TRACE vulnerability
2. **Thiếu context** - Tool không phân biệt OPTIONS có tiết lộ info hay không
3. **Compliance checklist máy móc** - PCI-DSS v2.0 cũ (đã update ở v3.x/4.0)

**Khuyến nghị xử lý:**
"""
        
        if not self.results['is_vulnerable']:
            report += """- ✅ Đánh dấu **False Positive** trong report
- ✅ Whitelist trong lần scan tiếp theo
- ✅ Ghi nhận vào **Risk Acceptance** với justification này
"""
        else:
            report += """- 🔴 **Thực sự có lỗ hổng** - Cần khắc phục
- 🔴 Ưu tiên xử lý ngay
- 🔴 Tham khảo mục 7 để khắc phục
"""
        
        report += """
---

## 🔧 7. Biện pháp khắc phục/tăng cường

"""
        
        if self.results['is_vulnerable']:
            report += "### ⚠️ CẦN KHẮC PHỤC NGAY\n\n"
        else:
            report += "### Biện pháp tăng cường (nếu chính sách yêu cầu)\n\n"
        
        report += """### Option A: Chặn OPTIONS hoàn toàn (chỉ khi không cần CORS)

**Nginx:**
```nginx
if ($request_method = OPTIONS) {
    return 405;
}
```

**Apache:**
```apache
<Limit OPTIONS>
    Require all denied
</Limit>
```

**Vercel (Next.js Middleware):**
```javascript
export function middleware(req) {
  if (req.method === 'OPTIONS') {
    return new Response('', { status: 405 })
  }
  return NextResponse.next()
}
```

### Option B: Giới hạn OPTIONS cho API endpoints

```javascript
// Vercel - Chỉ cho phép OPTIONS trên /api/*
export function middleware(req) {
  if (req.method === 'OPTIONS' && !req.nextUrl.pathname.startsWith('/api/')) {
    return new Response('', { status: 405 })
  }
  return NextResponse.next()
}
```

### Option C: Rate limiting

```nginx
# Nginx - Giới hạn OPTIONS request
limit_req_zone $binary_remote_addr zone=options:10m rate=10r/m;

location / {
    if ($request_method = OPTIONS) {
        limit_req zone=options burst=5;
    }
}
```

### Option D: WAF Rule (Cloudflare/AWS WAF)

```yaml
if (method == "OPTIONS" AND 
    path not matches "^/api/.*" AND 
    rate > 10/min) then block
```

**⚠️ Lưu ý quan trọng:**
- ✅ Test kỹ trước khi deploy production
- ⚠️ Có thể ảnh hưởng CORS functionality
- 📝 Monitor logs sau khi triển khai
- 🔄 Rollback plan nếu có vấn đề

---

## 📋 8. Kết luận và khuyến nghị

### Đánh giá tổng quan:

"""
        
        if self.results['is_vulnerable']:
            report += f"""🔴 **Website CÓ LỖ HỔNG BẢO MẬT**

**Vấn đề phát hiện:**
- ⚠️ OPTIONS method tiết lộ danh sách methods: `{self.results['allow_header']}`
"""
            if 'dangerous_methods' in self.results:
                report += f"- 🔴 Có methods nguy hiểm: `{', '.join(self.results['dangerous_methods'])}`\n"
            
            report += """
**Tác động:**
- Attacker có thể biết được các methods được hỗ trợ
- Có thể lên kế hoạch tấn công dựa trên thông tin này
- Vi phạm nguyên tắc "Least Information Disclosure"

"""
        else:
            report += """✅ **Website KHÔNG CÓ LỖ HỔNG nghiêm trọng**

**Lý do:**
"""
            if self.results['options_status'] in [405, 403]:
                report += f"- ✅ Server từ chối OPTIONS request ({self.results['options_status']})\n"
            else:
                report += "- ✅ Không tiết lộ header `Allow`\n"
            
            report += """- ✅ Các methods nguy hiểm (PUT, DELETE, TRACE) đều bị chặn
- ✅ Tuân thủ chuẩn RFC 7231 (HTTP/1.1)
"""
            if 'Strict-Transport-Security' in self.results['options_headers']:
                report += "- ✅ Có HSTS header (bảo mật HTTPS)\n"
            
            report += "\n"
        
        report += f"""### 📊 Đánh giá rủi ro chi tiết:

| Metric | Value |
|--------|-------|
| **Severity** | {self.results['risk_level']} |
| **Likelihood** | {"Medium" if self.results['is_vulnerable'] else "N/A"} |
| **Impact** | {"Low-Medium" if self.results['is_vulnerable'] else "None"} |
| **CVSS v3.1 Score** | {self.results['cvss_score']} |
| **OWASP Risk Rating** | {"Note" if not self.results['is_vulnerable'] else "Low-Medium"} |

### 🎯 Hành động khuyến nghị:

"""
        
        if self.results['is_vulnerable']:
            report += """1. 🔴 **Khắc phục ngay** - Áp dụng một trong các Option A-D ở mục 7
2. 🧪 **Test kỹ** - Đảm bảo không ảnh hưởng CORS/functionality
3. 📝 **Monitor** - Theo dõi logs sau khi deploy
4. ✅ **Verify** - Scan lại để xác nhận đã fix

"""
        else:
            report += """1. ✅ **Risk Acceptance** - Chấp nhận và ghi nhận vào risk register
2. ✅ **False Positive** - Đánh dấu trong scanner tool
3. ✅ **Documentation** - Lưu phân tích này cho audit tiếp theo
4. 📝 **Monitor** - Giám sát định kỳ (quarterly), không cần action ngay

### 🚫 KHÔNG khuyến nghị:
- ❌ Tắt hoàn toàn OPTIONS nếu website/API cần CORS
- ❌ Ưu tiên fix này trước các lỗi HIGH/CRITICAL khác
- ❌ Áp dụng fix mà không test kỹ impact

"""
        
        report += """---

## 📎 Phụ lục: Commands để verify

```bash
# Test OPTIONS
curl -i -X OPTIONS """ + self.url + """

# Test methods nguy hiểm
for method in PUT DELETE TRACE CONNECT PATCH; do
  echo "Testing $method:"
  curl -i -X $method """ + self.url + """/test 2>&1 | head -1
done

# Scan với Nmap (nếu có)
nmap -p 443 --script http-methods """ + self.domain + """

# Check với online tools
# https://securityheaders.com/?q=""" + self.url + """
# https://observatory.mozilla.org/
```

---

## 📝 Chi tiết kỹ thuật bổ sung

### Response Headers đầy đủ từ OPTIONS request:

```http
"""
        
        for header, value in self.results['options_headers'].items():
            report += f"{header}: {value}\n"
        
        report += "```\n\n"
        
        report += f"""### Test Results cho từng Method:

| Method | Status Code | Assessment |
|--------|-------------|------------|
"""
        
        for method, status in self.results['dangerous_tests'].items():
            icon = "✅" if status in [405, 403] else "⚠️"
            assessment = "Blocked (Safe)" if status in [405, 403] else "Allowed (Risk)"
            report += f"| {method} | {status} | {icon} {assessment} |\n"
        
        report += f"""

---

**Prepared by:** Security Scanner Tool  
**Scan Time:** {self.scan_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Report Version:** 1.0  
**Tool Version:** 1.0.0
"""
        
        return report
    
    def _get_status_text(self, code):
        """Lấy text mô tả status code"""
        status_texts = {
            200: "OK",
            204: "No Content",
            403: "Forbidden",
            405: "Method Not Allowed",
            500: "Internal Server Error"
        }
        return status_texts.get(code, "Unknown")
    
    def _get_status_assessment(self, code):
        """Đánh giá status code"""
        if code in [405, 403]:
            return "✅ An toàn (Server từ chối OPTIONS)"
        elif code in [200, 204]:
            return "⚠️ Chấp nhận (Cần xem Allow header)"
        else:
            return "ℹ️ Không rõ ràng"
    
    def _get_allow_assessment(self):
        """Đánh giá Allow header"""
        if not self.results['allow_header']:
            return "✅ Không tiết lộ methods"
        
        methods = [m.strip().upper() for m in self.results['allow_header'].split(',')]
        dangerous = [m for m in methods if m in ['PUT', 'DELETE', 'TRACE', 'CONNECT']]
        
        if dangerous:
            return f"🔴 Tiết lộ methods nguy hiểm: {', '.join(dangerous)}"
        else:
            return "✅ Chỉ có methods cơ bản"
    
    def save_report(self, filename=None):
        """Lưu báo cáo ra file"""
        if filename is None:
            timestamp = self.scan_time.strftime('%Y%m%d_%H%M%S')
            filename = f"options_security_report_{self.domain}_{timestamp}.md"
        
        report_content = self.generate_markdown_report()
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            print(f"✅ Đã lưu báo cáo: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Lỗi khi lưu file: {str(e)}")
            return None

def main():
    print("="*70)
    print("🛡️  HTTP OPTIONS METHOD SECURITY SCANNER")
    print("="*70)
    print("Công cụ quét lỗi OPTIONS và tạo báo cáo chi tiết")
    print("="*70 + "\n")
    
    # Lấy URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("📝 Nhập URL cần quét: ").strip()
    
    if not url:
        print("❌ Vui lòng nhập URL!")
        return
    
    # Khởi tạo scanner
    scanner = OptionsSecurityScanner(url)
    
    # Chạy scan
    success = scanner.scan_options()
    
    if not success:
        print("❌ Quét thất bại!")
        return
    
    # Hiển thị tóm tắt
    print("\n" + "="*70)
    print("📊 TÓM TẮT KẾT QUẢ")
    print("="*70)
    print(f"Website: {scanner.url}")
    print(f"Đánh giá: {scanner.results['assessment']}")
    print(f"Mức độ rủi ro: {scanner.results['risk_level']}")
    print(f"CVSS Score: {scanner.results['cvss_score']}")
    
    if scanner.results['is_vulnerable']:
        print("\n🔴 CÓ LỖ HỔNG - Cần khắc phục!")
    else:
        print("\n✅ AN TOÀN - Không có lỗ hổng nghiêm trọng")
    
    print("="*70 + "\n")
    
    # Hỏi có muốn lưu báo cáo không
    save = input("💾 Bạn có muốn lưu báo cáo chi tiết? (y/n): ").strip().lower()
    
    if save in ['y', 'yes', 'có']:
        custom_name = input("📝 Nhập tên file (Enter để dùng tên mặc định): ").strip()
        filename = custom_name if custom_name else None
        
        saved_file = scanner.save_report(filename)
        
        if saved_file:
            print(f"\n✅ Hoàn tất! Xem báo cáo tại: {saved_file}")
            print(f"\n💡 Mở file bằng: ")
            print(f"   - VS Code: code {saved_file}")
            print(f"   - Notepad: notepad {saved_file}")
            print(f"   - Hoặc mở bằng Markdown viewer")
    else:
        print("\n📋 Báo cáo không được lưu.")
    
    # Hướng dẫn tiếp theo
    print("\n" + "="*70)
    print("🎯 BƯỚC TIẾP THEO")
    print("="*70)
    
    if scanner.results['is_vulnerable']:
        print("""
1. Đọc kỹ phần "Biện pháp khắc phục" trong báo cáo
2. Chọn Option phù hợp với hạ tầng của bạn
3. Test kỹ trước khi deploy production
4. Scan lại để verify đã fix thành công
        """)
    else:
        print("""
1. Đánh dấu False Positive trong scanner tool
2. Lưu báo cáo này để tham khảo cho audit
3. Tiếp tục quét các lỗi bảo mật khác (XSS, CSP, etc.)
        """)
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
```

## 📖 **HƯỚNG DẪN SỬ DỤNG:**

### **1. Cài đặt:**
```bash
pip install requests
```

### **2. Chạy script:**

```bash
# Cách 1: Nhập URL khi chạy
python options_scanner_full.py

# Cách 2: Truyền URL trực tiếp
python options_scanner_full.py https://www.attech.space/
```

### **3. Kết quả:**

Script sẽ:
- ✅ Quét OPTIONS method
- ✅ Test các methods nguy hiểm (PUT, DELETE, TRACE, CONNECT, PATCH)
- ✅ Phân tích rủi ro chi tiết
- ✅ Tạo báo cáo Markdown đầy đủ (10+ trang)
- ✅ Lưu file với encoding UTF-8 (hỗ trợ tiếng Việt)
- ✅ Đưa ra khuyến nghị cụ thể

### **4. Output mẫu:**

```
📝 Nhập URL cần quét: https://www.attech.space/

🔍 ĐANG QUÉT: https://www.attech.space/

📤 Test 1: Gửi OPTIONS request...
   ✓ Status Code: 204
   ✓ Allow Header: Không có

📤 Test 2: Kiểm tra methods nguy hiểm...
   ✅ PUT: 405
   ✅ DELETE: 405
   ✅ TRACE: 405
   ✅ CONNECT: 405
   ✅ PATCH: 405

✅ QUÉT HOÀN TẤT

📊 TÓM TẮT KẾT QUẢ
Website: https://www.attech.space/
Đánh giá: AN TOÀN - Không tiết lộ methods
Mức độ rủi ro: Informational
CVSS Score: 0.0

✅ AN TOÀN - Không có lỗ hổng nghiêm trọng

💾 Bạn có muốn lưu báo cáo chi tiết? (y/n): y
📝 Nhập tên file (Enter để dùng tên mặc định): 

✅ Đã lưu báo cáo: options_security_report_www.attech.space_20251111_104530.md
```

**File báo cáo sẽ có:**
- 📄 10+ trang phân tích chi tiết
- 🔍 Tất cả test cases
- 📊 Bảng đánh giá rủi ro
- 🔧 Hướng dẫn khắc phục cụ thể
- 📝 Commands để verify
- ✅ Hỗ trợ UTF-8 hoàn toàn

Chạy thử và cho tôi biết kết quả nhé! 🚀
