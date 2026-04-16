import faiss
import numpy as np
import pickle
import os
import logging
from django.conf import settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class BookVectorStore:
    def __init__(self):
        self.model = None
        self.index = None
        self.metadata = {}  # id -> {book_id, title, author, book_type, category, price, description, is_active}
        self._load()

    def _get_model(self):
        if self.model is None:
            logger.info("Loading SentenceTransformer model...")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("SentenceTransformer model loaded.")
        return self.model

    def _load(self):
        try:
            if os.path.exists(settings.FAISS_INDEX_PATH):
                self.index = faiss.read_index(settings.FAISS_INDEX_PATH)
                logger.info(f"FAISS index loaded: {self.index.ntotal} vectors")
            if os.path.exists(settings.FAISS_METADATA_PATH):
                with open(settings.FAISS_METADATA_PATH, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"FAISS metadata loaded: {len(self.metadata)} entries")
        except Exception as e:
            logger.error(f"FAISS load error: {e}")

    def _save(self):
        try:
            if self.index:
                faiss.write_index(self.index, settings.FAISS_INDEX_PATH)
            with open(settings.FAISS_METADATA_PATH, 'wb') as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"FAISS save error: {e}")

    def _build_book_text(self, title: str, author: str, description: str, book_type: str,
                         category: str, attributes: dict) -> str:
        """Build searchable text representation of a book."""
        text = (
            f"{title}. Author: {author}. Description: {description}. "
            f"Type: {book_type}. Category: {category}."
        )
        text = f"{title}. {description}. Loại: {book_type}. Danh mục: {category}."
        text = f"{title}. Author: {author}. Description: {description}. Type: {book_type}. Category: {category}."
        for k, v in attributes.items():
            text += f" {k}: {v}."
        return text

    def add_book(self, book_id: int, title: str, author: str, description: str, book_type: str,
                 category: str, price: float, attributes: dict, is_active: bool = True):
        """Add or update a book in the vector index."""
        model = self._get_model()
        text = self._build_book_text(title, author, description, book_type, category, attributes or {})
        embedding = model.encode([text])[0].astype('float32')
        dim = len(embedding)

        if self.index is None:
            self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
        else:
            # Remove existing entry to avoid duplicates
            id_selector = faiss.IDSelectorArray(np.array([book_id], dtype='int64'))
            self.index.remove_ids(id_selector)

        # Normalize for cosine similarity
        faiss.normalize_L2(embedding.reshape(1, -1))
        self.index.add_with_ids(embedding.reshape(1, -1), np.array([book_id], dtype='int64'))

        self.metadata[book_id] = {
            'book_id': book_id,
            'title': title,
            'author': author,
            'book_type': book_type,
            'category': category,
            'price': price,
            'description': description[:200],
            'is_active': bool(is_active),
        }
        self._save()

    def search(self, query: str, k: int = 10) -> list:
        """Semantic search returning list of metadata dicts."""
        if self.index is None or self.index.ntotal == 0:
            return []
        model = self._get_model()
        embedding = model.encode([query])[0].astype('float32')
        faiss.normalize_L2(embedding.reshape(1, -1))
        k = min(k, self.index.ntotal)
        scores, ids = self.index.search(embedding.reshape(1, -1), k)
        results = []
        for score, book_id in zip(scores[0], ids[0]):
            if book_id != -1 and book_id in self.metadata and self.metadata[book_id].get('is_active', True):
                meta = self.metadata[book_id].copy()
                meta['score'] = float(score)
                results.append(meta)
        return results

    def keyword_search(self, query: str, k: int = 20) -> list:
        """Simple keyword search across metadata."""
        query_lower = query.lower()
        results = []
        for book_id, meta in self.metadata.items():
            if not meta.get('is_active', True):
                continue
            score = 0
            if query_lower in meta.get('title', '').lower():
                score += 3
            if query_lower in meta.get('author', '').lower():
                score += 2
            if query_lower in meta.get('description', '').lower():
                score += 1
            if query_lower in meta.get('book_type', '').lower():
                score += 2
            if query_lower in meta.get('category', '').lower():
                score += 2
            if score > 0:
                m = meta.copy()
                m['score'] = score
                results.append(m)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]

    def add_knowledge_doc(self, doc_id: int, title: str, content: str, doc_type: str = 'faq'):
        """Add a knowledge document (FAQ, policy) to the index."""
        model = self._get_model()
        text = f"{title}. {content}"
        embedding = model.encode([text])[0].astype('float32')
        dim = len(embedding)

        if self.index is None:
            self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))

        faiss.normalize_L2(embedding.reshape(1, -1))
        self.index.add_with_ids(embedding.reshape(1, -1), np.array([doc_id], dtype='int64'))
        self.metadata[doc_id] = {
            'book_id': doc_id,
            'title': title,
            'author': '',
            'book_type': doc_type,
            'category': 'knowledge',
            'price': 0,
            'description': content[:200],
            'is_active': True,
        }
        self._save()

    def get_stats(self) -> dict:
        """Return index statistics."""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'total_metadata': len(self.metadata),
            'index_path': settings.FAISS_INDEX_PATH,
        }


vector_store = BookVectorStore()
