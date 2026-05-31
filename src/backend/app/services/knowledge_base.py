import json
from pathlib import Path
from typing import Any

from ..config import KB_DIR


class KnowledgeBaseService:
    def __init__(self, kb_dir: Path = KB_DIR):
        self.kb_dir = kb_dir
        self._index = self._load_index()
        self._question_bank = self._load_json("question_bank.json")
        self._coding_cases = self._load_json("coding_cases.json")

    def _load_json(self, file_name: str) -> list[dict[str, Any]]:
        file_path = self.kb_dir / file_name
        if not file_path.exists():
            return []
        return json.loads(file_path.read_text(encoding="utf-8"))

    def _load_index(self) -> list[dict[str, Any]]:
        index_file = self.kb_dir / "metadata.json"
        if not index_file.exists():
            return []
        return json.loads(index_file.read_text(encoding="utf-8"))

    def list_modules(self) -> list[dict[str, Any]]:
        return self._index

    def list_questions(self) -> list[dict[str, Any]]:
        return self._question_bank

    def list_coding_cases(self) -> list[dict[str, Any]]:
        return self._coding_cases

    def get_questions_by_module(self, module_id: str) -> list[dict[str, Any]]:
        for item in self._question_bank:
            if item["module_id"] == module_id:
                return item.get("questions", [])
        return []

    def get_coding_cases_by_module(self, module_id: str) -> list[dict[str, Any]]:
        return [item for item in self._coding_cases if item["module_id"] == module_id]

    def get_module_content(self, module_id: str) -> str:
        file_path = self.kb_dir / f"{module_id}.md"
        return file_path.read_text(encoding="utf-8")

    def get_knowledge_graph(self) -> dict[str, Any]:
        """Load knowledge dependency graph for visualization."""
        graph_file = self.kb_dir / "knowledge_graph.json"
        if not graph_file.exists():
            return {"nodes": [], "edges": [], "module_map": {}}
        return json.loads(graph_file.read_text(encoding="utf-8"))

    def search(self, weak_points: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for item in self._index:
            score = 0
            haystack = " ".join(item.get("keywords", []) + item.get("knowledge_units", []))
            for weak_point in weak_points:
                if weak_point in haystack:
                    score += 1
            if score > 0:
                results.append({"score": score, **item})
        if not results:
            results = [{"score": 1, **item} for item in self._index[:3]]
        return sorted(results, key=lambda item: item["score"], reverse=True)
