Dưới đây là bản tổng hợp và hướng dẫn chi tiết về các công cụ mạnh mẽ nhất trong hệ sinh thái **Claude Code** tính đến năm 2026. Bản hướng dẫn này được thiết kế để giúp bạn biến Claude từ một chatbot thành một kỹ sư phần mềm thực thụ.

---

## 🛠️ Các công cụ cốt lõi (Core Ecosystem)

### 1. Superpowers (obra)

**Mô tả:** Framework chuẩn hóa quy trình làm việc. Nó ép AI phải tuân thủ kỷ luật: Brainstorm -> Lập kế hoạch -> Viết Test (TDD) -> Code.

* **Cài đặt:**
```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

```


* **Cách sử dụng:**
* Sử dụng `/superpowers:brainstorm` để thảo luận thiết kế trước khi code.
* Dùng `/superpowers:write-plan` để AI chia nhỏ tác vụ thành các task 2-5 phút.
* Dùng `/superpowers:execute-plan` để AI tự động thực hiện và chạy test.



### 2. agents (wshobson)

**Mô tả:** Kho gồm hơn 100 agent chuyên biệt (Python, DevOps, Security...). Bạn không cần nạp mọi thứ, chỉ cài "chuyên gia" bạn cần để tiết kiệm token.

* **Cài đặt:**
```bash
/plugin marketplace add wshobson/agents
/plugin install [tên-plugin] # Ví dụ: python-development hoặc security-scanning

```


* **Cách sử dụng:** Triệu hồi các agent chuyên biệt bằng cách đề cập tên họ hoặc dùng lệnh:
* Ví dụ: `/python-development:python-scaffold` để tạo cấu trúc dự án chuẩn.



### 3. claude-mem (thedotmack)

**Mô tả:** Giải quyết vấn đề "mất trí nhớ" của AI sau mỗi phiên làm việc. Nó ghi lại nhật ký, nén bằng AI và tự động nạp lại ngữ cảnh cũ khi bạn quay lại dự án.

* **Cài đặt:**
```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem

```


* **Cách sử dụng:** * Hoạt động tự động ngầm.
* Bạn có thể xem "dòng suy nghĩ" của AI tại `http://localhost:37777`.
* Tra cứu quá khứ bằng lệnh: `/mem-search "lần trước tôi đã sửa lỗi auth như thế nào?"`



### 4. planning-with-files (OthmanAdi)

**Mô tả:** Lưu kế hoạch làm việc vào file `.md` trong project. Điều này giúp cả bạn và AI luôn nhìn thấy mục tiêu chung, không bị lạc đề khi hội thoại quá dài.

* **Cài đặt:**
```bash
/plugin marketplace add OthmanAdi/planning-with-files
/plugin install planning-with-files@planning-with-files

```


* **Cách sử dụng:**
* Gõ `/planning-with-files` để bắt đầu lập kế hoạch.
* AI sẽ tạo các file như `task_plan.md`, `findings.md`. Bạn có thể chỉnh sửa các file này để điều hướng AI.



### 5. oh-my-claudecode (Yeachan-Heo)

**Mô tả:** "Đao to búa lớn" cho việc điều phối nhiều agent (Multi-agent). Phù hợp để scale nhanh workflow mà không cần cấu hình phức tạp.

* **Cài đặt:**
```bash
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode

```


* **Cách sử dụng:** * Chạy `/oh-my-claudecode:omc-setup` để bắt đầu.
* Sử dụng các chế độ như `Autopilot` (tự trị) hoặc `Swarm` (phối hợp nhóm agent).



---

## 🚀 Các công cụ đang Trending (Advanced)

| Công cụ | Loại hình | Công dụng chính |
| --- | --- | --- |
| **Model Context Protocol (MCP)** | Giao thức | "Cổng kết nối" vạn năng giúp Claude Code đọc Database, Google Drive, hay Slack an toàn. |
| **claude-flow (ruvnet)** | Orchestration | **Cài đặt:** `npm install -g claude-flow@alpha`. Dùng để tạo các "hive-mind" (tổ hợp trí tuệ) giải quyết task siêu khó. |
| **Serena** | MCP Server | Giúp Claude hiểu sâu codebase và thực thi lệnh có kiểm soát, tránh việc AI "quậy phá" lung tung. |
| **claude-scientific-skills** | Domain Skills | **Cài đặt:** `/plugin marketplace add K-Dense-AI/claude-scientific-skills`. Cung cấp 140+ kỹ năng phân tích y sinh, hóa học và dữ liệu. |

---

## 💡 Kết luận: Cách build "AI Developer Stack" của bạn

Để đạt hiệu suất tối đa, đừng chỉ dùng Claude Code "vã". Hãy kết hợp theo công thức sau:

1. **Nền tảng:** Cài **Superpowers** để có quy trình chuẩn.
2. **Trí nhớ:** Cài **claude-mem** để không bao giờ phải giải thích lại từ đầu.
3. **Công cụ:** Cài các plugin từ **wshobson** hoặc **scientific-skills** tùy theo ngôn ngữ bạn đang viết.
4. **Kết nối:** Sử dụng **MCP** để AI có thể truy cập dữ liệu thực tế (thay vì chỉ đọc file code).

**Bước tiếp theo bạn nên làm:** Bạn có muốn tôi hướng dẫn cấu hình một **MCP Server** cụ thể (như kết nối với GitHub hay Database) để dùng cùng với các plugin này không?


Bạn có một nhận xét rất tinh tế! Đúng là Claude (đặc biệt là bản Web) đã có tính năng **Memory** để nhớ những sở thích cá nhân của bạn. Tuy nhiên, **Claude-Mem** là một "con quái vật" hoàn toàn khác, được thiết kế riêng cho dân lập trình dùng **Claude Code** trong Terminal.

Hãy tưởng tượng sự khác biệt thế này:

* **Memory mặc định của Claude:** Nhớ bạn thích dùng thư viện nào, bạn tên là gì, hay bạn muốn code theo style nào. (Giống như một người bạn nhớ tính cách của bạn).
* **Claude-Mem:** Nhớ chi tiết hôm qua bạn đã chạy lệnh Terminal nào bị lỗi, bạn đã sửa file nào, và tại sao bạn lại chọn giải pháp đó thay vì giải pháp kia. (Giống như một cuốn **nhật ký kỹ thuật siêu cấp**).

---

## Tại sao bạn lại cần nó khi đã có Memory mặc định?

Dưới đây là 3 lý do chính khiến công cụ này trở nên khác biệt:

### 1. Vượt qua giới hạn "Mất trí nhớ" sau mỗi Session

Khi bạn dùng Claude Code, mỗi lần bạn tắt Terminal hoặc gõ `/exit`, toàn bộ "luồng suy nghĩ" (context) của phiên làm việc đó sẽ bị xóa sạch. Lần sau mở lại, Claude chỉ nhìn thấy đống code hiện tại mà **không biết** bạn đã thử những gì và thất bại ở đâu.
**Claude-Mem** lưu lại toàn bộ lịch sử này vào một cơ sở dữ liệu (SQLite & Chroma) để phiên làm việc ngày mai "thừa kế" được trí khôn của ngày hôm nay.

### 2. Nén ngữ cảnh (Memory Compression)

Claude có giới hạn về số lượng từ (token) mà nó có thể nhớ trong một lúc. Nếu bạn bắt nó nhớ tất cả mọi thứ, nó sẽ nhanh chóng hết chỗ trống và trở nên "ngáo".

* **Claude-Mem** sử dụng quy trình 3 lớp: Nó chỉ nén và tóm tắt những gì quan trọng nhất.
* Khi cần, nó mới tìm kiếm (Search) và lấy đúng mẩu thông tin liên quan nhất để nạp vào đầu Claude. Điều này giúp bạn **tiết kiệm tiền (token)** và giữ cho Claude luôn sắc bén.

### 3. Có giao diện Web riêng (Web Viewer)

Điểm "ăn tiền" là bạn có thể mở trình duyệt tại `http://localhost:37777` để xem lại toàn bộ dòng suy nghĩ của AI, các quan sát (observations) và các bước thực hiện dưới dạng một dòng thời gian (Timeline).

---

## Cách cài đặt và sử dụng nhanh

Nếu bạn đã cài Claude Code, hãy chạy các lệnh sau:

1. **Thêm Marketplace:**
```bash
/plugin marketplace add thedotmack/claude-mem

```


2. **Cài đặt:**
```bash
/plugin install claude-mem

```


3. **Khởi động lại Claude Code:** Sau đó, nó sẽ tự động chạy ngầm. Bạn không cần làm gì thêm, nó sẽ tự "ghi nhật ký" cho bạn.

---

## Một lưu ý nhỏ về "Hệ sinh thái"

Bạn sẽ thấy trong GitHub này có nhắc đến **$CMEM** (một loại token trên Solana). Đây là một dự án có yếu tố cộng đồng và tiền điện tử (Crypto). Nếu bạn chỉ quan tâm đến tính năng lập trình thì cứ lờ nó đi và dùng plugin như một công cụ hỗ trợ bình thường, nó vẫn hoạt động cực kỳ hiệu quả.

> **Tóm lại:** Nếu bạn làm dự án lớn, làm nhiều ngày mới xong, thì **Claude-Mem** là thứ giúp AI không hỏi lại những câu "ngớ ngẩn" mà bạn đã giải quyết từ hôm trước.

Bạn có muốn tôi hướng dẫn cách dùng lệnh `/mem-search` để tìm lại một đoạn logic cũ trong quá khứ không?


Hệ thống bạn vừa gửi là **Claude Code Plugins: Orchestration and Automation** (của tác giả `wshobson`).

Nếu dự án *Superpowers* trước đó là một "workflow" (quy trình), thì hệ thống này giống như một **"siêu siêu thị kỹ năng"**. Nó cung cấp một số lượng khổng lồ các chuyên gia AI (Agents) và công cụ cho mọi ngóc ngách của việc lập trình.

Dưới đây là chi tiết:

---

## 1. Hệ thống này là gì?

Đây là một bộ sưu tập gồm:

* **72 Plugins:** Chia nhỏ theo từng nhiệm vụ (Backend, Frontend, Security, DevOps...).
* **108 Specialized Agents:** Các "chuyên gia" ảo. Ví dụ: thay vì chỉ có Claude chung chung, bạn sẽ có `python-pro`, `kubernetes-architect`, hay `security-auditor`.
* **15 Workflow Orchestrators:** Các bộ điều phối giúp nhiều AI làm việc cùng lúc (ví dụ: một ông thiết kế DB, một ông viết API, một ông viết Frontend).

**Điểm khác biệt:** Nó sử dụng chiến lược **"Tiết kiệm Token"**. Bạn chỉ cài những gì cần dùng, tránh việc nạp quá nhiều thông tin dư thừa làm AI bị "loãng" hoặc tốn tiền.

---

## 2. Cách cài đặt (Installation)

Tương tự như Superpowers, bạn thực hiện trong terminal của **Claude Code**:

**Bước 1: Thêm Marketplace của wshobson**

```bash
/plugin marketplace add wshobson/agents

```

**Bước 2: Cài đặt các plugin cụ thể theo nhu cầu**
Bạn không nên cài tất cả. Hãy cài theo ngôn ngữ hoặc tác vụ bạn đang làm:

* **Làm Python:** `/plugin install python-development`
* **Làm Web (JS/TS):** `/plugin install javascript-typescript`
* **Làm DevOps/K8s:** `/plugin install kubernetes-operations`
* **Muốn AI tự điều phối dự án lớn:** `/plugin install full-stack-orchestration`

---

## 3. Cách sử dụng (Usage)

Sau khi cài đặt và **khởi động lại Claude Code**, bạn sử dụng thông qua các lệnh hoặc gọi tên chuyên gia:

### Sử dụng lệnh trực tiếp (Slash Commands)

Mỗi plugin sẽ cung cấp các lệnh riêng. Ví dụ:

* `/python-development:python-scaffold`: Để tạo nhanh cấu trúc dự án Python chuẩn.
* `/full-stack-orchestration:full-stack-feature "tên tính năng"`: Để bắt đầu một quy trình làm việc đa tác nhân cho một tính năng mới.

### Tận dụng các "Siêu chuyên gia"

Bạn có thể ra lệnh cho Claude gọi đúng chuyên gia đó ra làm việc:

> *"Sử dụng `security-auditor` để kiểm tra các lỗ hổng bảo mật trong file này."*

### Cơ chế "Progressive Disclosure" (Tiết lộ dần dần)

Đây là điểm hay nhất: Các kiến thức chuyên sâu (Skills) chỉ được AI nạp vào khi cần thiết. Bạn không cần làm gì cả, AI sẽ tự nhận biết khi nào cần dùng đến skill `async-python-patterns` hay `terraform-optimization` dựa trên yêu cầu của bạn.

---

## So sánh nhanh với Superpowers

| Đặc điểm | Superpowers | Wshobson Agents |
| --- | --- | --- |
| **Trọng tâm** | Quy trình làm việc (Workflow) nghiêm ngặt, TDD. | Kho công cụ và chuyên gia đa dạng. |
| **Điểm mạnh** | Giúp code chắc chắn, ít bug, ép AI làm đúng bước. | Cung cấp kiến thức chuyên sâu cho từng ngôn ngữ/công nghệ. |
| **Quy mô** | Thích hợp cho dự án đơn lẻ, cần kỷ luật. | Thích hợp cho hệ thống lớn, đa ngôn ngữ, hạ tầng phức tạp. |

**Lời khuyên:** Bạn có thể **cài cả hai**. Dùng *Superpowers* để quản lý quy trình (brainstorm -> plan -> execute) và cài thêm các plugin từ *wshobson* để Claude có thêm kiến thức chuyên môn về ngôn ngữ bạn đang dùng (như Python hay React).

Bạn đang làm việc chủ yếu trên ngôn ngữ hay công nghệ nào (ví dụ: Node.js, Python, hay Cloud)? Tôi sẽ chỉ cho bạn plugin cụ thể nhất từ bộ này để bạn cài.


Tuyệt vời, bạn đã đi được 90% chặng đường rồi! Bước tiếp theo là kích hoạt các "siêu năng lực" này vào dự án của bạn.

Dưới đây là các bước cụ thể:

### 1. Khởi động lại Claude Code

Như thông báo bạn nhận được (`Restart Claude Code to load new plugins`), bạn cần **tắt terminal đang chạy Claude Code và mở lại**. Đây là bước bắt buộc để plugin được nạp vào bộ nhớ.

### 2. Kiểm tra lại cài đặt

Sau khi khởi động lại, hãy gõ lệnh sau để đảm bảo các lệnh của Superpowers đã sẵn sàng:

```bash
/help

```

Nếu bạn thấy danh sách có các lệnh như `/superpowers:brainstorm`, `/superpowers:write-plan`,... thì bạn đã thành công.

---

### 3. Bắt đầu Workflow thực tế

Để trải nghiệm sức mạnh của plugin này, đừng bắt đầu bằng việc viết code ngay. Hãy thực hiện theo trình tự "chuẩn" của Superpowers:

1. **Mở dự án của bạn:** Di chuyển vào thư mục code mà bạn muốn làm việc.
2. **Kích hoạt Brainstorm:** Thay vì nói "Viết cho tôi tính năng X", hãy gõ:
> `/superpowers:brainstorm "Tôi muốn thêm tính năng đăng nhập bằng Google vào ứng dụng này"`


3. **Tương tác với AI:** Claude sẽ không code ngay mà sẽ hỏi bạn các câu hỏi về kiến trúc, bảo mật, thư viện bạn muốn dùng... Cho đến khi cả hai thống nhất được một bản thiết kế (Design Doc).
4. **Lập kế hoạch (Plan):** Sau khi xong bước brainstorm, hãy dùng:
> `/superpowers:write-plan`
> Claude sẽ chia nhỏ việc đó ra thành 5-10 task cực nhỏ.


5. **Thực thi (Execute):** Cuối cùng, gõ:
> `/superpowers:execute-plan`
> Lúc này, Claude sẽ bắt đầu tạo branch mới, viết test lỗi, viết code pass test và commit một cách tự động.



### Một vài lưu ý quan trọng:

* **Đừng sốt ruột:** Superpowers bắt bạn phải "nghĩ kỹ trước khi làm". Thời gian đầu có vẻ chậm vì phải trả lời câu hỏi, nhưng code đầu ra sẽ rất chất lượng và ít bug.
* **TDD là bắt buộc:** Nếu bạn thấy Claude tự xóa code nó vừa viết, đừng hoảng nhé. Đó là vì nó phát hiện ra nó chưa viết test cho đoạn code đó (quy tắc của plugin).

Bạn đã có dự án nào cụ thể để thử nghiệm chưa? Nếu có, hãy thử chạy lệnh `/superpowers:brainstorm` với ý tưởng đó xem sao!

Dự án **Superpowers** này thực chất là một "hệ điều hành workflow" dành cho các AI coder (như Claude Code, Codex). Thay vì để AI tự do viết code (thường dễ gây lỗi hoặc lạc đề), Superpowers ép AI phải tuân thủ một quy trình kỹ thuật nghiêm ngặt.

Dưới đây là cách bạn có thể bắt đầu sử dụng nó:

---

## 1. Cài đặt (Installation)

Tùy vào công cụ bạn đang dùng mà cách cài đặt sẽ khác nhau:

* **Nếu dùng Claude Code:** Đây là cách tối ưu nhất. Bạn mở terminal của Claude Code và chạy:
```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

```


* **Nếu dùng Codex hoặc OpenCode:** Bạn chỉ cần copy và gửi link hướng dẫn cấu hình (URL trong file README bạn gửi) và yêu cầu AI "Fetch and follow instructions".

## 2. Quy trình hoạt động (Workflow)

Khi đã cài đặt, AI của bạn sẽ không còn "nhảy bổ" vào viết code ngay. Nó sẽ tự động kích hoạt các kỹ năng theo trình tự:

1. **Brainstorming:** AI sẽ hỏi bạn mục tiêu cuối cùng là gì, phản biện lại ý tưởng của bạn và chia nhỏ thiết kế ra để bạn duyệt.
2. **Writing Plans:** Sau khi bạn chốt thiết kế, AI lập một kế hoạch cực kỳ chi tiết. Mỗi tác vụ (task) chỉ kéo dài khoảng 2-5 phút.
3. **Subagent-Driven Development:** AI chính sẽ "thuê" các AI phụ (subagents) để thực hiện từng task nhỏ. Điều này giúp code sạch và ít lỗi hơn.
4. **Test-Driven Development (TDD):** Đây là điểm "vô học" nhất nhưng cực kỳ hiệu quả: AI **bắt buộc** phải viết unit test lỗi trước, sau đó mới viết code để pass test đó. Nếu AI viết code trước khi có test, hệ thống sẽ tự động xóa code đó.

## 3. Các lệnh quan trọng

Sau khi cài đặt, bạn có thể kiểm tra xem các "siêu năng lực" đã hoạt động chưa bằng lệnh:

* `/help`: Liệt kê các lệnh mới như `/superpowers:brainstorm`, `/superpowers:write-plan`.
* `/plugin update superpowers`: Để cập nhật các kỹ năng mới nhất.

---

### Tại sao bạn nên dùng cái này?

Nếu bạn đang làm các dự án phức tạp, Superpowers giúp AI giữ được "sự tỉnh táo":

* **Kỷ luật cao:** Ép AI dùng Git worktrees để tách biệt môi trường làm việc.
* **Chống lười:** Buộc AI phải viết test và review code nghiêm chỉnh.
* **Tự động hóa:** Bạn có thể để AI tự chạy trong vài giờ mà không lo nó đi chệch khỏi kế hoạch ban đầu.

> **Lưu ý nhỏ:** Công cụ này cực kỳ thích hợp nếu bạn muốn AI đóng vai trò như một **Senior Engineer** dẫn dắt các **Junior Subagents**, thay vì chỉ là một chatbot viết code đơn thuần.

Bạn có đang sử dụng **Claude Code** hay một công cụ AI coding nào cụ thể không? Tôi có thể hướng dẫn bạn cấu hình chi tiết hơn cho công cụ đó.
