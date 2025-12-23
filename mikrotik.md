Ok, mình sẽ **viết lại bài này theo đúng hướng “hướng dẫn thực hiện”**, bỏ marketing, **đứng trên góc độ kỹ sư triển khai**, có **tư duy – sơ đồ logic – các bước cấu hình – lưu ý sai lầm thường gặp**.
Mình sẽ giả định **thiết bị MikroTik RouterOS v7**, quy mô **resort / khu công nghiệp vừa**, ring L3 chuẩn chỉnh.

---

# THIẾT KẾ & TRIỂN KHAI HỆ THỐNG MẠNG VÒNG (L3 RING)

## Cho Resort / Khu Công Nghiệp – MikroTik RouterOS

---

## 0️⃣ Mục tiêu thiết kế (Design Goals)

* **Không downtime khi đứt 1 tuyến cáp**
* **Tách Staff / Guest tuyệt đối**
* **Không dùng Ring L2 (tránh STP, loop, broadcast)**
* **Mỗi khu tự vận hành được khi core gặp sự cố**
* **Dễ mở rộng, dễ debug**

👉 Giải pháp: **L3 Ring + OSPF + Gateway cục bộ mỗi zone**

---

## 1️⃣ Kiến trúc tổng thể (Logical Architecture)

### 1.1 Thành phần

**Core**

* 01 Firewall (FortiGate / RouterOS cũng được)
* 02 Router Core (MikroTik CCR – có thể HA bằng VRRP)

**Zone (A / B / C / …)**

* Mỗi zone:

  * 01 Router L3 (CCR / RB5009)
  * 01 Switch PoE
  * AP / User

---

### 1.2 Nguyên tắc quan trọng

❌ Không kéo VLAN L2 xuyên ring
✅ Ring **chỉ chạy Layer 3 (routing)**
✅ Mỗi zone **1 subnet riêng**

---

## 2️⃣ Quy hoạch IP (IP Planning – cực kỳ quan trọng)

### 2.1 IP cho link ring (inter-router)

Dùng subnet nhỏ để tránh lãng phí & dễ quản lý.

| Link            | IP            |
| --------------- | ------------- |
| Core ↔ Zone A   | 10.255.0.0/31 |
| Zone A ↔ Zone B | 10.255.0.2/31 |
| Zone B ↔ Zone C | 10.255.0.4/31 |
| Zone C ↔ Core   | 10.255.0.6/31 |

👉 /31 đủ cho point-to-point, RouterOS v7 hỗ trợ tốt.

---

### 2.2 IP LAN cho mỗi Zone

| Zone | Staff         | Guest         |
| ---- | ------------- | ------------- |
| A    | 10.10.10.0/24 | 10.20.10.0/24 |
| B    | 10.10.20.0/24 | 10.20.20.0/24 |
| C    | 10.10.30.0/24 | 10.20.30.0/24 |

👉 **Mỗi zone khác subnet**, dễ routing, dễ firewall.

---

## 3️⃣ Cấu hình Ring L3 bằng OSPF (khuyến nghị)

> ❗ Không dùng RIP trong triển khai thực tế

---

### 3.1 Cấu hình IP cho link ring (ví dụ Zone A)

```bash
/ip address
add address=10.255.0.1/31 interface=to-core
add address=10.255.0.3/31 interface=to-zone-b
```

---

### 3.2 Bật OSPF (RouterOS v7)

```bash
/routing ospf instance
add name=ospf-core router-id=1.1.1.1
```

Zone A:

```bash
/routing ospf interface-template
add interfaces=to-core area=backbone
add interfaces=to-zone-b area=backbone
```

---

### 3.3 Quảng bá mạng LAN zone

```bash
/routing ospf interface-template
add networks=10.10.10.0/24 area=backbone
add networks=10.20.10.0/24 area=backbone
```

👉 Core sẽ **tự học route**, không cần static.

---

## 4️⃣ Cơ chế dự phòng khi đứt cáp (Ring Failover)

### Tình huống

* Đứt link Zone A ↔ Zone B

### Điều gì xảy ra?

* OSPF phát hiện link down
* Recalculate SPF
* Traffic từ Zone A → Core → Zone C → Zone B

⏱ Thời gian hội tụ:

* OSPF mặc định: ~5–10s
* Có BFD: <1s

---

### (Khuyến nghị) Bật BFD

```bash
/routing bfd interface
add interface=to-core
add interface=to-zone-b
```

---

## 5️⃣ Cấu hình Gateway + DHCP tại Zone

### 5.1 VLAN tại Zone

| VLAN | Mục đích |
| ---- | -------- |
| 10   | Staff    |
| 20   | Guest    |

---

### 5.2 DHCP

```bash
/ip pool
add name=staff-a ranges=10.10.10.100-10.10.10.200
add name=guest-a ranges=10.20.10.100-10.20.10.200

/ip dhcp-server
add name=dhcp-staff interface=vlan10 address-pool=staff-a
add name=dhcp-guest interface=vlan20 address-pool=guest-a
```

---

## 6️⃣ Tách Staff / Guest (Firewall Rules)

### 6.1 Guest **chỉ ra Internet**

```bash
/ip firewall filter
add chain=forward src-address=10.20.0.0/16 dst-address=10.10.0.0/16 action=drop
```

---

### 6.2 Guest không vào thiết bị quản trị

```bash
add chain=input src-address=10.20.0.0/16 action=drop
```

---

## 7️⃣ NAT & Internet Gateway

### Phương án chuẩn

* NAT đặt **tại Core / Firewall**
* Zone **KHÔNG NAT**

```bash
/ip firewall nat
add chain=srcnat src-address=10.0.0.0/8 out-interface=wan action=masquerade
```

---

## 8️⃣ High Availability (nếu cần)

### 8.1 Core Router HA

* 2 CCR
* VRRP cho gateway LAN

```bash
/interface vrrp
add interface=bridge-lan vrid=1 priority=110 virtual-address=10.10.0.1
```

---

### 8.2 Firewall HA

* FortiGate HA
* Sync policy + session

---

## 9️⃣ Những sai lầm cần TRÁNH

❌ Kéo VLAN xuyên ring
❌ Dùng RIP cho hệ > 3 router
❌ Đặt NAT rải rác nhiều zone
❌ Không chuẩn hóa IP plan
❌ Không test failover trước nghiệm thu

---

## 🔚 Kết luận

Mô hình **L3 Ring + OSPF + Gateway cục bộ**:

* Phù hợp resort / khu CN phân tán
* Dễ vận hành
* Chịu lỗi tốt
* Không phụ thuộc STP

Nếu làm đúng, hệ thống:

* Đứt 1 link **không mất mạng**
* Core chết → **zone vẫn chạy LAN**
* Mở rộng thêm zone **chỉ cần cắm vào ring**

---

Nếu bạn muốn, mình có thể:

* 📐 Vẽ **sơ đồ logic + vật lý**
* 🔍 Viết **checklist nghiệm thu**
* 🧪 Hướng dẫn **test đứt cáp / failover**
* ⚖️ So sánh **Ring L3 vs Spine–Leaf**

Bạn muốn đào sâu tiếp phần nào?
