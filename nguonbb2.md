Dưới đây là **Bản Yêu cầu Thiết kế Kỹ thuật (Design Specification Sheet)** cho **bộ nguồn/driver biển báo LED sân bay 100W** theo đúng khung bạn đưa ra, và mình “neo” các điểm bắt buộc bằng yêu cầu trong **FAA AC 150/5345-44L** + **FAA EB 67D** + tham chiếu **EASA/ICAO (CS-ADR-DSN Chapter U)**.

> Ghi chú quan trọng: FAA phân loại biển theo **Style**. Nếu bạn làm “series circuit 2.8–6.6A” thì đang nhắm vào **Style 3** (2.8–6.6A) hoặc một số trường hợp **Style 2** (4.8–6.6A). AC ghi rõ Style 3 = 2.8–6.6A. ([Cục Hàng không Liên bang][1])

---

## 📋 Bản Yêu cầu Thiết kế Bộ nguồn Biển báo LED (100W) – CCR Series 2.8–6.6A

### 1) Thông số Đầu vào (Input Specifications)

**1.1 Loại mạch & nguồn cấp**

* **Loại mạch:** Airport **Series Lighting Circuit** điều khiển bởi **CCR** (constant current regulator).
* **Dải dòng điện hoạt động (RMS):** **2.8–6.6 A**, **50/60 Hz** (tương thích **Style 3**). ([Cục Hàng không Liên bang][1])
* **Yêu cầu hành vi theo CCR steps:** Bộ nguồn phải hoạt động ổn định tại mọi “brightness steps” của CCR và không gây biến dạng vận hành. AC yêu cầu vận hành/kiểm tra ở mọi bước CCR. ([Cục Hàng không Liên bang][1])

**1.2 Biến áp cách ly / điểm đo tiêu chuẩn**

* **Mặc định hệ FAA:** đo kiểm **power factor tại primary của isolation transformer**. ([Cục Hàng không Liên bang][1])
* Với mạch **20A**, FAA khuyến nghị dùng **isolation transformer secondary 6.6A** phù hợp. ([Cục Hàng không Liên bang][1])
  ➡️ Vì vậy, nếu mục tiêu là “đúng hệ sân bay/FAA”, kiến trúc nên **tương thích mô hình có biến áp cách ly** (L-830/L-831/L-832 tùy hệ thống), và thiết kế của bạn phải “đẹp” khi nhìn từ **primary**.

**1.3 Kết nối vật lý (đề xuất thiết kế công nghiệp)**

* Dây dẫn: **AWG 12** (khuyến nghị thực hành để giảm tổn hao và tăng độ bền cơ học; AC không bắt buộc cỡ AWG trong đoạn mình trích).
* **Cách điện (insulation) tối thiểu:** **≥ 1000 V** (đặt mục tiêu phù hợp bối cảnh: tiêu chuẩn surge test tham chiếu IEEE/thiết bị “low-voltage 1000 V and less”). ([Cục Hàng không Liên bang][1])
* Jack kết nối: **L-823 2-pin** (chuẩn hệ airfield series circuit – đây là yêu cầu thực tế triển khai; AC 44L chủ yếu mô tả yêu cầu sign và test, còn loại connector thường nằm trong tiêu chuẩn phần cứng liên quan L-823/L-830/L-831).

---

### 2) Kiến trúc Chuyển đổi Năng lượng (Power Topology)

**2.1 Công nghệ cốt lõi**

* **Front-end:** chỉnh lưu + lọc + bảo vệ surge/EMI.
* **Power stage:** **Boost Converter** tạo DC bus để cấp cho tầng điều khiển dòng LED (hợp lý với mục tiêu “boost”).
* **Current regulation stage:** CC (constant-current) output cho chuỗi LED (có thể là buck từ DC bus, hoặc điều khiển dòng trực tiếp tùy kiến trúc).

**2.2 Điều khiển – khuyến nghị theo chuẩn FAA**
Bạn đưa “DSP” là hướng tốt, nhưng có 1 ràng buộc cực quan trọng từ FAA EB 67D:

* Với ứng dụng series circuit, **độ sáng phải thay đổi theo dòng CCR** và **“phải theo đường cong liên tục, không được nhảy theo step rời rạc”**. ([Cục Hàng không Liên bang][2])

➡️ Vì vậy:

* **Được dùng DSP** (nếu bạn muốn), nhưng thuật toán phải đảm bảo **output light intensity là hàm liên tục của I_in** (hoặc ít nhất không tạo “bậc” do xử lý số).
* Nếu không dùng DSP, vẫn OK nếu mạch analog đạt được hành vi “continuous curve” tự nhiên.

**2.3 Hệ số công suất (PF) – yêu cầu bắt buộc**

* **True PF (không phải cosφ) ≥ 0.7**
* **Đo tại primary isolation transformer**, và **phải đạt trên mọi CCR current steps**. ([Cục Hàng không Liên bang][1])
* Băng thông đo PF tối thiểu **100 kHz**, nguồn test **pure sine wave**, crest factor < 1.7 (đây là điều kiện test). ([Cục Hàng không Liên bang][1])

**2.4 Hiệu suất chuyển đổi (Efficiency)**

* **Mục tiêu nội bộ (design goal):** ≥ **88–92%** tại 100W (không phải “bắt buộc FAA” trong đoạn trích, nhưng là mức hợp lý để giảm nhiệt trong encapsulation/IP67).

---

### 3) Thông số Đầu ra và Điều khiển (Output & Control)

**3.1 Công suất định mức**

* **P_rated:** **100 W continuous** (theo mục tiêu bạn đặt).

**3.2 Đặc tính dòng ra**

* **Output mode:** constant-current DC cho LED string.
* **Ripple dòng LED:** mục tiêu thấp (ví dụ < 5–10% p-p ở chế độ danh định) để giảm stress LED và tránh nhấp nháy.

**3.3 Khả năng điều chỉnh (Factory Customization)**

* Thiết kế cho phép **cấu hình dòng ra khi xuất xưởng** (DSP parameter / resistor network / trimmer / firmware profile).
* Mục tiêu: dùng chung nền tảng phần cứng cho nhiều cỡ biển (module 1/2/3/4), chỉ đổi cấu hình.

**3.4 Tương quan độ sáng (CCR dimming behavior)**

* Output phải “đi theo CCR”, nhưng theo **chuẩn FAA thì phải “continuous curve”**, không nhảy bậc do thuật toán. ([Cục Hàng không Liên bang][2])
* Đồng thời, với **Style 2 & 3 signs**, FAA yêu cầu **không có “noticeable variance” của luminance** xuyên suốt các bước CCR (ý nghĩa thực dụng: không flicker/patchy/loang bất thường khi CCR đổi mức). ([Cục Hàng không Liên bang][1])

---

### 4) Tính năng Bảo vệ và Giám sát

**4.1 OVP / Open-load**

* Khi hở mạch LED: hạn chế điện áp / ngắt / latch-off có kiểm soát để bảo vệ MOSFET/diode/cap.

**4.2 OTP**

* Foldback công suất hoặc shutdown khi vượt ngưỡng (khuyến nghị có hysteresis).

**4.3 Chống xung sét / Surge**

* FAA yêu cầu bài **Sign Surge Voltage Test**: áp **2 xung** cách nhau 15 giây theo **IEEE C62.41 Table 4 – Location Category C2** (áp vào đầu vào sign khi AC power off), và thiết bị phải hoạt động bình thường sau test. ([Cục Hàng không Liên bang][1])
* **Khuyến nghị thiết kế:** chọn SPD/TVS/MOV + phối hợp mạch để vượt qua profile C2. (Nếu bạn đặt mục tiêu 10kV nội bộ, coi đó là “design margin”, nhưng “bắt buộc FAA” trong AC đang gọi theo C2, không ghi thẳng “10kV”.)

**4.4 EMI/EMC**

* AC liệt kê tham chiếu **FCC Part 15 Subpart B** (unintentional radiators) như tài liệu liên quan. ([Cục Hàng không Liên bang][1])
  ➡️ Nên thiết kế EMI filter phù hợp (đặc biệt vì boost + switching dễ gây conducted emission).

**4.5 Encapsulation / chống nước**

* FAA không nói “IP67” trực tiếp cho toàn sign, nhưng yêu cầu sign chịu **wind-driven rain**, **sunlight**, và các bài test môi trường (MIL-STD-810F được dẫn). ([Cục Hàng không Liên bang][1])
* Riêng **external sign power adapter** có bài **immersion test** theo MIL-STD-810F Method 512.4. ([Cục Hàng không Liên bang][1])

➡️ Vì bạn muốn “bộ nguồn riêng” và đi sân bay: đặt mục tiêu **IP67/IP68 encapsulated** là hợp lý như “spec nhà sản xuất”, dù không phải câu chữ bắt buộc trong AC 44L.

---

### 5) Yêu cầu về Độ tin cậy (Reliability)

**5.1 MTBF**

* **Mục tiêu đề xuất:** **≥ 100,000 giờ** (25°C, ground benign), hoặc **≥ 50,000 giờ** ở profile nhiệt cao hơn (đây là mục tiêu thiết kế; FAA AC 44L không đưa MTBF con số cụ thể).

**5.2 Nhiệt độ vận hành**

* Theo AC 150/5345-44L:

  * **Class 1:** **-20°C đến +55°C**
  * **Class 2:** **-40°C đến +55°C** ([Cục Hàng không Liên bang][1])
    ➡️ Nếu làm “chuẩn sân bay” mình khuyên bạn đặt là **Class 2**.

---

## Phụ lục ngắn: Ràng buộc “Euro/ICAO” về màu (ảnh hưởng gián tiếp lên driver)

Nếu bạn làm thị trường EU/ICAO, phần **màu sắc/chromaticity** của signs/panels nằm trong hệ “Colours for aeronautical ground lights, markings, signs and panels”. CS-ADR-DSN có các biên chromaticity cho nguồn sáng solid-state (LED). ([EASA][3])
➡️ Với driver: phải kiểm soát **current ripple/thermal drift** để tránh trôi màu và sai chromaticity khi đổi CCR step hoặc khi nhiệt môi trường thay đổi.

---

# Gợi ý chỉnh một điểm trong “phân tích DSP” của bạn (để khớp FAA)

Bạn viết “DSP nhận diện step CCR để dim mịn” — ý tốt, nhưng nhớ ràng buộc FAA EB 67D: **không được tạo “bậc rời rạc” do điều khiển**, mà phải ra **đường cong liên tục theo dòng**. ([Cục Hàng không Liên bang][2])

---

Nếu bạn muốn, mình có thể làm tiếp 2 phần rất “thực chiến”:

1. **Bảng “Test & Acceptance”** cho đúng FAA AC 150/5345-44L: PF test setup (pure sine, crest factor), surge C2, low/high temp shock, immersion (nếu adapter), v.v. (để bạn giao cho lab).
2. **Kiến trúc mạch đề xuất (block-level)** cho boost + CC + PF đạt ≥0.7 trên mọi step, kèm “điểm dễ fail CCR” khi bạn ghép 2–3 bộ nguồn chung 1 biến áp.

Bạn muốn mình ưu tiên làm (1) hay (2)?

[1]: https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC-150-5345-44L-Signage.pdf "150/5345-44L, Specification for Runway and Taxiway Signs, dated 9/30/2024"
[2]: https://www.faa.gov/sites/faa.gov/files/2024-07/eb_67d_rev.pdf "FAA Engineering Brief 67D, Engineering Brief No.67D Light Sources Other Than Incandescent and Xenon For Airport and Obstruction Lighting Fixtures, 6 March 2012"
[3]: https://www.easa.europa.eu/en/downloads/136283/en "CS-ADR-DSN Issue 6 "
