# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Chưa cập nhật
**Nhóm:** Chưa cập nhật
**Ngày:** 2026-09-19

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có hướng gần nhau, nghĩa là hai đoạn văn bản có nội dung hoặc ý nghĩa gần nhau trong không gian biểu diễn. Giá trị gần 1 thể hiện mức tương đồng cao; gần 0 là ít liên quan và gần -1 là đối hướng.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên cần hoàn thành tối thiểu 15 tín chỉ trong học kỳ."
- Câu B: "Trong mỗi học kỳ, người học phải đăng ký ít nhất 15 tín chỉ."
- Tại sao tương đồng: Hai câu dùng từ khác nhau một phần nhưng cùng diễn đạt điều kiện về số tín chỉ tối thiểu.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên cần hoàn thành tối thiểu 15 tín chỉ trong học kỳ."
- Câu B: "Hôm nay thư viện đóng cửa lúc sáu giờ tối."
- Tại sao khác: Một câu nói về điều kiện học tập, câu kia nói về thời gian hoạt động của thư viện, nên chủ đề và ý nghĩa khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào góc giữa hai vector nên ít bị ảnh hưởng bởi độ dài hoặc độ lớn tuyệt đối của văn bản. Điều này phù hợp với text embedding vì hướng vector thường biểu diễn ngữ nghĩa, còn văn bản dài hơn không nhất thiết có nghĩa gần hơn chỉ vì vector có độ lớn lớn hơn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Số chunk = ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = **23 chunk**. Kiểm tra bằng `FixedSizeChunker(chunk_size=500, overlap=50)` cũng cho 23 chunk.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk = ceil((10.000 - 100) / (500 - 100)) = ceil(9.900 / 400) = **25 chunk**. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk, nhưng làm tăng số chunk, chi phí embedding và khả năng lặp thông tin.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách tại vị trí sau dấu câu, vì vậy dấu chấm, chấm than và chấm hỏi vẫn nằm trong câu. Văn bản rỗng trả về `[]`, các câu được strip khoảng trắng rồi gom theo `max_sentences_per_chunk`. Edge case chưa xử lý hoàn hảo là chữ viết tắt như `TS.` hoặc `v.v.` và số thập phân, vì chúng có thể bị tách nhầm như một câu mới.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử các separator theo thứ tự `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là cắt theo ký tự. Mảnh không vượt `chunk_size` là base case; mảnh quá dài được đệ quy với separator tiếp theo, sau đó các mảnh liền kề được gom lại gần giới hạn kích thước. Khi danh sách separator rỗng hoặc separator hiện tại không xuất hiện, thuật toán fallback sang separator tiếp theo hoặc cắt cố định.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuyển thành một record gồm id, content, metadata và embedding; `add_documents` không tự chunk. `search` embed query, tính dot product với các vector đã chuẩn hóa, sắp xếp giảm dần theo score và trả về tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc record theo metadata trước rồi mới xếp hạng similarity, nên các kết quả trả về đều thỏa bộ lọc. `delete_document` xóa mọi record có `metadata["doc_id"]` tương ứng; khi metadata không có trường này, record dùng id của `Document` làm `doc_id` mặc định.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` lấy top-k chunk liên quan từ store, đánh số `[1]`, `[2]`... và kèm nguồn từ metadata trong phần Context. Prompt yêu cầu LLM chỉ dùng context, trích dẫn số chunk khi trả lời và nói rõ nếu không tìm thấy; store rỗng được xử lý bằng thông báo trực tiếp, không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Kết quả chạy: 42 passed in 0.11s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên cần hoàn thành tối thiểu 15 tín chỉ. | Người học phải đăng ký ít nhất 15 tín chỉ. | cao | 0.0635 | Không; MockEmbedder không hiểu ngữ nghĩa. |
| 2 | Học bổng loại Giỏi là 70% học phí. | Học bổng loại Xuất sắc là 100% học phí. | cao | -0.1034 | Không; mock băm chuỗi. |
| 3 | Quy trình xét học bổng gồm phân bổ kinh phí và công khai danh sách. | Thư viện đóng cửa lúc sáu giờ. | thấp | 0.1420 | Không; score mock không phản ánh chủ đề. |
| 4 | USTH có học bổng Khuyến khích học tập. | USTH có Merit Scholarship. | cao | -0.0578 | Không; mock không biểu diễn tương đương Việt-Anh. |
| 5 | Sinh viên không bị kỷ luật trong học kỳ xét. | Sinh viên đạt điểm rèn luyện loại Tốt. | thấp | 0.2175 | Không; score mock ngẫu nhiên. |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1 có cùng ý nghĩa nhưng chỉ đạt 0.0635, trong khi cặp 5 khác điều kiện nhưng đạt 0.2175. Đây là bằng chứng trực tiếp rằng `MockEmbedder` chỉ băm MD5 và không thể dùng để kết luận embedding hiểu ngữ nghĩa; cần multilingual embedding thật để đánh giá các dự đoán này.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Marketing CLC TV K48 cần tối thiểu bao nhiêu tín chỉ? | `ueh-scholarship-hkc2025#2`, bảng 13 tín chỉ | 0.3048 | Có; gold content ở top-1 | Gold: 13 tín chỉ. |
| 2 | Điều kiện tiếp tục nhận học bổng USSH từ HKII năm nhất? | `uet-scholarship-announcement-2025-2026#1`, căn cứ UET | 0.2699 | Không; không chứa 14 tín chỉ/điều kiện USSH | Không thể trả lời đúng từ top-3. |
| 3 | Quy trình xét học bổng KKHT HUIT? | `ussh-basic-sciences-scholarship#11`, bước xét USSH | 0.1879 | Không; đúng chủ đề nhưng sai quy trình | Không thể trả lời đúng từ top-3. |
| 4 | USTH có những loại học bổng nào? | `huit-scholarship-regulation#7`, quy trình HUIT | 0.2556 | Không; không chứa danh sách 12 loại | Không thể trả lời đúng từ top-3. |
| 5 | Học bổng loại Giỏi OU bằng bao nhiêu phần trăm? | `ussh-basic-sciences-scholarship#6`, mức hỗ trợ USSH | 0.2167 | Không; không chứa 70% của OU | Không thể trả lời đúng từ top-3. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5 theo kiểm tra chuỗi gold content.

**Backend và cách chấm:** `MockEmbedder`; mỗi query có một `needle` bắt buộc phải xuất hiện trong content top-3. Vì mock không mã hóa ngữ nghĩa, score và thứ hạng chỉ dùng để ghi nhận failure case, không dùng để kết luận chất lượng embedding thật.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chất lượng retrieval phải được đánh giá ở mức nội dung chunk, không chỉ xem đúng `doc_id`. Một chunk cùng chủ đề nhưng thiếu con số hoặc điều kiện trả lời vẫn là failure; vì vậy benchmark cần gold needle và ghi nhận nguồn để truy vết.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
