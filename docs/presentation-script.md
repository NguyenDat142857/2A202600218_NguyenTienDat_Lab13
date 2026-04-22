# 🎤 KỊCH BẢN THUYẾT TRÌNH LAB 13 – OBSERVABILITY (FULL VERSION)

**Người trình bày:** Nguyen Tien Dat

---

## 🟢 1. MỞ BÀI – GIỚI THIỆU HỆ THỐNG

"Chào Thầy/Cô, hôm nay em xin trình bày về Lab 13 – xây dựng hệ thống **Observability cho một AI Agent** sử dụng FastAPI.

Trong bài lab này, em tập trung vào việc giúp hệ thống AI có thể **quan sát được toàn bộ hành vi bên trong**, từ lúc người dùng gửi request cho tới khi model trả về kết quả.

Hệ thống của em được chia thành 2 lớp quan sát chính:

* Thứ nhất là **Local Logging**: sử dụng Structlog để ghi log dạng JSON ngay tại server
* Thứ hai là **Cloud Tracing**: sử dụng Langfuse để theo dõi toàn bộ pipeline, bao gồm latency, token usage và cost của model

Mục tiêu cuối cùng là giúp hệ thống:

* dễ debug
* dễ scale
* và đảm bảo an toàn dữ liệu người dùng"

---

## 🧠 2. TẠI SAO AI CẦN OBSERVABILITY?

"Khác với các hệ thống backend thông thường, hệ thống AI có 3 vấn đề lớn:

* Thứ nhất là **Cost** – mỗi lần gọi model đều tốn tiền
* Thứ hai là **Latency** – model có thể phản hồi chậm
* Thứ ba là **Quality** – output có thể sai hoặc không ổn định

Nếu không có observability, chúng ta sẽ không biết:

* request nào đang bị chậm
* user nào gây tốn chi phí
* hay lỗi xảy ra ở bước nào trong pipeline

Vì vậy, observability là yếu tố bắt buộc nếu muốn đưa AI system lên production."

---

## 🔥 3. PHẦN CHÍNH – LOGGING + PII + CORRELATION

### 🔹 3.1 Correlation ID – Truy vết request

"Đầu tiên, em giải quyết bài toán log bị rối khi có nhiều request chạy đồng thời.

Em đã implement một middleware trong `middleware.py` để tạo ra một **Correlation ID** cho mỗi request, dạng 8 ký tự hex.

ID này sẽ:

* được gắn vào request
* lưu trong `request.state`
* và trả về cho client qua header

Nhờ đó, mỗi request sẽ có một mã riêng, ví dụ như `req-a91f3c`."

---

👉 **Giải thích thêm (nếu bị hỏi):**

"Khi có 1000 user chat cùng lúc, log sẽ bị trộn lẫn rất khó đọc.
Nhưng nhờ correlation ID, em chỉ cần search mã đó là có thể xem toàn bộ flow của request:

* nhận input
* gọi RAG
* gọi LLM
* trả output

Điều này giúp debug nhanh hơn rất nhiều."

---

### 🔹 3.2 Log Enrichment – Làm giàu log

"Tiếp theo, em sử dụng Structlog để enrich log với metadata.

Cụ thể, em bind các thông tin như:

* user_id (đã hash)
* session_id
* request_id
* feature

vào context của log.

Nhờ đó, mỗi dòng log sẽ tự động chứa đầy đủ thông tin mà không cần phải truyền thủ công mỗi lần log."

---

👉 **Điểm quan trọng:**

"DevOps khi đọc log chỉ cần nhìn một dòng là biết:

* request này của ai
* đang chạy feature gì
* thuộc session nào

→ không cần join thêm database."

---

### 🔹 3.3 PII Scrubbing – Bảo mật dữ liệu

"Đây là phần quan trọng nhất trong hệ thống logging.

Em đã xây dựng một module `pii.py` sử dụng Regex để phát hiện các thông tin nhạy cảm như:

* Email
* Số điện thoại Việt Nam
* CCCD
* API key
* Passport

Trước khi log được ghi ra file hoặc gửi lên cloud, toàn bộ dữ liệu sẽ được xử lý và thay thế bằng dạng `[REDACTED_*]`."

---

👉 **Ví dụ:**

"Ví dụ:

* `dat@gmail.com` → `[REDACTED_EMAIL]`
* `0901234567` → `[REDACTED_PHONE_VN]`"

---

👉 **Giải thích nếu bị hỏi:**

"Nếu không làm bước này, log có thể chứa:

* thông tin cá nhân
* số điện thoại
* thậm chí là API key

Khi log bị đẩy lên cloud, điều này có thể gây rò rỉ dữ liệu nghiêm trọng.

Vì vậy, PII scrubbing phải được thực hiện ngay trong RAM trước khi ghi log."

---

## 🔍 4. TRACING VỚI LANGFUSE

"Tiếp theo là phần tracing.

Em sử dụng Langfuse để theo dõi toàn bộ pipeline của AI agent.

Em sử dụng decorator `@observe()` để bọc các hàm chính như:

* agent.run
* retrieval
* LLM generation

Nhờ đó, mỗi request sẽ được biểu diễn dưới dạng một **trace tree**."

---

👉 **Giải thích thêm:**

"Mỗi trace sẽ bao gồm nhiều step:

* retrieval (lấy dữ liệu)
* LLM (generate output)
* post-processing

Tất cả các step đều có:

* thời gian thực thi
* input / output
* token usage
* cost"

---

👉 **Điểm ăn điểm:**

"Nhờ trace waterfall, em có thể thấy rõ:

* step nào đang chậm
* step nào tốn nhiều cost

→ rất dễ tìm bottleneck."

---

## 📊 5. DASHBOARD & ALERT

"Em xây dựng một dashboard gồm 6 panel chính:

1. Request volume – số lượng request
2. Latency – P50, P95, P99
3. Error rate
4. Cost (USD)
5. Token usage
6. Top slow operations

Ngoài ra, em cũng cấu hình alert:

* Khi latency > 3000ms
* Khi error rate > 2%
* Khi cost vượt ngưỡng

Khi xảy ra sự cố, hệ thống sẽ tự động cảnh báo."

---

## 🚨 6. INCIDENT & DEBUG

"Trong quá trình làm lab, em đã simulate một số incident như:

* rag_slow
* cost_spike

Khi chạy load test, em quan sát thấy:

* latency tăng mạnh
* cost tăng bất thường"

---

👉 **Cách debug:**

"Em sử dụng:

* trace để xác định step chậm
* metrics để xem latency
* logs để xem chi tiết lỗi

Kết quả cho thấy:

* bottleneck nằm ở bước retrieval"

---

👉 **Cách fix:**

"Em đã:

* thêm timeout cho retrieval
* giảm độ trễ giả lập
* thêm fallback nếu retrieval fail

Sau đó hệ thống ổn định trở lại."

---

## 🏁 7. KẾT LUẬN

"Qua bài lab này, em đã xây dựng được một hệ thống observability hoàn chỉnh cho AI agent, bao gồm:

* Structured logging
* Correlation ID
* PII protection
* Tracing
* Metrics & dashboard
* Alerting

Hệ thống này giúp:

* debug nhanh hơn
* tối ưu cost
* đảm bảo an toàn dữ liệu

Và có thể scale lên production."

---

