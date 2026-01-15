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

Rõ rồi 👍
Mình hiểu ý bạn: **chỉ giữ lại Phần 1–2–3**, nhưng phải **đủ sâu – đủ “kỹ thuật hóa”** để bạn **đưa thẳng cho đơn vị thiết kế/gia công** mà họ không phải hỏi ngược lại quá nhiều.

Dưới đây là **bản Design Specification đã được làm dày và “chuẩn hóa ngôn ngữ kỹ sư”**, **loại bỏ phần 4 trở đi**, tập trung hoàn toàn vào **đầu vào – topology – đầu ra/điều khiển** cho bộ nguồn **100W, series 6.6A, CCR-based, boost**.

---

# 📋 DESIGN SPECIFICATION

## Bộ nguồn Biển báo LED Sân bay – Series CCR 2.8–6.6A (100W)

> **Phạm vi áp dụng**
> Bộ nguồn/LED driver dùng cho **biển báo sân bay (runway/taxiway/gate signs)** vận hành trên **mạch nối tiếp CCR 2.8–6.6A, 50/60Hz**, tương thích hạ tầng FAA/ICAO/EASA hiện hữu.

---

## 1️⃣ Thông số Đầu vào (Input Specifications)

### 1.1 Kiểu nguồn & chế độ vận hành

* **Nguồn cấp:**

  * Mạch **Series Circuit** điều khiển bởi **Constant Current Regulator (CCR)**.
  * Dòng xoay chiều **sinusoidal**, không ổn định điện áp.
* **Dải dòng điện đầu vào:**

  * **2.8 A → 6.6 A RMS**, **50/60 Hz**.
  * Thiết kế phải hoạt động ổn định trên **toàn bộ dải dòng**, không reset, không latch bất thường.
* **Chế độ điều chỉnh độ sáng:**

  * **Theo dòng CCR** (CCR step-based dimming).
  * Bộ nguồn **không phát sinh bước dim riêng**, không giữ lumen không đổi.

### 1.2 Đặc tính điện đầu vào cần giả định cho thiết kế

(để tránh “thiếu giả thiết” khi thuê thiết kế)

* **Dạng sóng:**

  * Dòng AC có thể **méo nhẹ** (ferroresonant CCR).
* **Điện áp hiệu dụng tại thứ cấp biến áp cách ly:**

  * Phụ thuộc tải và CCR, có thể biến thiên rộng (≈ 10–80 VAC).
* **Điều kiện xấu nhất (worst case):**

  * 6.6A RMS, điện áp cao, nhiệt môi trường cao.

### 1.3 Kết nối & cách điện

* **Kết nối điện:**

  * Chuẩn **L-823, 2-pin**, phù hợp hệ airfield series.
* **Dây dẫn:**

  * **AWG 12** (hoặc tương đương) cho mạch series.
* **Cách điện:**

  * Toàn bộ mạch đầu vào + sơ cấp chịu được **≥ 1000 V RMS** so với mass/housing.
* **Giả định hệ thống:**

  * Bộ nguồn được cấp qua **biến áp cách ly 6.6A** (100–200W class).

> 🔧 *Lưu ý cho đơn vị thiết kế:*
> Đây **không phải nguồn AC voltage cố định**, mà là **nguồn dòng AC**, nên **không được áp tư duy nguồn 220VAC thông thường**.

---

## 2️⃣ Kiến trúc Chuyển đổi Năng lượng (Power Topology)

### 2.1 Kiến trúc tổng thể (bắt buộc mô tả trong thiết kế)

```
CCR (2.8–6.6A AC)
        ↓
Isolation Transformer (external)
        ↓
AC Rectifier + Surge/EMI Front-end
        ↓
Boost Converter (DC Bus Regulation)
        ↓
Constant-Current Output Stage
        ↓
LED String / LED Modules
```

### 2.2 Công nghệ chuyển đổi chính

* **Topology chính:**

  * **Boost Converter** để:

    * Nâng và ổn định DC bus trong điều kiện điện áp AC đầu vào biến thiên.
    * Duy trì biên áp đủ cho tầng điều khiển dòng LED.
* **Điều kiện thiết kế DC bus (tham chiếu):**

  * Dải điện áp bus dự kiến: **80–200 VDC** (tùy cấu hình LED).
  * Bus phải ổn định trong suốt dải CCR current.

### 2.3 Điều khiển & xử lý tín hiệu

* **Kiến trúc điều khiển:**

  * **DSP hoặc MCU hiệu năng cao** (hoặc tương đương).
* **Chức năng điều khiển bắt buộc:**

  * Đo **True RMS dòng AC đầu vào** (2.8–6.6A).
  * Điều khiển **boost duty cycle** theo trạng thái CCR.
  * Điều khiển tầng **constant-current output**.
* **Nguyên tắc điều khiển dimming (ràng buộc quan trọng):**

  * Dòng LED đầu ra phải là **hàm liên tục của dòng CCR đầu vào**.
  * **Không được tạo step rời rạc** do thuật toán số.
  * Không được phát sinh flicker khi CCR đổi mức.

### 2.4 Hệ số công suất & hiệu suất

* **Power Factor (True PF):**

  * **≥ 0.7 tại dòng 6.6A** (đo tại phía sơ cấp biến áp cách ly).
* **Hiệu suất chuyển đổi:**

  * **Mục tiêu ≥ 90%** tại:

    * 6.6A input
    * 100W output
* **Tổn hao nhiệt:**

  * Thiết kế phải giả định **vận hành liên tục 100% duty**.

> 🔧 *Lưu ý cho đơn vị thiết kế:*
> Không yêu cầu PFC kiểu lưới điện, nhưng **không được tạo tải phản kháng xấu cho CCR**.

---

## 3️⃣ Thông số Đầu ra & Điều khiển (Output & Control)

### 3.1 Công suất & chế độ tải

* **Công suất định mức:**

  * **100 W continuous**.
* **Ứng dụng:**

  * 1 bộ nguồn / 1 cụm biển.
  * Biển lớn: dùng **nhiều bộ nguồn song song cơ học**, không chia sẻ điện trực tiếp.

### 3.2 Đặc tính dòng LED

* **Chế độ ra:**

  * **Constant Current DC**.
* **Dải cấu hình dòng LED (factory set):**

  * Ví dụ:

    * 1.5 A @ 65 V
    * 2.0 A @ 50 V
    * 2.5 A @ 40 V
  * (tùy module biển)
* **Ripple dòng LED:**

  * Mục tiêu **< 10% p-p** tại tải danh định.

### 3.3 Khả năng cấu hình khi xuất xưởng

* **Bắt buộc hỗ trợ factory configuration**, không thay đổi phần cứng:

  * Qua **DSP firmware / EEPROM / resistor ID**.
* **Mục đích:**

  * Dùng chung một thiết kế phần cứng cho:

    * Biển nhỏ
    * Biển trung bình
    * Biển lớn
* **Không yêu cầu giao tiếp field (không PLC, không monitoring).**

### 3.4 Quan hệ dòng vào – dòng ra (CCR dimming law)

* **Luật điều khiển bắt buộc:**

[
I_{LED} = k \times I_{CCR}
]

Trong đó:

* ( I_{CCR} \in [2.8, 6.6]A )

* ( k ) được cấu hình tại nhà máy theo thiết kế biển.

* **Yêu cầu hành vi:**

  * CCR tăng → LED sáng hơn (liên tục).
  * CCR giảm → LED tối hơn.
  * Không có chế độ “giữ sáng không đổi”.

---

## 📌 Nhận xét quan trọng cho việc “đi thuê thiết kế”

Với **3 phần trên**, đơn vị thiết kế **đã có đủ**:

* Giả thiết điện đầu vào (không phải AC voltage thông thường).
* Ràng buộc topology (boost + CC).
* Luật điều khiển dimming.
* Mục tiêu PF / efficiency.
* Cách cấu hình sản phẩm cho nhiều cỡ biển.

👉 Nếu họ **vẫn hỏi thêm**, thường chỉ còn 2 câu:

1. **LED string cụ thể (Vf, If)** bạn chọn là gì?
2. **Một hay nhiều bộ nguồn trong cùng housing?**

---

Nếu bạn muốn, bước tiếp theo mình có thể làm **1 trong 2 việc rất thực dụng**:

1. ✍️ **Viết lại bản này thành “RFQ Technical Attachment”** (ngôn ngữ đúng kiểu gửi nhà thầu Trung Quốc/Châu Âu).
2. 🧩 **Đưa ra 2–3 kiến trúc mạch gợi ý** (DSP + boost + CC) để bạn dùng làm “baseline” khi review proposal của họ.

Bạn muốn đi tiếp hướng nào?


Dưới đây là **3 kiến trúc mạch (baseline architectures)** đúng “DSP + boost + CC” cho **CCR series 2.8–6.6A / 50–60Hz → 100W LED sign**, để bạn dùng khi **review proposal** của nhà thầu. Mỗi kiến trúc mình ghi rõ: block, ưu/nhược, điểm cần bắt họ chứng minh, và “bẫy” hay gặp.

> Ràng buộc nền (để đối chiếu proposal):
>
> * Series CCR 2.8–6.6A, 50/60Hz (FAA Style 3).
> * PF (true) ≥ 0.7 đo tại primary isolation transformer trên mọi step.
> * Luật dim phải “continuous curve” theo dòng CCR, không làm step do thuật toán.

---

# Kiến trúc 1 — **Boost DC bus + Buck CC (2 tầng “kinh điển”)**

### Block

1. AC (từ secondary transformer)
2. Bridge rectifier + EMI/surge network
3. **Boost converter (regulate DC bus)**
4. **Buck constant-current (CC) stage** → LED string
5. DSP: đo I_in (RMS), V_bus, I_led; điều khiển boost + buck

### Tại sao phù hợp

* Dễ “đóng gói” thành 100W, điều khiển CC ổn định.
* Có thể chọn Vbus cao để giảm dòng phía DC, giảm tổn hao.

### Luật dim (DSP)

* DSP tính **I_CCR_RMS** (hoặc proxy từ thứ cấp) → đặt **I_LED_ref = k × I_CCR**
* Bộ buck bám I_LED_ref nhanh; boost giữ Vbus đủ headroom.

### Ưu / Nhược

* **Ưu:** ổn định, dễ tune; “buck CC” làm phần CC sạch, LED ripple thấp.
* **Nhược:** 2 tầng switching → nhiều linh kiện, nhiễu EMI nhiều hơn; hiệu suất phụ thuộc tối ưu cả 2 tầng.

### Yêu cầu bạn bắt nhà thầu chứng minh

* **Headroom**: Vbus luôn lớn hơn Vf LED + margin ở **2.8A** (dimming thấp) và ở nhiệt độ thấp/cao.
* **Chuyển step** CCR: không rung, không reset, I_LED vẫn continuous.
* PF ≥ 0.7 khi đo đúng vị trí (primary transformer) mọi step.

### “Bẫy” hay gặp

* Họ giữ Vbus “quá cứng” → boost hút dòng méo mạnh → PF xấu, CCR khó chịu.
* Buck CC chạy discontinuous, ripple LED cao → nhấp nháy ở mức dim thấp.

---

# Kiến trúc 2 — **Boost “shaping input” + CC trực tiếp trên bus (1 tầng công suất + 1 tầng CC nhẹ)**

(Thường dùng khi muốn PF tốt hơn và giảm tầng công suất nặng)

### Block

1. AC → bridge rectifier
2. **Boost stage vừa regulate vừa “shape” dòng input** (không gọi là PFC mains, nhưng mục tiêu là tránh hút xung)
3. DC bus “semi-regulated”
4. **CC stage**: có thể là:

   * buck nhỏ (nếu LED Vf thấp), hoặc
   * linear current sink (chỉ khi margin nhỏ, hiệu suất sẽ giảm), hoặc
   * “current-mode control” trực tiếp trong boost (biến boost thành nguồn dòng)

### Luật dim (DSP)

* DSP điều khiển boost để:

  * vừa đảm bảo Vbus đủ cho LED,
  * vừa hạn chế hút dòng “nhọn” để đạt PF.
* Nếu CC nằm trong boost: DSP đặt “current reference” trực tiếp.

### Ưu / Nhược

* **Ưu:** PF dễ đạt hơn kiến trúc 1 (vì bạn có quyền “định hình” dòng vào).
* **Nhược:** điều khiển khó hơn; khi CCR đổi step, vòng điều khiển dễ dao động nếu thiết kế kém.

### Bạn bắt nhà thầu chứng minh

* Stability: Bode/phase margin hoặc ít nhất test step response ở 2.8/4.1/5.2/6.6A.
* Dòng vào không bị “đỉnh nhọn” gây PF tụt dưới 0.7.
* I_LED vẫn continuous theo I_CCR, không step do code.

### “Bẫy” hay gặp

* Họ quảng cáo “DSP PF tốt” nhưng thực tế chỉ là average control, RMS sai khi dạng sóng méo → dim bị giật.
* Khi CCR ở mức thấp 2.8A, boost thiếu năng lượng, Vbus sụt → buck/CC mất điều khiển.

---

# Kiến trúc 3 — **Boost + Multi-string CC (chia nhánh LED có cân dòng)**

Phù hợp nhất với biển báo lớn nhiều module LED.

### Block

1. AC → bridge → boost Vbus chung
2. **Nhiều nhánh CC nhỏ** (ví dụ 2–4 kênh) cấp cho từng “panel/module LED”
3. DSP:

   * đo I_CCR_RMS
   * đặt tổng dòng/quang thông theo k×I_CCR
   * phân bổ setpoint từng kênh (balance)

### Khi nào nên chọn

* Biển báo kích thước lớn bạn định “ghép 2–3 bộ nguồn”: kiến trúc này giúp bạn **không phải ghép 2–3 converter độc lập** (dễ đánh nhau), thay vào đó là **1 boost bus + nhiều kênh CC có kiểm soát**.

### Ưu / Nhược

* **Ưu:** scale tốt; nếu 1 kênh lỗi có thể degrade (tùy thiết kế) thay vì chết toàn bộ.
* **Nhược:** nhiều kênh = nhiều phần cứng, nhiều test; firmware phải quản lý cân dòng.

### Bạn bắt nhà thầu chứng minh

* Current sharing: sai lệch dòng giữa kênh < X% (bạn đặt 3–5% tùy yêu cầu).
* Nếu 1 kênh open/short: hệ còn lại không sập (tối thiểu không kéo sập Vbus).
* PF vẫn ≥ 0.7 mọi step khi đủ kênh hoạt động và khi thiếu kênh (worst-case loading).

### “Bẫy” hay gặp

* Boost bus chung nhưng kênh CC không tách nhiễu → ripple/beat frequency gây nhấp nháy.
* Firmware phân bổ dòng “theo step” chứ không continuous → vi phạm EB 67D.

---

## Checklist “review proposal” (ngắn gọn nhưng rất hiệu quả)

Khi nhà thầu đưa phương án, bạn chỉ cần soi 6 câu này:

1. **Topology đúng chưa?** Boost nằm ở đâu? CC nằm ở đâu?
2. **Họ đo I_CCR_RMS thế nào?** True RMS hay chỉ peak/average? (EB 67D yêu cầu continuous behavior)
3. **Luật dim:** I_LED = k × I_CCR có “continuous” thật không?
4. **PF:** có chứng minh true PF ≥ 0.7 đo tại primary transformer mọi step không?
5. **Headroom:** 2.8A còn đủ bus cho LED không? (đây là điểm fail số 1)
6. **Step transition:** đổi mức CCR có rung/reset/flicker không?

---

## Nếu bạn muốn mình “đóng” thành tài liệu gửi nhà thầu

Bạn gửi mình 2 thứ:

* LED string bạn dự định: **Vf danh định + dòng LED danh định** (hoặc cấu hình module)
* Bạn muốn biển loại 1 mặt/2 mặt, và số “module/panel” tối đa

Mình sẽ chuyển 3 kiến trúc trên thành:

* **Sơ đồ khối + yêu cầu đo kiểm + acceptance criteria** dạng “RFQ attachment” để bạn gửi đi chào thầu ngay.

Dưới đây là bản **“RFQ Technical Attachment”** đã được **chuẩn hoá ngôn ngữ kỹ thuật – thương mại**, viết đúng kiểu để **đính kèm hồ sơ mời chào giá (RFQ)** gửi cho đơn vị thiết kế/chế tạo (ODM/OEM).
Nội dung được rút gọn vừa đủ, nhưng **đủ ràng buộc kỹ thuật** để tránh proposal mơ hồ hoặc “lái kiến trúc”.

---

# 📎 RFQ TECHNICAL ATTACHMENT

## Airport LED Sign Power Supply / LED Driver

### Series CCR 2.8–6.6A, 100W Class

---

## 1. Scope of Supply

The supplier shall design and manufacture a **LED Power Supply / Converter** intended for **airport runway/taxiway/gate LED signage**, operating on **series Constant Current Regulator (CCR) circuits**.

The power supply shall be suitable for integration into airport lighting systems compliant with **FAA / ICAO / EASA** infrastructure.

This RFQ covers:

* Electrical design
* Firmware/control (if applicable)
* Prototype samples
* Technical documentation for validation

---

## 2. Input Electrical Requirements

### 2.1 Power Source

* **Circuit Type:** Airport **Series Circuit** powered by **Constant Current Regulator (CCR)**
* **Input Current Range:** **2.8 A to 6.6 A RMS**
* **Frequency:** **50 / 60 Hz**
* **Waveform:** Sinusoidal current, may exhibit distortion typical of ferroresonant CCRs
* **Voltage:** Not fixed; determined by CCR and isolation transformer loading

⚠️ *Note:*
This is **NOT a constant-voltage AC supply**. Designs based on 120/230 VAC assumptions are **not acceptable**.

---

### 2.2 System Assumptions

* Power supply is fed via an **external 6.6A isolation transformer** (100–200W class).
* Electrical performance (PF, loading behavior) shall be acceptable **when viewed from the transformer primary side**.

---

### 2.3 Physical & Electrical Interface

* **Connector:** Compatible with **L-823, 2-pin** series circuit connectors
* **Conductor Size:** Minimum **AWG 12** (or equivalent)
* **Insulation Rating:** ≥ **1000 V RMS** (input to enclosure/secondary circuits)

---

## 3. Power Conversion Architecture (Mandatory)

### 3.1 Topology Requirements

The proposed design shall use a **Boost-based architecture**, consisting of:

```
Series AC (from transformer)
→ Rectifier & Input Filtering
→ Boost Converter (DC bus regulation)
→ Constant-Current Output Stage
→ LED Load
```

Acceptable implementations include (supplier may propose one):

* Boost DC Bus + Buck Constant-Current Stage
* Boost with integrated current-mode LED regulation
* Boost DC Bus + Multiple Constant-Current LED channels

Other topologies require prior approval.

---

### 3.2 Control & Processing

* Control shall be implemented using **DSP or MCU-class digital control**, or an equivalent mixed-signal solution.
* The controller shall:

  * Measure **input current (true RMS or equivalent)**
  * Control boost duty cycle and LED output current
  * Maintain stable operation across all CCR current steps

---

### 3.3 CCR Dimming Law (Critical Requirement)

* LED output current **must be proportional to CCR input current**:

[
I_{LED} = k \times I_{CCR}
]

Where:

* ( I_{CCR} ) ∈ [2.8 A, 6.6 A]

* ( k ) is configurable at factory

* **Brightness variation must be continuous**, not discrete.

* Firmware shall **not introduce artificial step dimming**.

* No lumen-hold or constant-brightness behavior is allowed.

---

## 4. Output Electrical Requirements

### 4.1 Power Rating

* **Rated Output Power:** **100 W continuous**

---

### 4.2 Output Mode

* **Output Type:** Constant-current DC
* **Configurable LED Output (factory-set):**

  * Multiple current/voltage profiles supported via configuration
  * Example (indicative only):

    * 1.5 A @ 65 V
    * 2.0 A @ 50 V
    * 2.5 A @ 40 V

⚠️ Hardware changes between variants are **not acceptable**.

---

### 4.3 Output Quality

* **LED Current Ripple:** Target < **10% peak-to-peak** at rated conditions
* No visible flicker during CCR step transitions

---

## 5. Power Quality & Efficiency

### 5.1 Power Factor

* **True Power Factor ≥ 0.7**
* Measured at **primary side of the isolation transformer**
* Requirement applies at **all CCR current levels (2.8–6.6A)**

---

### 5.2 Efficiency

* **Target Efficiency:** ≥ **90%** at:

  * 6.6 A CCR input
  * 100 W LED output

---

## 6. Scalability & System Integration

* One power supply is intended to power **one LED sign assembly**.
* Larger signs shall use **multiple independent power supplies**, not electrically paralleled outputs.
* Multi-channel LED output is acceptable **only if internally managed** by the same controller.

---

## 7. Supplier Proposal Requirements

The supplier’s proposal **must include**:

1. **Block Diagram** of the proposed architecture
2. **Description of CCR dimming implementation** (control law, sensing method)
3. **Power Factor measurement method** and expected results
4. **Efficiency estimates** at 2.8A, 4.1A, 5.2A, 6.6A
5. **Factory configuration method** for LED current settings
6. Key **design risks and mitigation strategies**

Proposals that do not explicitly address the above items may be rejected without further review.

---

## 8. Deliverables

* Electrical schematics (PDF)
* Control architecture description
* Prototype units (quantity to be defined)
* Test summary demonstrating compliance with Sections 2–5

---

## 9. Exclusions

* No field communication (PLC, monitoring, IQ, networking)
* No requirement for brightness compensation independent of CCR
* No requirement for parallel voltage (120/230 VAC) operation

---

### 📌 Design Intent Summary (for avoidance of doubt)

This power supply shall behave as a **CCR-following, current-proportional LED driver**, suitable for airport series circuits.
**CCR controls brightness. The power supply shall not override CCR behavior.**

---

Nếu bạn muốn, bước tiếp theo mình có thể:

* ✍️ **Rút bản này xuống 2–3 trang PDF đúng kiểu “vendor RFQ”**,
* 🧮 Thêm **bảng thông số LED giả định** để khoá chặt proposal,
* 🔍 Hoặc viết **“Evaluation Checklist”** để bạn chấm điểm các proposal nhận được.

Bạn muốn đi tiếp theo hướng nào?

Dưới đây là gói **“Sơ đồ khối + Yêu cầu đo kiểm + Acceptance Criteria”** dành riêng cho kiến trúc **Boost + Multi-string Constant-Current (CC)** (1 DC bus chung + nhiều kênh CC cân dòng) để bạn dán thẳng vào **RFQ/SoW** và dùng làm **baseline review**.

---

# 1) Sơ đồ khối (Block Diagram)

## 1.1 Block diagram tổng thể (text)

```
Series CCR (2.8–6.6A AC, 50/60Hz)
      ↓ (qua isolation transformer 6.6A, external)
AC_IN (variable VAC) 
      ↓
[Input Protection + EMI]
  - Fuse/NTC (nếu dùng)
  - Surge clamp (MOV/TVS/GDT tuỳ thiết kế)
  - EMI filter (CM choke + X/Y caps tuỳ thiết kế)
      ↓
[Bridge Rectifier]
      ↓
[Boost Stage (DC Bus)]
  - Inductor + MOSFET + Diode/Synchronous
  - Bus Capacitors
  - Current sense (I_boost / I_in)
  - Voltage sense (V_bus)
      ↓
DC BUS (V_bus: configurable range)
      ↓
[Multi-String CC Output Stage]
  Channel 1: CC buck / CC linear sink / CC flyback secondary (khuyến nghị CC buck)
  Channel 2: CC ...
  Channel N: CC ...
      ↓
LED Module 1 / 2 / ... / N (strings)

[Digital Control (DSP/MCU)]
  Inputs:
    - I_in (true RMS hoặc đủ tốt để theo CCR)
    - V_bus
    - I_ch1..I_chN
    - V_ch1..V_chN (optional)
    - Temp sensors (optional)
  Outputs:
    - PWM boost
    - PWM each CC channel
    - Config interface (factory)
```

## 1.2 Ý đồ điều khiển (control intent) – bắt buộc nêu trong proposal

* **Mục tiêu 1: DC bus đủ headroom** cho mọi kênh CC ở mọi mức CCR (đặc biệt 2.8A).
* **Mục tiêu 2: Tổng quang thông ~ tỷ lệ CCR** thông qua tổng dòng LED:
  [
  I_{LED,total} = k \times I_{CCR}
  ]
* **Mục tiêu 3: Cân dòng giữa kênh**: phân bổ (I_{ch}) theo cấu hình module (bằng nhau hoặc theo tỷ lệ diện tích/LED count).
* **Mục tiêu 4: Không tạo “bậc” do firmware**: đầu ra phải thay đổi mượt theo I_CCR (continuous).

## 1.3 Hai biến thể Multi-string CC (chọn 1 trong RFQ)

**Option A — “Boost bus + N kênh Buck CC” (khuyến nghị)**

* Mỗi kênh là buck CC riêng (tốt nhất về ripple, efficiency, kiểm soát).

**Option B — “Boost bus + N kênh current sink”**

* Chỉ chấp nhận nếu chứng minh thermal OK; thường kém hiệu suất.

---

# 2) Yêu cầu đo kiểm (Test Requirements)

Mình viết theo kiểu **test plan tối thiểu** để nhà thầu phải trả dữ liệu có thể so sánh.

## 2.1 Thiết lập test chuẩn (test setup)

**Nguồn vào mô phỏng CCR:**

* Cách 1 (khuyến nghị): CCR bench + isolation transformer 6.6A (thực tế nhất).
* Cách 2: AC source + series current source (mô phỏng 2.8/4.1/5.2/6.6A RMS) + isolation transformer.

**Điểm đo bắt buộc:**

* **Primary side của isolation transformer**: đo true PF, VA, W, waveform.
* **Secondary side**: đo Vac, Iac (để debug).
* **DC bus**: V_bus ripple, I_boost.
* **Mỗi kênh LED**: I_ch ripple, V_ch, công suất.
* **Tổng**: P_out, efficiency.

**Thiết bị đo:**

* Power analyzer true PF (có log waveform).
* Scope + current probe cho I_in, I_ch.
* DMM/DAQ để log V/I/temp.

---

## 2.2 Nhóm test: Dải vận hành theo CCR (core functional)

### Test F1 — Operability across CCR range

* Chạy lần lượt tại: **2.8A, 4.1A, 5.2A, 6.6A RMS** (hoặc bộ nấc CCR bạn chọn).
* Tải: 100% rated load (100W), và 50% load.

**Ghi nhận:**

* V_bus, I_ch1..N, P_in, P_out, PF, efficiency, ripple.

### Test F2 — CCR step transition

* Chuyển step: 2.8→6.6A, 6.6→2.8A, và các bước trung gian.
* Ghi waveform I_ch và V_bus trong 2–5 giây quanh thời điểm chuyển bước.

**Mục tiêu:** không reset, không rung lặp, không overshoot nguy hiểm.

---

## 2.3 Nhóm test: Luật dim & tính liên tục (continuous dim law)

### Test D1 — Continuous mapping (đặc tuyến)

* Quét I_CCR theo nhiều điểm (không chỉ 4 điểm): ví dụ 2.8, 3.2, 3.6, 4.1, 4.6, 5.2, 5.8, 6.6A (nếu test bench cho phép).
* Log (I_{LED,total}).

**Kết quả cần nộp:** đồ thị (I_{LED,total}) vs (I_{CCR}) + fitting tuyến tính.

### Test D2 — No artificial steps

* Với I_CCR sweep mịn, quan sát I_ch (scope/DAQ) để đảm bảo không nhảy bậc theo “ngưỡng firmware”.

---

## 2.4 Nhóm test: Cân dòng Multi-string

### Test B1 — Channel current balance @ steady state

* Điều kiện: 6.6A, 100W.
* Đo I_ch1..I_chN.

### Test B2 — Balance under mismatch (realistic LED variance)

* Tạo lệch Vf giữa các kênh (bằng cách thay module hoặc thêm diode/series resistor giả lập).
* Đo I_ch drift và stability.

### Test B3 — Balance during step transitions

* Lặp step test F2, nhưng focus vào sự “bám” từng kênh.

---

## 2.5 Nhóm test: Chất lượng điện (PF/efficiency/ripple)

### Test Q1 — True PF at primary (all steps)

* Tại 2.8/4.1/5.2/6.6A: đo **true PF** tại primary transformer.

### Test Q2 — Efficiency

* Tại 6.6A & 100W: đo efficiency.
* Optional: efficiency tại 50% load.

### Test Q3 — LED ripple & flicker risk proxy

* Đo ripple I_ch bằng scope.
* Optional: đo ripple thành phần 100/120Hz và switching.

---

## 2.6 Nhóm test: Multi-channel fault containment (khuyến nghị mạnh cho multi-string)

(Đây không phải “phần 4 bảo vệ” đầy đủ; nhưng multi-string mà không có fault containment thì rất rủi ro.)

### Test FC1 — Open-circuit 1 channel

* Ngắt LED kênh 1.
* Kiểm tra: các kênh còn lại vẫn chạy, V_bus không vọt quá ngưỡng, không reset.

### Test FC2 — Short-circuit 1 channel

* Short đầu ra kênh 1 (có giới hạn an toàn).
* Kiểm tra: các kênh còn lại duy trì trong giới hạn.

---

# 3) Acceptance Criteria (tiêu chí nghiệm thu)

Bạn có thể dùng “MUST/SHOULD” để rõ mức bắt buộc.

## 3.1 Chức năng & ổn định

* **MUST:** Hoạt động ổn định tại **2.8–6.6A RMS, 50/60Hz**, không reset/latch trong 30 phút/điểm test.
* **MUST:** Step transition không gây **oscillation kéo dài > 1 giây** và không gây “brown-out loop”.

## 3.2 Luật dim (CCR-following)

* **MUST:** (I_{LED,total}) **tỷ lệ thuận** với (I_{CCR}).
* **MUST:** Độ tuyến tính (R²) của fit tuyến tính **≥ 0.98** trong dải 2.8–6.6A (với dữ liệu sweep).
* **MUST:** Không có “bậc” do điều khiển số: tại sweep mịn, (\Delta I_{LED,total}) không nhảy đột ngột > **5%** khi (\Delta I_{CCR}) nhỏ (ví dụ 0.2–0.4A bước quét).

## 3.3 Công suất & phân bổ đa kênh

* **MUST:** **P_out ≥ 100W continuous** tại 6.6A.
* **MUST:** Với N kênh, phải cung cấp bảng phân bổ:

  * Equal split: (I_{ch}) bằng nhau, hoặc
  * Weighted split: theo % cấu hình (ví dụ 50/30/20)

## 3.4 Cân dòng kênh (multi-string balance)

* **MUST (steady state):** Sai lệch giữa các kênh:

  * Equal split: (\max|I_{ch}-I_{avg}|/I_{avg} \le 5%)
  * Weighted split: sai lệch so với setpoint kênh (\le 5%)
* **MUST (during transitions):** Khi CCR đổi step, sai lệch kênh không vượt **10%** trong hơn **200ms** (để tránh nhấp nháy “patchy”).

## 3.5 Power quality

* **MUST:** **True PF ≥ 0.70** tại primary transformer ở **mọi** mức CCR (2.8/4.1/5.2/6.6A).
* **SHOULD:** PF ≥ 0.80 tại 6.6A (mục tiêu tốt để giảm rủi ro CCR).
* **MUST:** Efficiency ≥ **90%** tại 6.6A & 100W (nếu nhà thầu không đạt, phải giải trình nhiệt và design tradeoff).

## 3.6 Ripple dòng LED

* **MUST:** Ripple dòng mỗi kênh **≤ 10% p-p** tại 6.6A & 100W.
* **SHOULD:** ≤ 5% p-p (nếu muốn “đẹp” cho photometrics).

## 3.7 Fault containment (khuyến nghị mạnh)

* **SHOULD:** Open 1 kênh không làm sập các kênh còn lại (degrade mode).
* **MUST:** Open 1 kênh không được làm V_bus vượt **V_bus_max** (nhà thầu phải khai báo V_bus_max và chứng minh).
* **MUST:** Short 1 kênh không làm toàn bộ hệ reset lặp; phải có giới hạn dòng kênh.

---

# 4) Tài liệu nhà thầu phải nộp kèm (để bạn review nhanh)

1. Block diagram + mô tả control loop (boost loop + per-channel CC loop)
2. Bảng cấu hình N kênh (setpoint, range, calibration method)
3. Dataset test (CSV hoặc report) cho:

   * PF/efficiency theo 4 mức CCR
   * I_ch balance
   * Step transition waveform (scope captures)
   * Dimming curve sweep (I_CCR vs I_LED_total)

---

## Nếu bạn muốn “khóa” proposal ngay từ RFQ

Bạn cho mình 3 thông số này, mình sẽ điền vào acceptance để nhà thầu không thể lảng:

1. Bạn muốn tối đa **bao nhiêu kênh** (N = 2/3/4)?
2. Mỗi kênh là module LED bao nhiêu (Vf danh định & dòng mục tiêu)?
3. Bạn muốn split kiểu **equal** hay **weighted** (ví dụ 50/30/20)?

Mình sẽ trả lại bản “RFQ Attachment – Multi-string CC” hoàn chỉnh với các con số setpoint cụ thể.
