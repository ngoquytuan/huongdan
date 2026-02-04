Dưới đây là “bộ 4” quan sát hệ thống (observability) rất phổ biến: **Prometheus (metrics) + Loki (logs) + Tempo (traces) + Grafana (dashboard/alert)**. Mỗi thành phần giải quyết **một loại dữ liệu khác nhau** và khi ghép lại sẽ giúp bạn trả lời nhanh 3 câu hỏi: *có vấn đề gì? ở đâu? vì sao?*

---

## 1) Prometheus — Metrics (số đo theo thời gian)

**Prometheus dùng để làm gì?**
Thu thập và lưu **metrics dạng time-series** (đo đạc theo thời gian), ví dụ:

* CPU, RAM, disk, network
* request/second, latency p95, error rate
* số job đang chạy, queue length, DB connections…

**Cách hoạt động (điển hình):**

* Prometheus **“kéo” (pull/scrape)** metrics từ các endpoint (thường là `/metrics`)
* Endpoint này do **exporter** cung cấp:

  * `node_exporter` (máy chủ)
  * `cAdvisor` (container)
  * app exporter (ứng dụng tự expose)
* Prometheus lưu vào **TSDB** và query bằng **PromQL**

**Prometheus mạnh ở:**

* Theo dõi sức khỏe tổng quan, xu hướng, SLO/SLA
* Alert dựa trên tỷ lệ/độ trễ (rất hiệu quả, ít tốn chi phí hơn log)

**Prometheus không mạnh ở:**

* Debug chi tiết từng request (cần logs/traces)

---

## 2) Loki — Logs (nhật ký sự kiện)

**Loki dùng để làm gì?**
Thu thập & truy vấn **log tập trung** từ nhiều máy/dịch vụ:

* log ứng dụng (info/warn/error)
* log hệ thống
* log container stdout/stderr

**Cách hoạt động (điển hình):**

* Agent trên máy client (thường là **Promtail / Fluent Bit / Vector**) đọc log:

  * file log
  * docker logs
  * systemd journal
* Agent **push** log về Loki
* Loki lưu log theo dạng “chunk” + index nhẹ dựa trên **labels**

**Điểm quan trọng của Loki: Labels vs Nội dung log**

* Loki **index chủ yếu bằng labels** (vd: `service`, `env`, `site`, `level`)
* Nội dung chi tiết nằm trong “body” log (có thể JSON)
* Vì vậy: **đừng label theo user_id/order_id** (cardinality cao → tốn tài nguyên, query chậm)

**Loki mạnh ở:**

* Xem log theo service/env/site nhanh
* Rẻ hơn full-text log engine nếu bạn thiết kế labels đúng

---

## 3) Tempo — Traces (vết theo dõi request end-to-end)

**Tempo dùng để làm gì?**
Lưu và truy vấn **distributed traces**: một request đi qua nhiều service (API → worker → DB → cache) thì Tempo cho bạn thấy:

* request này đi qua những “span” nào
* mỗi span tốn bao lâu
* lỗi phát sinh ở span nào, service nào

**Cách hoạt động (điển hình):**

* Ứng dụng được instrument bằng **OpenTelemetry SDK** (hoặc Jaeger/Zipkin SDK)
* Dữ liệu trace thường gửi tới **OpenTelemetry Collector** (khuyên dùng) hoặc gửi thẳng Tempo
* Tempo lưu trace (thường dùng object storage, tối ưu chi phí)

**Tempo mạnh ở:**

* Debug latency/lỗi theo *một request cụ thể*
* Phân tích “nút cổ chai” giữa các service

---

## 4) Grafana — Dashboard + Explore + Alerting (UI & điều phối)

**Grafana dùng để làm gì?**

* Là “mặt tiền” để:

  * xem dashboard metrics (Prometheus)
  * xem logs (Loki)
  * xem traces (Tempo)
  * correlate (liên kết) 3 loại dữ liệu
* Tạo **Alert rules** (và gửi thông báo qua email/Slack/Telegram…)

**Grafana mạnh ở:**

* Một nơi duy nhất để quan sát và điều tra sự cố
* Drill-down: từ metrics → click qua logs → click qua trace của đúng request

---

# Cách 4 món phối hợp với nhau (luồng điều tra sự cố “đúng bài”)

### Tình huống: “API chậm và error tăng”

1. **Prometheus (metrics)** báo:

   * latency p95 tăng
   * error rate tăng
     → bạn biết *có vấn đề* và *từ khi nào*, mức độ ra sao

2. Từ panel đó, mở **Loki (logs)** theo `service=api` + thời điểm tương ứng
   → thấy *lỗi cụ thể* (timeout DB, upstream 502, OOM…)

3. Nếu bạn có trace, mở **Tempo (traces)**:

   * trace cho request chậm nhất
   * span nào tốn thời gian (DB query? gọi service B? cache miss?)
     → biết *đang nghẽn ở đâu* và *vì sao*

4. **Grafana** là nơi bạn nhảy qua lại giữa 3 thứ này.

---

# “Glue” để liên kết logs ↔ traces ↔ metrics (quan trọng để chuyên nghiệp)

Để Grafana liên kết được, bạn nên chuẩn hoá:

* **Trace context**: `trace_id`, `span_id`
* **Request correlation**: `request_id` (nếu không dùng trace)
* Log dạng JSON có field `trace_id` để “click từ log sang trace”
* Metrics có exemplars/labels tương ứng (tuỳ mức độ)

**Tối thiểu nên làm:**

* Mỗi request sinh `trace_id` (OpenTelemetry)
* Log của service luôn in kèm `trace_id`
* Loki label: `service`, `env`, `site`, `level` (đủ dùng, ít tốn)

---

# Mỗi thứ nên đặt ở đâu (tư duy triển khai)

* **Prometheus / Loki / Tempo / Grafana**: đặt ở “trung tâm” (nhà bạn), phía sau VPN (Tailscale/WireGuard)
* **Trên mỗi máy client**:

  * metrics: node_exporter/cAdvisor (để Prometheus scrape hoặc push qua gateway tuỳ mạng)
  * logs: promtail/fluent-bit
  * traces: OpenTelemetry Collector (hoặc app gửi thẳng)

---

Nếu bạn muốn mình vẽ cho bạn một kiến trúc “chuẩn home-lab” cho dưới 10 service (kèm agent nào đặt ở đâu, port nào mở, retention bao lâu) theo tình huống của bạn, chỉ cần nói:

* các service chạy Docker hay systemd?
* bạn có muốn làm traces ngay từ đầu (OpenTelemetry) hay để giai đoạn 2?


Không bắt buộc “toàn bộ hệ” phải cài **Loki trước**. “Trung tâm” về mặt giao diện thường là **Grafana**, còn “trung tâm phần logs” thì **Loki là backend** (nếu bạn chọn stack Loki). Bạn có thể triển khai theo thứ tự nào cũng được, nhưng để **bắt đầu giám sát log** thì đúng là bạn cần **một log backend** (Loki hoặc OpenSearch/Elastic). Với mô hình tiết kiệm, Loki là lựa chọn rất hợp lý.

Dưới đây là cách cài **Loki trên Debian** theo kiểu **an toàn, ít xung đột, dễ tháo bỏ**: chạy **Docker Compose** trong một thư mục riêng, bind cổng chỉ trên **Tailscale/localhost**, không “đụng” hệ thống.

---

## Cách cài Loki trên Debian an toàn (Docker Compose, tách biệt, dễ gỡ)

### 0) Kiểm tra không xung đột cổng

Mặc định Loki dùng `3100`. Kiểm tra:

```bash
ss -lntp | grep ':3100' || true
```

* Nếu đã có dịch vụ khác dùng 3100 → đổi sang 3101 (mình sẽ chỉ luôn chỗ đổi).

### 1) Tạo thư mục riêng cho Loki (dễ xoá sạch)

```bash
sudo mkdir -p /opt/obs/loki
cd /opt/obs/loki
```

### 2) Tạo cấu hình Loki (retention + lưu dữ liệu)

Tạo file `loki-config.yml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

limits_config:
  retention_period: 336h   # 14 ngày (đổi theo nhu cầu)
```

> `auth_enabled: false` là ổn **nếu** bạn chỉ cho truy cập qua VPN/localhost (không public).

### 3) Docker Compose cho Loki (khuyến nghị: chỉ mở trên Tailscale hoặc localhost)

Tạo `docker-compose.yml`:

**Phương án A (khuyên dùng): bind chỉ trên IP Tailscale của server**
Lấy IP tailscale:

```bash
tailscale ip -4
```

Giả sử IP là `100.64.12.34`, compose:

```yaml
version: "3.8"
services:
  loki:
    image: grafana/loki:2.9.4
    command: -config.file=/etc/loki/config.yml
    volumes:
      - ./loki-config.yml:/etc/loki/config.yml:ro
      - loki-data:/loki
    ports:
      - "100.64.12.34:3100:3100"  # chỉ nghe trên tailscale
    restart: unless-stopped

volumes:
  loki-data:
```

**Phương án B: chỉ bind localhost** (khi bạn sẽ reverse proxy / hoặc client ship log vào qua tunnel/VPN khác):

```yaml
ports:
  - "127.0.0.1:3100:3100"
```

> Nếu bạn cần đổi cổng vì xung đột, đổi `3100` → `3101` ở cả hai phía.

### 4) Chạy Loki

```bash
docker compose up -d
docker logs -f loki
```

Test:

```bash
curl http://100.64.12.34:3100/ready
```

Trả `ready` là OK.

### 5) Kết nối Grafana vào Loki

Trong Grafana → **Data sources** → Add → **Loki**

* URL (nếu Grafana chạy trên cùng máy):
  `http://100.64.12.34:3100` (theo Tailscale)
  hoặc `http://127.0.0.1:3100` (nếu bạn bind localhost và Grafana cũng nhìn thấy localhost theo cách của bạn)

> Nếu Grafana của bạn đang chạy trong Docker và **không dùng host network**, thì `127.0.0.1` bên trong container là “container đó”, không phải host. Lúc đó dùng IP Tailscale/host IP hoặc cho Grafana & Loki cùng một docker network (mình có thể hướng dẫn theo setup của bạn).

---

## Hardening tối thiểu để “an toàn”

1. **Không public port 3100 ra Internet** (không port-forward router).
2. Bind port chỉ trên **Tailscale IP** (như ở trên) là cách gọn nhất.
3. (Tuỳ chọn) Chặn firewall inbound 3100 từ ngoài VPN:

* UFW ví dụ (nếu bạn dùng UFW):

  * Chỉ cho phép từ interface tailscale `tailscale0` hoặc subnet tailscale.

---

## Gỡ bỏ Loki “sạch sẽ” (không để rác, không ảnh hưởng hệ khác)

Vì mọi thứ nằm trong `/opt/obs/loki` + docker volume, nên tháo rất dễ:

```bash
cd /opt/obs/loki
docker compose down -v
```

Tuỳ chọn xoá image:

```bash
docker image rm grafana/loki:2.9.4
```

Xoá thư mục cấu hình:

```bash
sudo rm -rf /opt/obs/loki
```

Xong. Không đụng package hệ thống Debian, không xung đột thư viện.

---

Nếu bạn nói rõ **Grafana của bạn đang chạy kiểu nào**:

* Grafana cài bằng apt (systemd service) hay Grafana container?
* Grafana container có `--network host` hay bridge network?

…thì mình sẽ chỉ đúng **URL datasource** và cách nối network để khỏi bị lỗi “Grafana không gọi được Loki”.

Vì trong bài toán “log server ở nhà nhưng các dịch vụ ở nhiều nơi”, cái khó nhất **không phải Loki**, mà là **kết nối an toàn & ổn định** từ nhiều mạng khác nhau về nhà. Tailscale giải quyết đúng phần này gọn nhất.

## Vì sao chọn Tailscale (thay vì mở port Internet)?

* **Không cần mở port ra Internet**: Loki mặc định không bật auth; nếu bạn expose thẳng cổng 3100 thì rất rủi ro. Tailscale giúp Loki chỉ “nằm trong mạng riêng”.
* **Vượt NAT / IP động dễ dàng**: nhà bạn thường IP WAN thay đổi, nhiều lớp NAT; Tailscale tự xử lý NAT traversal, không cần DDNS + port-forward.
* **Dễ nối nhiều điểm**: bạn có nhiều server/VPS/địa điểm → chỉ cần cài Tailscale, là các máy “nhìn thấy nhau” như LAN.
* **Mã hoá end-to-end**: traffic giữa client → nhà đi trong tunnel (dựa trên WireGuard).
* **Quản trị đơn giản**: đặt tên máy, bật/tắt máy khỏi mạng, chia nhóm, (tuỳ gói) ACL theo dịch vụ/port.

## Vì sao đặc biệt hợp cho log server?

* **Bạn có thể để Loki “mở” nhưng chỉ trong VPN** (bind vào IP Tailscale), không cần dựng auth phức tạp ngay.
* Các client ở xa chỉ cần push log tới **IP Tailscale của log server** → ít lỗi mạng vặt.

## Có lựa chọn khác không?

Có, nhưng thường “tốn công hơn”:

* **WireGuard tự dựng**: nhẹ và chuẩn, nhưng bạn phải tự lo key, routing, NAT, cấu hình từng node.
* **Mở public + HTTPS reverse proxy + auth**: làm được, nhưng phải lo chứng chỉ, bảo mật, firewall, rate-limit… và vẫn bị scan.
* **SSH tunnel**: đơn giản cho vài máy, nhưng quản lý nhiều máy sẽ mệt và kém “hệ thống”.

## Điểm trừ của Tailscale (để bạn cân nhắc)

* Phụ thuộc dịch vụ điều phối của Tailscale (dù dữ liệu thường đi P2P). Nếu bạn muốn tự chủ 100% thì có thể dùng **Headscale** (self-host control plane) hoặc quay về WireGuard tự dựng.

Nếu bạn muốn, mình có thể đề xuất 2 cấu hình cụ thể cho bạn:

1. **Tailscale “thuần”** (nhanh, ít công)
2. **WireGuard/Headscale** (tự chủ hơn)

…tuỳ mức bạn ưu tiên “tiện vận hành” hay “tự quản trị hoàn toàn”.

Dưới đây là hướng **Hybrid “chuẩn bài”** cho bạn: **máy trong LAN đẩy log qua IP LAN (192.168.1.88)**, máy ở ngoài đẩy log qua **IP Tailscale**. Mục tiêu là **an toàn (không lộ Internet), không xung đột, dễ tháo bỏ**.

---

## 0) Nguyên tắc an toàn (cốt lõi)

* **Không port-forward** 3100 (Loki) ra Internet trên router.
* Loki **không bật auth** → vì vậy **chỉ cho phép truy cập từ LAN + Tailscale** bằng cách:

  1. bind port vào **LAN IP + Tailscale IP**
  2. firewall chặn truy cập từ nơi khác

---

## 1) Xác định IP Tailscale của Debian server

Trên máy Debian (log server):

```bash
tailscale ip -4
```

Ví dụ ra `100.64.12.34` → mình gọi là `<TS_IP>`.

Kiểm tra cổng 3100 có bị dùng chưa:

```bash
ss -lntp | grep ':3100' || true
```

---

## 2) Cài Loki trên Debian bằng Docker Compose (tách biệt, dễ gỡ)

Tạo thư mục riêng:

```bash
sudo mkdir -p /opt/obs/loki
cd /opt/obs/loki
```

### 2.1 Tạo cấu hình Loki

Tạo file `loki-config.yml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

limits_config:
  retention_period: 336h   # 14 ngày (tùy chỉnh)
```

### 2.2 Docker Compose “Hybrid” (nghe cả LAN + Tailscale, không public WAN)

Tạo `docker-compose.yml` (nhớ thay `<TS_IP>` bằng IP thật):

```yaml
version: "3.8"

services:
  loki:
    image: grafana/loki:2.9.4
    command: -config.file=/etc/loki/config.yml
    volumes:
      - ./loki-config.yml:/etc/loki/config.yml:ro
      - loki-data:/loki
    ports:
      - "192.168.1.88:3100:3100"   # LAN
      - "<TS_IP>:3100:3100"        # Tailscale
    restart: unless-stopped

volumes:
  loki-data:
```

Chạy Loki:

```bash
docker compose up -d
docker logs -f loki
```

Test ngay trên server:

```bash
curl http://192.168.1.88:3100/ready
curl http://<TS_IP>:3100/ready
```

Thấy `ready` là OK.

---

## 3) Khóa truy cập bằng firewall (an toàn hơn nhiều)

Mục tiêu: port **3100 chỉ cho LAN + tailscale0**.

### Nếu bạn dùng UFW (khuyến nghị)

Kiểm tra UFW:

```bash
sudo ufw status verbose || true
```

Thiết lập (an toàn nhất là default deny inbound, rồi allow cần thiết):

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Cho phép Loki từ LAN
sudo ufw allow from 192.168.1.0/24 to any port 3100 proto tcp

# Cho phép Loki từ Tailscale interface
sudo ufw allow in on tailscale0 to any port 3100 proto tcp

# (Tuỳ chọn) Grafana 3000 cũng chỉ mở LAN+Tailscale
sudo ufw allow from 192.168.1.0/24 to any port 3000 proto tcp
sudo ufw allow in on tailscale0 to any port 3000 proto tcp

sudo ufw enable
sudo ufw status verbose
```

> Nếu bạn đang SSH từ xa qua Internet, nhớ **allow ssh** trước khi enable UFW (vd `sudo ufw allow 22/tcp`) để khỏi tự khóa mình.

---

## 4) Kết nối Grafana với Loki

Trong Grafana → Add data source → **Loki**:

* Nếu bạn truy cập Grafana trong LAN: URL dùng `http://192.168.1.88:3100`
* Nếu bạn truy cập từ ngoài qua Tailscale: URL dùng `http://<TS_IP>:3100`

> Nếu Grafana chạy Docker trên cùng host, vẫn dùng `http://192.168.1.88:3100` hoặc `http://<TS_IP>:3100` là ổn (tránh dùng `localhost` trong container vì dễ nhầm).

---

## 5) Client đẩy log về (LAN vs Outside)

Bạn sẽ cài **Promtail** trên từng máy client.

### 5.1 Máy client trong LAN (push qua LAN IP)

Trong `promtail-config.yml` của client LAN:

```yaml
clients:
  - url: http://192.168.1.88:3100/loki/api/v1/push
```

### 5.2 Máy client ở ngoài (push qua Tailscale IP)

Trên client đã cài Tailscale:

```yaml
clients:
  - url: http://<TS_IP>:3100/loki/api/v1/push
```

Nếu bạn cần mẫu Promtail Docker “đọc log Docker” cho client, dùng bộ chuẩn này:

**/opt/promtail/docker-compose.yml**

```yaml
version: "3.8"
services:
  promtail:
    image: grafana/promtail:2.9.4
    command: -config.file=/etc/promtail/config.yml
    volumes:
      - ./promtail-config.yml:/etc/promtail/config.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - promtail-positions:/tmp
    restart: unless-stopped
volumes:
  promtail-positions:
```

**/opt/promtail/promtail-config.yml (mẫu)**

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://192.168.1.88:3100/loki/api/v1/push   # LAN client (đổi sang TS_IP nếu remote)

scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    relabel_configs:
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'
      - target_label: 'env'
        replacement: 'prod'
      - target_label: 'site'
        replacement: 'lan-1'   # đổi theo nơi đặt
    pipeline_stages:
      - docker: {}
```

---

## 6) Kiểm tra end-to-end

* Trên client:

```bash
docker logs -f promtail
```

* Trong Grafana → Explore → Loki:

  * Query thử: `{env="prod"}` hoặc `{site="lan-1"}`

---

## 7) Dễ tháo bỏ (clean uninstall)

Trên server:

```bash
cd /opt/obs/loki
docker compose down -v
sudo rm -rf /opt/obs/loki
```

---

Nếu bạn nói thêm **Grafana của bạn đang chạy kiểu nào** (cài apt/service hay container), mình sẽ chỉ đúng 1 cấu hình “đẹp” nhất để Grafana kết nối Loki (tránh lỗi network/localhost), và mình cũng có thể đưa luôn rules firewall tối ưu theo đúng setup SSH của bạn để không bị tự khóa.

Grafana của tôi đang chạy ở đây, 1 container khác.http://192.168.1.88:3001/,  root@DietPi:/opt/obs/loki# curl http://192.168.1.88:3100/ready
ready
root@DietPi:/opt/obs/loki# curl http://100.108.146.4:3100/ready
ready
root@DietPi:/opt/obs/loki# docker exec -it fr02-grafana sh -lc 'wget -qO- http://192.168.1.88:3100/ready || curl -s http://192.168.1.88:3100/ready'
ready , giờ cho tôi một script python để bắn log từ máy windows trong mạng lan vào loki rồi vào grafana xem, tôi đã Add Loki datasource trong Grafana

Được — Loki **nhận log qua HTTP endpoint `POST /loki/api/v1/push`** (có thể gửi **JSON** trực tiếp), nên bạn có thể dùng Python trên Windows để “bắn log” vào Loki rồi xem trong Grafana. ([Grafana Labs][1])
(Lưu ý: Loki **không có cơ chế auth trong API**; an toàn là nhờ bạn giới hạn truy cập bằng LAN/Tailscale/firewall như bạn đang làm. ([Grafana Labs][1]))

Dưới đây là 1 script Python **chạy được trên Windows**, hỗ trợ:

* Gửi 1 dòng test
* Hoặc chạy liên tục gửi log định kỳ
* Hoặc tail 1 file log (đọc các dòng mới appended)

---

## 1) Cài thư viện trên Windows

Mở PowerShell / CMD:

```bash
py -m pip install requests
```

---

## 2) Lưu script: `loki_push.py`

> Sửa `LOKI_URL` nếu cần (mặc định đúng với bạn: `http://192.168.1.88:3100`)

```python
import argparse
import os
import socket
import sys
import time
from typing import Dict, List, Optional

import requests


def now_ns_str() -> str:
    # Loki expects Unix epoch timestamp in nanoseconds, as a string. :contentReference[oaicite:2]{index=2}
    return str(time.time_ns())


def build_stream(labels: Dict[str, str], lines: List[str]) -> Dict:
    values = [[now_ns_str(), line] for line in lines]
    return {"stream": labels, "values": values}


def push_to_loki(loki_push_url: str, labels: Dict[str, str], lines: List[str], timeout: int = 5) -> None:
    payload = {"streams": [build_stream(labels, lines)]}
    headers = {"Content-Type": "application/json"}

    # Simple retry with backoff
    backoff = 1.0
    for attempt in range(1, 6):
        try:
            r = requests.post(loki_push_url, json=payload, headers=headers, timeout=timeout)
            if 200 <= r.status_code < 300:
                return
            # Loki returns useful error message in body on 4xx/5xx
            raise RuntimeError(f"HTTP {r.status_code}: {r.text}")
        except Exception as e:
            if attempt == 5:
                raise
            time.sleep(backoff)
            backoff *= 2


def tail_file(path: str, sleep_sec: float = 0.25):
    # Basic "tail -f" for Windows text files
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(sleep_sec)
                continue
            yield line.rstrip("\r\n")


def main():
    parser = argparse.ArgumentParser(description="Push logs from Windows to Grafana Loki (JSON push API).")
    parser.add_argument("--loki", default="http://192.168.1.88:3100", help="Loki base URL, e.g. http://192.168.1.88:3100")
    parser.add_argument("--service", default="win-test", help="service label")
    parser.add_argument("--env", default="prod", help="env label")
    parser.add_argument("--site", default="lan", help="site label (lan/sg-vps/etc)")
    parser.add_argument("--level", default="info", help="level label (info/warn/error)")
    parser.add_argument("--host", default=socket.gethostname(), help="host label (default: this PC name)")
    parser.add_argument("--message", help="Send one message and exit")
    parser.add_argument("--loop", action="store_true", help="Send messages repeatedly (every --interval seconds)")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between messages in --loop mode")
    parser.add_argument("--file", help="Tail a log file and push new lines to Loki")
    parser.add_argument("--batch", type=int, default=20, help="Batch size for file/loop mode")
    args = parser.parse_args()

    loki_push_url = args.loki.rstrip("/") + "/loki/api/v1/push"

    labels = {
        "job": "windows",
        "service": args.service,
        "env": args.env,
        "site": args.site,
        "host": args.host,
        "level": args.level,
    }

    # Mode 1: single message
    if args.message:
        push_to_loki(loki_push_url, labels, [args.message])
        print("OK: pushed 1 log line")
        return

    # Mode 2: tail file
    if args.file:
        buf: List[str] = []
        last_flush = time.time()
        flush_every_sec = 1.0

        for line in tail_file(args.file):
            buf.append(line)
            if len(buf) >= args.batch or (time.time() - last_flush) >= flush_every_sec:
                push_to_loki(loki_push_url, labels, buf)
                print(f"OK: pushed {len(buf)} lines")
                buf.clear()
                last_flush = time.time()
        return

    # Mode 3: loop generator
    if args.loop:
        i = 0
        buf: List[str] = []
        while True:
            i += 1
            buf.append(f"hello from {args.host} #{i}")
            if len(buf) >= args.batch:
                push_to_loki(loki_push_url, labels, buf)
                print(f"OK: pushed {len(buf)} lines")
                buf.clear()
            time.sleep(args.interval)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 3) Chạy test (gửi 1 dòng log)

Trên Windows:

```bash
py loki_push.py --message "Windows says hello" --service win-demo --env prod --site lan --level info
```

---

## 4) Xem trong Grafana

Grafana → **Explore** → chọn datasource **Loki** → query:

* Xem tất cả log từ Windows:

```logql
{job="windows"}
```

* Theo máy cụ thể:

```logql
{job="windows", host="TEN_MAY_WINDOWS"}
```

* Theo service:

```logql
{job="windows", service="win-demo"}
```

---

## 5) Tail file log trên Windows (ví dụ)

Ví dụ bạn có log ở `C:\logs\app.log`:

```bash
py loki_push.py --file "C:\logs\app.log" --service myapp --env prod --site lan --level info
```

---

### Ghi chú quan trọng

* Loki yêu cầu timestamp theo **Unix epoch nanoseconds dạng string**; script đã làm đúng. ([GitHub][2])
* “Bắn log trực tiếp” như vậy phù hợp để test/nhỏ lẻ; production thì vẫn nên dùng agent (Promtail/Vector/Fluent Bit) để có retry/buffer tốt hơn. ([Stack Overflow][3])

Nếu bạn nói bạn muốn gửi log kiểu nào (file log ứng dụng, Windows Event Log, hay log của app tự viết), mình có thể chỉnh script cho đúng chuẩn format/label của hệ bạn (service/env/site/level + JSON log).

[1]: https://grafana.com/docs/loki/latest/reference/loki-http-api/?utm_source=chatgpt.com "Loki HTTP API | Grafana Loki documentation"
[2]: https://github.com/grafana/loki/issues/5226?utm_source=chatgpt.com "Log line pushed via http POST api (/loki/api/v1/push) not ... - GitHub"
[3]: https://stackoverflow.com/questions/67316535/send-logs-directly-to-loki-without-use-of-agents?utm_source=chatgpt.com "Send logs directly to Loki without use of agents - Stack Overflow"

Đây là các **label** (nhãn) bạn gắn kèm mỗi dòng log khi gửi vào Loki. Loki dùng label để **lọc nhanh** khi query trong Grafana (LogQL). Mỗi label là một cặp `key=value`.

* **env = prod**
  *Môi trường chạy* (environment).
  Ví dụ: `dev`, `staging`, `prod`.
  Dùng để tách log production ra khỏi log test.

* **host = design**
  *Tên máy/host phát sinh log* (tên Windows PC hoặc server).
  Dùng để lọc log theo máy cụ thể: `{host="design"}`.

* **job = windows**
  *Nhóm nguồn thu thập log* (source/collector job).
  Ở đây bạn đặt `windows` để biết log này đến từ “nhóm máy Windows” (phân loại cao-level).
  Thường dùng để tách nhóm như `docker`, `linux`, `nginx`, `windows`, `app-logs`.

* **level = info**
  *Mức độ log* (severity).
  Thường: `debug`, `info`, `warn`, `error`.
  Dùng để lọc nhanh log lỗi: `{level="error"}`.

* **service = win-demo**
  *Tên dịch vụ/ứng dụng* phát sinh log.
  Đây là label quan trọng nhất để bạn tách log theo từng app: `{service="win-demo"}`.
  Với hệ <10 dịch vụ, label `service` cực hữu ích.

* **site = lan**
  *Vị trí/điểm đặt* (địa điểm/mạng).
  Ví dụ: `lan`, `home`, `office`, `vps-sg`, `aws-ap-southeast-1`.
  Dùng để phân biệt log đến từ máy nội bộ hay máy ở xa: `{site="lan"}`.

### Ví dụ truy vấn trong Grafana (Explore)

* Tất cả log Windows trong prod:
  `{job="windows", env="prod"}`
* Log của service win-demo ở LAN:
  `{service="win-demo", site="lan"}`
* Chỉ log info từ máy design:
  `{host="design", level="info"}`

**Tip nhỏ “đúng bài”:** Những label như `env/service/site/level/host` là ổn vì số lượng giá trị ít (cardinality thấp). Tránh tạo label kiểu `user_id`, `order_id`, `request_id` vì sẽ làm Loki nặng và query chậm.


OK, trạng thái của bạn đang **đúng chuẩn Hybrid** rồi: Loki “ready” trên cả **LAN (192.168.1.88)** và **Tailscale (100.108.146.4)**. 👍

Giờ bước tiếp theo là **cho Grafana container ([http://192.168.1.88:3001](http://192.168.1.88:3001))** kết nối tới Loki một cách **không xung đột + an toàn**.

---

## 1) Kiểm tra Grafana container có gọi được Loki không

Trên Debian host, tìm tên container Grafana:

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

Giả sử container tên `grafana` (nếu khác thì thay tên), test từ *bên trong container*:

```bash
docker exec -it grafana sh -lc 'wget -qO- http://192.168.1.88:3100/ready || curl -s http://192.168.1.88:3100/ready'
```

Kỳ vọng ra `ready`.

> Nếu container không có `curl/wget`, bạn vẫn có thể test bằng container tạm:

```bash
docker run --rm curlimages/curl:8.5.0 -s http://192.168.1.88:3100/ready
```

---

## 2) Add Loki datasource trong Grafana (cách đúng cho container)

Vào Grafana (UI) tại: `http://192.168.1.88:3001`

* **Connections → Data sources → Add data source → Loki**
* Ở **URL** nhập:

  * **Khuyên dùng:** `http://192.168.1.88:3100` (đường LAN, nhanh, ổn định trong nhà)
  * (Tuỳ chọn) nếu bạn muốn Grafana “tự dùng được khi bạn chỉ truy cập qua Tailscale”: `http://100.108.146.4:3100`

Bấm **Save & Test** → phải xanh.

> Lưu ý quan trọng: URL datasource là **Grafana server (container) gọi tới**, không phải trình duyệt của bạn gọi tới. Nhưng dùng `192.168.1.88:3100` vẫn OK vì container thường gọi được IP LAN của host.

---

## 3) Test log trong Grafana (Explore)

Vào **Explore → chọn datasource Loki**, thử query:

* Tất cả log theo label (nếu bạn đã ship log từ promtail):

  * `{env="prod"}`
* Hoặc filter service:

  * `{service="api", env="prod"}`
* Tìm chuỗi:

  * `{env="prod"} |= "error"`

Nếu chưa có promtail client thì sẽ chưa thấy dữ liệu (bình thường).

---

## 4) Làm “an toàn” cho Grafana container (giống Loki)

Hiện Grafana của bạn đang mở ở `:3001`. Để đúng bài “LAN + Tailscale, không public”, bạn nên **bind port Grafana chỉ vào LAN + Tailscale** (giống Loki).

Nếu Grafana đang chạy bằng docker-compose, trong phần `ports:` nên là kiểu:

```yaml
ports:
  - "192.168.1.88:3001:3000"
  - "100.108.146.4:3001:3000"
```

Và **không dùng** kiểu `"3001:3000"` (vì nó bind 0.0.0.0 → dễ lộ ra ngoài nếu máy có public interface).

---

## 5) Firewall tối thiểu (khuyến nghị)

Bạn đã làm đúng với Loki; làm tương tự cho Grafana port 3001:

* Cho LAN:

  * allow `192.168.1.0/24 → 3001/tcp`
* Cho Tailscale:

  * allow inbound trên interface `tailscale0` → 3001/tcp

*(Nếu bạn đang dùng UFW thì thêm rules tương tự như Loki, chỉ đổi port thành 3001.)*

---

## 6) Tiếp theo: Promtail client (LAN dùng 192.168.1.88, remote dùng 100.108.146.4)

* **Client trong LAN:** `http://192.168.1.88:3100/loki/api/v1/push`
* **Client ở ngoài:** `http://100.108.146.4:3100/loki/api/v1/push`

Nếu bạn nói client của bạn chạy log kiểu **Docker** hay **file/systemd**, mình sẽ đưa đúng 1 bộ `promtail-config.yml` tối ưu (labels: `service/env/site/level`) để bạn copy-paste là thấy log ngay trong Grafana.

Log của bạn đang ở dạng “human-readable”:

`2026-01-28 18:37:23,085 [INFO] APP START - ...`

Để “hay và chuyên nghiệp” khi đẩy về Loki, có 2 hướng (mình khuyên theo thứ tự):

## Hướng 1 (khuyến nghị production): **Ghi log ra file + dùng agent (Grafana Alloy) ship lên Loki**

Lý do: agent có **buffer/retry**, chịu được mất mạng, batch tối ưu, ít rủi ro “bắn rơi log”. Grafana cũng **khuyến nghị Alloy để gửi log vào Loki**. ([Grafana Labs][1])

**Bạn làm như sau (Windows trong LAN):**

1. App tiếp tục ghi log ra file (vd `C:\logs\app.log`) với format hiện tại.
2. Cài **Grafana Alloy** trên Windows (collector mới; Grafana Agent cũ đã EOL và được hướng migrate sang Alloy). ([Grafana Labs][2])
3. Cấu hình Alloy “tail file” và push về:

* LAN: `http://192.168.1.88:3100/loki/api/v1/push`

**Điểm “pro”**: bạn giữ label ít và ổn định: `service, env, site, host, level` (giống bạn đang làm), còn nội dung chi tiết nằm trong dòng log. Tránh label kiểu `request_id/user_id` vì gây “high-cardinality” làm Loki nặng/chậm. ([Stack Overflow][3])

> Nếu bạn muốn, mình sẽ đưa đúng file config Alloy cho Windows + cách cài service (vì đoạn này dài hơn một chút và bạn sẽ copy-paste chạy luôn).

---

## Hướng 2 (nhanh gọn, hợp với app Python của bạn): **Tạo “Loki handler” trong Python logging**

Cách này “chuyên nghiệp” khi bạn:

* Gửi log **theo batch**
* Parse đúng `timestamp` từ dòng log (không dùng thời gian gửi)
* Map `[INFO]` → label `level="info"`
* Gắn label: `service=... env=... site=... host=... job=windows`

Loki nhận log qua HTTP Push API `/loki/api/v1/push` và timestamp là **epoch nanoseconds**. ([Grafana Labs][4])

### Script Python (Windows): tail file log hiện tại và đẩy lên Loki (parse timestamp)

Lưu thành `tail_to_loki.py`:

```python
import argparse
import os
import re
import socket
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict

import requests

LINE_RE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[(?P<level>[A-Z]+)\] (?P<msg>.*)$'
)

LEVEL_MAP = {
    "DEBUG": "debug",
    "INFO": "info",
    "WARNING": "warn",
    "WARN": "warn",
    "ERROR": "error",
    "CRITICAL": "error",
}

def dt_to_ns(dt: datetime) -> str:
    # Loki expects Unix epoch in nanoseconds as string
    return str(int(dt.timestamp() * 1_000_000_000))

def push(loki_url: str, labels: Dict[str, str], batch: List[List[str]], timeout=5):
    payload = {"streams": [{"stream": labels, "values": batch}]}
    r = requests.post(loki_url, json=payload, timeout=timeout)
    if not (200 <= r.status_code < 300):
        raise RuntimeError(f"Push failed: HTTP {r.status_code} {r.text}")

def tail_f(path: str):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.25)
                continue
            yield line.rstrip("\r\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True, help="Path to log file, e.g. C:\\logs\\app.log")
    p.add_argument("--loki", default="http://192.168.1.88:3100/loki/api/v1/push")
    p.add_argument("--service", default="win-demo")
    p.add_argument("--env", default="prod")
    p.add_argument("--site", default="lan")
    p.add_argument("--job", default="windows")
    p.add_argument("--host", default=socket.gethostname().lower())
    p.add_argument("--tz", default="+07:00", help="Timezone offset of log timestamps, e.g. +07:00")
    p.add_argument("--batch", type=int, default=50, help="Max lines per push")
    p.add_argument("--flush_sec", type=float, default=1.0, help="Flush interval seconds")
    args = p.parse_args()

    # Parse timezone offset like +07:00
    sign = 1 if args.tz.startswith("+") else -1
    hh, mm = args.tz[1:].split(":")
    tz = timezone(sign * timedelta(hours=int(hh), minutes=int(mm)))

    base_labels = {
        "job": args.job,
        "service": args.service,
        "env": args.env,
        "site": args.site,
        "host": args.host,
    }

    buf: List[List[str]] = []
    last_flush = time.time()

    for line in tail_f(args.file):
        m = LINE_RE.match(line)
        if m:
            ts = datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S,%f").replace(tzinfo=tz)
            level = LEVEL_MAP.get(m.group("level"), "info")
            msg = m.group("msg")
        else:
            # Fallback: if line doesn't match, use "now"
            ts = datetime.now(tz=timezone.utc)
            level = "info"
            msg = line

        labels = dict(base_labels)
        labels["level"] = level

        buf.append([dt_to_ns(ts.astimezone(timezone.utc)), msg])

        if len(buf) >= args.batch or (time.time() - last_flush) >= args.flush_sec:
            try:
                push(args.loki, labels, buf)
                buf.clear()
                last_flush = time.time()
            except Exception as e:
                # simple backoff and keep buffer
                print(f"Push error: {e}")
                time.sleep(2)

if __name__ == "__main__":
    main()
```

### Chạy trên Windows

```bash
py -m pip install requests
py tail_to_loki.py --file "C:\Users\Admin\Documents\tesst\...\app.log" --service fr-app --env prod --site lan --tz +07:00
```

### Xem trong Grafana (Explore → Loki)

```logql
{service="fr-app", env="prod", site="lan"}
```

---

## “Pro upgrade” cho log format của bạn (nếu bạn chỉnh được app)

Hiện bạn đang log “text”. Nếu nâng lên **JSON structured logging** (vẫn gửi vào Loki), bạn sẽ:

* lọc/sort tốt hơn
* dễ link trace_id/request_id (để trong JSON body, **không làm label**)

---

Nếu bạn nói rõ app của bạn là **Python** (logging module) hay app khác, và log đang **ghi ra file nào**, mình sẽ đề xuất dứt khoát 1 phương án tối ưu (Alloy hay logging handler) + config đúng “chuẩn labels” cho hệ của bạn (service/env/site/host/level) để về sau mở rộng lên 10 dịch vụ vẫn mượt.

[1]: https://grafana.com/docs/loki/latest/send-data/alloy/?utm_source=chatgpt.com "Ingesting logs to Loki using Alloy | Grafana Loki documentation"
[2]: https://grafana.com/docs/agent/latest/?utm_source=chatgpt.com "Grafana Agent | Grafana Agent documentation"
[3]: https://stackoverflow.com/questions/67316535/send-logs-directly-to-loki-without-use-of-agents?utm_source=chatgpt.com "Send logs directly to Loki without use of agents - Stack Overflow"
[4]: https://grafana.com/docs/loki/latest/reference/loki-http-api/?utm_source=chatgpt.com "Loki HTTP API | Grafana Loki documentation"
