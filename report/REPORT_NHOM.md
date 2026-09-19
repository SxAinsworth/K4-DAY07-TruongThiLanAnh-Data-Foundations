# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và chính sách học bổng sinh viên đại học

**Tại sao nhóm chọn chủ đề này?**
> Đây là nhóm quy định có nhiều điều kiện, ngưỡng điểm, mức tiền và quy trình, phù hợp để kiểm tra retrieval theo số liệu lẫn nội dung dài. Các nguồn đều là trang công khai của trường đại học, có metadata về đối tượng, đơn vị, chủ đề và phiên bản.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | ussh-basic-sciences-scholarship.md | USSH/VNU | 2026-09-19 / not-stated | | student, student-affairs, scholarship, vi |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string | `student` | Lọc tài liệu theo đối tượng người đọc. |
| `department` | string | `student-affairs` | Phân biệt nguồn thuộc công tác sinh viên. |
| `category` | string | `scholarship` | Giới hạn truy xuất vào nhóm học bổng. |
| `document_version` | string | `2025`, `2026-2027`, `not-stated` | Theo dõi năm học hoặc phiên bản quy định. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `huit-scholarship-regulation.md` | FixedSizeChunker (`fixed_size`) | 6 | 470.7 | Giữ kích thước ổn định nhưng có thể cắt giữa điều kiện. |
| `huit-scholarship-regulation.md` | SentenceChunker (`by_sentences`) | 5 | 512.8 | Giữ câu nhưng một số chunk vượt ngưỡng 500. |
| `huit-scholarship-regulation.md` | RecursiveChunker (`recursive`) | 8 | 318.0 | Giữ ranh giới mục tốt hơn, có nhiều chunk hơn. |
| `ou-scholarship-regulation.md` | FixedSizeChunker (`fixed_size`) | 5 | 491.4 | Kích thước đều, có thể tách bảng/điều kiện. |
| `ou-scholarship-regulation.md` | SentenceChunker (`by_sentences`) | 5 | 449.4 | Phù hợp văn bản ngắn theo câu. |
| `ou-scholarship-regulation.md` | RecursiveChunker (`recursive`) | 6 | 371.8 | Giữ cấu trúc đoạn và tiêu đề tương đối tốt. |
| `ueh-scholarship-hkc2025.md` | FixedSizeChunker (`fixed_size`) | 6 | 482.8 | Giữ kích thước ổn định nhưng bảng có thể bị cắt. |
| `ueh-scholarship-hkc2025.md` | SentenceChunker (`by_sentences`) | 8 | 329.1 | Nhiều chunk ngắn, giữ câu rõ. |
| `ueh-scholarship-hkc2025.md` | RecursiveChunker (`recursive`) | 7 | 373.6 | Cân bằng giữa độ dài và ranh giới nội dung. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** custom — HeadingChunker (R3)
- **Mô tả & lý do chọn cho chủ đề này:** Tách trước theo heading Markdown để giữ trọn từng mục quy định. Nếu một mục dài quá 500 ký tự, dùng RecursiveChunker và gắn lại heading vào mọi mảnh con để không mất ngữ cảnh.
- **Code snippet (nếu custom):**
```python
# HeadingChunker được triển khai trong bench.py.
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> HeadingChunker phù hợp nhất về mặt cấu trúc vì giữ các mục điều kiện, mức học bổng và quy trình cùng heading; khi split section dài, heading được gắn lại vào từng mảnh. Tuy nhiên với MockEmbedder, chất lượng top-k vẫn bị chi phối bởi hash MD5 nên cần chạy lại bằng embedding ngữ nghĩa trước khi kết luận chiến lược truy xuất tốt nhất.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Marketing CLC TV K48 của UEH cần tối thiểu bao nhiêu tín chỉ? | 13 tín chỉ. | `ueh-scholarship-hkc2025.md`, mục “Số tín chỉ tối thiểu”. Filter: `{"audience": "student"}`. |
| 2 | Sinh viên USSH từ học kỳ II năm thứ nhất cần điều kiện gì để tiếp tục nhận học bổng? | Đã nhận học bổng Thu hút tài năng ở học kỳ I; học tập và rèn luyện Giỏi trở lên; thuộc diện xét KKHT ĐHQGHN; không bị kỷ luật; không có môn dưới 7,0/B; học tối thiểu 14 tín chỉ. | `ussh-basic-sciences-scholarship.md`, mục “Tiêu chí xét, cấp học bổng”. Filter: `{"audience": "student"}`. |
| 3 | Quy trình xét học bổng KKHT HUIT gồm những bước chính nào? | Dự trù và duyệt kinh phí; phân bổ suất; tổng kết điểm; khoa họp xét; công khai danh sách; CTSV kiểm tra, tổng hợp; Hội đồng trình Hiệu trưởng và công bố danh sách. | `huit-scholarship-regulation.md`, mục “Quy trình xét”. Filter: `{"audience": "student"}`. |
| 4 | USTH có những loại học bổng nào cho sinh viên, học viên và nghiên cứu sinh? | 12 loại: Tài năng, Ươm mầm khoa học, Khuyến khích học tập, Kiến tạo, Thực tập, Xuất sắc Song bằng, Vượt khó, Tiếp nối, Tăng cường năng lực, Hạt giống tài năng, Kết nối, Đồng hành. | `usth-scholarship-regulation-2026-2027.md`. Filter: `{"audience": "student"}`. |
| 5 | Học bổng loại Giỏi của OU bằng bao nhiêu phần trăm học phí mỗi học kỳ? | 70% học phí/học kỳ; học tập loại Giỏi và rèn luyện Tốt hoặc Xuất sắc. | `ou-scholarship-regulation.md`, mục “Mức học bổng”. Filter: `{"audience": "student"}`. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> `bench.py` truyền `metadata_filter={"audience": "student"}` qua `search_with_filter()` cho cả 5 câu. Tuy nhiên corpus hiện tại chỉ có tài liệu dành cho sinh viên, nên filter chưa tạo ra đối chứng mạnh giữa hai nhóm audience khác nhau; cần bổ sung nguồn có audience khác trước khi kết luận filter cải thiện độ chính xác.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Đánh giá chỉ theo `doc_id` sẽ thổi phồng kết quả; kiểm tra `needle` trong content cho thấy chỉ 1/5 query có đáp án trong top-3 với MockEmbedder.
> - HeadingChunker giữ ngữ cảnh tốt hơn khi một mục dài phải tách nhỏ, nhưng không tự khắc phục được embedding không có ngữ nghĩa.
> - A/B có và không có `audience=student` cho Q5 cho kết quả giống nhau ở fixed, sentence và recursive, nên corpus hiện chưa chứng minh được filter là cần thiết.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một corpus có thể cho số chunk và độ dài trung bình rất khác giữa fixed, sentence và recursive. Nhưng retrieval score với MockEmbedder không đủ đáng tin để xếp hạng ngữ nghĩa; cần tách rõ chất lượng chunk khỏi chất lượng embedding.

**Failure case đã kiểm chứng:**
> Query 5 hỏi mức học bổng loại Giỏi của OU, nhưng top-3 lần lượt là USSH, HUIT và UET; không chunk nào chứa chuỗi gold `70% học phí/học kỳ`. Nguyên nhân là MockEmbedder băm MD5 nên không hiểu “OU”, “loại Giỏi” và “70%” có quan hệ; hướng sửa là dùng embedding ngữ nghĩa, bổ sung reranking theo từ khóa/số liệu và giữ section “Mức học bổng” đủ nguyên vẹn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Cài `sentence-transformers` và chạy lại benchmark bằng multilingual embedding. Đồng thời bổ sung tài liệu có audience khác nhau để A/B metadata filter thật sự có ý nghĩa, thay vì tất cả tài liệu đều mang `audience=student`.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
