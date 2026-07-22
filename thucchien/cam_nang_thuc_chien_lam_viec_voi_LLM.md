# Cẩm Nang Thực Chiến: Làm Việc Hiệu Quả Với LLM

*Dành cho sinh viên học tập và nghiên cứu cùng AI*

---

## Phần 1: Hiểu đúng bản chất — trước khi dùng, phải biết mình đang dùng cái gì

Phần lớn người dùng LLM sai không phải vì thiếu kỹ năng, mà vì mang nhầm mô hình tư duy (mental model) của "con người" hoặc "phần mềm truyền thống" sang áp cho LLM. Ba khái niệm sau là nền tảng, hiểu sai một trong ba là hiểu sai cả cách dùng.

### 1.1 Context là gì

Context **không phải trí nhớ**. Context là **toàn bộ những gì model nhìn thấy tại đúng thời điểm nó sinh ra câu trả lời** — gồm: system prompt, toàn bộ lịch sử chat từ đầu phiên, tài liệu/ảnh bạn đính kèm, kết quả tool gọi được (search, đọc file...). Hết. Không có gì tồn tại ngoài cái danh sách này.

Hệ quả quan trọng nhất: **mọi lượt trả lời là một phép tính độc lập, mới hoàn toàn**, chỉ khác nhau ở chỗ input (context) dài ngắn khác nhau. Model không "nhớ lại" cuộc nói chuyện — nó *đọc lại từ đầu* toàn bộ context mỗi lần bạn gửi tin nhắn mới. Vì vậy:

- Context càng dài, càng có nhiều thứ để "đọc lại", và không phải phần nào cũng được xử lý đều nhau (xem hiện tượng *lost-in-the-middle* ở mục 3.2).
- Nếu một thông tin quan trọng nằm cách đây 50 lượt chat, đừng mặc định model "còn nhớ" — nó chỉ nhớ nếu thông tin đó còn nằm *trong context hiện tại* và model *xử lý đúng* phần đó.

### 1.2 "Khả năng nhớ" giữa các phiên chat — không phải học, mà là chưng cất

Đây là điểm gây hiểu lầm nhiều nhất. Khi một sản phẩm AI nói "tôi nhớ bạn thích X từ lần trước", **model không hề học lại, không hề cập nhật trọng số (weights) của nó**. Cái đang diễn ra là:

1. Có một **hệ thống bên ngoài model** (không phải bản thân LLM) đọc lại các cuộc hội thoại cũ.
2. Hệ thống đó **tóm tắt/chưng cất** những điểm được cho là đáng nhớ thành vài dòng văn bản ngắn.
3. Vài dòng đó được **nhét vào context của phiên chat mới**, y như bạn tự paste một đoạn ghi chú vào đầu tin nhắn.

Nói cách khác: "trí nhớ" của một AI hiện nay = context cũ được nén lại rồi tái sử dụng, không phải model "học thuộc" theo nghĩa neural network cập nhật tham số. Hai hệ quả thực tế:

- Bản tóm tắt có thể **sai lệch hoặc lỗi thời** — vì nó là một phép tóm tắt (lossy), không phải bản ghi đầy đủ.
- Không có gì đảm bảo thứ bạn nói hôm nay sẽ được "nhớ" chính xác hôm sau — nó phụ thuộc vào hệ thống chưng cất có chọn đúng thông tin đó để giữ lại hay không.

**Bài học:** đừng dựa dẫm vào "AI sẽ nhớ" cho những thông tin quan trọng, đặc biệt trong nghiên cứu — luôn nhắc lại tường minh những gì cần model dùng đúng trong context hiện tại, thay vì tin nó tự nhớ từ phiên trước.

### 1.3 Ảo giác (hallucination) là gì

Ảo giác **không phải lỗi phần mềm theo nghĩa "bug cần fix"** — nó là hệ quả tất yếu của cơ chế sinh văn bản: model không có khái niệm "tra cứu sự thật", nó chỉ có một việc duy nhất là **sinh ra chuỗi token có xác suất hợp lý nhất tiếp theo**, dựa trên những gì đã học và context hiện tại. Khi context đủ rõ và đủ dữ liệu hỗ trợ, chuỗi "hợp lý nhất" trùng với sự thật. Khi không đủ, chuỗi "hợp lý nhất" vẫn được sinh ra — chỉ là nó không còn đúng nữa. Model **không biết** nó đang bịa — với nó, quá trình sinh ra câu đúng và câu sai là **cùng một cơ chế**, không có công tắc nào để phân biệt.

---

## Phần 2: Vì sao ảo giác xảy ra — và tại sao lỗi không chỉ ở model

### 2.1 Câu hỏi mơ hồ → model buộc phải "đoán"

Khi đề bài không đủ ràng buộc, model không có lựa chọn "dừng lại và hỏi" như một người cộng tác giỏi sẽ làm — trong nhiều tình huống, nó bắt buộc phải chọn phương án có xác suất hợp lý nhất theo phân phối nó học được, dù dữ liệu đầu vào không đủ để chọn chắc chắn. Hỏi "Tóm tắt tài liệu này" (không nói tóm tắt phần nào, độ dài bao nhiêu, tập trung khía cạnh gì) — model sẽ tự chọn một cách hiểu, và đó chính là điểm gieo mầm cho việc "chọn nhầm" hướng, chọn nhầm chi tiết, hoặc lấp đầy phần thiếu bằng suy đoán.

### 2.2 "Bản tính lấy lòng" — hệ quả học từ con người, không phải bịa đặt vô cớ

Đây là phần tinh tế nhất: các model hiện đại được tinh chỉnh dựa trên phản hồi của con người (RLHF) — tức là, model được thưởng khi câu trả lời khiến người đánh giá *hài lòng*. Vấn đề: con người có xu hướng **thích câu trả lời tự tin, đầy đủ, ngay lập tức** hơn là câu "tôi không biết" hoặc "câu hỏi của bạn chưa đủ rõ, cho tôi hỏi lại". Kết quả huấn luyện là model học được một thiên hướng thực: **thà đưa ra một câu trả lời nghe hợp lý còn hơn từ chối hoặc hỏi ngược lại** — vì trong dữ liệu huấn luyện, hành vi "trả lời" được thưởng nhiều hơn hành vi "hỏi lại/từ chối", ngay cả khi im lặng hỏi lại mới là lựa chọn đúng đắn hơn.

Đây không phải model "cố tình lừa" — nó là hệ quả tự nhiên của việc học từ một tập phản hồi con người vốn thiên vị về sự tự tin.

### 2.3 Công thức của ảo giác

> **Ảo giác = (Đầu bài chưa đủ ràng buộc) × (Model bị huấn luyện thiên về trả lời tự tin hơn là hỏi lại/từ chối)**

Hai vế nhân với nhau: đầu bài rõ và chặt sẽ thu hẹp không gian "đoán" của model tới mức gần như chỉ còn một đáp án đúng để chọn — dù model vẫn có thiên hướng tự tin, nhưng không còn nhiều chỗ để thiên hướng đó gây hại. Ngược lại, đầu bài càng mơ hồ, thiên hướng "thà đoán còn hơn hỏi" càng có đất diễn.

**Hệ quả thực chiến quan trọng nhất: trách nhiệm giảm ảo giác phần lớn nằm ở người ra đề bài, không chỉ ở model.**

---

## Phần 3: Kỹ thuật thực chiến

### 3.1 Đặt câu hỏi để thu hẹp không gian "đoán" của model

| Thay vì... | Hãy... |
|---|---|
| "Tóm tắt tài liệu này" | "Tóm tắt phần Phương pháp (mục 3) trong 150 từ, tập trung vào cỡ mẫu và cách chọn mẫu" |
| "Code này sai ở đâu?" | "Hàm `calc_tax()` trả về sai với input âm — đây là log lỗi, đây là input mẫu, hãy chỉ ra dòng gây lỗi" |
| "Phân tích dữ liệu này giúp tôi" | "Phân tích cột `revenue` theo `region`, trả về bảng top 3 vùng tăng trưởng, không suy diễn nguyên nhân nếu dữ liệu không có cột giải thích" |

Nguyên tắc chung: nếu đầu bài có thể được hiểu theo hai cách hợp lý trở lên, model sẽ chọn một cách — và bạn không biết nó chọn cách nào cho tới khi đọc xong câu trả lời. Rõ ràng ngay từ đầu tiết kiệm hơn sửa sau.

### 3.2 Chủ động yêu cầu model "được phép nói không biết"

Vì thiên hướng ở mục 2.2 là do huấn luyện, cách hiệu quả nhất để giảm nó là **tường minh cho phép** hành vi ngược lại ngay trong prompt:

- "Nếu thông tin không có trong tài liệu, hãy nói rõ 'không tìm thấy trong tài liệu' thay vì suy đoán."
- "Nếu câu hỏi của tôi chưa đủ rõ để trả lời chính xác, hãy hỏi lại trước khi làm."
- "Đánh dấu rõ phần nào là sự kiện có trong nguồn, phần nào là suy luận/diễn giải của bạn."

Câu lệnh dạng này không loại bỏ hoàn toàn thiên hướng tự tin, nhưng nó thay đổi "phần thưởng ngầm" trong chính lượt trả lời đó — bạn đang tự tay nói với model rằng lần này, hỏi lại/từ chối *mới là điều bạn muốn*.

### 3.3 Tự kiểm tra xem model có thực sự "đọc" hay đang "đoán"

Đừng tin lời model tự nhận là đã đọc kỹ — hãy tự verify bằng vài kỹ thuật đơn giản:

- **Cấy fact lạ (canary test)**: chèn một thông tin bịa hoàn toàn không trùng kiến thức nền vào tài liệu, hỏi lại đúng thông tin đó. Trả lời đúng → chắc chắn model đọc context, không phải đoán từ kiến thức có sẵn.
- **Test cắt bớt (ablation)**: chạy cùng câu hỏi với tài liệu đầy đủ và tài liệu đã xoá đoạn chứa đáp án. Nếu vẫn trả lời đúng khi thiếu đoạn đó → model đang bịa từ kiến thức nền, không phải đọc tài liệu.
- **Đối chiếu tài liệu dài với câu hỏi ở nhiều vị trí khác nhau**: model có xu hướng đọc tốt hơn ở đầu/cuối tài liệu, kém hơn ở giữa (*lost-in-the-middle*). Với tài liệu dài, đừng chỉ hỏi về phần đầu để "test cho có" — hỏi cả phần giữa.
- **Với ảnh/scan**: đối chiếu chéo với công cụ OCR khác, hoặc crop riêng vùng nghi ngờ (số liệu, tên riêng) rồi hỏi lại chỉ vùng đó — model dễ "tự sửa" các chi tiết lạ/hiếm (số, tên riêng, dấu câu tiếng Việt) theo hướng "nghe hợp lý" hơn là đúng pixel.

### 3.4 Quản lý hội thoại dài

- Hội thoại càng dài, context càng "loãng" — thông tin quan trọng nói từ đầu có thể bị model xử lý kém chính xác hơn so với thông tin vừa nói. Nếu một chi tiết quan trọng đã nói từ lâu, **nhắc lại tường minh** thay vì tin model tự nhớ.
- Khi đổi chủ đề hoàn toàn, cân nhắc mở phiên chat mới — context cũ không liên quan chỉ làm tăng "nhiễu", tăng khả năng model lẫn lộn giữa các mạch thông tin khác nhau.
- Đừng nhầm "chat có bật tính năng nhớ giữa các phiên" với "model học từ bạn" — như mục 1.2, đó vẫn là chưng cất văn bản, không phải học.

### 3.5 Khi nào bắt buộc phải nghi ngờ và double-check

Luôn tự kiểm tra độc lập (không chỉ hỏi lại model đó) khi:

- Con số cụ thể (số liệu tài chính, ngày tháng, mã số, trích dẫn điều luật/công thức).
- Tên riêng, thuật ngữ hiếm, hoặc bất cứ thứ gì có nhiều biến thể chính tả gần giống nhau.
- Câu hỏi đóng vai "chuyên gia" về một lĩnh vực rất hẹp — model có thể tự tin trả lời dù kiến thức nền mỏng.
- Trích dẫn nguồn/quote — luôn yêu cầu model chỉ rõ trích từ đâu, rồi tự bạn verify nguồn đó có thật và đúng nội dung không.

---

## Phần 4: Checklist nhanh trước khi tin một câu trả lời

- [ ] Đầu bài của tôi có thể hiểu theo hai cách khác nhau không? Nếu có → viết lại cho chặt hơn.
- [ ] Tôi có yêu cầu model được phép nói "không biết"/hỏi lại chưa?
- [ ] Câu trả lời có số liệu, tên riêng, trích dẫn quan trọng không? → cần verify độc lập.
- [ ] Nếu tài liệu dài, tôi có test cả phần giữa tài liệu, không chỉ đầu/cuối?
- [ ] Tôi có đang nhầm "AI nhớ tôi" với "AI học từ tôi" không? (Câu trả lời luôn là: không, nó chỉ chưng cất context cũ.)
- [ ] Nếu đây là việc quan trọng (báo cáo, nghiên cứu, số liệu dùng để quyết định), tôi có đang tự kiểm chứng hay chỉ tin lời model tự nhận là đúng?

---

## Tổng kết một câu

**LLM không "biết" và không "nhớ" theo nghĩa con người vẫn hiểu — nó tính toán lại từ đầu mỗi lần, dựa trên context nó thấy và một thiên hướng học được là thà trả lời tự tin còn hơn hỏi lại. Người dùng giỏi là người thu hẹp không gian đoán của model bằng đầu bài rõ ràng, và luôn tự kiểm chứng phần quan trọng thay vì tin tưởng tuyệt đối.**
