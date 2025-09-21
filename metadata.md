Câu hỏi rất hay 👍. Metadata có thể **lưu trữ** theo nhiều cách khác nhau, tùy hệ thống quản lý tài liệu hay dữ liệu mà bạn dùng. Tôi chia ra 3 trường hợp để bạn dễ hình dung:

---

## 1. Metadata lưu **trực tiếp trong file**

Một số định dạng file đã có chỗ dành riêng cho metadata:

* **Microsoft Word, Excel, PowerPoint (Office)**: Lưu metadata trong phần *Properties* (Author, Title, Tags, Last Modified).
* **PDF**: Có metadata chuẩn XMP (XML Metadata Platform) để nhúng thông tin như tác giả, chủ đề, ngày tạo.
* **Ảnh (JPEG, PNG)**: Metadata EXIF chứa thông tin máy ảnh, ngày chụp, GPS.
* **MP3**: Metadata ID3 tag (tên bài hát, ca sĩ, album).

👉 Ưu điểm: Metadata **đi kèm file**, không sợ thất lạc.
👉 Nhược điểm: Khó cập nhật hàng loạt, file có thể phình to, và nếu đổi định dạng có thể mất metadata.

---

## 2. Metadata lưu **tách riêng trong cơ sở dữ liệu (database)**

* Dùng trong **Document Management System (DMS)** hoặc **Content Management System (CMS)**.
* File gốc chỉ là *blob* (binary), còn metadata lưu trong **bảng database** (MySQL, PostgreSQL, MongoDB…).
* Ví dụ bảng `documents`:

| document\_id | filename               | version | author       | department | last\_updated | access\_level  | tags                           |
| ------------ | ---------------------- | ------- | ------------ | ---------- | ------------- | -------------- | ------------------------------ |
| DOC-001      | leave\_policy\_v2.docx | v2.0    | Nguyễn Văn A | HR         | 2025-09-21    | employee\_only | \[“HR”, “nghỉ phép”, “policy”] |

👉 Ưu điểm: Dễ tìm kiếm, cập nhật, tích hợp hệ thống.
👉 Nhược điểm: Metadata và file gốc **không nằm chung một nơi**, nếu quản lý kém có thể mất liên kết.

---

## 3. Metadata lưu **song song trong file riêng (sidecar file)**

* Tạo một file metadata đi kèm file gốc, thường ở dạng **JSON, XML, YAML**.
* Ví dụ: bạn có file `leave_policy_v2.docx`, thì có thể lưu metadata ở `leave_policy_v2.json`:

```json
{
  "document_id": "DOC-001",
  "source_file": "leave_policy_v2.docx",
  "version": "v2.0",
  "department_owner": "HR",
  "author": "Nguyễn Văn A",
  "last_updated": "2025-09-21",
  "access_level": "employee_only",
  "document_type": "policy",
  "tags": ["HR", "nghỉ phép", "policy"]
}
```

👉 Ưu điểm: Linh hoạt, dễ di chuyển, không phụ thuộc định dạng file gốc.
👉 Nhược điểm: Phải **giữ cặp file đồng bộ**, nếu tách rời thì metadata mất ý nghĩa.

---

## 4. Vậy “đính kèm file văn bản” thế nào?

* **Nếu bạn dùng Word/PDF** → metadata có thể nhúng ngay trong file (Properties, XMP).
* **Nếu bạn xây hệ thống quản lý tài liệu riêng** → nên lưu metadata trong database (cách 2).
* **Nếu bạn muốn trao đổi file qua nhiều hệ thống** → dùng sidecar file JSON/XML (cách 3) sẽ an toàn và chuẩn hóa hơn.

---

👉 Tóm lại:

* Metadata **có thể nằm trong file, trong database, hoặc trong file đi kèm**.
* Lựa chọn cách nào tùy vào **quy mô hệ thống và yêu cầu quản lý**.

Bạn muốn tôi minh họa chi tiết **cách nhúng metadata vào file Word/PDF** hay là **cách thiết kế bảng database lưu metadata cho toàn bộ tài liệu của bạn**?
