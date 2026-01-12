Đây là bản hướng dẫn tổng hợp toàn bộ quy trình thiết lập hệ thống giám sát sức khỏe Server (CPU, RAM, Disk) và ổ cứng (S.M.A.R.T) trên DietPi/Debian mà chúng ta đã thực hiện.

---

# HƯỚNG DẪN THIẾT LẬP HỆ THỐNG GIÁM SÁT SERVER (MONITORING STACK)

Hệ thống này giúp bạn theo dõi chi tiết hiệu năng CPU, RAM, dung lượng đĩa và các chỉ số "sinh tử" của ổ cứng HDD thông qua InfluxDB và Python.

## 1. Chuẩn bị môi trường (Prerequisites)

Trước tiên, cài đặt các công cụ cần thiết để lấy dữ liệu phần cứng:

```bash
sudo apt update
sudo apt install python3-pip python3-psutil smartmontools sysstat -y
pip3 install influxdb

```

* **psutil**: Lấy thông số RAM, CPU Load, Disk Usage.
* **smartmontools**: Truy xuất dữ liệu S.M.A.R.T từ ổ cứng.
* **sysstat**: Cung cấp lệnh `sar` để theo dõi `%iowait` chính xác.

---

## 2. Thiết lập cơ sở dữ liệu InfluxDB

Dữ liệu sẽ được lưu trữ trong InfluxDB để có thể truy vấn hoặc vẽ biểu đồ sau này.

```bash
# Truy cập vào InfluxDB shell
influx

# Tạo database mới
> CREATE DATABASE cpu_hdd_mon

# (Tùy chọn) Thiết lập chỉ lưu dữ liệu trong 30 ngày để tiết kiệm bộ nhớ
> ALTER RETENTION POLICY "autogen" ON "cpu_hdd_mon" DURATION 30d REPLICATION 1 DEFAULT

> EXIT

```

---

## 3. Script Giám sát Python (`cpu_hdd_mon.py`)

Tạo file script tại đường dẫn `/mnt/dietpi_userdata/scripts/cpu_hdd_mon.py`:

```python
import subprocess
import json
import datetime
import psutil
from influxdb import InfluxDBClient

# --- CẤU HÌNH ---
DEVICE = "/dev/sda"
DB_NAME = "cpu_hdd_mon"

def get_smart_data():
    result = subprocess.run(['sudo', 'smartctl', '-a', '-j', DEVICE], capture_output=True, text=True)
    return json.loads(result.stdout) if result.stdout.strip() else {}

def get_cpu_data():
    try:
        # Lấy CPU và IOWait bằng lệnh sar (Text Mode)
        result = subprocess.run(['env', 'LC_ALL=C', 'sar', '-u', '1', '1'], capture_output=True, text=True)
        last_line = result.stdout.strip().split('\n')[-1].split()
        return {"load_total": round(100 - float(last_line[-1]), 2), "iowait": float(last_line[-3])}
    except:
        return {"load_total": 0.0, "iowait": 0.0}

def get_system_metrics():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    load1, _, _ = psutil.getloadavg()
    return {
        "mem_percent": mem.percent,
        "mem_used_gb": round(mem.used / (1024**3), 2),
        "disk_percent": disk.percent,
        "load_1min": load1
    }

def send_to_influx(smart_data, cpu_data, sys_data):
    attr_table = smart_data.get('ata_smart_attributes', {}).get('table', [])
    attrs = {attr['name']: attr['raw']['value'] for attr in attr_table}

    json_body = [{
        "measurement": "system_health",
        "tags": {"device": DEVICE, "model": smart_data.get('model_name', 'Unknown')},
        "fields": {
            "hdd_temp": float(smart_data.get('temperature', {}).get('current', 0)),
            "power_on_hours": float(attrs.get('Power_On_Hours', 0)),
            "pending_sectors": float(attrs.get('Current_Pending_Sector', 0)),
            "reallocated_sectors": float(attrs.get('Reallocated_Sector_Ct', 0)),
            "cpu_load": float(cpu_data['load_total']),
            "cpu_iowait": float(cpu_data['iowait']),
            "load_1min": float(sys_data['load_1min']),
            "mem_percent": float(sys_data['mem_percent']),
            "mem_used_gb": float(sys_data['mem_used_gb']),
            "disk_usage_percent": float(sys_data['disk_percent'])
        }
    }]
    client = InfluxDBClient('localhost', 8086, database=DB_NAME)
    client.write_points(json_body)
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Logged Successfully.")

if __name__ == "__main__":
    try:
        send_to_influx(get_smart_data(), get_cpu_data(), get_system_metrics())
    except Exception as e:
        print(f"Error: {e}")

```

---

## 4. Tự động hóa với Cron

Thiết lập để script tự động chạy mỗi 5 phút và ghi đè file log để tránh đầy bộ nhớ.

1. Mở bảng điều khiển Cron: `crontab -e`
2. Thêm dòng sau vào cuối file:

```cron
*/5 * * * * /usr/bin/python3 /mnt/dietpi_userdata/scripts/cpu_hdd_mon.py > /mnt/dietpi_userdata/scripts/hdd_cron.log 2>&1

```

---

## 5. Các chỉ số cần đặc biệt lưu ý (Health Check)

Khi kiểm tra dữ liệu trong InfluxDB (`SELECT * FROM system_health`), hãy chú ý:

* **`pending_sectors` / `reallocated_sectors**`: Phải luôn bằng **0**. Nếu > 0, ổ cứng đang hỏng vật lý.
* **`cpu_iowait`**: Nếu > 10%, ổ cứng đang quá chậm so với tốc độ xử lý của CPU.
* **`mem_percent`**: Nếu thường xuyên > 90%, server cần thêm RAM hoặc tối ưu ứng dụng.

---

## 6. Lệnh kiểm tra nhanh (Cheat Sheet)

* **Xem thời gian máy đã chạy:** `uptime -p`
* **Xem log mới nhất từ Database:**
`influx -database 'cpu_hdd_mon' -precision rfc3339 -execute 'SELECT * FROM system_health ORDER BY time DESC LIMIT 1' -format table`
* **Xem lỗi script (nếu có):** `cat /mnt/dietpi_userdata/scripts/hdd_cron.log`

---

**Bước tiếp theo bạn có thể thực hiện:**
Bản hướng dẫn này đã hoàn tất phần "xương sống" dữ liệu. Nếu bạn muốn trực quan hóa, tôi có thể giúp bạn viết **Dashboard JSON mẫu cho Grafana** để bạn chỉ cần Import là có ngay biểu đồ chuyên nghiệp. Bạn có muốn thử không?
