from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        # TODO: store references to store and llm_fn
        # Lưu reference của Embedding Store (knowledge base) và hàm LLM
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # TODO: retrieve chunks, build prompt, call llm_fn
        # Bước 1: Truy xuất (Retrieve) ngữ cảnh relevant nhất
        retrieved_results = self.store.search(question, top_k=top_k)
        
        # Bước 2: Trích xuất nội dung từ kết quả và nối thành Context text
        context_text = "\n---\n".join([r["content"] for r in retrieved_results])
        
        # Bước 3: Build Prompt tránh hallucination và ép model dựa vào context
        prompt = (
            f"Dựa vào các thông tin cung cấp dưới đây, hãy trả lời câu hỏi.\n"
            f"Nếu thông tin không nằm trong ngữ cảnh, hãy nói không biết.\n\n"
            f"Ngữ cảnh tham khảo:\n{context_text}\n\n"
            f"Câu hỏi: {question}"
        )
        
        # Bước 4: Gọi hàm tạo text từ LLM
        return self.llm_fn(prompt)