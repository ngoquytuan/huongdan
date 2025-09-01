Cảm ơn bạn đã đặt câu hỏi chi tiết! Dưới đây, mình sẽ giải đáp từng vấn đề liên quan đến việc sử dụng **WireGuard VPN** trên **MikroTik PC** (CPU N4100, SSD 100GB, 4 cổng LAN 2.5G) để truy cập các dịch vụ (camera, Nextcloud, Emby) từ xa qua mạng 4G, như thể điện thoại của bạn đang ở nhà. Mình cũng sẽ giải thích về nhà cung cấp dịch vụ VPN, mức độ an toàn, tốc độ, và chi phí.

---

### 1. Sau khi truy cập VPN, điện thoại của bạn như đang ở nhà đúng không?
**Đúng vậy!**  
Khi bạn kết nối qua **WireGuard VPN** từ điện thoại (qua mạng 4G) đến MikroTik, điện thoại sẽ được gán một IP trong mạng VPN (ví dụ: `10.0.0.2`) và có thể truy cập các thiết bị trong mạng nhà như thể nó đang ở trong mạng nội bộ. Cụ thể:

- **Truy cập dịch vụ**:
  - Camera (`192.168.10.3` trong VLAN 10): Gõ `rtsp://192.168.10.3:554`.
  - Nextcloud (`192.168.20.10` trong VLAN 20): Gõ `http://192.168.20.10`.
  - Emby (`192.168.20.10`): Gõ `http://192.168.20.10:8096`.
- **Cơ chế hoạt động**:
  - WireGuard tạo một **đường hầm mã hóa** giữa điện thoại và MikroTik, cho phép điện thoại gửi/nhận lưu lượng đến các VLAN (10, 20) như khi bạn kết nối Wi-Fi nhà (`192.168.1.0/24`).
  - MikroTik định tuyến lưu lượng từ IP VPN (`10.0.0.2`) đến các VLAN, dựa trên quy tắc firewall và NAT đã cấu hình (xem file `wireguard_vlan_config.rsc` trong câu trả lời trước).
- **Kết quả**: Điện thoại của bạn hoạt động như một thiết bị trong mạng nhà, truy cập được camera, Nextcloud, và Emby mà không cần mở cổng công khai (80, 8096, 554) trên router nhà mạng.

---

### 2. Dịch vụ VPN do ai cung cấp?
- **Nhà cung cấp**: Trong trường hợp này, **chính MikroTik PC của bạn** cung cấp dịch vụ VPN thông qua **WireGuard**, một giao thức VPN mã nguồn mở được tích hợp sẵn trong RouterOS (phiên bản 7.x trở lên, mà MikroTik PC của bạn đang dùng).
- **Không phụ thuộc vào bên thứ ba**: 
  - Bạn không sử dụng dịch vụ VPN thương mại (như NordVPN, ExpressVPN). Thay vào đó, MikroTik đóng vai trò là **VPN server**, và điện thoại của bạn là **VPN client**.
  - Bạn tự quản lý toàn bộ cấu hình (key pair, firewall, DDNS) trên MikroTik, đảm bảo quyền kiểm soát hoàn toàn.
- **DDNS**: Bạn dùng `swatcloud.duckdns.org` (hoặc `venhadicon.ddns.net`) từ **DuckDNS**, một dịch vụ miễn phí để cập nhật IP động, cho phép điện thoại tìm MikroTik qua tên miền thay vì IP công cộng thay đổi.

---

### 3. VPN này có an toàn và bảo mật không?
WireGuard là một trong những giao thức VPN **an toàn nhất** hiện nay, và khi triển khai trên MikroTik, mức độ bảo mật phụ thuộc vào cách bạn cấu hình. Dưới đây là phân tích:

#### **Ưu điểm bảo mật**:
- **Mã hóa mạnh mẽ**:
  - WireGuard sử dụng các thuật toán mã hóa hiện đại (ChaCha20, Poly1305), bảo vệ lưu lượng giữa điện thoại và MikroTik. Hacker không thể chặn hoặc giải mã dữ liệu khi bạn truy cập qua 4G.
- **Không mở cổng dịch vụ**:
  - Chỉ cần mở cổng 51820 (UDP) trên router nhà mạng cho WireGuard. Các cổng dịch vụ (80, 8096, 554) không cần mở công khai, giảm nguy cơ bị quét hoặc tấn công.
- **Kiểm soát truy cập**:
  - MikroTik firewall giới hạn truy cập VPN chỉ từ các thiết bị có **public key** hợp lệ (ví dụ, điện thoại của bạn với IP `10.0.0.2`).
  - Quy tắc firewall chặn camera (VLAN 10) truy cập Internet và NAS (VLAN 20), đảm bảo cô lập:
    ```
    /ip firewall filter
    add chain=forward src-address=192.168.10.0/24 out-interface=ether1 action=drop
    add chain=forward dst-address=192.168.10.0/24 in-interface=ether1 action=drop
    add chain=forward src-address=192.168.10.0/24 dst-address=192.168.20.0/24 action=drop
    ```
- **Không phụ thuộc bên thứ ba**:
  - Vì bạn tự chạy VPN server trên MikroTik, không có nhà cung cấp VPN thương mại nào ghi lại dữ liệu hoặc theo dõi hoạt động của bạn.
- **DDNS an toàn**:
  - DuckDNS là dịch vụ miễn phí, mã nguồn mở, và đáng tin cậy. Chỉ cần giữ `duckdns_token` bí mật.

#### **Rủi ro tiềm tàng và cách giảm thiểu**:
- **Lộ key pair**:
  - Nếu private key của điện thoại hoặc MikroTik bị lộ, hacker có thể giả mạo kết nối. **Giảm thiểu**: Lưu trữ key an toàn, không chia sẻ; thay đổi key định kỳ:
    ```
    /interface wireguard generate-key
    ```
- **Cổng 51820 bị tấn công**:
  - Hacker có thể quét cổng 51820, nhưng WireGuard yêu cầu public key hợp lệ để kết nối, nên rất khó bị khai thác. **Giảm thiểu**: Giới hạn số lần thử kết nối:
    ```
    /ip firewall filter
    add chain=input dst-port=51820 protocol=udp action=accept
    add chain=input action=drop
    ```
- **Thiết bị bị xâm nhập**:
  - Nếu điện thoại hoặc MikroTik bị nhiễm malware, hacker có thể truy cập VPN. **Giảm thiểu**: Cập nhật RouterOS, đặt mật khẩu mạnh cho MikroTik, và kiểm tra log:
    ```
    /log print where topics=firewall
    ```
- **DDNS bị tấn công**:
  - Nếu tài khoản DuckDNS bị xâm nhập, hacker có thể thay đổi IP. **Giảm thiểu**: Dùng mật khẩu mạnh cho DuckDNS và bật xác thực hai yếu tố (nếu có).

**Kết luận**: WireGuard trên MikroTik rất an toàn khi được cấu hình đúng, vượt trội hơn so với việc mở cổng công khai (80, 8096, 554). Với firewall chặt chẽ và DDNS, bạn kiểm soát hoàn toàn bảo mật.

---

### 4. VPN có nhanh hay chậm?
Tốc độ của WireGuard phụ thuộc vào phần cứng MikroTik, tốc độ Internet nhà bạn, và mạng 4G trên điện thoại. Dưới đây là phân tích:

#### **Tốc độ WireGuard**:
- **Phần cứng MikroTik**:
  - CPU N4100 (quad-core, 1.1-2.4 GHz) đủ mạnh để xử lý mã hóa WireGuard cho 1-5 thiết bị đồng thời mà không bị nghẽn.
  - Với 4 cổng LAN 2.5G, MikroTik không giới hạn băng thông nội bộ (VLAN 10, VLAN 20).
- **Tốc độ Internet**:
  - Tốc độ VPN bị giới hạn bởi tốc độ **upload** của mạng nhà (thường thấp hơn download). Ví dụ, nếu mạng nhà có upload 20 Mbps, tốc độ VPN tối đa là ~20 Mbps.
  - Mạng 4G trên điện thoại thường có tốc độ download/upload đủ để stream video từ camera (RTSP) hoặc Emby (1080p cần ~5-10 Mbps).
- **WireGuard hiệu quả**:
  - WireGuard là giao thức VPN nhẹ, có độ trễ thấp và overhead nhỏ hơn so với OpenVPN hoặc IPsec.
  - Trong điều kiện lý tưởng, tốc độ VPN gần bằng tốc độ thực tế của Internet nhà (trừ ~5-10% do mã hóa).
- **Thực tế**:
  - **Camera**: Stream RTSP (720p-1080p) cần ~2-5 Mbps, WireGuard xử lý tốt.
  - **Emby**: Stream video 1080p cần ~5-10 Mbps, hoặc 4K cần ~25-50 Mbps (tùy codec). Nếu upload nhà bạn đủ mạnh, không bị chậm.
  - **Nextcloud**: Truy cập file hoặc web nhẹ, không đòi hỏi băng thông cao (~1-5 Mbps).

#### **Tối ưu tốc độ**:
- Đảm bảo Internet nhà có tốc độ upload tốt (kiểm tra bằng `speedtest.net`).
- Nếu stream camera hoặc Emby bị giật, giảm chất lượng video (720p thay vì 1080p).
- Kiểm tra CPU MikroTik:
  ```
  /system resource monitor
  ```
  Nếu CPU gần 100%, giảm số lượng thiết bị kết nối VPN đồng thời.

**Kết luận**: WireGuard trên MikroTik rất nhanh, đủ để stream camera, Emby, hoặc dùng Nextcloud qua 4G, miễn là tốc độ upload của mạng nhà không quá thấp.

---

### 5. VPN có mất phí không?
- **WireGuard trên MikroTik**: **Hoàn toàn miễn phí**.
  - WireGuard là giao thức mã nguồn mở, tích hợp sẵn trong RouterOS (không cần mua license).
  - MikroTik PC của bạn đã hỗ trợ WireGuard, không cần phần cứng/phần mềm bổ sung.
- **DuckDNS**: **Miễn phí**.
  - DuckDNS là dịch vụ DDNS miễn phí, chỉ cần đăng ký tài khoản và lấy token.
- **Chi phí tiềm tàng**:
  - **Internet nhà**: Bạn cần gói cước Internet có IP động hoặc tĩnh (IP động đủ dùng với DuckDNS).
  - **Điện thoại**: Mạng 4G có thể tốn phí dữ liệu, tùy nhà mạng (Việt Nam: Viettel, Mobifone, v.v.). Stream video qua 4G (camera, Emby) có thể tiêu tốn ~1-2 GB/giờ cho 1080p.
  - **Router nhà mạng**: Không tốn phí thêm, chỉ cần mở cổng 51820 (miễn phí trên hầu hết router).

**Kết luận**: Giải pháp này **không mất phí**, trừ chi phí Internet nhà và dữ liệu 4G (nếu có). Bạn tự quản lý VPN, không phụ thuộc vào dịch vụ trả phí.

---

### 6. Đề xuất cụ thể
- **Cấu hình WireGuard**: Sử dụng file `wireguard_vlan_config.rsc` từ câu trả lời trước để thiết lập VPN:
  - MikroTik: `wg1`, IP `10.0.0.1`, cổng 51820.
  - Điện thoại: IP `10.0.0.2`, kết nối qua `swatcloud.duckdns.org:51820`.
- **Truy cập dịch vụ**:
  - Camera: `rtsp://192.168.10.3:554`.
  - Nextcloud: `http://192.168.20.10`.
  - Emby: `http://192.168.20.10:8096`.
- **Bảo mật**:
  - Kiểm tra log để phát hiện kết nối lạ từ camera:
    ```
    /log print where topics=firewall
    ```
  - Giữ key pair an toàn, thay đổi định kỳ.
- **Tốc độ**:
  - Kiểm tra tốc độ upload của mạng nhà.
  - Giảm chất lượng video nếu stream bị giật.

---

### 7. Hỏi thêm
- Bạn muốn hướng dẫn chi tiết cách thay đổi key pair WireGuard định kỳ?
- Cần hỗ trợ thêm cổng dịch vụ khác trên DietPi (ngoài 80, 8096)?
- Hoặc muốn kiểm tra tốc độ VPN bằng công cụ trên MikroTik?
Hãy cung cấp thêm thông tin (như tốc độ Internet nhà, số lượng camera, hoặc model router Wi-Fi) để mình tối ưu hơn!
---
Dưới đây là hướng dẫn chi tiết để **cài đặt và triển khai WireGuard VPN** trên **MikroTik PC** (CPU N4100, SSD 100GB, 4 cổng LAN 2.5G) và **điện thoại** (iOS/Android) cũng như **máy tính** (Windows/Linux/Mac) để bạn có thể truy cập các dịch vụ như camera (`192.168.10.3` trong VLAN 10), Nextcloud, và Emby (`192.168.20.10` trong VLAN 20) từ xa (qua mạng 4G hoặc Internet khác) mà không cần mở cổng công khai (80, 8096, 554) trên router nhà mạng. Hướng dẫn bao gồm kích hoạt, cấu hình, kiểm tra trên MikroTik, và triển khai trên điện thoại/máy tính, sử dụng **DDNS** (`swatcloud.duckdns.org` hoặc `venhadicon.ddns.net`) để xử lý IP động.

---

### 1. Tổng quan và giả định
- **Mục tiêu**: 
  - Thiết lập WireGuard VPN trên MikroTik để truy cập camera, Nextcloud, Emby từ xa.
  - Đảm bảo camera trong VLAN 10 bị cô lập, không kết nối Internet.
  - Điện thoại/máy tính kết nối qua VPN như thể đang ở trong mạng nhà (`192.168.1.0/24`, VLAN 10, VLAN 20).
- **Giả định**:
  - **MikroTik**: IP `192.168.1.2` trên mạng Wi-Fi nhà mạng (`ether1`), chạy RouterOS 7.x (hỗ trợ WireGuard).
  - **Camera**: `192.168.10.3` (VLAN 10, cổng `ether2`, cổng 554/RTSP, 80/web).
  - **DietPi PC**: `192.168.20.10` (VLAN 20, cổng `ether3`, Nextcloud cổng 80, Emby cổng 8096).
  - **PC/điện thoại cục bộ**: `192.168.1.37` (mạng Wi-Fi nhà mạng).
  - **Router nhà mạng**: `192.168.1.1`, hỗ trợ mở cổng (51820/UDP) cho WireGuard.
  - **DDNS**: `swatcloud.duckdns.org` (hoặc `venhadicon.ddns.net`).
- **Yêu cầu**:
  - Chỉ mở cổng 51820 (UDP) trên router nhà mạng.
  - Camera không kết nối cloud/Internet.
  - Điện thoại/máy tính truy cập dịch vụ từ xa qua 4G/Internet.

---

### 2. Cấu hình WireGuard trên MikroTik

#### Bước 1: Kích hoạt WireGuard
RouterOS 7.x trên MikroTik đã tích hợp sẵn WireGuard, nên không cần cài đặt thêm. Kiểm tra phiên bản RouterOS:
```
/system package print
```
- Nếu RouterOS < 7.0, nâng cấp:
  ```
  /system package update
  ```
- Đảm bảo MikroTik có kết nối Internet qua router nhà mạng (`192.168.1.1`).

#### Bước 2: Tạo giao diện WireGuard
Tạo giao diện WireGuard và gán IP:
```
/interface wireguard
add name=wg1 listen-port=51820 private-key="your_private_key"
/ip address
add address=10.0.0.1/24 interface=wg1
```
- **Tạo private key**:
  ```
  /interface wireguard generate-key
  ```
  Sao chép **public key** của `wg1` (ví dụ: `aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789abcdefg=`), cần dùng cho client (điện thoại/máy tính).
- **Lưu ý**: Thay `your_private_key` bằng private key thực tế hoặc để MikroTik tự tạo.

#### Bước 3: Cấu hình VLAN và cô lập camera
Dùng cấu hình VLAN từ trước để đặt camera trong VLAN 10, DietPi PC trong VLAN 20, và cô lập camera khỏi Internet:
<xaiArtifact artifact_id="a5222066-9f96-470c-979c-9c0d2fbee40c" artifact_version_id="76b723e9-241a-4bef-b369-ad7ddc80d6ee" title="wireguard_vlan_config.rsc" contentType="text/plain">
/interface bridge
add name=bridge1
/interface vlan
add name=vlan10-camera vlan-id=10 interface=bridge1
add name=vlan20-nas vlan-id=20 interface=bridge1
/ip address
add address=192.168.10.1/24 interface=vlan10-camera
add address=192.168.20.1/24 interface=vlan20-nas
add address=192.168.1.2/24 interface=ether1
add address=10.0.0.1/24 interface=wg1
/interface bridge port
add bridge=bridge1 interface=ether2 pvid=10
add bridge=bridge1 interface=ether3 pvid=20
/interface bridge
set bridge1 vlan-filtering=yes
/interface bridge vlan
add bridge=bridge1 vlan-ids=10 tagged=bridge1 untagged=ether2
add bridge=bridge1 vlan-ids=20 tagged=bridge1 untagged=ether3
/ip pool
add name=pool-camera ranges=192.168.10.2-192.168.10.254
add name=pool-nas ranges=192.168.20.2-192.168.20.254
/ip dhcp-server
add name=dhcp-camera address-pool=pool-camera interface=vlan10-camera
add name=dhcp-nas address-pool=pool-nas interface=vlan20-nas
/ip dhcp-server network
add address=192.168.10.0/24 gateway=192.168.10.1 dns-server=192.168.10.1
add address=192.168.20.0/24 gateway=192.168.20.1 dns-server=192.168.20.1
/ip route
add gateway=192.168.1.1
/interface wireguard
add name=wg1 listen-port=51820 private-key="your_private_key"
/interface wireguard peers
add interface=wg1 public-key="phone_public_key" allowed-address=10.0.0.2/32
add interface=wg1 public-key="pc_public_key" allowed-address=10.0.0.3/32
/ip firewall filter
add chain=forward src-address=192.168.10.0/24 action=log log-prefix="Camera-Out" comment="Log Camera outgoing traffic"
add chain=forward dst-address=192.168.10.0/24 action=log log-prefix="Camera-In" comment="Log Camera incoming traffic"
add chain=forward src-address=192.168.10.0/24 out-interface=ether1 action=drop comment="Block Camera to Internet"
add chain=forward dst-address=192.168.10.0/24 in-interface=ether1 action=drop comment="Block Internet to Camera"
add chain=forward src-address=192.168.1.0/24 dst-address=192.168.10.0/24 dst-port=554,80 protocol=tcp action=accept comment="Wi-Fi to Camera"
add chain=forward src-address=192.168.10.0/24 dst-address=192.168.1.0/24 action=accept comment="Camera response to Wi-Fi"
add chain=forward src-address=192.168.1.0/24 dst-address=192.168.20.0/24 dst-port=80,8096 protocol=tcp action=accept comment="Wi-Fi to NAS"
add chain=forward src-address=192.168.20.0/24 dst-address=192.168.1.0/24 action=accept comment="NAS response to Wi-Fi"
add chain=forward src-address=192.168.10.0/24 dst-address=192.168.20.0/24 action=drop comment="Block Camera to NAS"
add chain=forward src-address=192.168.20.0/24 dst-address=192.168.10.0/24 action=drop comment="Block NAS to Camera"
add chain=input dst-port=51820 protocol=udp action=accept comment="Allow WireGuard"
add chain=forward src-address=10.0.0.0/24 dst-address=192.168.10.0/24 dst-port=554,80 protocol=tcp action=accept comment="WireGuard to Camera"
add chain=forward src-address=10.0.0.0/24 dst-address=192.168.20.0/24 dst-port=80,8096 protocol=tcp action=accept comment="WireGuard to NAS"
add chain=forward src-address=192.168.10.0/24 dst-address=10.0.0.0/24 action=accept comment="Camera response to WireGuard"
add chain=forward src-address=192.168.20.0/24 dst-address=10.0.0.0/24 action=accept comment="NAS response to WireGuard"
add chain=forward action=accept
/ip firewall nat
add chain=dstnat dst-address=192.168.1.2 dst-port=554 protocol=tcp action=dst-nat to-addresses=192.168.10.3 to-ports=554 comment="PC to Camera RTSP"
add chain=dstnat dst-address=192.168.1.2 dst-port=80 protocol=tcp action=dst-nat to-addresses=192.168.10.3 to-ports=80 comment="PC to Camera Web"
add chain=dstnat dst-address=192.168.1.2 dst-port=8080 protocol=tcp action=dst-nat to-addresses=192.168.20.10 to-ports=80 comment="PC to Nextcloud"
add chain=dstnat dst-address=192.168.1.2 dst-port=8096 protocol=tcp action=dst-nat to-addresses=192.168.20.10 to-ports=8096 comment="PC to Emby"
add chain=srcnat src-address=192.168.10.0/24 action=masquerade
add chain=srcnat src-address=192.168.20.0/24 action=masquerade
add chain=srcnat src-address=10.0.0.0/24 action=masquerade
add chain=srcnat out-interface=ether1 action=masquerade
/system script
add name=duckdns source=":global ddnsuser \"your_duckdns_token\"; \
:global ddnshost \"swatcloud.duckdns.org\"; \
:global wanif \"ether1\"; \
:local currentIP [/ip address get [/ip address find interface=\$wanif] address]; \
:local currentIP [:pick \$currentIP 0 [:find \$currentIP \"/\"]]; \
/tool fetch url=\"https://www.duckdns.org/update?domains=\$ddnshost&token=\$ddnsuser&ip=\$currentIP\" mode=https"
/system scheduler
add interval=5m name=duckdns on-event=duckdns policy=read,write,policy,test
</xaiArtifact>

- **Cập nhật**:
  - Thêm peer cho máy tính (`10.0.0.3/32`).
  - Giữ camera cô lập khỏi Internet và NAS.
  - Cho phép WireGuard (`10.0.0.0/24`) truy cập camera (cổng 554, 80) và DietPi PC (cổng 80, 8096).

#### Bước 4: Cấu hình DDNS
Đảm bảo `swatcloud.duckdns.org` cập nhật IP động:
- Đăng ký tại `duckdns.org`, lấy `duckdns_token`.
- Script DuckDNS đã có trong file trên, kiểm tra hoạt động:
  ```
  /system script run duckdns
  ```
- Xác nhận IP khớp:
  ```
  /tool fetch url="https://api.ipify.org" mode=https
  ping swatcloud.duckdns.org
  ```

#### Bước 5: Mở cổng trên router nhà mạng
- Truy cập giao diện router nhà mạng (`192.168.1.1`).
- Trong **Port Forwarding**, thêm:
  - Protocol: UDP
  - External Port: 51820
  - Internal IP: `192.168.1.2` (MikroTik)
  - Internal Port: 51820
- Lưu và kiểm tra cổng mở:
  ```
  /tool netwatch add host=swatcloud.duckdns.org port=51820
  ```

#### Bước 6: Kiểm tra WireGuard trên MikroTik
- Kiểm tra giao diện WireGuard:
  ```
  /interface wireguard print
  ```
  Xác nhận `listen-port=51820` và public key.
- Kiểm tra peer sau khi client kết nối:
  ```
  /interface wireguard peers print
  ```
  Nếu thấy `last-handshake`, VPN hoạt động.
- Kiểm tra log:
  ```
  /log print where topics=firewall
  ```
  Tìm lưu lượng từ `10.0.0.2` (điện thoại) hoặc `10.0.0.3` (máy tính).

---

### 3. Cấu hình WireGuard trên điện thoại

#### Bước 1: Cài đặt ứng dụng
- **iOS**: Tải **WireGuard** từ App Store (nhà phát triển: WireGuard Development Team).
- **Android**: Tải **WireGuard** từ Google Play Store.

#### Bước 2: Tạo cấu hình
1. Mở ứng dụng WireGuard, nhấn **Add a tunnel** (hoặc dấu `+`).
2. Chọn **Create from scratch** hoặc nhập cấu hình:
   ```
   [Interface]
   PrivateKey = <phone_private_key>
   Address = 10.0.0.2/32

   [Peer]
   PublicKey = <mikrotik_public_key>
   AllowedIPs = 192.168.10.0/24,192.168.20.0/24
   Endpoint = swatcloud.duckdns.org:51820
   PersistentKeepalive = 25
   ```
   - **PrivateKey**: Nhấn **Generate key pair** trong ứng dụng, sao chép private key và public key.
   - **PublicKey**: Public key của MikroTik (từ `/interface wireguard print`).
   - **AllowedIPs**: Cho phép truy cập VLAN 10 (camera) và VLAN 20 (DietPi PC).
3. Lưu tunnel, đặt tên (ví dụ: `Home-VPN`).

#### Bước 3: Thêm public key vào MikroTik
- Lấy public key của điện thoại (từ ứng dụng WireGuard).
- Thêm vào MikroTik:
  ```
  /interface wireguard peers
  add interface=wg1 public-key="phone_public_key" allowed-address=10.0.0.2/32
  ```

#### Bước 4: Kết nối và kiểm tra
- Bật tunnel `Home-VPN` trong ứng dụng (qua 4G).
- Truy cập:
  - Camera: `rtsp://192.168.10.3:554` (dùng VLC).
  - Nextcloud: `http://192.168.20.10`.
  - Emby: `http://192.168.20.10:8096`.
- Kiểm tra trạng thái trong ứng dụng WireGuard: Xem lưu lượng gửi/nhận.

---

### 4. Cấu hình WireGuard trên máy tính

#### Bước 1: Cài đặt ứng dụng
- **Windows**:
  - Tải WireGuard từ [wireguard.com](https://www.wireguard.com/install/).
  - Cài đặt và mở ứng dụng.
- **Linux**:
  - Cài qua terminal (Ubuntu/Debian):
    ```
    sudo apt update
    sudo apt install wireguard
    ```
- **Mac**:
  - Tải từ Mac App Store hoặc [wireguard.com](https://www.wireguard.com/install/).

#### Bước 2: Tạo cấu hình
1. Mở ứng dụng WireGuard, nhấn **Add Tunnel** > **Empty Tunnel**.
2. Nhập cấu hình:
   ```
   [Interface]
   PrivateKey = <pc_private_key>
   Address = 10.0.0.3/32

   [Peer]
   PublicKey = <mikrotik_public_key>
   AllowedIPs = 192.168.10.0/24,192.168.20.0/24
   Endpoint = swatcloud.duckdns.org:51820
   PersistentKeepalive = 25
   ```
   - **PrivateKey**: Tạo key pair trong ứng dụng hoặc dùng lệnh (Linux):
     ```
     wg genkey | tee privatekey | wg pubkey > publickey
     ```
   - **PublicKey**: Public key của MikroTik.
3. Lưu cấu hình (ví dụ: `home-vpn.conf`).

#### Bước 3: Thêm public key vào MikroTik
- Lấy public key của máy tính (từ ứng dụng hoặc file `publickey`).
- Thêm vào MikroTik:
  ```
  /interface wireguard peers
  add interface=wg1 public-key="pc_public_key" allowed-address=10.0.0.3/32
  ```

#### Bước 4: Kết nối và kiểm tra
- **Windows/Mac**: Bật tunnel trong ứng dụng WireGuard.
- **Linux**:
  ```
  sudo wg-quick up home-vpn.conf
  ```
- Truy cập:
  - Camera: `rtsp://192.168.10.3:554` (dùng VLC).
  - Nextcloud: `http://192.168.20.10`.
  - Emby: `http://192.168.20.10:8096`.
- Kiểm tra trạng thái:
  - Windows/Mac: Xem lưu lượng trong ứng dụng.
  - Linux:
    ```
    sudo wg show
    ```

---

### 5. Kiểm tra và bảo mật
- **Kiểm tra trên MikroTik**:
  - Xem peer:
    ```
    /interface wireguard peers print
    ```
    Tìm `last-handshake` cho `10.0.0.2` (điện thoại) và `10.0.0.3` (máy tính).
  - Kiểm tra log:
    ```
    /log print where topics=firewall
    ```
  - Dùng Packet Sniffer để phân tích:
    ```
    /tool sniffer quick interface=wg1
    ```
- **Bảo mật**:
  - Đặt mật khẩu mạnh cho MikroTik, giữ key pair an toàn.
  - Thay đổi key định kỳ:
    ```
    /interface wireguard generate-key
    ```
  - Giới hạn truy cập cổng 51820:
    ```
    /ip firewall filter
    add chain=input dst-port=51820 protocol=udp action=accept
    add chain=input action=drop
    ```
- **Sao lưu**:
  ```
  /system backup save
  ```

---

### 6. Kết quả
- **MikroTik**: Chạy WireGuard server (`wg1`, `10.0.0.1`, cổng 51820), cô lập camera (VLAN 10), hỗ trợ truy cập từ xa.
- **Điện thoại**: Kết nối VPN qua `swatcloud.duckdns.org:51820`, truy cập camera/Nextcloud/Emby như trong mạng nhà.
- **Máy tính**: Tương tự điện thoại, dùng IP `10.0.0.3`.
- **Router nhà mạng**: Chỉ mở cổng 51820 (UDP), không mở cổng dịch vụ (80, 8096, 554).

---

### 7. Hỏi thêm
- Bạn cần hỗ trợ thêm cổng dịch vụ trên DietPi (ngoài 80, 8096)?
- Muốn hướng dẫn cách dùng Wireshark để kiểm tra lưu lượng camera?
- Hoặc cần tối ưu tốc độ VPN (kiểm tra CPU, băng thông)?
Hãy cung cấp thêm thông tin (tốc độ Internet, số lượng camera, hoặc model router) để mình tối ưu hơn!
