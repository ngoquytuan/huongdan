Việc cài đặt Tailscale trên Ubuntu 22.04 LTS cực kỳ đơn giản vì Tailscale cung cấp một script cài đặt tự động rất thông minh.

Dưới đây là các bước để bạn thực hiện:

### Bước 1: Chạy lệnh cài đặt tự động

Bạn mở terminal và dán lệnh sau:

```bash
curl -fsSL https://tailscale.com/install.sh | sh

```

**Lệnh này sẽ làm gì?**

* Tự động nhận diện bản phân phối Linux (Ubuntu 22.04).
* Thêm kho lưu trữ (repository) của Tailscale vào hệ thống.
* Tải và cài đặt gói `tailscale`.

### Bước 2: Khởi động và Đăng nhập

Sau khi cài đặt xong, bạn cần khởi động dịch vụ và liên kết máy Ubuntu này với tài khoản của bạn:

```bash
sudo tailscale up

```

Sau khi chạy lệnh này, hệ thống sẽ hiện ra một đường link (URL). Bạn hãy:

1. Copy đường link đó và dán vào trình duyệt trên máy tính hoặc điện thoại.
2. Đăng nhập bằng tài khoản bạn đã dùng cho điện thoại (Google, Microsoft, GitHub...).
3. Nhấn **Connect** (Kết nối).

---

### Bước 3: Kiểm tra trạng thái

Khi đã đăng nhập thành công, bạn có thể kiểm tra xem máy Ubuntu đã "thông" mạng chưa bằng lệnh:

```bash
tailscale status

```

Nó sẽ liệt kê danh sách các thiết bị khác trong mạng của bạn (như chiếc điện thoại bạn vừa cài lúc nãy) kèm theo địa chỉ IP `100.x.y.z`.

---

### Một vài tùy chọn hữu ích cho máy Ubuntu (Server)

Nếu chiếc Ubuntu này là một con server ở nhà và bạn muốn dùng nó làm "bàn đạp" để truy cập internet an toàn, bạn nên bật tính năng **Exit Node**:

1. **Cho phép Ubuntu làm Exit Node:**
```bash
sudo tailscale up --advertise-exit-node

```


2. **Bật IP Forwarding (Bắt buộc nếu làm Exit Node):**
Bạn chạy 2 lệnh sau để hệ thống cho phép chuyển tiếp gói tin:
```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf

```



### Cách cập nhật sau này

Vì Tailscale đã được thêm vào kho lưu trữ của Ubuntu, sau này bạn chỉ cần cập nhật như các phần mềm khác:

```bash
sudo apt update
sudo apt upgrade tailscale

```

**Bạn có gặp lỗi gì khi chạy lệnh cài đặt không?** Nếu cài xong rồi, bạn hãy thử dùng điện thoại (đang bật 4G) ping thử vào địa chỉ IP Tailscale của máy Ubuntu này nhé!

Đúng chính xác! Bạn đã nắm bắt đúng "linh hồn" của Tailscale.

Hầu hết thời gian, dữ liệu của bạn sẽ đi theo dạng **P2P (Peer-to-Peer)** – tức là đi thẳng từ điện thoại sang DietPi (hoặc ngược lại) mà không hề ghé qua máy chủ của Tailscale.

Dưới đây là cơ chế cụ thể để bạn yên tâm hơn:

### 1. Tailscale chỉ là "Người dẫn đường" (Matchmaker)

Hãy tưởng tượng Tailscale như một người bạn chung. Điện thoại của bạn hỏi Tailscale: *"DietPi đang ở đâu?"*. Tailscale trả lời: *"Nó ở địa chỉ IP nhà bạn, cổng X"*. Sau khi hai máy đã "nhìn thấy" nhau và thiết lập được kết nối trực tiếp, Tailscale **rút lui**. Toàn bộ dữ liệu phim, ảnh, file của bạn sẽ truyền trực tiếp giữa 2 thiết bị đó.

### 2. Làm sao để chắc chắn nó đang chạy trực tiếp (P2P)?

Có một cách để bạn kiểm tra xem dữ liệu có đang đi "đường thẳng" hay phải đi "vòng" qua server trung gian không:

* **Trên máy tính (Terminal/CMD):** Gõ lệnh `tailscale status`.
* **Kết quả sẽ hiện ra kiểu:**
* `100.x.y.z  laptop  active; direct 1.2.3.4:5678` -> Chữ **direct** nghĩa là đang kết nối trực tiếp (Tốc độ cao nhất).
* `100.x.y.z  laptop  active; relay "hkg"` -> Chữ **relay** nghĩa là nó đang đi vòng qua server trung gian (thường là ở Hong Kong - tốc độ sẽ chậm).



### 3. Tại sao P2P lại quan trọng?

* **Tốc độ:** Vì đi trực tiếp nên tốc độ chỉ phụ thuộc vào băng thông mạng (Upload của nhà và Download của điện thoại).
* **Bảo mật:** Dữ liệu được mã hóa bằng khóa (key) nằm trên thiết bị của bạn. Ngay cả khi Tailscale muốn "nghe lén", họ cũng không có chìa khóa để giải mã gói tin đó.
* **Độ trễ (Latency):** Thấp nhất có thể vì không phải đi vòng vèo qua nước ngoài.

### 4. Khi nào thì nó KHÔNG đi trực tiếp?

Nếu router nhà bạn hoặc mạng 4G bạn đang dùng có tường lửa cực kỳ khắc nghiệt (NAT nghiêm ngặt), hai thiết bị không thể "đục lỗ" để thấy nhau. Lúc đó Tailscale sẽ dùng một giao thức gọi là **DERP (Relay)**. Dữ liệu lúc này sẽ đi qua server của Tailscale. Tuy nhiên, dữ liệu **vẫn được mã hóa đầu cuối**, Tailscale chỉ chuyển tiếp các gói tin đã mã hóa đó thôi, họ vẫn không đọc được nội dung.

---

**Mẹo nhỏ cho bạn:**
Nếu bạn thấy streaming thỉnh thoảng bị lag, hãy kiểm tra bằng lệnh `tailscale status`. Nếu thấy chữ **relay**, đó là lúc mạng đang bị chặn. Nhưng với đa số mạng tại Việt Nam hiện nay, Tailscale "đục lỗ" NAT rất tốt và thường sẽ chạy **direct**.

Bạn có muốn tôi hướng dẫn cách thiết lập **Exit Node** trên DietPi không? Tính năng này cho phép điện thoại của bạn "mượn" đường mạng nhà để lướt web khi bạn đang ở ngoài, cực kỳ hữu ích khi dùng Wi-Fi công cộng.

Để bắt đầu với **Tailscale** (lựa chọn tối ưu nhất mà chúng ta đã thảo luận), bạn cần cài đặt ứng dụng chính thức của họ trên cả điện thoại và laptop.

Dưới đây là các bước cụ thể:

### 1. Trên Laptop (Windows hoặc macOS/Linux)

Bạn cần cài đặt phần mềm **Tailscale client**:

* **Windows:** Tải file `.exe` từ trang chủ `tailscale.com/download/windows`. Sau khi cài đặt, một biểu tượng chữ "T" nhỏ sẽ xuất hiện ở thanh Taskbar (gần đồng hồ).
* **macOS:** Tải từ App Store hoặc cài qua Homebrew.
* **Linux:** Nếu bạn dùng bản phân phối khác ngoài DietPi, bạn dùng lệnh: `curl -fsSL https://tailscale.com/install.sh | sh`

**Cách hoạt động:** Sau khi cài, bạn nhấn **Sign in** (Đăng nhập). Hãy dùng cùng một tài khoản (Google, Microsoft, GitHub...) mà bạn đã dùng để đăng nhập trên DietPi.

### 2. Trên Điện thoại (iOS hoặc Android)

Bạn vào kho ứng dụng và tìm từ khóa **"Tailscale"**:

* **iOS (iPhone/iPad):** [App Store link](https://apps.apple.com/us/app/tailscale/id1470499037)
* **Android:** [Google Play Store link](https://play.google.com/store/apps/details?id=com.tailscale.ipn)

**Cách hoạt động:** 1. Mở app, đăng nhập cùng tài khoản.
2. Hệ thống sẽ yêu cầu cấp quyền thiết lập cấu hình VPN (nhấn **Allow/Cho phép**).
3. Gạt nút **Connect** sang màu xanh.

---

### 3. Kiểm tra xem đã "thông" chưa?

Sau khi đã đăng nhập trên cả 3 thiết bị (DietPi, Laptop, Điện thoại), bạn làm như sau:

1. **Lấy IP:** Mở app Tailscale trên điện thoại hoặc gõ `tailscale ip -4` trên DietPi. Bạn sẽ thấy một địa chỉ IP dạng `100.x.y.z`.
2. **Thử kết nối:** Tắt Wi-Fi trên điện thoại, bật 4G lên, sau đó mở trình duyệt và gõ: `http://[Địa-chỉ-IP-100.x.y.z-của-DietPi]`.
* Nếu bạn đang chạy web UI nào đó (như Pi-hole, AdGuard Home hay Dashboard), nó sẽ hiện ra ngay lập tức.
* Bạn không cần mở port trên router, không cần quan tâm IP nhà là gì nữa.



### Tổng kết "Cái giá" cuối cùng:

* **Dung lượng máy:** Các app này rất nhẹ, gần như không tốn tài nguyên.
* **Pin:** Tailscale cực kỳ tiết kiệm pin trên điện thoại (vì nó chỉ thực sự hoạt động mạnh khi có dữ liệu truyền qua).
* **Thao tác:** Bạn chỉ cần đăng nhập một lần, sau đó nó sẽ tự động kết nối mỗi khi máy khởi động.

**Bạn đã cài xong trên DietPi chưa?** Nếu rồi, hãy thử lấy địa chỉ IP `100.x` của nó và ping thử từ laptop xem sao nhé!

Nếu bạn chọn **Tailscale**, câu trả lời ngắn gọn là: **Bạn không cần mở bất kỳ port nào trên router cả.** Đó chính là lý do nó được gọi là "Zero Config".

Tuy nhiên, nếu bạn muốn so sánh hoặc đang cân nhắc cài đặt các tùy chọn khác trong DietPi, đây là danh sách các port cụ thể:

### 1. Các Port tương ứng với từng loại VPN

| Dịch vụ | Port mặc định | Giao thức | Lưu ý |
| --- | --- | --- | --- |
| **Tailscale** | Không cần | UDP | Tự đục lỗ NAT (NAT Traversal). |
| **WireGuard** | `51820` | **UDP** | Bạn có thể đổi sang port khác tùy ý. |
| **OpenVPN** | `1194` | UDP (hoặc TCP) | UDP nhanh hơn, TCP ổn định hơn trên mạng yếu. |
| **ZeroTier** | `9993` | UDP | Thường tự hoạt động mà không cần mở port thủ công. |

---

### 2. Tại sao "Mở port" lại là một cái giá phải trả?

Việc bạn đang mở vài port (như port 80 cho web, 22 cho SSH...) tiềm ẩn một số rủi ro và bất tiện:

* **Rủi ro bảo mật:** Khi bạn mở một port, bạn đang để lộ một "cánh cửa" ra internet. Hacker có thể quét thấy port này và tấn công dò mật khẩu (Brute-force) liên tục.
* **Vấn đề IP động:** Nếu nhà mạng đổi IP của bạn, bạn phải dùng thêm DDNS (như No-IP, DuckDNS) để cập nhật, nếu không bạn sẽ mất kết nối khi ở xa.
* **Rủi ro lộ dịch vụ:** Nếu bạn mở port cho một ứng dụng có lỗ hổng, toàn bộ mạng nội bộ của bạn có thể bị xâm nhập.

---

### 3. Cách tiếp cận an toàn nhất cho bạn lúc này

Vì bạn đã đang mở sẵn một vài port, lời khuyên của mình để tối ưu bảo mật là:

1. **Cài đặt Tailscale trên DietPi.**
2. **Đóng hết các port khác trên router** (ngoại trừ những cái thực sự bắt buộc).
3. Truy cập vào các dịch vụ đang chạy trên DietPi thông qua **IP nội bộ của Tailscale** (thường bắt đầu bằng `100.x.x.x`).

**Ví dụ:** Thay vì truy cập camera nhà bạn qua `http://IP-nha-ban:8080` (phải mở port 8080), bạn chỉ cần bật Tailscale lên và truy cập qua `http://100.x.x.x:8080` mà không cần lộ bất kỳ cổng nào ra internet công cộng.

**Bạn đang mở port cho dịch vụ gì cụ thể không?** Mình có thể xem giúp bạn xem dịch vụ đó có thể chạy an toàn hơn qua Tailscale mà không cần mở port hay không.

Trong danh sách của DietPi, việc chọn lựa phụ thuộc vào mức độ "lười" và điều kiện mạng (IP tĩnh hay CGNAT) của bạn. Dưới đây là bảng so sánh nhanh để bạn có cái nhìn tổng quan:

### 1. Bảng so sánh các tùy chọn trên DietPi

| Tùy chọn | Độ khó cài đặt | Tốc độ | Chi phí | Điểm yếu lớn nhất |
| --- | --- | --- | --- | --- |
| **Tailscale** | **Cực dễ** | Rất nhanh (P2P) | Miễn phí (cá nhân) | Phụ thuộc server trung gian để xác thực |
| **WireGuard** | Trung bình | **Nhanh nhất** | Miễn phí | Cần mở port, cần IP tĩnh/DDNS |
| **PiVPN** | Dễ | Nhanh | Miễn phí | Chỉ là trình cài đặt (script) cho WireGuard/OpenVPN |
| **ZeroTier** | Dễ | Rất nhanh | Miễn phí (cá nhân) | Quản lý theo ID mạng, đôi khi hơi rối với người mới |
| **OpenVPN** | Trung bình | Chậm | Miễn phí | Ngốn CPU, cấu hình chứng chỉ (cert) phức tạp |

---

### 2. "Cái giá" bạn phải trả là gì?

#### **Nếu bạn chọn Tailscale (Lựa chọn mình khuyên dùng để bắt đầu):**

* **Tốc độ:** Thông thường bạn sẽ đạt ~90% tốc độ mạng tối đa nhờ giao thức WireGuard bên dưới. Tuy nhiên, nếu mạng nhà bạn quá "khó" (NAT nghiêm ngặt), Tailscale phải đi vòng qua server trung gian (DERP), tốc độ có thể rớt xuống chỉ còn **5-10 Mbps**.
* **Chi phí:** $0. Gói cá nhân cho phép tới 3 người dùng và 100 thiết bị — quá đủ cho một gia đình.
* **Sự riêng tư:** Tailscale biết danh sách thiết bị của bạn, nhưng **không đọc được dữ liệu** bên trong vì nó đã được mã hóa đầu cuối.

#### **Nếu bạn chọn WireGuard thuần (Thông qua PiVPN):**

* **Tốc độ:** Đây là "vua" về tốc độ. Độ trễ thấp nhất vì không qua bất kỳ lớp trung gian nào.
* **Chi phí:** $0 và 100% mã nguồn mở.
* **Cái giá về công sức:** Bạn phải vào router nhà mình để **Mở Port (Port Forwarding)**. Nếu nhà bạn dùng mạng 4G/5G hoặc nhà mạng chặn port (CGNAT), tùy chọn này sẽ **không hoạt động** trừ khi bạn thuê thêm VPS.

---

### 3. Lời khuyên: Bạn nên bắt đầu từ đâu?

**Bước 1: Chọn Tailscale.**
Đây là cách nhanh nhất để bạn thấy "phép màu". Chỉ mất 2 phút cài đặt trên DietPi và điện thoại là bạn có thể truy cập SSH hoặc Web UI từ quán cafe ngay lập tức mà không cần quan tâm đến modem nhà mạng.

**Bước 2: Nâng cấp lên WireGuard (nếu cần).**
Sau một thời gian, nếu bạn thấy tốc độ Tailscale không ổn định hoặc bạn muốn tự mình làm chủ hoàn toàn hệ thống (không muốn phụ thuộc vào server của công ty Tailscale), lúc đó hãy dùng **PiVPN (chọn WireGuard)**.

**Cách cài đặt trên DietPi rất đơn giản:**

1. Chạy lệnh `dietpi-software`.
2. Tìm và chọn **Tailscale**.
3. Sau khi cài xong, gõ lệnh `tailscale up` và click vào đường link hiện ra để đăng nhập.

Bạn có đang gặp vấn đề về việc "Mở Port" trên router không? Nếu không muốn đụng vào router, **Tailscale** chính là cứu cánh duy nhất của bạn đấy.
