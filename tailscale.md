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
