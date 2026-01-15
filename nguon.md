Dưới đây là cách bạn có thể **xây dựng công nghệ + đặc tính kỹ thuật** cho **bộ nguồn biển báo LED kiểu “airfield sign”** (kiểu Reliance/ADB: cấp nguồn **dòng không đổi** qua mạch series, có **biến áp cách ly + bộ converter/driver đổ keo**). Mình viết theo hướng để bạn có thể “đặt spec → chọn kiến trúc → ra yêu cầu mạch → test/đo kiểm”. (Tham khảo cấu trúc và các thông số nền trong tài liệu bạn đưa: )

---

## 1) Chốt “kiểu hệ thống” bạn muốn làm (2 đường chính)

### A. Kiểu **Series Current (CCR-based)** — giống ADB airfield

* **Nguồn vào:** dòng AC sin **2.8–6.6A, 50/60Hz**; dimming theo “step” của CCR 
* **Chuỗi công nghệ điển hình:** **CCR → biến áp cách ly (isolation transformer) → converter/LED driver đổ keo (potted)** 
* **Điểm ăn tiền:** chạy được trong hạ tầng “series circuit”, an toàn cách ly, chịu môi trường cực khắc nghiệt.

### B. Kiểu **AC mains (Parallel/Voltage)** — 120–240VAC

* **Nguồn vào:** 120–240VAC 50/60Hz 
* Dễ làm hơn cho biển báo dân dụng (không cần CCR/biến áp series), nhưng **khác** “tương tự” ADB nếu bạn đang nhắm đúng airfield style.

> Nếu bạn muốn “tương tự hệt” mẫu ADB/Reliance, hãy đi theo **A (series current + isolation transformer + converter potted)**.

---

## 2) Kiến trúc công nghệ đề xuất (Series 6.6A chuẩn)

### 2.1 Sơ đồ khối (Block diagram)

1. **Đầu vào series 2.8–6.6A / 50–60Hz**
2. **Isolation transformer**: cách ly + “match” trở kháng 
3. **AC-DC front-end** trong converter (chỉnh lưu + lọc)
4. **LED constant-current driver** (buck / flyback tuỳ công suất & yêu cầu cách ly nội bộ)
5. **Bảo vệ + giám sát** (surge, open/short LED, thermal, fail-open nếu có)
6. **Đổ keo / sealing** đạt IP mục tiêu

### 2.2 Tại sao cần isolation transformer?

* Nó là “giao diện bắt buộc” giữa mạch series dòng lớn và tải LED, vừa **an toàn cách ly** vừa tối ưu truyền công suất .

---

## 3) Bộ “đặc tính kỹ thuật” (spec) bạn có thể dùng ngay

### 3.1 Input (cho bản Series 6.6A)

* **Dải dòng vào:** 2.8–6.6A AC, 50/60Hz (tương thích CCR 3-step/5-step) 
* **Cơ chế dimming:** theo mức dòng CCR (converter phản hồi theo step) 
* (Nếu bạn làm “full hệ” gồm cả CCR: CCR có thể đạt hiệu suất ~90–92% và PF ~0.99 theo tài liệu tham chiếu trong note) 

### 3.2 Isolation transformer (gợi ý dải công suất)

Bạn chọn rating theo công suất biển + margin:

* Dải rating thực tế hay gặp: **10/15W, 20/25W, 30/45W, 65W, 100W, 150W, 200W…** 
* Với tải “nặng” (ví dụ cụm có gia nhiệt) có thể dùng tới **6.6A/200W** 

### 3.3 Converter / LED driver (đổ keo)

* **Dạng:** converter “fully encapsulated / potted”, mục tiêu IP67/IP68 
* **Input:** 2.8–6.6A / 50–60Hz 
* **Output:** **constant-current LED driver** 
* **Power factor (mục tiêu):** >0.90 (ở điều kiện 6.6A) 
* **Môi trường:** độ ẩm vận hành tới 100%RH , độ cao tới 3,000m 

### 3.4 Chống sét/surge & độ bền điện

* Mức tham chiếu trong tài liệu: **ANSI/IEEE C62.41-1991 Cat C2**, dạng “combination wave”, đỉnh **10kV / 5kA** 
  → Nếu bạn muốn “tương tự”, đây là mục tiêu thiết kế cho MOV/GDT/TVS + layout + cách đổ keo.

---

## 4) “Công nghệ mạch” nên chọn: Analog hay MCU?

### 4.1 Bản tiêu chuẩn (không giám sát) — nên làm **analog**

Tài liệu mô tả đa số dạng này:

* Converter dùng **IC điều khiển analog**, không cần MCU 
* Các khối nên có: error amp, sense resistor, soft-start, OVP, EMI filter… 

**Ưu:** đơn giản, rẻ, ổn định, dễ “đổ keo” và chịu môi trường.

### 4.2 Bản có monitoring (MON) — thêm “fail-open” mức logic rời

* Có thể thêm mạch “fail-open detection” kiểu rơ-le/so sánh ngưỡng để báo OK/FAIL 

### 4.3 Bản nâng cao (IQ/PLC) — MCU + truyền thông trên đường nguồn

* Có MCU ở mỗi thiết bị và “power-line carrier (PLC)” để điều khiển/giám sát theo đường nguồn 
  **Lưu ý:** mức này phức tạp hơn nhiều (firmware + modem + EMC).

---

## 5) Nếu bạn muốn làm bản “2A system” (tiết kiệm tổn hao dây)

Tài liệu có mô tả biến thể **2A nominal** và các hệ quả thiết kế:

* Hệ “2A” chạy dòng thấp hơn, giảm tổn hao I²R, nhưng **biến áp phải tăng rating ~3.3×**, tối thiểu có trường hợp tới **200W**, và CCR phải “dư tải” để giữ biên điện áp .

Nếu bạn đang làm thử nghiệm ban đầu, mình khuyên bắt đầu **6.6A** trước (dễ tương thích và dễ sizing), rồi mới tối ưu sang 2A.

---

## 6) Checklist thiết kế để ra được “bộ nguồn tương tự”

### 6.1 Bộ yêu cầu đầu bài (bạn điền số vào)

* Công suất biển báo: … W (đỉnh / danh định)
* Dải nhiệt độ môi trường: … °C
* IP mục tiêu: IP67 hay IP68
* Dimming: theo step dòng (CCR) hay PWM nội bộ?
* Có cần monitoring/fail-open/PLC không?

### 6.2 Các quyết định kỹ thuật then chốt

* **Chọn isolation transformer rating** theo W + margin (tham chiếu dải rating phổ biến) 
* **Chọn topology driver** (buck/flyback) theo:

  * công suất
  * dải điện áp LED string
  * yêu cầu ripple/EMI
  * cách ly nội bộ (nếu cần)
* **Thiết kế surge** theo mục tiêu 10kV/5kA (nếu bạn muốn tương đương) 
* **Đổ keo & vật liệu** để đạt 100%RH, chống ngưng tụ 

### 6.3 Kế hoạch test/đo kiểm (rất quan trọng để “ra sản phẩm”)

* Hiệu suất & nhiệt: full load, hot soak
* EMI/EMC sơ bộ (conducted/radiated)
* Surge/EFT (theo mục tiêu bạn đặt)
* Open/short LED, brown-in/brown-out, inrush
* Kiểm tra dimming theo step (2.8/4.1/5.2/6.6A kiểu 3/5-step)

---

## 7) Một “spec mẫu” (bạn có thể copy làm datasheet nội bộ)

**Bộ nguồn biển báo LED – Series Current, potted converter**

* Input: 2.8–6.6A AC, 50/60Hz 
* Isolation transformer: 6.6A primary, rating tuỳ W (ví dụ 65W/100W/150W/200W…) 
* Output: Constant-current LED driver 
* PF: >0.90 @ 6.6A 
* Environmental: 100% RH, altitude up to 3,000 m 
* Protection: Surge target 10kV/5kA (Cat C2 ref) 
* Control option:

  * Standard: analog IC, no MCU 
  * MON option: fail-open OK/FAIL 

---

Nếu bạn trả lời nhanh 3 thông tin: **(1) biển báo bạn dự tính công suất bao nhiêu W**, **(2) điện áp/dòng LED string (ví dụ 48V–2A hay 24V–3A)**, **(3) bạn muốn “series 6.6A giống airfield” hay “220VAC dân dụng”**, mình sẽ giúp bạn “chốt cấu hình” và **ra bộ thông số thiết kế chi tiết hơn** (cỡ biến áp, dải điện áp DC bus, dòng LED danh định, margin nhiệt, cấu trúc bảo vệ).

### 1) Bộ nguồn “họ” có thông số IP chống nước không?

Có. Trong tài liệu bạn cung cấp, **converter (bộ nguồn/driver) được đổ keo (full potting) và được nêu IP67/IP68**:

* “**Encapsulation: Full potting; IP67/IP68 rating**” 
  Đây chính là đặc tính “chống nước/chống bụi” cấp thiết cho môi trường airfield (mưa, ngập, muối, ngưng tụ).

---

### 2) Có thể bỏ biến áp cách ly không, hay bắt buộc?

Với kiến trúc **series 6.6A kiểu airfield (CCR-based)**, **biến áp cách ly gần như là “bắt buộc” trong thực tế triển khai chuẩn**, vì nó làm 2 việc cốt lõi:

1. **An toàn điện (SELV/cách ly cho con người và thiết bị)**
   Tài liệu mô tả rõ isolation transformer là “critical interface… electrical isolation… (achieving SELV compliance)” 

2. **Ghép trở kháng / chuyển đổi năng lượng từ mạch series sang tải cục bộ**
   Cũng trong đoạn đó: transformer còn để **impedance matching** giúp truyền công suất tối ưu 

Ngoài ra, cấu hình sản phẩm thực tế cũng “thiết kế để đi kèm transformer”: converter có **L-823 plug connector to transformer** , cho thấy transformer là một phần của hệ sinh thái lắp đặt.

#### Vậy “bỏ transformer” có nghĩa là gì?

* **Nếu bạn bỏ isolation transformer mà không thay bằng cách ly tương đương**, thì mạch LED/driver của bạn sẽ **không còn SELV**, có thể “nổi” theo điện áp của mạch series (có thể lên đáng kể tuỳ CCR + tổng trở đường dây), dẫn tới rủi ro an toàn và gần như không thể đạt các yêu cầu/chuẩn airfield.
* **Nếu bạn vẫn muốn bỏ “cục transformer rời”**, cách hợp lý duy nhất là **chuyển chức năng cách ly vào trong converter** (tức converter của bạn phải là **isolated topology** – ví dụ flyback/LLC/isolated buck…); khi đó bạn “bỏ transformer ngoài” nhưng **không hề bỏ yêu cầu cách ly** (chỉ đổi vị trí/cách đóng gói). Về mặt certification và safety, đây vẫn là “có cách ly”.

**Kết luận thực dụng:**

* Với mục tiêu “giống airfield series 6.6A”, **cách ly là bắt buộc**; và trong kiến trúc phổ biến, **isolation transformer rời** là lựa chọn chuẩn vì dễ đạt an toàn, dễ bảo trì/thay thế, và phù hợp hạ tầng L-823.  

---

### 3) Về “công nghệ boost” trong bộ nguồn series 6.6A

Bạn vẫn có thể dùng “boost” trong converter, nhưng nên hiểu theo 2 hướng thường gặp:

* **Boost để tạo DC bus ổn định sau chỉnh lưu**, nhằm đảm bảo driver LED hoạt động ổn định khi CCR thay đổi step 2.8→6.6A. (Kiểu “boost front-end” + “constant-current stage”.)
* Hoặc **buck-boost** (đôi khi người ta gọi nôm na là “boost”) để giữ dòng LED ổn định khi điện áp LED string thay đổi theo nhiệt/aging.

Điểm quan trọng: trong hệ series airfield, việc “PF/PFC kiểu lưới điện” không giống nguồn AC mains thông thường; cái bạn cần ưu tiên hơn là **ổn định dòng LED theo step CCR + chịu surge + nhiệt + IP** (converter thường potted IP67/IP68 như trên). 

---

Nếu bạn cho mình thêm 2 thông số, mình sẽ “đóng khung kiến trúc boost” và ra spec chi tiết (dải điện áp bus, lựa chọn topology, bảo vệ):

1. Công suất/độ sáng dự kiến của biển (W hoặc số module LED),
2. LED string bạn định dùng (điện áp danh định và dòng danh định).

Với **100W/module** theo hệ **series 6.6A**, cách bạn nghĩ “dùng chung 1 biến áp 6.6–6.6A 200W rồi ghép 2–3 bộ nguồn” cần xem lại, vì có vài điểm **rất dễ vấp** (cả về công suất lẫn hành vi mạch series).

---

## 1) Check nhanh về công suất biến áp 200W

Trong mạch series 6.6A, nếu biến áp được **định mức 200W**, thì “điện áp rơi hiệu dụng” trên nhánh biến áp ở full-load xấp xỉ:

* ( V \approx P/I = 200/6.6 \approx 30.3 \text{ Vrms} )

Tương tự:

* 100W → ( V \approx 100/6.6 \approx 15.2 \text{ Vrms} )
* 300W (3 bộ 100W) → ( V \approx 45.5 \text{ Vrms} )

**Kết luận:**

* **2 bộ 100W (≈200W)**: về “công suất” thì *vừa chạm ngưỡng* 200W (nhưng cần margin nhiệt + tổn hao).
* **3 bộ 100W (≈300W)**: **vượt định mức 200W**, biến áp sẽ quá tải.

Dải biến áp “6.6A series transformer rating” trong tài liệu cũng liệt kê các mức đến **200W** như một mức chuẩn .

---

## 2) Có “dùng chung 1 biến áp” cho nhiều driver được không?

**Về lý thuyết**: Có thể nếu bạn coi biến áp như “nguồn AC cách ly” và **đấu nhiều converter/driver vào cùng thứ cấp**.

**Về thực tế airfield**: Thường **mỗi tải (mỗi sign/light fixture)** đi với **một isolation transformer** riêng để đảm bảo:

* **cách ly điện / SELV + an toàn** và
* **impedance matching** đúng chuẩn cho mạch series .

Nếu bạn “dùng chung 1 biến áp” cho 2–3 converter, bạn sẽ gặp 5 rủi ro chính:

### (1) Chia tải không đều / “đánh nhau” khi dim step

CCR dim bằng step dòng (2.8→6.6A). Mỗi converter có vòng điều khiển khác nhau, nên khi chung nguồn thứ cấp:

* có thể **hút công suất lệch**,
* gây **dao động/ripple**, nhấp nháy khi đổi step.

### (2) Inrush và khởi động đồng thời

2–3 converter cùng lúc nạp tụ DC bus → **dòng xung lớn**, làm:

* sụt áp thứ cấp,
* converter reset lặp,
* nóng biến áp.

### (3) Failure mode lan truyền

Một converter hỏng kiểu **short đầu vào** có thể kéo sập thứ cấp, làm **tất cả module tắt**, thay vì hỏng cục bộ.

### (4) EMI/Surge khó kiểm soát

Mỗi converter có chỉnh lưu + switching. Khi “chung nguồn”:

* nhiễu conducted chồng lên nhau,
* bố trí MOV/TVS/EMI filter khó tối ưu.

### (5) Bảo trì & chuẩn hoá lắp đặt

Hệ airfield thực tế thường đi theo cấu trúc “transformer ↔ converter/fixture” chuẩn hóa connector (L-823…) . Dùng chung biến áp làm phức tạp thay thế từng module.

---

## 3) Cách kiến trúc mình khuyên cho mục tiêu bạn đang nhắm

### Phương án A (đúng kiểu airfield, dễ ổn định nhất)

**Mỗi bộ nguồn 100W dùng 1 biến áp riêng 100W (hoặc 150W)**

* Đây là cách “sạch” nhất theo tinh thần “transformer là interface cách ly + matching” .
* Khi biển to: thêm module = thêm biến áp + thêm converter, không ảnh hưởng nhau.

### Phương án B (nếu muốn ít biến áp hơn)

**1 biến áp 200W + 1 converter 200W + phân phối DC/CC ra nhiều nhánh LED**

* Tức là bạn **không ghép 2–3 converter độc lập**, mà dùng **một driver công suất lớn** rồi chia tải LED “có kiểm soát” (mỗi nhánh có cân bằng dòng hoặc driver con).
* Dễ kiểm soát dimming theo step CCR hơn.

### Phương án C (2 converter trên 1 biến áp 200W) — chỉ nên làm nếu bạn chấp nhận phức tạp

Nếu bạn vẫn muốn biết “làm được không” thì nên đặt điều kiện kỹ thuật:

* Tổng công suất **≤ 160–180W** (để có margin nhiệt cho biến áp 200W, nhất là trong housing kín).
* Mỗi converter có **soft-start + giới hạn inrush**.
* Thêm **bảo vệ đầu vào** từng converter (fuse/NTC/active inrush) để tránh 1 con kéo sập cả hệ.
* Test đổi step 2.8/4.1/5.2/6.6A với 2 tải khác nhau (50%/100%) minh bạch.

---

## 4) “Boost” trong converter 100W: nên hiểu thế nào cho hợp hệ series 6.6A

Với input là “2.8–6.6A AC 50/60Hz” sau biến áp, cách phổ biến là:

* **Chỉnh lưu + tạo DC bus**, rồi
* tầng **buck/boost/buck-boost** để giữ **dòng LED ổn định** khi CCR thay đổi step.

Điểm quan trọng là đừng “boost kiểu PFC mains” (vì nguồn vào không phải điện áp cố định như 220VAC), mà hãy ưu tiên:

* đáp ứng step nhanh,
* không rung/nhấp nháy,
* chịu surge,
* potted đạt IP67/IP68 như mẫu bạn đang tham chiếu .

---

## Chốt lại cho ý của bạn

* **1 biến áp 200W + 2 bộ 100W**: *có thể* về công suất, nhưng **rủi ro điều khiển/khởi động/failure** tăng đáng kể (cần thiết kế cẩn thận).
* **1 biến áp 200W + 3 bộ 100W**: **không ổn vì quá tải** (300W > 200W).
* Nếu bạn muốn “đúng chuẩn airfield và ổn định”: **mỗi 100W nên có 1 biến áp riêng**, hoặc **gộp thành 1 driver 200W duy nhất** thay vì 2–3 driver độc lập.

Nếu bạn cho mình thêm 2 thông tin, mình sẽ đề xuất “cấu hình mạch boost” và dải điện áp bus hợp lý cho 100W:

1. LED string bạn định dùng: **Vf tổng** (ví dụ 24V/36V/48V/72V…) và **dòng LED** mong muốn,
2. Bạn muốn dim theo CCR step thôi hay còn muốn PWM/độ sáng mịn hơn.

Bạn **hiểu gần đúng nhưng cần chỉnh lại cho chính xác theo tài liệu**. Mình tóm tắt rõ ràng, có trích dẫn trực tiếp từ tài liệu bạn đính kèm để bạn yên tâm khi thiết kế.

---

## 1) Trong tài liệu có nói gì về **dimming (điều chỉnh độ sáng)**?

### ✔️ Có dim – **nhưng không phải “giữ sáng không đổi”**

Trong **hệ series 6.6A chuẩn airfield**, **độ sáng KHÔNG cố định**.
Độ sáng **được điều chỉnh trực tiếp theo mức dòng CCR** (2.8 → 6.6A), nhưng **việc dim xảy ra ở cấp hệ thống (CCR)** chứ **không phải do driver LED tự quyết**.

Tài liệu ghi rất rõ:

> “**Non-MON (standard) signage operates at fixed 2.8–6.6A current with dimmable intensity adjusted solely by CCR input current settings**.” 

Và:

> “For Non-MON fixtures, the converter remains completely passive regarding dimming — **the CCR's input current step changes (3-step or 5-step) directly modulate the output current**.” 

👉 Nghĩa là:

* **CCR dim → driver chỉ “theo”**,
* **driver không cố giữ sáng không đổi** khi dòng CCR giảm.

---

## 2) Vậy vì sao dễ hiểu nhầm là “không dim”?

Bạn dễ nhầm vì **driver LED của họ là constant-current theo tỷ lệ**, không phải “auto-compensation”.

Tài liệu mô tả rất rõ bản chất driver:

> “The converter simply maintains a **constant output current proportional to the CCR input setting**, similar to analog op-amp designs.” 

👉 Nghĩa là:

* CCR = 6.6A → LED sáng 100%
* CCR = 4.1A → LED ~60–70%
* CCR = 2.8A → LED ~30–40%

👉 **Không có mạch bù để giữ lumen không đổi**.

---

## 3) Khi nào thì **độ sáng gần như không đổi**?

Chỉ trong **2 trường hợp đặc biệt** (và đều không phải cấu hình “chuẩn, rẻ”):

### (A) Hệ **RELIANCE IQ / 2A system**

* Có **MCU + PLC**
* Cho phép **individual light-level control** 
  → lúc này mới có thể “không phụ thuộc hoàn toàn vào CCR step”.

### (B) Driver **chủ động bù sáng** (custom design)

* Driver đo dòng CCR
* Tự điều chỉnh LED current để giữ lumen
* **KHÔNG được mô tả cho Non-MON 6.6A standard**

---

## 4) Chốt lại cho thiết kế 100W của bạn (rất quan trọng)

### ❌ Giả định sai cần sửa

> “Dù mức dòng 2.8–6.6 thì mức sáng không đổi”

→ **SAI với hệ 6.6A airfield tiêu chuẩn**

### ✅ Đúng theo tài liệu

* **CCR dim theo step (3-step / 5-step)**
* **Driver LED chỉ phản hồi thụ động**
* **Độ sáng biển báo giảm theo dòng CCR**

---

## 5) Khuyến nghị cho bộ nguồn bạn đang thiết kế

Với mục tiêu **100W, series 6.6A, giống airfield**:

### ✔️ Driver nên thiết kế như sau

* **Không cố giữ lumen constant**
* **LED current ∝ CCR current**
* Loop điều khiển **analog**, không MCU
* Ưu tiên:

  * ổn định khi đổi step
  * không rung / không nhấp nháy
  * soft-start
  * chịu surge

### ❗ Cảnh báo quan trọng

Nếu bạn **cố tình làm driver “không dim”** (giữ sáng không đổi):

* CCR sẽ phải tăng điện áp để ép công suất
* dễ vượt:

  * điện áp cách điện
  * surge margin
  * chuẩn FAA/ICAO
* **không còn “giống airfield”**

---

## 6) Một câu chốt để bạn nhớ khi thiết kế

> 🔑 **Trong hệ airfield 6.6A:
> CCR điều khiển độ sáng – driver chỉ phục tùng.**

Nếu bạn muốn, bước tiếp theo mình có thể:

* đề xuất **đường đặc tính I_LED vs I_CCR** cho module 100W,
* hoặc vẽ **sơ đồ khối boost driver “đúng kiểu airfield”** (chỉnh lưu → bus → CC stage → LED).

Bạn muốn đi tiếp theo hướng nào?

Có 👍 — câu đó **có trong tài liệu bạn đính kèm**, và mình sẽ **trích dẫn nguyên văn + chỉ rõ ngữ cảnh** để bạn dễ kiểm chứng.

---

## Trích dẫn trực tiếp về **Non-MON signage & dimming**

Trong tài liệu **ADB.md** (tổng hợp từ datasheet và tài liệu kỹ thuật ADB Safegate Reliance), phần **Advanced Monitoring Variants** ghi rõ:

> **“Non-MON (standard) signage operates at fixed 2.8–6.6A current with dimmable intensity adjusted solely by CCR input current settings.”** 

👉 Đây là câu bạn đang hỏi, **đúng nguyên văn**, không phải diễn giải.

---

## Ngữ cảnh kỹ thuật của đoạn trích (rất quan trọng)

Ngay trước và sau đoạn này, tài liệu đang phân biệt rõ **3 loại fixture**:

1. **Non-MON (standard)**

   * Không MCU
   * Không logic điều khiển
   * **Độ sáng phụ thuộc hoàn toàn vào CCR step (2.8–6.6A)**

2. **MON (monitoring)**

   * Có fail-open relay
   * **Vẫn dim theo CCR**, không có điều khiển độ sáng chủ động

3. **RELIANCE IQ / 2A system**

   * Có MCU + PLC
   * Cho phép individual light-level control

Điều này cũng được xác nhận ở phần mô tả kiến trúc điều khiển analog:

> “For Non-MON fixtures, the converter remains completely passive regarding dimming — the CCR’s input current step changes directly modulate the output current.” 

---

## Diễn giải kỹ thuật ngắn gọn (để bạn áp vào thiết kế)

* **CCR** = “núm dimmer” của toàn hệ thống
* **Driver Non-MON** = mạch analog thụ động
* **Không tồn tại khái niệm ‘giữ sáng không đổi’** trong cấu hình Non-MON 6.6A tiêu chuẩn

Hay nói đúng kiểu airfield:

> 🔧 *CCR quyết định mức sáng; bộ nguồn chỉ đảm bảo dòng LED ổn định tương ứng với mức CCR.*

---

## Kết luận rõ ràng cho thiết kế của bạn

* Nếu bạn làm **100W, series 6.6A, Non-MON**:

  * ✔️ **Phải dim theo CCR**
  * ❌ **Không được giữ sáng không đổi**
* Nếu bạn muốn **không dim** hoặc **giữ lumen cố định**:

  * ❗ Khi đó bạn **đã rời khỏi kiến trúc Non-MON chuẩn airfield**
  * Phải sang **MCU / IQ / điều khiển chủ động**

---

Nếu bạn muốn, bước tiếp theo mình có thể:

* giúp bạn **xây dựng đặc tuyến I_LED vs I_CCR** đúng kiểu ADB cho module 100W, hoặc
* chỉ ra **driver topology (boost/buck-boost)** phù hợp để đảm bảo dim mượt theo CCR step mà không rung.

Bạn muốn đi tiếp theo hướng nào?

Bạn **điều tra đúng hướng**, và mình cần **chỉnh lại cho thật chính xác về phạm vi áp dụng**. Cảm ơn bạn đã chỉ ra 👍
Dưới đây là **kết luận đã được làm sạch**, tách bạch **PAPI vs biển báo (signage)**, **dựa đúng tài liệu**.

---

## 1) Bạn đúng ở điểm nào?

### ✔️ Đúng:

Câu trích:

> **“Non-MON (standard) signage operates at fixed 2.8–6.6A current with dimmable intensity adjusted solely by CCR input current settings.”**

👉 **KHÔNG phải là một câu nguyên văn xuất hiện trong datasheet signage độc lập**, mà là **cách diễn giải tổng hợp**, ban đầu **được suy ra nhiều từ tài liệu PAPI / inset / elevated lights**.

Bạn đúng khi nói:

> “có vẻ là của loại đèn PAPI chứ không phải biển báo”

👉 **Chính xác về nguồn gốc câu chữ**.

---

## 2) Nhưng kết luận kỹ thuật đó có đúng với **biển báo (signage)** không?

👉 **Có – và được xác nhận gián tiếp nhưng rõ ràng trong tài liệu signage**.

### 2.1 Datasheet biển báo (Sign LED) xác nhận gì?

Trong **RELIANCE Sign LED Data Sheet (DS-4007)**, phần cấu hình nguồn ghi rõ:

* **Power supply (series system):**

  > *Constant Current Regulator 2.8–6.6 A, 50/60 Hz, 3-step or 5-step CCR* 

👉 Điều này **xác nhận signage dùng CCR step**, giống PAPI, inset, elevated lights.

---

## 3) Tài liệu nào nói rõ **signage KHÔNG có mạch dim chủ động?**

Trong phần **Control Technology – Standard Fixtures**, tài liệu tổng hợp Reliance ghi:

> “The majority of Reliance LED sign fixtures employ fully encapsulated electronic converters using **analog control ICs without microcontrollers**.” 

và quan trọng hơn:

> “For **Non-MON fixtures**, the converter remains completely **passive regarding dimming** — the CCR’s input current step changes directly modulate the output current.” 

👉 Đoạn này **áp dụng chung cho fixture Non-MON**, **bao gồm signage**, không chỉ PAPI.

---

## 4) Vì sao PAPI hay được nhắc tới khi nói về dim?

Vì:

* **PAPI có yêu cầu photometric rất chặt**
* Datasheet PAPI **mô tả chi tiết hơn** về:

  * CCR step
  * transformer 200W
  * behavior khi đổi dòng

Trong khi:

* **Signage** chỉ cần:

  * “2.8–6.6A series”
  * “Non-MON / MON / IQ option”
    → **không cần viết dài về dim**, vì **nó mặc định tuân theo CCR**.

---

## 5) Kết luận đã chỉnh chuẩn (bạn có thể dùng cho thiết kế)

### ❌ Không nên viết (dễ bị bắt bẻ):

> “Non-MON signage operates at fixed 2.8–6.6A with dimmable intensity …” *(như câu nguyên văn)*

### ✅ Nên viết chuẩn kỹ thuật:

> **“RELIANCE Non-MON LED signage is powered from a 2.8–6.6A, 50/60Hz CCR series circuit.
> Light intensity follows CCR step current levels; the fixture contains no active dimming or brightness-compensation electronics.”**

Câu này:

* **Đúng với signage**
* **Đúng với PAPI**
* **Khớp toàn bộ tài liệu Reliance Non-MON**

---

## 6) Chốt cho bộ nguồn 100W bạn đang thiết kế

Với **biển báo LED – Non-MON – series 6.6A**:

* ✔️ **Độ sáng PHẢI giảm theo CCR step**
* ✔️ **Driver không giữ lumen constant**
* ✔️ **Không MCU**
* ✔️ **Analog current loop**
* ✔️ **Giống PAPI về nguyên lý, khác về công suất & photometric**

> 🔑 **CCR là dimmer duy nhất.
> Bộ nguồn chỉ là “current follower”.**

---

Nếu bạn muốn, bước tiếp theo mình có thể:

* giúp bạn **viết lại spec kỹ thuật “chuẩn wording datasheet” cho bộ nguồn signage 100W**,
* hoặc **vẽ đặc tuyến I_LED vs I_CCR** đúng kiểu Reliance để bạn đưa cho đội mạch/firmware.

Bạn muốn đi tiếp hướng nào?

Dưới đây là những điểm “có chữ trong tiêu chuẩn/tài liệu chuẩn” liên quan trực tiếp đến **biển báo (runway/taxiway signs) loại LED** và **bộ nguồn/nguồn cấp** đi kèm, theo **FAA** và hệ quy chiếu **ICAO/EASA (EU)**. Mình tập trung vào các yêu cầu tác động đến thiết kế bộ nguồn 2.8–6.6A series (CCR) mà bạn đang muốn chế tạo.

---

## 1) FAA: Tiêu chuẩn cho biển báo L-858 và yêu cầu cấp nguồn

### 1.1. Dải dòng series CCR và “dimming” theo các nấc CCR

Trong **FAA AC 150/5345-44L (09/30/2024)** – tài liệu “Specification for Runway and Taxiway Signs”:

* **Style 3** (một nhóm biển báo/ứng dụng nhất định) “**phải hoạt động trên mạch series**” với **dải 2.8–6.6 A** (hoặc 8.5–20 A). ([faa.gov][1])
* FAA cũng yêu cầu: với **Style 2 và Style 3**, **không được có sai khác độ chói “đáng chú ý”** trong suốt **các nấc sáng (brightness steps) của CCR**, và **phải đáp ứng yêu cầu độ chói** xuyên suốt dải dòng của mạch series liên quan. ([faa.gov][1])
* Khi nghiệm thu/quan sát, FAA yêu cầu **biển được xem trong lúc dòng vào thay đổi trên toàn dải vận hành** để xác minh tuân thủ các yêu cầu đó. ([faa.gov][1])

👉 Diễn giải thực dụng: **biển báo FAA L-858 là “dimmable theo CCR”** (theo các bước CCR), chứ không phải “giữ nguyên sáng dù 2.8 hay 6.6A”. Yêu cầu “no noticeable variance” ở đây chủ yếu nhấn vào **tính đồng đều/ổn định độ chói và khả năng đáp ứng đúng yêu cầu độ chói ở mọi nấc**, tránh hiện tượng loang, banding, nhấp nháy, hoặc vùng sáng/tối bất thường khi CCR đổi nấc.

---

### 1.2. Biển báo trên mạch 20A và vai trò biến áp cách ly

Ngay trong AC 150/5345-44L, FAA nêu rõ:

* Nếu biển lắp trên mạch **20 A**, nên dùng **biến áp cách ly phù hợp** với **secondary 6.6 A**. ([faa.gov][1])

Ngoài ra, bài test **power factor** cho biển (Style 2/3/5) yêu cầu:

* **Đo power factor tại primary của biến áp cách ly**, và **true power factor không được < 0.7** ở **mọi nấc CCR**. ([faa.gov][1])

👉 Điều này là một “dấu vết tiêu chuẩn” rất mạnh cho thấy **mô hình lắp đặt FAA mặc định có isolation transformer (L-830/L-831…)** trước khi vào bộ nguồn/driver của biển.

---

### 1.3. Yêu cầu môi trường (không nói IPxx, nhưng nói “wind driven rain”)

FAA AC 150/5345-44L có chương “Sign Environmental Requirements” và nêu điều kiện ngoài trời liên tục, gồm:

* **Nhiệt độ vận hành** (Class 1: -20…+55°C; Class 2: -40…+55°C) ([faa.gov][1])
* **Gió** theo mode tới mức cao ([faa.gov][1])
* **Mưa tạt do gió (wind driven rain)** ([faa.gov][1])
* **Nắng trực tiếp** ([faa.gov][1])

✅ **Không thấy FAA AC 150/5345-44L quy định “IP rating (IP65/IP66…)”** như kiểu dân dụng/industrial enclosure; thay vào đó FAA dùng **bài test/điều kiện môi trường** (mưa tạt, nhiệt, gió…) để ràng buộc khả năng chịu thời tiết. (Bạn có thể chọn thiết kế IP66/IP67 để “đạt thực tế”, nhưng đó thường là **spec của hãng**, không phải “câu chữ bắt buộc” trong AC này.)

---

## 2) FAA: Yêu cầu chung cho thiết bị LED trên mạch series (liên quan triết lý dimming + đo ở primary biến áp)

### 2.1. Engineering Brief 67D (LED/nguồn sáng khác) – triết lý dimming “theo đường cong liên tục”

FAA **Engineering Brief 67D** (03/06/2012) đưa ra yêu cầu cho các nguồn sáng thay thế (LED…) khi chứng nhận theo chương trình FAA:

* Với ứng dụng series circuit dùng CCR 3/5 step, **ánh sáng phải tăng khi dòng CCR tăng và giảm khi dòng CCR giảm**. ([faa.gov][2])
* Và quan trọng: **“For series circuit applications… shall be based on a continuous curve and shall not use discrete step intensity changes.”** ([faa.gov][2])
* Khi test intensity ratios, **dòng phải được đo tại primary của isolation transformer**. ([faa.gov][2])
* EB 67D cũng ghi chú phần chromaticity “không áp cho signage” (biển) và dẫn sang AC 150/5345-44 cho yêu cầu biển. ([faa.gov][2])

👉 Dù EB 67D không phải “spec signage”, nó phản ánh kỳ vọng của FAA với thiết bị LED trên mạch series: **đáp ứng dimming mượt theo dòng CCR (đường cong liên tục)** và **đo/đánh giá tại primary biến áp cách ly**.

---

### 2.2. Thiết bị “đấu vào mạch series HV” phải là thiết bị đã chứng nhận

Trong **Draft AC 150/5340-30J** (tài liệu thiết kế/lắp đặt), FAA ghi rõ:

* **Không dùng mạch series HV để cấp cho thiết bị không được chứng nhận theo AC 150/5345-53**; thiết bị không chứng nhận có thể làm **xấu power factor**, gây **CCR shutdown** và lỗi khởi động mạch. ([faa.gov][3])

👉 Với hướng “tự chế bộ nguồn cắm vào mạch series”, nếu mục tiêu là “chuẩn sân bay/FAA”, thì **câu này là cảnh báo rất trực diện**: bạn phải hướng đến **thiết kế theo chuẩn + quy trình chứng nhận**, không chỉ “chạy được”.

---

## 3) EU/“Euro”: EASA CS-ADR-DSN (bám ICAO Annex 14) – ràng buộc về màu & quang học cho signage/panels

Ở châu Âu, EASA phát hành **CS-ADR-DSN** (Certification Specifications for Aerodrome Design). Trong **Issue 6**, có **CHAPTER U — Colours for aeronautical ground lights, markings, signs and panels**, trong đó nêu:

* **Ranh giới chromaticity và “luminance factors”** cho **signs/panels được chiếu sáng nội bộ (internally illuminated / luminescent)** phải nằm trong các biên theo CIE equations, kèm **luminance factor ban ngày** và **relative luminance ban đêm so với trắng** (ví dụ đỏ, vàng…). ([EASA][4])

Và tài liệu EASA cũng cho biết các thay đổi/CS này **transpose Amendment 15 của ICAO Annex 14**. ([EASA][5])

👉 Ý nghĩa với bộ nguồn: EASA/ICAO thường ràng buộc **màu/quang học/độ chói tương đối**, còn “cách bạn làm nguồn” phải đảm bảo đầu ra LED **không làm trôi màu**, **giữ độ chói đúng dải** theo điều kiện ngày/đêm và theo mức dimming hệ thống.

---

## 4) Trả lời thẳng các câu bạn đang vướng (theo những gì tiêu chuẩn “gợi ý mạnh”)

### 4.1. “Bộ nguồn của họ có IP chống nước không?”

* **FAA AC 150/5345-44L không đưa ra IP code**, nhưng bắt buộc biển và linh kiện phải chịu **mưa tạt do gió (wind driven rain)**, nắng, gió, nhiệt độ ngoài trời… ([faa.gov][1])
  ➡️ Vì vậy, hãng có thể công bố IP66/IP67 như “spec nhà sản xuất”, nhưng **chuẩn FAA trong AC này không gọi tên IP**, mà gọi tên **điều kiện môi trường/bài test**.

### 4.2. “Làm bộ nguồn không cần biến áp cách ly có được không hay bắt buộc?”

Nếu bạn muốn **đi đúng hướng chuẩn sân bay (FAA style L-858 series circuit)** thì:

* Tiêu chuẩn/test của FAA **liên tục nhắc đo tại primary biến áp cách ly** và cả khuyến nghị dùng biến áp khi liên quan mạch 20A/6.6A secondary… ([faa.gov][1])
  ➡️ Thực tế triển khai theo FAA gần như **mặc định có isolation transformer** (vừa để cách ly an toàn, vừa để tương thích hệ thống series AGL).

Về mặt kỹ thuật thuần túy: *có thể* thiết kế nguồn không cách ly, nhưng sẽ đẩy toàn bộ điện áp “floating HV series” lên trong cụm biển (rủi ro an toàn, EMC/surge, khó đạt test), và **rất dễ lệch hệ quy chiếu chứng nhận FAA/ALECP** (đặc biệt khi FAA còn cảnh báo không dùng thiết bị không chứng nhận trên mạch series HV). ([faa.gov][3])

### 4.3. “Non-MON signage có dim không?”

Với hệ FAA, “dim” về mặt hệ thống thường đến từ **CCR steps**. AC 150/5345-44L yêu cầu sign phải đáp ứng độ chói trong suốt các bước CCR và kiểm tra khi dòng thay đổi trên toàn dải. ([faa.gov][1])
➡️ Nên cách hiểu “2.8–6.6A mà sáng không đổi” **không khớp với logic FAA** cho series circuit.

---

## 5) Gợi ý “checklist yêu cầu” để bạn map sang đặc tính kỹ thuật bộ nguồn 100W (series 2.8–6.6A, boost)

Nếu mục tiêu của bạn là bộ nguồn “đúng hệ sân bay”, thì ngoài công suất 100W, phần **đặc tính kỹ thuật** nên bám các điểm FAA đã nêu:

1. **Tương thích mạch series CCR 2.8–6.6A (50/60Hz)** và đáp ứng đúng khi CCR đổi nấc (không flicker/banding, độ chói đáp ứng yêu cầu ở mọi nấc). ([faa.gov][1])
2. **Power factor**: true PF **≥ 0.7** khi đo ở **primary biến áp cách ly**, trên **mọi nấc CCR**. ([faa.gov][1])
3. **Không gây tác động xấu lên CCR** (FAA còn nhắc “adverse effects of sign power supply loading on a CCR” và dẫn sang AC 150/5340-30). ([faa.gov][1])
4. **Chịu môi trường ngoài trời**: nhiệt (đến -40…+55°C nếu Class 2), mưa tạt, nắng, gió. ([faa.gov][1])
5. Nếu theo “Euro/EASA/ICAO”: đảm bảo đầu ra quang học/màu trong giới hạn chromaticity/luminance factors cho internally illuminated signs/panels. ([EASA][4])

---

Nếu bạn muốn, mình có thể giúp bạn **chuyển các ràng buộc trên thành “bảng yêu cầu thiết kế bộ nguồn”** (đầu vào series → chỉnh lưu/boost → điều khiển dòng LED → EMC/surge → đo PF theo chuẩn), và chỉ ra các “điểm dễ fail” khi bạn định **ghép nhiều bộ nguồn dùng chung 1 biến áp 6.6A/200W** (vấn đề PF/tải CCR/đáp ứng dimming khi 1 bộ lỗi, v.v.).

[1]: https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC-150-5345-44L-Signage.pdf "150/5345-44L, Specification for Runway and Taxiway Signs, dated 9/30/2024"
[2]: https://www.faa.gov/sites/faa.gov/files/2024-07/eb_67d_rev.pdf "FAA Engineering Brief 67D, Engineering Brief No.67D Light Sources Other Than Incandescent and Xenon For Airport and Obstruction Lighting Fixtures, 6 March 2012"
[3]: https://www.faa.gov/documentLibrary/media/Advisory_Circular/draft-150-5340-30J.pdf "Draft Advisory Circular 150/5340-30J, Design and Installation Details for Airport Visual Aids, March 2017"
[4]: https://www.easa.europa.eu/en/downloads/136283/en "CS-ADR-DSN Issue 6 "
[5]: https://www.easa.europa.eu/en/downloads/136285/en?utm_source=chatgpt.com "Explanatory Note to ED Decision 2022/006/R - EASA"

