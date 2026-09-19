from __future__ import annotations

import re
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from src.chunking import ChunkingStrategyComparator, RecursiveChunker
from src.models import Document
from src.store import EmbeddingStore


DATA_DIR = Path("data/hoc-bong-crawl")

# Change this one line when comparing a different personal strategy.
CHUNKER = "heading"
CHUNK_SIZE = 500


def load_markdown(path: Path) -> tuple[dict[str, str], str]:
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Missing frontmatter: {path}")
    metadata = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, parts[2].strip()


class HeadingChunker:
    """Keep Markdown sections together and retain headings on split pieces."""

    heading_pattern = re.compile(r"(?=^#{1,6}\s+.+$)", re.MULTILINE)

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self.recursive = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = [section.strip() for section in self.heading_pattern.split(text.strip()) if section.strip()]
        chunks: list[str] = []
        for section in sections:
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue
            lines = section.splitlines()
            heading = lines[0].strip() if lines and lines[0].lstrip().startswith("#") else ""
            body = "\n".join(lines[1:]).strip() if heading else section
            for piece in self.recursive.chunk(body):
                chunks.append(f"{heading}\n\n{piece}".strip() if heading else piece)
        return chunks


def choose_chunks(content: str) -> list[str]:
    if CHUNKER == "heading":
        return HeadingChunker(CHUNK_SIZE).chunk(content)
    if CHUNKER == "fixed_size":
        from src.chunking import FixedSizeChunker

        return FixedSizeChunker(CHUNK_SIZE, overlap=50).chunk(content)
    if CHUNKER == "by_sentences":
        from src.chunking import SentenceChunker

        return SentenceChunker(max_sentences_per_chunk=3).chunk(content)
    if CHUNKER == "recursive":
        return RecursiveChunker(chunk_size=CHUNK_SIZE).chunk(content)
    raise ValueError(f"Unknown chunker: {CHUNKER}")


QUERIES = [
    {
        "question": "Marketing CLC TV khóa K48 của UEH cần tối thiểu bao nhiêu tín chỉ?",
        "gold": "Tối thiểu 13 tín chỉ.",
        "needle": "Marketing CLC TV - K48",
        "metadata_filter": {"audience": "student"},
    },
    {
        "question": "Sinh viên USSH từ học kỳ II năm thứ nhất cần đáp ứng những điều kiện nào để tiếp tục nhận học bổng?",
        "gold": "Đã được xét học bổng Thu hút tài năng ở học kỳ I năm thứ nhất; đạt học tập và rèn luyện loại Giỏi trở lên; thuộc diện xét học bổng KKHT của ĐHQGHN; không bị kỷ luật; không có môn dưới 7,0 hoặc B; và học tối thiểu 14 tín chỉ.",
        "needle": "14 tín chỉ",
        "metadata_filter": {"audience": "student"},
    },
    {
        "question": "Quy trình xét học bổng KKHT HUIT gồm những bước chính nào?",
        "gold": "Dự trù và duyệt kinh phí; phân bổ suất; tổng kết điểm; các khoa họp xét; công khai danh sách; phòng Công tác sinh viên kiểm tra, tổng hợp; sau đó Hội đồng trình Hiệu trưởng ra quyết định và công bố danh sách.",
        "needle": "Bước 1",
        "metadata_filter": {"audience": "student"},
    },
    {
        "question": "USTH có những loại học bổng nào cho sinh viên, học viên và nghiên cứu sinh?",
        "gold": "12 loại: Tài năng, Ươm mầm khoa học, Khuyến khích học tập, Kiến tạo, Thực tập, Xuất sắc Song bằng, Vượt khó, Tiếp nối, Tăng cường năng lực, Hạt giống tài năng, Kết nối và Đồng hành.",
        "needle": "12 loại",
        "metadata_filter": {"audience": "student"},
    },
    {
        "question": "Học bổng loại Giỏi của OU được tính bằng bao nhiêu phần trăm học phí mỗi học kỳ?",
        "gold": "70% học phí mỗi học kỳ; điều kiện là học tập loại Giỏi và rèn luyện loại Tốt hoặc Xuất sắc.",
        "needle": "70% học phí/học kỳ",
        "metadata_filter": {"audience": "student"},
    },
]


def build_documents(strategy: str = CHUNKER) -> list[Document]:
    documents = []
    for path in sorted(DATA_DIR.glob("*.md")):
        metadata, content = load_markdown(path)
        for index, chunk in enumerate(choose_chunks(content) if strategy == CHUNKER else choose_chunks_for(content, strategy)):
            chunk_metadata = {**metadata, "doc_id": path.stem, "chunk_index": index}
            documents.append(Document(id=f"{path.stem}#{index}", content=chunk, metadata=chunk_metadata))
    return documents


def choose_chunks_for(content: str, strategy: str) -> list[str]:
    global CHUNKER
    previous = CHUNKER
    CHUNKER = strategy
    try:
        return choose_chunks(content)
    finally:
        CHUNKER = previous


def print_baseline() -> None:
    print("=== Baseline (body only, no frontmatter) ===")
    for path in sorted(DATA_DIR.glob("*.md"))[:3]:
        _, content = load_markdown(path)
        comparison = ChunkingStrategyComparator().compare(content, chunk_size=CHUNK_SIZE)
        print(path.name)
        for strategy, stats in comparison.items():
            print(f"  {strategy}: count={stats['count']} avg_length={stats['avg_length']:.1f}")


def run_benchmark() -> None:
    print_baseline()
    documents = build_documents()
    store = EmbeddingStore(collection_name="scholarship_benchmark")
    store.add_documents(documents)
    print(f"\nChunker: {CHUNKER}; loaded chunks: {store.get_collection_size()}")

    for index, query in enumerate(QUERIES, start=1):
        results = store.search_with_filter(
            query["question"], top_k=3, metadata_filter=query["metadata_filter"]
        )
        print(f"\nQ{index}: {query['question']}")
        print(f"Gold: {query['gold']}")
        for rank, result in enumerate(results, start=1):
            contains_gold = query["needle"].lower() in result["content"].lower()
            level = 2 if rank == 1 and contains_gold else 1 if contains_gold else 0
            print(
                f"  {rank}. score={result['score']:.4f} "
                f"doc_id={result['metadata'].get('doc_id')} "
                f"chunk={result['id']} gold_content={'YES' if contains_gold else 'NO'} level={level}"
            )
            print(f"     {result['content'][:240].replace(chr(10), ' ')}...")

    filter_query = QUERIES[4]
    print("\n=== Filter A/B for Q5 across baseline strategies ===")
    for strategy in ["fixed_size", "by_sentences", "recursive"]:
        strategy_documents = build_documents(strategy)
        strategy_store = EmbeddingStore(collection_name=f"ab_{strategy}")
        strategy_store.add_documents(strategy_documents)
        for label, metadata_filter in [("with_filter", filter_query["metadata_filter"]), ("without_filter", None)]:
            results = strategy_store.search_with_filter(filter_query["question"], top_k=3, metadata_filter=metadata_filter)
            summary = [
                f"{result['metadata'].get('doc_id')}:{'YES' if filter_query['needle'].lower() in result['content'].lower() else 'NO'}"
                for result in results
            ]
            print(f"{strategy} {label}: {summary}")


def main() -> None:
    output = StringIO()
    with redirect_stdout(output):
        run_benchmark()
    text = output.getvalue()
    print(text, end="")
    Path("ket_qua_benchmark.txt").write_text(
        "Backend: MockEmbedder (sentence-transformers chưa cài; score không phản ánh ngữ nghĩa).\n\n" + text,
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()