import re
import unicodedata
from .knowledge_base import KnowledgeBase


def _remove_accents(text):
    """Normalize Vietnamese text: remove diacritics for keyword matching."""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn').lower()


class RAGEngine:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def _get_behavior_scores(self, customer_id, book_ids):
        if not customer_id:
            return {}
        try:
            from .ncf_model import BehaviorModelManager
            mgr = BehaviorModelManager()
            if not mgr.is_trained():
                return {}
            int_ids = []
            for bid in book_ids:
                try:
                    int_ids.append(int(bid))
                except (ValueError, TypeError):
                    pass
            if not int_ids:
                return {}
            return mgr.predict(int(customer_id), int_ids)
        except Exception:
            return {}

    def _extract_price_limit(self, query_lower):
        q = _remove_accents(query_lower)
        max_price = None
        min_price = None
        m = re.search(r'(?:duoi|under|below|less than)\s*\$?(\d+(?:\.\d+)?)', q)
        if m:
            max_price = float(m.group(1))
        m2 = re.search(r'(?:tren|above|over|more than)\s*\$?(\d+(?:\.\d+)?)', q)
        if m2:
            min_price = float(m2.group(1))
        return max_price, min_price

    def _extract_author_name(self, query_original):
        patterns = [
            r'sách của\s+(.+)',
            r'sach cua\s+(.+)',
            r'books? by\s+(.+)',
            r'của\s+([A-Z][a-zA-Z .]+)',
            r'cua\s+([A-Z][a-zA-Z .]+)',
            r'by\s+([A-Z][a-zA-Z .]+)',
            r'tác giả\s+(.+)',
            r'tac gia\s+(.+)',
            r'author\s+(.+)',
        ]
        for pat in patterns:
            m = re.search(pat, query_original, re.IGNORECASE)
            if m:
                return m.group(1).strip().rstrip('?.')
        return None

    def _rank_faq_by_category(self, faq_entries, query_norm):
        """Re-rank FAQ entries: boost entries whose category keywords match query."""
        category_keywords = {
            'payment':   ['thanh toan', 'payment', 'tra tien', 'visa', 'mastercard', 'paypal', 'bao mat'],
            'shipping':  ['giao hang', 'shipping', 'phi ship', 'van chuyen', 'theo doi', 'tracking'],
            'return':    ['doi tra', 'return', 'hoan tien', 'refund', 'tra hang'],
            'promotion': ['khuyen mai', 'discount', 'giam gia', 'ma giam', 'sale', 'uu dai'],
            'account':   ['tai khoan', 'account', 'dang ky', 'thanh vien'],
            'support':   ['ho tro', 'support', 'lien he', 'contact', 'hotline'],
        }
        def score(entry):
            cat = entry.get('metadata', {}).get('category', '')
            kws = category_keywords.get(cat, [])
            return sum(1 for kw in kws if kw in query_norm)
        return sorted(faq_entries, key=score, reverse=True)

    def _detect_genre(self, query_norm):
        """Return genre label if detected in query."""
        genre_map = {
            'fantasy':   ['fantasy', 'phieu luu', 'phep thuat', 'magic', 'tolkien', 'hobbit'],
            'sci-fi':    ['sci-fi', 'science fiction', 'khoa hoc vien tuong', 'vien tuong', 'space', 'robot', 'future'],
            'mystery':   ['mystery', 'trinh tham', 'detective', 'crime', 'thriller', 'giet nguoi'],
            'romance':   ['romance', 'tinh cam', 'love', 'tinh yeu'],
            'horror':    ['horror', 'kinh di', 'scary', 'ghost', 'ma'],
            'biography': ['biography', 'tieu su', 'memoir', 'autobiography'],
        }
        for genre, kws in genre_map.items():
            if any(kw in query_norm for kw in kws):
                return genre
        return None

    def generate_response(self, user_query, customer_id=None, context_books=None):
        query_lower = user_query.lower()
        query_norm  = _remove_accents(user_query)

        def _match(kws):
            return any(kw in query_lower or _remove_accents(kw) in query_norm for kw in kws)

        service_kw   = ["thanh toán", "payment", "giao hàng", "shipping", "đổi trả", "return",
                        "hoàn tiền", "refund", "khuyến mãi", "discount", "giảm giá", "hỗ trợ",
                        "support", "liên hệ", "contact", "tài khoản", "account", "phí ship",
                        "chính sách", "policy"]
        recommend_kw = ["recommend", "gợi ý", "suggest", "like", "tương tự", "similar",
                        "nên đọc", "muốn đọc", "hay không", "hay nhất", "best", "top"]
        price_kw     = ["price", "giá", "bao nhiêu", "cheap", "rẻ", "đắt", "tiền", "usd", "dưới", "trên"]
        author_kw    = ["author", "tác giả", "who wrote", "ai viết", "viết bởi", "sách của", "books by"]
        genre_kw     = ["genre", "thể loại", "loại sách", "category", "fantasy", "sci-fi",
                        "romance", "mystery", "horror", "thriller", "biography",
                        "khoa học viễn tưởng", "trinh thám", "kinh dị", "phiêu lưu"]

        is_service   = _match(service_kw)
        is_recommend = _match(recommend_kw)
        is_price     = _match(price_kw)
        is_author    = _match(author_kw)
        is_genre     = _match(genre_kw)

        # ── SERVICE intent ────────────────────────────────────────────────────
        if is_service:
            faq_entries = self.kb.query_faq(user_query, n_results=10)
            faq_entries = self._rank_faq_by_category(faq_entries, query_norm)
            if faq_entries:
                lines = [f"- {r.get('text', '')}" for r in faq_entries[:3]]
                response = "Thông tin dịch vụ Bookstore:\n" + "\n".join(lines)
            else:
                response = "Tôi chưa có thông tin về dịch vụ này. Vui lòng liên hệ support@bookstore.com."
            return {'query': user_query, 'response': response, 'sources': [], 'retrieved_count': len(faq_entries), 'personalized': False}

        # For all book intents: query with more results for better filtering
        book_entries = self.kb.query_books(user_query, n_results=20)

        # ── AUTHOR intent ─────────────────────────────────────────────────────
        if is_author:
            author_name = self._extract_author_name(user_query)
            if author_name:
                filtered = [
                    r for r in book_entries
                    if author_name.lower() in r.get('metadata', {}).get('author', '').lower()
                ]
                if filtered:
                    lines = [
                        f"- \"{r['metadata'].get('title','?')}\" by {r['metadata'].get('author','?')} (${float(r['metadata'].get('price',0)):.2f})"
                        for r in filtered[:6]
                    ]
                    sources = [{'title': r['metadata'].get('title',''), 'author': r['metadata'].get('author','')} for r in filtered[:3]]
                    return {'query': user_query, 'response': f"Sách của {author_name}:\n" + "\n".join(lines),
                            'sources': sources, 'retrieved_count': len(filtered), 'personalized': False}
            # fallback
            lines = [f"- \"{r['metadata'].get('title','?')}\" — {r['metadata'].get('author','?')}" for r in book_entries[:5]]
            sources = [{'title': r['metadata'].get('title',''), 'author': r['metadata'].get('author','')} for r in book_entries[:3]]
            return {'query': user_query, 'response': "Kết quả tìm kiếm:\n" + "\n".join(lines) if lines else "Không tìm thấy.",
                    'sources': sources, 'retrieved_count': len(book_entries), 'personalized': False}

        # ── PRICE intent ─────────────────────────────────────────────────────
        if is_price:
            max_price, min_price = self._extract_price_limit(query_lower)
            filtered = book_entries
            if max_price is not None:
                filtered = [r for r in filtered if float(r.get('metadata', {}).get('price', 9999)) <= max_price]
            if min_price is not None:
                filtered = [r for r in filtered if float(r.get('metadata', {}).get('price', 0)) >= min_price]
            if not filtered and (max_price or min_price):
                # fallback: get more books and filter
                all_books = self.kb.query_books("book", n_results=50)
                filtered = all_books
                if max_price is not None:
                    filtered = [r for r in filtered if float(r.get('metadata', {}).get('price', 9999)) <= max_price]
                if min_price is not None:
                    filtered = [r for r in filtered if float(r.get('metadata', {}).get('price', 0)) >= min_price]
            filtered.sort(key=lambda r: float(r.get('metadata', {}).get('price', 0)),
                          reverse=(min_price is not None and max_price is None))
            if filtered:
                label = f"dưới ${max_price:.0f}" if max_price else (f"trên ${min_price:.0f}" if min_price else "")
                lines = [
                    f"- \"{r['metadata'].get('title','?')}\" by {r['metadata'].get('author','?')} — ${float(r['metadata'].get('price',0)):.2f}"
                    for r in filtered[:6]
                ]
                response = f"Sách {label}:\n" + "\n".join(lines)
            else:
                response = "Không tìm thấy sách phù hợp với mức giá đó."
            sources = [{'title': r['metadata'].get('title',''), 'author': r['metadata'].get('author','')} for r in filtered[:3]]
            return {'query': user_query, 'response': response, 'sources': sources, 'retrieved_count': len(filtered), 'personalized': False}

        # ── GENRE intent: keyword-boost authors known for that genre ──────────
        if is_genre:
            detected_genre = self._detect_genre(query_norm)
            genre_authors = {
                'fantasy':   ['tolkien', 'rowling', 'lewis', 'jordan', 'martin'],
                'sci-fi':    ['asimov', 'dick', 'clarke', 'herbert', 'orwell', 'atwood', 'gaiman'],
                'mystery':   ['christie', 'doyle', 'king', 'brown', 'grisham'],
                'romance':   ['austen', 'bronte', 'sparks'],
                'horror':    ['king', 'lovecraft', 'poe'],
                'biography': [],
            }
            known_authors = genre_authors.get(detected_genre, []) if detected_genre else []
            if known_authors:
                boosted = [r for r in book_entries if any(a in r.get('metadata', {}).get('author', '').lower() for a in known_authors)]
                rest    = [r for r in book_entries if r not in boosted]
                book_entries = boosted + rest

        # ── RECOMMEND / DEFAULT: NCF re-ranking ──────────────────────────────
        behavior_scores = {}
        if customer_id and book_entries:
            raw_ids = [r.get('metadata', {}).get('id') for r in book_entries if r.get('metadata', {}).get('id')]
            behavior_scores = self._get_behavior_scores(customer_id, raw_ids)

        def _rank_score(r):
            meta = r.get('metadata', {})
            kb_sim = 1.0 - float(r.get('distance', 1.0))
            ncf = behavior_scores.get(str(meta.get('id', '')), 0.0)
            return 0.6 * kb_sim + 0.4 * ncf if behavior_scores else kb_sim

        ranked = sorted(book_entries, key=_rank_score, reverse=True)
        is_personalized = bool(behavior_scores)
        personal_prefix = "Dựa trên hành vi mua sắm và sở thích của bạn, " if is_personalized else ""

        sources = [
            {'title': r['metadata'].get('title', ''), 'author': r['metadata'].get('author', '')}
            for r in ranked if r.get('metadata', {}).get('title')
        ]

        if ranked:
            lines = []
            for r in ranked[:5]:
                meta = r['metadata']
                ncf_score = behavior_scores.get(str(meta.get('id', '')), None)
                score_note = f" [Phù hợp: {round(ncf_score * 100)}%]" if ncf_score else ""
                lines.append(f"- \"{meta.get('title','?')}\" by {meta.get('author','?')} (${float(meta.get('price',0)):.2f}){score_note}")
            book_list = ", ".join(f'"{s["title"]}"' for s in sources[:3] if s["title"])
            response = f"{personal_prefix}đây là những cuốn sách tôi gợi ý cho bạn:\n" + "\n".join(lines)
            if book_list:
                response += f"\n\nBạn có thể thích: {book_list}."
            if is_personalized:
                response += "\n\n💡 Gợi ý được cá nhân hóa dựa trên lịch sử của bạn."
        else:
            response = "Tôi không tìm thấy sách phù hợp. Bạn có thể mô tả thêm không?"

        return {'query': user_query, 'response': response, 'sources': sources,
                'retrieved_count': len(ranked), 'personalized': is_personalized}

    def chat(self, messages, customer_id=None):
        last_user_message = ''
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content', '')
                break
        result = self.generate_response(last_user_message, customer_id=customer_id)
        result['history_length'] = len(messages)
        return result
