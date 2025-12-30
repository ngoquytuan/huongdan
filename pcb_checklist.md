### Tài Liệu Rule Check Design PCB: Chống Nhiễu EMI Cho Hiển Thị (LED 7-Segment với MAX7219 & LCD Text/Graphic)

Dưới đây là tổng hợp tất cả các cách chống nhiễu EMI (Electromagnetic Interference) mà chúng ta đã thảo luận, được cấu trúc thành dạng **checklist quy tắc thiết kế PCB** (Design Rules Checklist). Các quy tắc này áp dụng cho môi trường noisy (như gần motor/khoan điện), tập trung vào radiated/conducted EMI ảnh hưởng đến tín hiệu SPI/I2C/parallel và nguồn. Chúng được phân loại theo giai đoạn thiết kế (Layout, Linh kiện thụ động, Tín hiệu, Shielding, Phần mềm) để dễ kiểm tra và áp dụng.

Sử dụng checklist này trong quá trình review PCB: Đánh dấu ✓ cho mỗi rule đã tuân thủ. Ưu tiên hardware fix trước phần mềm. Các giá trị linh kiện là khuyến nghị phổ biến; test thực tế để điều chỉnh.

#### 1. **Layout & Routing (Thiết Kế Mạch In)**
   - [ ] Giữ dây tín hiệu (SPI/I2C/parallel: DIN/CLK/CS/RS/EN/D0-D7) ngắn nhất có thể (<10-20cm giữa MCU và display).
   - [ ] Sử dụng twisted pair cho tín hiệu: Xoắn dây data/clock với GND (hoặc route parallel trên PCB với ground plane ở giữa).
   - [ ] Tách biệt route nguồn (Vcc/GND) khỏi tín hiệu digital; tránh route song song dài.
   - [ ] Đặt chip driver (MAX7219/ST7920/HD44780) sát display để giảm loop antenna.
   - [ ] Sử dụng ground plane đầy đủ dưới display và tín hiệu để tăng shielding tự nhiên.
   - [ ] Tránh route gần edge PCB hoặc cạnh kim loại để giảm coupling với nhiễu ngoài.

#### 2. **Linh Kiện Thụ Động Lọc Nhiễu (Passive Filtering)**
   - **Decoupling Capacitors (Bypass cho Nguồn):**
     - [ ] Thêm tụ ceramic 0.1µF song song Vcc-GND sát chân nguồn của chip driver (MAX7219/LCD controller) và MCU.
     - [ ] Thêm tụ electrolytic 10µF song song Vcc-GND gần display để lọc ripple/low-freq noise.
     - [ ] Áp dụng tương tự cho backlight LCD (nếu có): Tụ 0.1µF trên nguồn backlight.
   - **Ferrite Beads/Cores:**
     - [ ] Lắp ferrite bead (hoặc quấn dây qua ferrite ring 2-3 vòng) trên dây nguồn Vcc/GND dẫn đến display.
     - [ ] Lắp ferrite trên các dây tín hiệu SPI/I2C (DIN, CLK, CS).
   - **Series Resistors (Damping cho Tín Hiệu):**
     - [ ] Thêm resistor nối tiếp 100-330Ω trên mỗi đường tín hiệu SPI/I2C/parallel (DIN/CLK/CS/RS/EN/D0-D7), đặt sát phía MCU.
     - [ ] Đối với LCD parallel: Thêm pull-up resistors 4.7kΩ trên data lines (D0-D7) để tăng noise margin.
   - **Điều Chỉnh Cường Độ (cho LED):**
     - [ ] Tăng giá trị resistor ISET trên MAX7219 lên 40-50kΩ để giảm current LED (5-10mA), giảm EMI nội bộ.

#### 3. **Tối Ưu Hóa Tín Hiệu & Clock (Signal Integrity)**
   - [ ] Giảm tốc độ giao tiếp: SPI/I2C clock xuống 500kHz-1MHz (thay vì max 10MHz); test để cân bằng tốc độ và noise immunity.
   - [ ] Sử dụng slew-rate limiting (nếu chip hỗ trợ, như MAX7221 thay MAX7219) để làm mượt edge tín hiệu.
   - [ ] Kiểm tra impedance matching: Đảm bảo trace width phù hợp (50Ω cho SPI nếu cần high-speed).

#### 4. **Shielding & Cách Ly (Bảo Vệ Vật Lý)**
   - [ ] Sử dụng hộp kim loại grounded (kết nối với GND PCB) bao quanh toàn bộ display/MCU để chắn radiated EMI.
   - [ ] Shielding thủ công: Quấn foil nhôm/EMI mesh quanh bó dây tín hiệu, connect foil đến GND.
   - [ ] Đối với LCD: Thêm EMI shielding film/mesh sau mặt display nếu lớn.
   - [ ] Cách ly tín hiệu: Sử dụng opto-isolator hoặc buffer (74HC125) trên đường SPI/parallel nếu nhiễu nặng.
   - [ ] Nguồn riêng: Sử dụng nguồn độc lập cho display nếu chia sẻ với thiết bị noisy (thêm EMI filter module như Schaffner FN nếu chung nguồn).

#### 5. **Phần Mềm Hỗ Trợ (Firmware Mitigations - Tạm Thời)**
   - [ ] Refresh display định kỳ: Resend toàn bộ data/registers mỗi 50-100ms để recover từ corruption.
   - [ ] Thêm checksum/redundancy: Gửi data với byte check; resend nếu detect lỗi.
   - [ ] Giám sát: MCU detect nhiễu (qua error flag) và retry transmission.

#### Lưu Ý Chung Khi Áp Dụng Checklist:
- **Ưu Tiên Thứ Tự**: Bắt đầu từ Layout > Linh kiện thụ động > Tín hiệu > Shielding > Phần mềm (hardware fix gốc rễ hơn).
- **Test & Verify**: Chạy test với nguồn nhiễu thực tế (khoan điện gần 10-20cm); đo oscilloscope trên tín hiệu để kiểm tra ringing/noise spikes.
- **Tuân Thủ Tiêu Chuẩn**: Tham khảo EMC (FCC/CE) cho sản phẩm hoàn chỉnh; datasheet chip (MAX7219/HD44780) có khuyến nghị cơ bản.
- **Chi Phí & Linh Hoạt**: Các rule này dễ thêm "câu kéo" nếu PCB đã fixed; ferrite/tụ rẻ (<1 USD/module).

Checklist này có thể copy-paste vào Notion/Markdown/Word để lưu làm template. Nếu cần thêm chi tiết (ví dụ schematic mẫu) hoặc mở rộng cho loại display khác, cho tôi biết nhé!
