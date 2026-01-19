Sử dụng **tmux** để chạy nhiều script cùng lúc là một lựa chọn rất thông minh. Thay vì phải mở nhiều kết nối SSH, bạn có thể chia màn hình terminal ra thành nhiều ô (panes) hoặc nhiều cửa sổ (windows) khác nhau ngay trong một phiên làm việc.

Dưới đây là cách bạn có thể chạy 2 hoặc nhiều script song song với tmux:

---

## 1. Cách chia màn hình (Split Panes)

Cách này giúp bạn quan sát cả 2 script đang chạy cùng một lúc trên một màn hình duy nhất.

1. **Mở tmux:** Gõ lệnh `tmux`.
2. **Chạy script thứ nhất:** Gõ `python3 script1.py`.
3. **Chia đôi màn hình:**
* Chia dọc: Nhấn `Ctrl + B`, sau đó nhấn phím `%`.
* Chia ngang: Nhấn `Ctrl + B`, sau đó nhấn phím `"`.


4. **Chuyển sang ô mới:** Nhấn `Ctrl + B`, sau đó dùng các **phím mũi tên** để di chuyển giữa các ô.
5. **Chạy script thứ hai:** Tại ô mới, gõ `python3 script2.py`.

---

## 2. Cách dùng nhiều cửa sổ (Multiple Windows)

Nếu code của bạn xuất ra quá nhiều log và việc chia nhỏ màn hình làm bạn khó nhìn, hãy dùng cơ chế "Cửa sổ" (giống như các tab trên trình duyệt).

1. **Tạo cửa sổ thứ nhất:** Chạy `python3 script1.py`.
2. **Tạo cửa sổ mới:** Nhấn `Ctrl + B`, sau đó nhấn phím `C` (Create). Bạn sẽ có một màn hình trống hoàn toàn.
3. **Chạy script thứ hai:** Tại đây, gõ `python3 script2.py`.
4. **Di chuyển giữa các cửa sổ:** * `Ctrl + B`, sau đó nhấn `N` (Next) để sang cửa sổ tiếp theo.
* `Ctrl + B`, sau đó nhấn `P` (Previous) để về cửa sổ trước đó.
* `Ctrl + B`, sau đó nhấn số hiệu cửa sổ (ví dụ `0`, `1`, `2`).



---

## 3. Các lệnh điều khiển cần nhớ

Để quản lý hiệu quả, bạn nên nhớ các tổ hợp phím sau (Luôn bắt đầu bằng **`Ctrl + B`**):

| Thao tác | Phím tắt (sau Ctrl+B) |
| --- | --- |
| **Thoát tạm thời (Detach)** | `D` (Script vẫn chạy ngầm) |
| **Chia màn hình dọc** | `%` |
| **Chia màn hình ngang** | `"` |
| **Tạo cửa sổ mới** | `C` |
| **Đóng ô hiện tại** | Gõ `exit` hoặc `Ctrl + D` |
| **Quay lại phiên cũ** | (Lệnh ngoài terminal) `tmux attach` |

---

## 4. Mẹo nhỏ: Đặt tên cho phiên làm việc

Khi bạn chạy nhiều dự án, thay vì chỉ gõ `tmux`, bạn hãy đặt tên để dễ quản lý:

* Khởi tạo: `tmux new -s my_project`
* Khi muốn quay lại đúng dự án đó: `tmux attach -t my_project`

Việc này giúp bạn không bị nhầm lẫn giữa các script khác nhau khi làm việc lâu dài trên server.

Bạn có muốn tôi hướng dẫn cách cài đặt một "Dashboard" trong terminal (như **htop**) để bạn vừa chạy script vừa theo dõi được nhiệt độ và RAM của máy Debian không?

Chào bạn, đây là một câu hỏi rất phổ biến khi mới làm việc với server Linux.

Câu trả lời ngắn gọn là: **Nếu bạn chỉ chạy lệnh `python3 my.py` thông thường, script sẽ bị dừng ngay khi bạn đóng kết nối SSH.**

Lý do là vì khi bạn thoát SSH, terminal sẽ gửi một tín hiệu gọi là `SIGHUP` (Signal Hang Up) đến tất cả các tiến trình đang chạy trong phiên làm việc đó, khiến chúng dừng lại.

Dưới đây là các cách để giữ script chạy ngầm và cách quản lý chúng:

---

## 1. Cách chạy script vẫn tiếp tục khi đóng SSH

Có 3 cách phổ biến nhất từ đơn giản đến chuyên nghiệp:

### Cách 1: Dùng lệnh `nohup` (Đơn giản nhất)

`nohup` (no hang up) sẽ bỏ qua tín hiệu ngắt kết nối.

* **Lệnh:** `nohup python3 my.py &`
* **Tác dụng:** Dấu `&` đưa script vào chạy nền (background). Toàn bộ kết quả xuất ra (output) sẽ được lưu vào file `nohup.out`.

### Cách 2: Dùng `Screen` hoặc `Tmux` (Khuyên dùng)

Đây là các "trình quản lý phiên làm việc". Bạn có thể mở một cửa sổ ảo, chạy script, rồi "rời khỏi" (detach) cửa sổ đó. Script vẫn chạy bình thường, và bạn có thể quay lại xem bất cứ lúc nào.

* **Cài đặt:** `sudo apt update && sudo apt install tmux`
* **Sử dụng với Tmux:**
1. Gõ `tmux` để mở phiên mới.
2. Chạy script: `python3 my.py`.
3. Nhấn tổ hợp phím `Ctrl + B`, sau đó nhấn `D` để thoát ra ngoài (script vẫn chạy).
4. Khi muốn quay lại: Gõ `tmux attach`.



### Cách 3: Chạy như một Service (Chuyên nghiệp)

Nếu đây là script quan trọng (như bot telegram, web server), bạn nên tạo một file `.service` trong `systemd`. Cách này giúp script tự khởi động lại nếu máy chủ bị reboot hoặc script bị crash.

---

## 2. Cách tìm và dừng script đang chạy ngầm

Nếu bạn đã lỡ chạy ngầm và muốn dừng nó, bạn cần tìm **Process ID (PID)** của nó.

### Bước 1: Tìm PID

Sử dụng lệnh `ps` hoặc `pgrep`:

* `ps aux | grep python3`: Liệt kê tất cả tiến trình python đang chạy.
* Hoặc cụ thể hơn: `pgrep -f my.py` (Lệnh này sẽ trả về ngay con số PID).

### Bước 2: Dừng tiến trình

Sử dụng lệnh `kill` kèm theo số PID bạn vừa tìm được:

* `kill PID_NUMBER` (Ví dụ: `kill 1234`)
* Nếu script "lì lợm" không chịu dừng: `kill -9 1234`

---

**Tóm tắt các lệnh cần nhớ:**

| Mục đích | Lệnh |
| --- | --- |
| **Chạy ngầm nhanh** | `nohup python3 my.py &` |
| **Xem các tiến trình python** | `ps aux |
| **Dừng tiến trình** | `kill [PID]` |
| **Công cụ quản lý tốt nhất** | `tmux` |

Bạn có muốn tôi hướng dẫn chi tiết cách tạo một **systemd service** để script của bạn tự động chạy mỗi khi bật máy Debian không?

Sử dụng **tmux** để chạy nhiều script cùng lúc là một lựa chọn rất thông minh. Thay vì phải mở nhiều kết nối SSH, bạn có thể chia màn hình terminal ra thành nhiều ô (panes) hoặc nhiều cửa sổ (windows) khác nhau ngay trong một phiên làm việc.

Dưới đây là cách bạn có thể chạy 2 hoặc nhiều script song song với tmux:

---

## 1. Cách chia màn hình (Split Panes)

Cách này giúp bạn quan sát cả 2 script đang chạy cùng một lúc trên một màn hình duy nhất.

1. **Mở tmux:** Gõ lệnh `tmux`.
2. **Chạy script thứ nhất:** Gõ `python3 script1.py`.
3. **Chia đôi màn hình:**
* Chia dọc: Nhấn `Ctrl + B`, sau đó nhấn phím `%`.
* Chia ngang: Nhấn `Ctrl + B`, sau đó nhấn phím `"`.


4. **Chuyển sang ô mới:** Nhấn `Ctrl + B`, sau đó dùng các **phím mũi tên** để di chuyển giữa các ô.
5. **Chạy script thứ hai:** Tại ô mới, gõ `python3 script2.py`.

---

## 2. Cách dùng nhiều cửa sổ (Multiple Windows)

Nếu code của bạn xuất ra quá nhiều log và việc chia nhỏ màn hình làm bạn khó nhìn, hãy dùng cơ chế "Cửa sổ" (giống như các tab trên trình duyệt).

1. **Tạo cửa sổ thứ nhất:** Chạy `python3 script1.py`.
2. **Tạo cửa sổ mới:** Nhấn `Ctrl + B`, sau đó nhấn phím `C` (Create). Bạn sẽ có một màn hình trống hoàn toàn.
3. **Chạy script thứ hai:** Tại đây, gõ `python3 script2.py`.
4. **Di chuyển giữa các cửa sổ:** * `Ctrl + B`, sau đó nhấn `N` (Next) để sang cửa sổ tiếp theo.
* `Ctrl + B`, sau đó nhấn `P` (Previous) để về cửa sổ trước đó.
* `Ctrl + B`, sau đó nhấn số hiệu cửa sổ (ví dụ `0`, `1`, `2`).



---

## 3. Các lệnh điều khiển cần nhớ

Để quản lý hiệu quả, bạn nên nhớ các tổ hợp phím sau (Luôn bắt đầu bằng **`Ctrl + B`**):

| Thao tác | Phím tắt (sau Ctrl+B) |
| --- | --- |
| **Thoát tạm thời (Detach)** | `D` (Script vẫn chạy ngầm) |
| **Chia màn hình dọc** | `%` |
| **Chia màn hình ngang** | `"` |
| **Tạo cửa sổ mới** | `C` |
| **Đóng ô hiện tại** | Gõ `exit` hoặc `Ctrl + D` |
| **Quay lại phiên cũ** | (Lệnh ngoài terminal) `tmux attach` |

---

## 4. Mẹo nhỏ: Đặt tên cho phiên làm việc

Khi bạn chạy nhiều dự án, thay vì chỉ gõ `tmux`, bạn hãy đặt tên để dễ quản lý:

* Khởi tạo: `tmux new -s my_project`
* Khi muốn quay lại đúng dự án đó: `tmux attach -t my_project`

Việc này giúp bạn không bị nhầm lẫn giữa các script khác nhau khi làm việc lâu dài trên server.

Bạn có muốn tôi hướng dẫn cách cài đặt một "Dashboard" trong terminal (như **htop**) để bạn vừa chạy script vừa theo dõi được nhiệt độ và RAM của máy Debian không?
