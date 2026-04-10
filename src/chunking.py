from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # TODO: split into sentences, group into chunks
        if not text.strip():
            return []
            
        # Tách câu dựa trên dấu chấm, chấm than, hỏi chấm, và xuống dòng. 
        # Sử dụng regex để tách và giữ lại dấu kết thúc câu trong các part.
        parts = re.split(r'(\.\s+|\!\s+|\?\s+|\.\n)', text)
        sentences = []
        current_sentence = ""
        
        for part in parts:
            current_sentence += part
            # Nếu part trùng với pattern dấu ngắt câu -> kết thúc một câu hoàn chỉnh
            if re.match(r'^(\.\s+|\!\s+|\?\s+|\.\n)$', part):
                sentences.append(current_sentence.strip())
                current_sentence = ""
                
        # Xử lý đoạn còn dư cuối cùng nếu không có dấu ngắt
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
            
        # Gộp các câu thành từng chunk dựa vào giới hạn max_sentences_per_chunk
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i + self.max_sentences_per_chunk]).strip()
            if chunk:
                chunks.append(chunk)
                
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # TODO: implement recursive splitting strategy
        if not text:
            return []
        # Gọi hàm đệ quy để tách văn bản với danh sách separator ưu tiên
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
        # Base case: text đã nằm trong giới hạn cho phép
        if len(current_text) <= self.chunk_size:
            return [current_text]
            
        # Tìm separator đầu tiên có tồn tại trong đoạn văn bản hiện tại
        sep = ""
        next_seps = remaining_separators
        for i, s in enumerate(remaining_separators):
            if s == "" or s in current_text:
                sep = s
                next_seps = remaining_separators[i + 1:]
                break
                
        # Cắt chuỗi theo separator tìm được
        splits = current_text.split(sep) if sep else list(current_text)
        
        chunks = []
        current_chunk = ""
        
        for split in splits:
            # Nếu một mảnh đã cắt vẫn lớn hơn chunk_size -> Đệ quy dùng mảng separator tiếp theo
            if len(split) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                chunks.extend(self._split(split, next_seps))
            else:
                # Nếu có thể ghép thêm vào chunk hiện tại thì ghép
                new_len = len(current_chunk) + len(sep) + len(split) if current_chunk else len(split)
                if new_len <= self.chunk_size:
                    current_chunk = current_chunk + sep + split if current_chunk else split
                else:
                    # Nếu vượt quá, lưu chunk hiện tại và khởi tạo chunk mới
                    chunks.append(current_chunk)
                    current_chunk = split
                    
        # Lưu chunk cuối cùng nếu có
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    # Tính tích vô hướng (dot product)
    dot_product = _dot(vec_a, vec_b)
    
    # Tính độ lớn (magnitude) của từng vector
    mag_a = math.sqrt(_dot(vec_a, vec_a))
    mag_b = math.sqrt(_dot(vec_b, vec_b))
    
    # Xử lý edge case: vector có độ lớn = 0
    if mag_a == 0 or mag_b == 0:
        return 0.0
        
    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # TODO: call each chunker, compute stats, return comparison dict
        # Hàm tính toán thống kê (số lượng chunk, độ dài trung bình)
        def get_stats(chunks: list[str]) -> dict:
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0
            return {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks
            }
            
        # Áp dụng 3 chiến lược chunking
        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=20).chunk(text)
        sentence = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)
        
        return {
            "fixed_size": get_stats(fixed),
            "by_sentences": get_stats(sentence),
            "recursive": get_stats(recursive)
        }