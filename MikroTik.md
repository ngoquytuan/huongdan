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
