# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Văn Huân
**Nhóm:** Z1
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai vector có hướng gần giống nhau, tức là nội dung ngữ nghĩa tương đồng cao dù cách diễn đạt có thể khác.

**Ví dụ HIGH similarity:**
- Sentence A:Tôi yêu thích AI
- Sentence B:Tôi học AI và cảm thấy vui
- Tại sao tương đồng:Cả hai câu đều mô tả rằng người nói thích AI

**Ví dụ LOW similarity:**
- Sentence A: Tôi yêu thích AI
- Sentence B:Thời tiết Hà Nội mấy hôm nay rất nóng
- Tại sao khác: tại vì hai câu nói nói về hai chủ đề khác nhau

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity đo góc giữa các vector nên tập trung vào ngữ nghĩa, không bị ảnh hưởng bởi độ lớn vector; trong khi Euclidean distance dễ bị lệch do độ dài vector.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Cách tính
Bước nhảy mỗi chunk:
= chunk_size - overlap = 500 - 50 = 450
Số chunk:
= (10000 - 500) / 450 + 1
= 9500 / 450 + 1
≈ 21.11 + 1 ≈ 22 chunks
> 22 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Overlap tăng → bước nhảy nhỏ hơn → số chunk tăng lên. Overlap lớn giúp giữ ngữ cảnh giữa các chunk tốt hơn, tránh mất thông tin ở ranh giới.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Vietnamese law
**Lý do chọn** : Vì có data sẵn, có struct để đánh giá;

**Tại sao nhóm chọn domain này?**
> phần data có label test của tác giả dữ liệu dễ cho đánh giá

### Data Inventory

| # | Tên / Mô tả tài liệu | Nguồn | Số ký tự (ước tính) | Metadata đã gán |
|---|----------------------|-------|---------------------|-----------------|
| 1 | Xử phạt vượt đèn đỏ — xe ô tô, xe máy, xe đạp, người đi bộ (Nghị định 168/2024/NĐ-CP, Điều 6, 7, 9, 10) | legal_documents.md | ~900 | doc_id=1, category=giao_thông, law=NĐ168/2024 |
| 2 | Thu hồi đất do vi phạm pháp luật đất đai (Luật Đất đai 2024, Điều 81) | legal_documents.md | ~1200 | doc_id=2, category=đất_đai, law=LĐĐ2024 |
| 3 | Phạt không có giải pháp ngăn cháy khu vực sạc xe điện (Nghị định 106/2025/NĐ-CP, Điều 12) | legal_documents.md | ~700 | doc_id=3, category=phòng_cháy, law=NĐ106/2025 |
| 4 | Vi phạm Luật Bảo hiểm xã hội 2024 — xử phạt hành chính, kỷ luật, hình sự (Điều 132) | legal_documents.md | ~400 | doc_id=4, category=bảo_hiểm_xã_hội, law=LBHXH2024 |
| 5 | Nguyên tắc bảo vệ môi trường (Luật BVMT 2020, Điều 4) | legal_documents.md | ~1100 | doc_id=5, category=môi_trường, law=LBVMT2020 |
| 6 | Điều kiện chào bán trái phiếu ra công chúng (Luật Chứng khoán 2019, Điều 15) | legal_documents.md | ~900 | doc_id=6, category=chứng_khoán, law=LCK2019 |
| 7 | Chuyển người lao động làm công việc khác so với hợp đồng (BLLĐ 2019, Điều 29) | legal_documents.md | ~500 | doc_id=7, category=lao_động, law=BLLĐ2019 |
| 8 | Mức lương tối thiểu vùng 2024 theo Nghị định 74/2024/NĐ-CP | legal_documents.md | ~700 | doc_id=8, category=lao_động, law=NĐ74/2024 |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị              | Tại sao hữu ích cho retrieval?                 |
| --------------- | ---- | -------------------------- | ---------------------------------------------- |
| source          | str  | luat_doanh_nghiep_2020.pdf | Xác định nguồn tài liệu để trích dẫn chính xác |
| article_id      | str  | Dieu_15                    | Giúp truy xuất đúng điều luật cụ thể           |
| category        | str  | law_tax                    | Hỗ trợ filter theo lĩnh vực                    |
| last_updated    | str  | 2023-10-01                 | Ưu tiên tài liệu mới hơn                       |


---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu                      | Strategy     | Chunk Count | Avg Length |
| ----------------------------- | ------------ | ----------- | ---------- |
| customer_support_playbook.txt | fixed_size   | 10          | 187.2      |
| customer_support_playbook.txt | by_sentences | 4           | 421.0      |
| customer_support_playbook.txt | recursive    | 14          | 119.1      |
| python_intro.txt              | fixed_size   | 11          | 194.9      |
| python_intro.txt              | by_sentences | 5           | 387.0      |
| python_intro.txt              | recursive    | 14          | 136.9      |


### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | | | |
| | **của tôi** | | | |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Bảo | Sliding Window | 0 | Dễ triển khai, tốc độ xử lý tốt, giữ được một phần ngữ cảnh nhờ overlap. | Cắt theo độ dài nên dễ làm vỡ ý pháp lý; phụ thuộc mạnh vào chất lượng embedding, kém với query khác diễn đạt. |
| Tuấn Anh | Recursive | 2 | Linh hoạt theo nhiều mức tách, xử lý được tài liệu dài và không đồng đều cấu trúc. | Nếu separator chưa tối ưu sẽ tạo nhiều chunk ngắn/nhiễu; khó kiểm soát độ ổn định giữa các loại văn bản. |
| Đức | Parent-Child | 2 | Giữ cân bằng giữa ngữ cảnh rộng (parent) và chi tiết (child), dễ truy vết nguồn. | Thiết kế phức tạp hơn, tốn tài nguyên lập chỉ mục; nếu map parent-child không tốt thì retrieval giảm rõ. |
| Nguyên | Document-structure | 3 | Khai thác tiêu đề/mục/điều khoản nên hợp tài liệu pháp lý, chunk có tính logic cao. | Phụ thuộc chất lượng cấu trúc tài liệu đầu vào; tài liệu không chuẩn định dạng thì hiệu quả giảm. |
| Huân | Semantic | 3 | Bám ý nghĩa tốt hơn keyword thuần, xử lý tốt paraphrase khi embedding đủ mạnh. | Nhạy với model embedding và ngôn ngữ; chi phí tính toán cao hơn, khó debug nguyên nhân sai lệch. |
| Thắng | Agentic | 2 | Có khả năng lập kế hoạch truy xuất nhiều bước, tổng hợp câu trả lời linh hoạt. | Dễ sinh nhiễu khi truy xuất nhiều bước; khó kiểm soát tính nhất quán và độ chính xác nếu retrieval nền chưa tốt. |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Nếu làm tốt thì có Secmantic và Document structure vì đau là văn bản luật có tiêu đề và ngữ nghĩa rõ ràng, các Strategy khác theo em có thể xử lý tôt hơn nhưng chưa phù hợp với dữ liệu hiện tại như Agent, và parent-child vì nó cần một lượng dữ liệu của một tài liều dai hơn để xử lý tốt.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Phương pháp sử dụng regex để tách câu dựa trên các dấu kết thúc như ., !, ? kết hợp khoảng trắng phía sau (ví dụ: r'(?<=[.!?])\s+'). Sau khi tách, các câu được gom lại thành chunk theo giới hạn max_sentences. Edge cases được xử lý bao gồm văn bản rỗng, câu quá ngắn hoặc thiếu dấu kết thúc.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán sử dụng chiến lược chia đệ quy theo danh sách separator ưu tiên (ví dụ: \n\n, \n, ., ). Nếu đoạn văn vẫn vượt quá chunk_size, tiếp tục chia nhỏ theo separator tiếp theo. Base case xảy ra khi không còn separator hoặc đoạn đã đủ nhỏ, khi đó trả về trực tiếp.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Dữ liệu được lưu dưới dạng danh sách các document kèm embedding vector tương ứng. Khi search, hệ thống tính cosine similarity giữa query embedding và các vector đã lưu, sau đó sắp xếp giảm dần theo score và trả về top-k kết quả.

**`search_with_filter` + `delete_document`** — approach:
> Filtering được thực hiện trước khi tính similarity để giảm không gian tìm kiếm (ví dụ theo category). Việc xóa document được thực hiện bằng cách tìm theo ID hoặc nội dung và loại bỏ khỏi collection, đồng thời trả về trạng thái thành công hoặc thất bại.

### KnowledgeBaseAgent

**`answer`** — approach:
> Agent thực hiện pipeline gồm: nhận query → retrieve top-k chunk liên quan → ghép thành context. Context sau đó được đưa vào prompt theo dạng: "Dựa vào thông tin sau, hãy trả lời câu hỏi...". Câu trả lời được sinh dựa trên context nhằm đảm bảo tính liên quan.

### Test Results
> collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

> 42========================= 42 passed in 0.05s ==========================
```
# Paste output of: pytest tests/ -v
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| # | Sentence A                                   | Sentence B                                    | Dự đoán | Actual Score | Đúng? |
| - | -------------------------------------------- | --------------------------------------------- | ------- | ------------ | ----- |
| 1 | Tôi rất thích lập trình Python.              | Python là ngôn ngữ lập trình tôi yêu thích... | High    | -0.112       | ❌x     |
| 2 | Vector database dùng để lưu trữ embedding... | ChromaDB lưu vector embedding để tìm kiếm...  | High    | -0.031       | ❌ x    |
| 3 | Con mèo đang ngủ trên sofa.                  | Luật doanh nghiệp năm 2020 quy định...        | Low     | 0.106        | ❌x     |
| 4 | Chunking giúp chia nhỏ văn bản dài.          | Việc cắt nhỏ text rất quan trọng trong RAG... | High    | 0.135        | ✅oke     |
| 5 | Trời hôm nay rất đẹp.                        | Hệ thống RAG cần một bộ retriever tốt.        | Low     | 0.223        | ❌ x    |


**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> kết quả thứ 2 bất ngờ nhất vì nó đã hiểu sai cả ngũ cảnh và tên riêng, Điều này cho thấy việc Embedding đúng nó thực sự quan trọng.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Xe máy vượt đèn đỏ bị phạt bao nhiêu tiền? | Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng, bị trừ 04 điểm giấy phép lái xe. Nếu gây tai nạn giao thông thì phạt từ 10.000.000 đồng đến 14.000.000 đồng và trừ 10 điểm (Nghị định 168/2024/NĐ-CP, Điều 7) |
| 2 | Nhà nước thu hồi đất trong trường hợp nào? | Thu hồi đất khi người sử dụng đất vi phạm pháp luật đất đai như: sử dụng đất không đúng mục đích, hủy hoại đất, không thực hiện nghĩa vụ tài chính, không đưa đất vào sử dụng theo thời hạn quy định (Luật Đất đai 2024, Điều 81) |
| 3 | Khu vực sạc xe điện tập trung trong nhà cần có gì về phòng cháy? | Phải có giải pháp ngăn cháy đối với khu vực sạc điện cho xe động cơ điện tập trung trong nhà. Nếu không có sẽ bị phạt từ 40-50 triệu đồng (cá nhân) hoặc 80-100 triệu đồng (tổ chức) (Nghị định 106/2025/NĐ-CP, Điều 12) |
| 4 | Vi phạm luật bảo hiểm xã hội bị xử lý như thế nào? | Tùy theo tính chất, mức độ vi phạm mà bị xử phạt vi phạm hành chính, xử lý kỷ luật hoặc bị truy cứu trách nhiệm hình sự. Nếu gây thiệt hại thì phải bồi thường theo quy định của pháp luật (Luật Bảo hiểm xã hội 2024, Điều 132) |
| 5 | Nguyên tắc bảo vệ môi trường theo luật là gì? | Bảo vệ môi trường là quyền, nghĩa vụ và trách nhiệm của mọi người; là điều kiện, nền tảng cho phát triển bền vững; ưu tiên phòng ngừa ô nhiễm; người gây ô nhiễm phải chi trả, bồi thường; hoạt động phải công khai, minh bạch (Luật Bảo vệ môi trường 2020, Điều 4) |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Xe máy vượt đèn đỏ bị phạt bao nhiêu tiền? | Nhà nước thu hồi đất khi người sử dụng đất vi phạm pháp luật... | 0.253 | **No** | Dựa theo luật: Nhà nước thu hồi đất khi người sử dụng đất vi... |
| 2 | Nhà nước thu hồi đất trong trường hợp nào? | Trường hợp vượt đèn đỏ mà gây tai nạn giao thông thì mức phạ... | 0.126 | **Yes** | Dựa theo luật: Trường hợp vượt đèn đỏ mà gây tai nạn giao th... |
| 3 | Khu vực sạc xe điện tập trung trong nhà cần có gì về phòng cháy? | Chủ cơ sở vi phạm quy định này, nếu không trang bị giải pháp... | 0.331 | **No** | Dựa theo luật: Chủ cơ sở vi phạm quy định này, nếu không tra... |
| 4 | Vi phạm luật bảo hiểm xã hội bị xử lý như thế nào? | Trong trường hợp hành vi vi phạm gây thiệt hại cho quỹ bảo h... | 0.222 | **Yes** | Dựa theo luật: Trong trường hợp hành vi vi phạm gây thiệt hạ... |
| 5 | Nguyên tắc bảo vệ môi trường theo luật là gì? | Điều 132. Xử lý vi phạm pháp luật về bảo hiểm xã hội. Tổ chứ... | 0.329 | **Yes** | Dựa theo luật: Điều 132. Xử lý vi phạm pháp luật về bảo hiểm... |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Các thành viên trong nhóm thống nhất nhanh dữ liệu, giải quyết vấn đề từ đâu trước tiên.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Tôi thấy qua demo thì nhóm demo đã làm khá tốt nhưng phần kết quả so sánh có recall bị lệch khá mạnh, nếu lệch như thế thì cần có biện pháp cân bằng lại với Precision, phần còn lại thì nhóm làm tốt.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Thay đổi cách tiếp cận thay vì chỉ sử dụng các phương pháp chunk thì sẽ để chunk như là một base và phát triển lên các phương pháp nếu có đủ thời gian, như là : xây theo node data, tree, graph,...

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 4/ 5 |
| Document selection | Nhóm | 8/ 10 |
| Chunking strategy | Nhóm | 11/ 15 |
| My approach | Cá nhân | 7/ 10 |
| Similarity predictions | Cá nhân | 3/ 5 |
| Results | Cá nhân | 7/ 10 |
| Core implementation (tests) | Cá nhân | 24/ 30 |
| Demo | Nhóm | 4/ 5 |
| **Tổng** | | **68/ 100** |
