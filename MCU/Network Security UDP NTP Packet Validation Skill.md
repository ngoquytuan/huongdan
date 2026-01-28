# Network Security & UDP/NTP Packet Validation

## Attack Vectors for Embedded Time Systems

### Threat Model

1. **UDP Spoofing**: Attacker sends fake NTP packets with wrong time
2. **Packet Flooding**: Overwhelm W5500 RX buffers, cause DoS
3. **Amplification Attack**: Use NTP server as DDoS reflector
4. **Time Desync**: Malicious time injection breaks dependent systems
5. **Buffer Overflow**: Crafted packets corrupt memory/stack

## NTP Packet Structure Validation

### Standard NTP Packet (48 bytes)

```c
typedef struct __attribute__((packed)) {
    uint8_t  li_vn_mode;          // Leap Indicator, Version, Mode
    uint8_t  stratum;             // 0-15, 0=unspecified, 1=primary
    uint8_t  poll;                // Poll interval (log2 seconds)
    int8_t   precision;           // Precision (log2 seconds)
    uint32_t root_delay;          // Round-trip delay to reference
    uint32_t root_dispersion;     // Dispersion to reference
    uint32_t reference_id;        // Reference clock identifier
    uint32_t reference_timestamp[2];   // Last clock update
    uint32_t originate_timestamp[2];   // Client request time
    uint32_t receive_timestamp[2];     // Server received time
    uint32_t transmit_timestamp[2];    // Server transmit time
} NTPPacket;  // Exactly 48 bytes
```

### Critical Validation Steps

```c
#define NTP_PACKET_SIZE 48
#define NTP_VERSION_3   3
#define NTP_VERSION_4   4
#define NTP_MODE_CLIENT 3
#define NTP_MODE_SERVER 4

bool validate_ntp_packet(uint8_t *buffer, uint16_t len) {
    // ✅ CRITICAL: Exact length check
    if (len != NTP_PACKET_SIZE) {
        DEBUG_LOG("[NTP] Invalid packet length: %d", len);
        return false;
    }
    
    NTPPacket *pkt = (NTPPacket *)buffer;
    
    // Extract fields from li_vn_mode byte
    uint8_t leap = (pkt->li_vn_mode >> 6) & 0x03;
    uint8_t version = (pkt->li_vn_mode >> 3) & 0x07;
    uint8_t mode = pkt->li_vn_mode & 0x07;
    
    // ✅ Version check
    if (version != NTP_VERSION_3 && version != NTP_VERSION_4) {
        DEBUG_LOG("[NTP] Invalid version: %d", version);
        return false;
    }
    
    // ✅ Mode check (must be server response)
    if (mode != NTP_MODE_SERVER) {
        DEBUG_LOG("[NTP] Invalid mode: %d (expected %d)", 
            mode, NTP_MODE_SERVER);
        return false;
    }
    
    // ✅ Stratum check (0=invalid, 1-15=valid, 16+=reserved)
    if (pkt->stratum == 0 || pkt->stratum > 15) {
        DEBUG_LOG("[NTP] Invalid stratum: %d", pkt->stratum);
        return false;
    }
    
    // ✅ Leap indicator check
    if (leap == 3) {  // 3 = clock not synchronized
        DEBUG_LOG("[NTP] Server clock unsynchronized");
        return false;
    }
    
    // ✅ Timestamp sanity check
    uint32_t tx_timestamp_sec = ntohl(pkt->transmit_timestamp[0]);
    
    // NTP epoch: 1900-01-01
    // Valid range: 2000-01-01 to 2100-01-01
    #define NTP_TIMESTAMP_2000 3155673600UL  // Seconds from 1900 to 2000
    #define NTP_TIMESTAMP_2100 3471292800UL  // Seconds from 1900 to 2100
    
    if (tx_timestamp_sec < NTP_TIMESTAMP_2000 || 
        tx_timestamp_sec > NTP_TIMESTAMP_2100) {
        DEBUG_LOG("[NTP] Timestamp out of range: %lu", tx_timestamp_sec);
        return false;
    }
    
    return true;
}
```

## Rate Limiting to Prevent Attacks

### Problem: UDP Flood Overwhelms RX Buffer

**Bug discovered:**
```c
// ❌ WRONG - No rate limiting
void W5500_ProcessNTP(void) {
    while (W5500_GetRxSize() > 0) {
        uint8_t buffer[48];
        uint16_t len = W5500_RecvData(buffer, 48);
        process_ntp_packet(buffer, len);
    }
}
// If attacker sends 1000 packets, system hangs processing them
```

**✅ CORRECT - Quota-based processing:**
```c
#define MAX_NTP_PACKETS_PER_CYCLE 10
#define NTP_UPDATE_COOLDOWN_MS 1000

static uint32_t last_ntp_update = 0;
static uint16_t packets_this_cycle = 0;

void W5500_ProcessNTP(void) {
    uint32_t now = HAL_GetTick();
    
    // Reset quota every cycle
    if (now - last_ntp_update > NTP_UPDATE_COOLDOWN_MS) {
        packets_this_cycle = 0;
        last_ntp_update = now;
    }
    
    // ✅ Process limited number of packets
    while (W5500_GetRxSize() > 0 && 
           packets_this_cycle < MAX_NTP_PACKETS_PER_CYCLE) {
        
        uint8_t buffer[48];
        uint16_t len = W5500_RecvData(buffer, 48);
        
        if (validate_ntp_packet(buffer, len)) {
            process_ntp_packet(buffer, len);
            packets_this_cycle++;
        } else {
            // Discard invalid packet
            packets_this_cycle++;  // Still counts against quota
        }
    }
    
    // Discard remaining packets to prevent buffer accumulation
    if (packets_this_cycle >= MAX_NTP_PACKETS_PER_CYCLE) {
        W5500_FlushRxBuffer();
        DEBUG_LOG("[NTP] Rate limit exceeded, flushed RX buffer");
    }
}
```

## Source IP Validation

### IP Whitelist for NTP Servers

```c
#define MAX_NTP_SERVERS 4

typedef struct {
    uint8_t ip[4];
    uint16_t port;
    bool enabled;
} NTPServerConfig;

NTPServerConfig ntp_servers[MAX_NTP_SERVERS] = {
    {{216, 239, 35, 0}, 123, true},   // time.google.com
    {{129, 6, 15, 28}, 123, true},    // time.nist.gov
    {{192, 168, 1, 1}, 123, true},    // Local NTP server
    {{0, 0, 0, 0}, 123, false}        // Disabled slot
};

bool is_trusted_ntp_source(uint8_t *src_ip, uint16_t src_port) {
    if (src_port != 123) {
        DEBUG_LOG("[NTP] Invalid source port: %d", src_port);
        return false;
    }
    
    for (int i = 0; i < MAX_NTP_SERVERS; i++) {
        if (!ntp_servers[i].enabled) continue;
        
        if (memcmp(src_ip, ntp_servers[i].ip, 4) == 0) {
            return true;
        }
    }
    
    DEBUG_LOG("[NTP] Untrusted source: %d.%d.%d.%d:%d",
        src_ip[0], src_ip[1], src_ip[2], src_ip[3], src_port);
    
    return false;
}

void W5500_ProcessNTP(void) {
    uint8_t src_ip[4];
    uint16_t src_port;
    
    W5500_GetRemoteInfo(&src_ip, &src_port);
    
    // ✅ Validate source before processing
    if (!is_trusted_ntp_source(src_ip, src_port)) {
        W5500_FlushRxBuffer();
        return;
    }
    
    // Process packet only if from trusted source
    // ...
}
```

## W5500 Buffer Management

### Problem: RX Buffer Deadlock

**Bug discovered:**
```c
// ❌ WRONG - Buffer size query race condition
void read_udp_packet(void) {
    uint16_t len = W5500_GetRxSize();  // Returns 48
    
    // ⚠️ Race: Another packet arrives here
    //     RX buffer now has 96 bytes
    
    uint8_t buffer[48];  // Only allocated 48 bytes
    W5500_ReadData(buffer, len);  // Tries to read 96! Overflow!
}
```

**✅ CORRECT - Read with size cap:**
```c
#define MAX_NTP_PACKET_SIZE 48

void read_udp_packet(void) {
    uint16_t len = W5500_GetRxSize();
    
    // ✅ Cap read size to prevent overflow
    if (len > MAX_NTP_PACKET_SIZE) {
        DEBUG_LOG("[NTP] Oversized packet: %d bytes, truncating", len);
        len = MAX_NTP_PACKET_SIZE;
    }
    
    uint8_t buffer[MAX_NTP_PACKET_SIZE];
    W5500_ReadData(buffer, len);
    
    // Validate after reading
    if (!validate_ntp_packet(buffer, len)) {
        return;  // Discard invalid packet
    }
    
    process_ntp_packet(buffer, len);
}
```

### W5500 Socket State Validation

```c
typedef enum {
    SOCK_CLOSED      = 0x00,
    SOCK_INIT        = 0x13,
    SOCK_LISTEN      = 0x14,
    SOCK_ESTABLISHED = 0x17,
    SOCK_CLOSE_WAIT  = 0x1C,
    SOCK_UDP         = 0x22,
    SOCK_IPRAW       = 0x32,
    SOCK_MACRAW      = 0x42,
    SOCK_PPPOE       = 0x5F
} W5500SocketStatus;

bool w5500_socket_ready(uint8_t socket) {
    uint8_t status = W5500_GetSocketStatus(socket);
    
    // ✅ Check socket is in valid state
    if (status != SOCK_UDP && status != SOCK_ESTABLISHED) {
        DEBUG_LOG("[W5500] Socket %d invalid state: 0x%02X", 
            socket, status);
        
        // Recover by closing and reopening
        W5500_Close(socket);
        W5500_Socket(socket, Sn_MR_UDP, NTP_PORT, 0);
        
        return false;
    }
    
    return true;
}
```

## HTTP Security (Web Configuration Interface)

### Input Validation for Configuration Parameters

```c
#define MAX_CONFIG_VALUE_LEN 64

bool validate_ip_address(const char *ip) {
    int a, b, c, d;
    
    // ✅ Strict format check
    if (sscanf(ip, "%d.%d.%d.%d", &a, &b, &c, &d) != 4) {
        return false;
    }
    
    // ✅ Range check each octet
    if (a < 0 || a > 255 || b < 0 || b > 255 ||
        c < 0 || c > 255 || d < 0 || d > 255) {
        return false;
    }
    
    // ✅ Reject reserved addresses
    if (a == 0 || a == 127 || a >= 224) {
        return false;  // Network, loopback, multicast
    }
    
    return true;
}

bool validate_timezone_offset(const char *offset) {
    // Format: "+05:30" or "-08:00"
    int hours, minutes;
    char sign;
    
    if (sscanf(offset, "%c%d:%d", &sign, &hours, &minutes) != 3) {
        return false;
    }
    
    if (sign != '+' && sign != '-') return false;
    if (hours < 0 || hours > 14) return false;
    if (minutes < 0 || minutes > 59) return false;
    if (minutes % 15 != 0) return false;  // Only 00, 15, 30, 45
    
    return true;
}

void http_handle_config_update(char *params) {
    char ntp_server[MAX_CONFIG_VALUE_LEN];
    char timezone[MAX_CONFIG_VALUE_LEN];
    
    // ✅ Bounded string copy
    strncpy(ntp_server, get_param(params, "ntp_server"), 
        MAX_CONFIG_VALUE_LEN - 1);
    ntp_server[MAX_CONFIG_VALUE_LEN - 1] = '\0';
    
    strncpy(timezone, get_param(params, "timezone"), 
        MAX_CONFIG_VALUE_LEN - 1);
    timezone[MAX_CONFIG_VALUE_LEN - 1] = '\0';
    
    // ✅ Validate before applying
    if (!validate_ip_address(ntp_server)) {
        send_http_error("Invalid NTP server IP");
        return;
    }
    
    if (!validate_timezone_offset(timezone)) {
        send_http_error("Invalid timezone format");
        return;
    }
    
    // Safe to apply configuration
    apply_ntp_server(ntp_server);
    apply_timezone(timezone);
    
    send_http_success("Configuration updated");
}
```

### Cross-Site Request Forgery (CSRF) Protection

```c
// Generate random token on boot
uint32_t csrf_token;

void init_csrf_protection(void) {
    // Use hardware RNG if available
    csrf_token = HAL_RNG_GetRandomNumber();
    
    DEBUG_LOG("[HTTP] CSRF token: 0x%08lX", csrf_token);
}

bool validate_csrf_token(char *params) {
    char token_str[16];
    uint32_t provided_token;
    
    strncpy(token_str, get_param(params, "token"), 15);
    token_str[15] = '\0';
    
    provided_token = strtoul(token_str, NULL, 16);
    
    if (provided_token != csrf_token) {
        DEBUG_LOG("[HTTP] CSRF token mismatch: expected 0x%08lX, got 0x%08lX",
            csrf_token, provided_token);
        return false;
    }
    
    return true;
}

void http_handle_post_request(char *params) {
    // ✅ Check CSRF token for state-changing operations
    if (!validate_csrf_token(params)) {
        send_http_error("Invalid CSRF token");
        return;
    }
    
    // Process validated request
    http_handle_config_update(params);
}
```

## SNMP Security

### Community String Validation

```c
#define SNMP_COMMUNITY_LEN 32

char snmp_read_community[SNMP_COMMUNITY_LEN] = "public";
char snmp_write_community[SNMP_COMMUNITY_LEN] = "private";

bool validate_snmp_community(char *provided, bool write_access) {
    char *expected = write_access ? 
        snmp_write_community : snmp_read_community;
    
    // ✅ Constant-time comparison to prevent timing attacks
    size_t len = strlen(provided);
    if (len != strlen(expected)) return false;
    
    uint8_t diff = 0;
    for (size_t i = 0; i < len; i++) {
        diff |= provided[i] ^ expected[i];
    }
    
    if (diff != 0) {
        DEBUG_LOG("[SNMP] Invalid community string");
        return false;
    }
    
    return true;
}
```

### OID Access Control

```c
typedef enum {
    ACCESS_NONE = 0,
    ACCESS_READ = 1,
    ACCESS_WRITE = 2,
    ACCESS_READ_WRITE = 3
} SNMPAccess;

typedef struct {
    const char *oid;
    SNMPAccess access;
} OIDAccessControl;

const OIDAccessControl oid_acl[] = {
    {"1.3.6.1.2.1.1.1.0", ACCESS_READ},      // sysDescr (read-only)
    {"1.3.6.1.2.1.1.3.0", ACCESS_READ},      // sysUpTime (read-only)
    {"1.3.6.1.2.1.1.5.0", ACCESS_READ_WRITE}, // sysName (read-write)
    {"1.3.6.1.4.1.12345.1", ACCESS_READ},    // Custom time OID
    {NULL, ACCESS_NONE}
};

SNMPAccess get_oid_access(const char *oid) {
    for (int i = 0; oid_acl[i].oid != NULL; i++) {
        if (strcmp(oid, oid_acl[i].oid) == 0) {
            return oid_acl[i].access;
        }
    }
    
    // Default: no access for unknown OIDs
    return ACCESS_NONE;
}

bool handle_snmp_request(char *oid, char *community, bool is_write) {
    // ✅ Check community string
    if (!validate_snmp_community(community, is_write)) {
        return false;
    }
    
    // ✅ Check OID permissions
    SNMPAccess access = get_oid_access(oid);
    
    if (is_write && !(access & ACCESS_WRITE)) {
        DEBUG_LOG("[SNMP] Write denied for OID: %s", oid);
        return false;
    }
    
    if (!is_write && !(access & ACCESS_READ)) {
        DEBUG_LOG("[SNMP] Read denied for OID: %s", oid);
        return false;
    }
    
    // Process authorized request
    return true;
}
```

## Firewall Rules (Defense in Depth)

```c
typedef struct {
    uint8_t src_ip[4];
    uint8_t src_mask[4];
    uint16_t dst_port;
    bool allow;
} FirewallRule;

#define MAX_FIREWALL_RULES 16

FirewallRule firewall_rules[MAX_FIREWALL_RULES] = {
    // Allow NTP from any source
    {{0, 0, 0, 0}, {0, 0, 0, 0}, 123, true},
    
    // Allow HTTP only from local network
    {{192, 168, 1, 0}, {255, 255, 255, 0}, 80, true},
    
    // Allow SNMP only from management subnet
    {{10, 0, 0, 0}, {255, 255, 0, 0}, 161, true},
    
    // Deny all other traffic (implicit)
};

bool firewall_check(uint8_t *src_ip, uint16_t dst_port) {
    for (int i = 0; i < MAX_FIREWALL_RULES; i++) {
        FirewallRule *rule = &firewall_rules[i];
        
        // Check if source IP matches rule
        bool ip_match = true;
        for (int j = 0; j < 4; j++) {
            if ((src_ip[j] & rule->src_mask[j]) != 
                (rule->src_ip[j] & rule->src_mask[j])) {
                ip_match = false;
                break;
            }
        }
        
        // Check if destination port matches
        if (ip_match && dst_port == rule->dst_port) {
            if (!rule->allow) {
                DEBUG_LOG("[FW] Blocked: %d.%d.%d.%d:%d",
                    src_ip[0], src_ip[1], src_ip[2], src_ip[3], dst_port);
            }
            return rule->allow;
        }
    }
    
    // Default: deny
    DEBUG_LOG("[FW] Blocked (default deny): %d.%d.%d.%d:%d",
        src_ip[0], src_ip[1], src_ip[2], src_ip[3], dst_port);
    return false;
}
```

## Testing & Validation

### Fuzzing NTP Packets

```python
#!/usr/bin/env python3
import socket
import struct
import random

def fuzz_ntp_server(target_ip, target_port=123):
    """Send malformed NTP packets to test validation"""
    
    test_cases = [
        # Test 1: Wrong packet size
        (b'\x00' * 32, "Undersized packet (32 bytes)"),
        (b'\x00' * 64, "Oversized packet (64 bytes)"),
        
        # Test 2: Invalid version
        (struct.pack('!B', 0x00 | (7 << 3) | 4) + b'\x00' * 47, "Version 7"),
        
        # Test 3: Invalid mode
        (struct.pack('!B', 0x00 | (4 << 3) | 7) + b'\x00' * 47, "Mode 7"),
        
        # Test 4: Invalid stratum
        (struct.pack('!BB', 0x1C, 0) + b'\x00' * 46, "Stratum 0"),
        (struct.pack('!BB', 0x1C, 16) + b'\x00' * 46, "Stratum 16"),
        
        # Test 5: Timestamp out of range
        (struct.pack('!BB', 0x1C, 1) + b'\x00' * 22 + 
         struct.pack('!I', 0) + b'\x00' * 20, "Timestamp = 0"),
    ]
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for packet, description in test_cases:
        print(f"Testing: {description}")
        sock.sendto(packet, (target_ip, target_port))
    
    sock.close()

if __name__ == '__main__':
    fuzz_ntp_server('192.168.1.100')
```

### Packet Flood Test

```python
#!/usr/bin/env python3
import socket
import time

def flood_test(target_ip, target_port=123, duration=10):
    """Send rapid NTP packets to test rate limiting"""
    
    # Valid NTP packet
    packet = b'\x1c' + b'\x00' * 47
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    start_time = time.time()
    count = 0
    
    while time.time() - start_time < duration:
        sock.sendto(packet, (target_ip, target_port))
        count += 1
    
    sock.close()
    
    print(f"Sent {count} packets in {duration} seconds")
    print(f"Rate: {count/duration:.1f} packets/second")

if __name__ == '__main__':
    flood_test('192.168.1.100')
```

## Summary Checklist

Before deploying networked embedded system:

- [ ] NTP packet length validated (exactly 48 bytes)
- [ ] NTP version/mode/stratum checked
- [ ] NTP timestamp range validated
- [ ] Rate limiting implemented (quota per cycle)
- [ ] Source IP whitelist enforced
- [ ] W5500 RX buffer protected from overflow
- [ ] HTTP input validated (IP, timezone, etc.)
- [ ] CSRF protection for state-changing operations
- [ ] SNMP community strings validated
- [ ] SNMP OID access control enforced
- [ ] Firewall rules configured
- [ ] Fuzz tested with malformed packets
- [ ] Flood tested for DoS resistance
- [ ] Long-duration test (48+ hours under attack)
