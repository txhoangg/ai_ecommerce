import logging
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Optional
from django.conf import settings
from .vector_store import vector_store
from modules.graph.services.graph_service import graph_service

logger = logging.getLogger(__name__)


def _remove_accents(text: str) -> str:
    """Normalize Vietnamese text by removing diacritics for unaccented matching."""
    text = text.replace('đ', 'd').replace('Đ', 'D')
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()


class RAGService:
    def __init__(self):
        self._llm_backoff_until = 0.0

    def _detect_book_type(self, query: str) -> Optional[str]:
        """Detect book type from query using Vietnamese and English keywords (with/without accents)."""
        query_norm = _remove_accents(query)
        query_lower = query.lower()

        def match(kw: str) -> bool:
            return kw in query_lower or _remove_accents(kw) in query_norm

        patterns = {
            'manga': ['manga', 'truyện tranh', 'comic', 'conan', 'one piece', 'naruto', 'doraemon'],
            'textbook': ['giáo khoa', 'textbook', 'học sinh', 'lớp ', 'sách giáo'],
            'newspaper': ['báo', 'newspaper', 'tuổi trẻ', 'thanh niên', 'tin tức', 'nhật báo'],
            'magazine': ['tạp chí', 'magazine', 'forbes', 'time', 'elle'],
            'ebook': ['ebook', 'pdf', 'epub', 'sách điện tử', 'digital', 'e-book'],
            'audiobook': ['audio', 'nghe sách', 'sách nói', 'audiobook', 'podcast'],
            'dictionary': ['từ điển', 'dictionary', 'anh-việt', 'việt-anh', 'từ vựng'],
            'children': ['thiếu nhi', 'trẻ em', 'children', 'kids'],
            'science': ['khoa học', 'science', 'vật lý', 'sinh học', 'thiên văn', 'hóa học'],
            'self_help': ['kỹ năng', 'self-help', 'đắc nhân tâm', 'phát triển bản thân',
                          'tư duy', 'thành công'],
            'fiction': ['tiểu thuyết', 'fiction', 'văn học', 'novel', 'truyện ngắn'],
            'encyclopedia': ['bách khoa', 'encyclopedia'],
        }
        for book_type, keywords in patterns.items():
            if any(match(kw) for kw in keywords):
                return book_type
        return None

    def _catalog_books(self) -> list:
        books = []
        for meta in vector_store.metadata.values():
            if not isinstance(meta, dict):
                continue
            if meta.get('book_type') == 'faq' or not meta.get('is_active', True):
                continue
            if not meta.get('book_id'):
                continue
            books.append(meta.copy())
        return books

    def _format_price(self, price: float | int | None) -> str:
        if price in (None, ''):
            return "Liên hệ"
        try:
            return f"{int(float(price)):,}đ".replace(',', '.')
        except (TypeError, ValueError):
            return "Liên hệ"

    def _pick_books_by_titles(self, books: list, titles: list[str], limit: int = 4) -> list:
        book_map = {_remove_accents(book.get('title', '')): book for book in books}
        selected = []
        for title in titles:
            match = book_map.get(_remove_accents(title))
            if match:
                selected.append(match)
        return selected[:limit]

    def _find_books_by_author(self, books: list, author_name: str, limit: int = 4) -> list:
        author_norm = _remove_accents(author_name)
        matched = [book for book in books if author_norm in _remove_accents(book.get('author', ''))]
        matched.sort(key=lambda b: (_remove_accents(b.get('title', '')), b.get('price', 0)))
        return matched[:limit]

    def _find_books_by_price(self, books: list, min_price: int | None = None,
                             max_price: int | None = None, limit: int = 4) -> list:
        matched = []
        for book in books:
            price = book.get('price')
            if price is None:
                continue
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            matched.append(book)
        matched.sort(key=lambda b: (b.get('price', 0), _remove_accents(b.get('title', ''))))
        return matched[:limit]

    def _find_books_by_keywords(self, books: list, keywords: list[str], limit: int = 4,
                                preferred_types: list[str] | None = None) -> list:
        scored = []
        normalized_keywords = [_remove_accents(keyword) for keyword in keywords]
        preferred_types = preferred_types or []
        for book in books:
            haystack = ' '.join([
                book.get('title', ''),
                book.get('author', ''),
                book.get('description', ''),
                book.get('category', ''),
                book.get('book_type', ''),
            ])
            haystack_norm = _remove_accents(haystack)
            score = sum(1 for keyword in normalized_keywords if keyword in haystack_norm)
            if preferred_types and book.get('book_type') in preferred_types:
                score += 2
            if score > 0:
                scored.append((score, book))
        scored.sort(key=lambda item: (-item[0], item[1].get('price', 0), _remove_accents(item[1].get('title', ''))))
        return [book for _, book in scored[:limit]]

    def _extract_price_amount(self, query: str) -> Optional[int]:
        query_norm = _remove_accents(query)
        match = re.search(r'(\d[\d\.,]*)\s*(usd|\$|trieu|k|nghin|ngan|dong|d|đ)?', query_norm)
        if not match:
            return None

        raw_value = match.group(1).replace('.', '').replace(',', '')
        unit = (match.group(2) or '').strip()
        try:
            amount = float(raw_value)
        except ValueError:
            return None

        if unit in {'usd', '$'}:
            amount *= 25000
        elif unit in {'k', 'nghin', 'ngan'}:
            amount *= 1000
        elif unit == 'trieu':
            amount *= 1000000
        return int(amount)

    def _build_book_response(self, intro: str, books: list, detected_type: Optional[str] = None,
                             empty_message: Optional[str] = None) -> dict:
        selected = books[:4]
        if not selected:
            return {
                'answer': empty_message or "Hiện tôi chưa tìm thấy đầu sách phù hợp trong catalog hiện tại.",
                'suggested_books': [],
                'detected_type': detected_type,
            }

        lines = [intro]
        for book in selected:
            lines.append(
                f"- {book.get('title', 'Không rõ tên')} - {book.get('author', 'Không rõ tác giả')} "
                f"({self._format_price(book.get('price'))})"
            )
        return {
            'answer': '\n'.join(lines),
            'suggested_books': selected,
            'detected_type': detected_type,
        }

    def _build_curated_response(self, query: str) -> Optional[dict]:
        q_norm = _remove_accents(query)
        books = self._catalog_books()
        core_books = [book for book in books if book.get('book_type') not in {'newspaper', 'magazine'}]

        if any(keyword in q_norm for keyword in ['giao hang', 'shipping', 'van chuyen', 'ship']):
            return {
                'answer': (
                    "Hiện hệ thống checkout của Bookstore hỗ trợ 3 cách giao hàng:\n"
                    "- Standard: 5-7 ngày\n"
                    "- Express: 2-3 ngày\n"
                    "- Overnight: giao nhanh trong ngày hôm sau\n"
                    "Bạn chọn trực tiếp phương thức giao hàng ở bước checkout."
                ),
                'suggested_books': [],
                'detected_type': None,
            }

        if any(keyword in q_norm for keyword in ['thanh toan', 'payment', 'cod', 'paypal', 'credit card', 'debit card']):
            return {
                'answer': (
                    "Ở giao diện checkout hiện tại, Bookstore hỗ trợ 4 phương thức thanh toán:\n"
                    "- Credit Card\n"
                    "- Debit Card\n"
                    "- PayPal\n"
                    "- Cash on Delivery (COD)"
                ),
                'suggested_books': [],
                'detected_type': None,
            }

        if any(keyword in q_norm for keyword in ['doi tra', 'return', 'refund', 'hoan tien', 'tra hang']):
            return {
                'answer': (
                    "Chính sách đổi trả hiện tại:\n"
                    "- Đổi/trả trong vòng 7 ngày kể từ khi nhận hàng\n"
                    "- Áp dụng khi sách lỗi in, giao sai tựa hoặc hư hỏng do vận chuyển\n"
                    "- Sách không lỗi từ nhà xuất bản thường không được đổi trả\n"
                    "- Liên hệ support@bookstore.vn để được hỗ trợ"
                ),
                'suggested_books': [],
                'detected_type': None,
            }

        if any(keyword in q_norm for keyword in ['khuyen mai', 'giam gia', 'discount', 'voucher', 'coupon']):
            return {
                'answer': (
                    "Hệ thống có hỗ trợ mã giảm giá ở bước checkout.\n"
                    "Nếu bạn có mã còn hiệu lực, nhập vào ô Discount Code để hệ thống tự kiểm tra và trừ tiền.\n"
                    "Trong dữ liệu mẫu hiện tại tôi chưa thấy seed sẵn một mã cố định nào để giới thiệu trực tiếp."
                ),
                'suggested_books': [],
                'detected_type': None,
            }

        if any(keyword in q_norm for keyword in ['nguyen nhat anh']):
            return self._build_book_response(
                "Hiện catalog có các sách của Nguyễn Nhật Ánh:",
                self._find_books_by_author(books, 'Nguyễn Nhật Ánh'),
                detected_type='fiction',
                empty_message="Hiện catalog chưa có sách của Nguyễn Nhật Ánh."
            )

        if any(keyword in q_norm for keyword in ['dale carnegie']):
            return self._build_book_response(
                "Các đầu sách của Dale Carnegie hiện có:",
                self._find_books_by_author(books, 'Dale Carnegie'),
                detected_type='self_help',
                empty_message="Hiện catalog chưa có sách của Dale Carnegie."
            )

        if any(keyword in q_norm for keyword in ['george orwell']):
            return {
                'answer': (
                    "Hiện catalog mẫu chưa có sách của George Orwell.\n"
                    "Nếu bạn muốn xem tác giả đang có sẵn, tôi gợi ý Nguyễn Nhật Ánh hoặc Dale Carnegie."
                ),
                'suggested_books': [],
                'detected_type': None,
            }

        if any(keyword in q_norm for keyword in ['j.k. rowling', 'jk rowling']):
            return {
                'answer': (
                    "Hiện catalog mẫu chưa có sách của J.K. Rowling.\n"
                    "Bạn có thể thử các tác giả đang có sẵn như Nguyễn Nhật Ánh, Dale Carnegie hoặc Stephen Hawking."
                ),
                'suggested_books': [],
                'detected_type': None,
            }

        if any(keyword in q_norm for keyword in ['thieu nhi', 'tre em', 'children']):
            curated = self._pick_books_by_titles(books, [
                'Dế Mèn Phiêu Lưu Ký',
                'Hoàng Tử Bé',
                'Totto-Chan: Cô Bé Bên Cửa Sổ',
                'Cho Tôi Xin Một Vé Đi Tuổi Thơ',
            ])
            return self._build_book_response(
                "Nếu bạn muốn sách thiếu nhi dễ đọc và nổi tiếng, tôi gợi ý:",
                curated,
                detected_type='children',
            )

        if any(keyword in q_norm for keyword in ['trinh tham', 'mystery', 'tham tu', 'conan']):
            curated = self._pick_books_by_titles(books, ['Thám Tử Lừng Danh Conan - Tập 1'])
            return self._build_book_response(
                "Với truyện trinh thám, lựa chọn phù hợp nhất hiện có là:",
                curated,
                detected_type='manga',
            )

        if any(keyword in q_norm for keyword in ['fantasy']):
            curated = self._pick_books_by_titles(books, [
                'Dế Mèn Phiêu Lưu Ký',
                'One Piece - Tập 1',
                'Doraemon - Tập 1',
            ])
            return self._build_book_response(
                "Catalog hiện chưa có fantasy thuần, nhưng nếu bạn thích không khí phiêu lưu và giàu tưởng tượng, bạn có thể thử:",
                curated,
                detected_type='fiction',
            )

        if any(keyword in q_norm for keyword in ['sci-fi', 'sci fi', 'khoa hoc vien tuong']):
            curated = self._pick_books_by_titles(books, [
                'Lược Sử Thời Gian',
                'Sapiens: Lược Sử Loài Người',
                'Bách Khoa Toàn Thư Khoa Học',
            ])
            return self._build_book_response(
                "Catalog hiện chưa có sci-fi thuần, nhưng nếu bạn thích chủ đề khoa học và khám phá, bạn có thể xem:",
                curated,
                detected_type='science',
            )

        if any(keyword in q_norm for keyword in ['khoa hoc', 'science']):
            curated = self._pick_books_by_titles(books, [
                'Lược Sử Thời Gian',
                'Sapiens: Lược Sử Loài Người',
                'Bách Khoa Toàn Thư Khoa Học',
            ])
            return self._build_book_response(
                "Nếu bạn muốn sách khoa học dễ đọc, đây là các lựa chọn nổi bật:",
                curated,
                detected_type='science',
            )

        if any(keyword in q_norm for keyword in ['hay nhat', 'noi bat', 'nen doc', 'de cu', 'best']):
            curated = self._pick_books_by_titles(books, [
                'Mắt Biếc',
                'Đắc Nhân Tâm',
                'Lược Sử Thời Gian',
                'Hoàng Tử Bé',
            ])
            return self._build_book_response(
                "Nếu bạn muốn chọn nhanh các đầu sách nổi bật hiện có, tôi gợi ý:",
                curated,
            )

        price_intent = any(keyword in q_norm for keyword in ['gia', 'duoi', 'tren', 're', 'cao cap', 'dat'])
        if price_intent:
            amount = self._extract_price_amount(query)
            if amount is not None and 'duoi' in q_norm:
                matched = self._find_books_by_price(core_books, max_price=amount)
                return self._build_book_response(
                    f"Nếu bạn muốn sách dưới {self._format_price(amount)}, đây là các lựa chọn phù hợp:",
                    matched,
                )
            if amount is not None and 'tren' in q_norm:
                matched = self._find_books_by_price(core_books, min_price=amount)
                return self._build_book_response(
                    f"Nếu bạn muốn sách từ {self._format_price(amount)} trở lên, tôi gợi ý:",
                    matched,
                )
            if any(keyword in q_norm for keyword in ['re', 'gia mem']):
                matched = self._find_books_by_price(core_books, max_price=50000)
                return self._build_book_response(
                    "Nếu bạn muốn sách giá mềm, đây là các đầu sách dưới 50.000đ:",
                    matched,
                )
            if any(keyword in q_norm for keyword in ['cao cap', 'dat']):
                matched = self._find_books_by_price(core_books, min_price=200000)
                return self._build_book_response(
                    "Nếu bạn muốn nhóm sách giá cao hơn, đây là các lựa chọn nổi bật:",
                    matched,
                )

        return None

    def chat(self, messages: list, user_id: Optional[int] = None) -> dict:
        """
        Main chat method - RAG pipeline:
        1. Get user's graph context (if logged in)
        2. Vector search + keyword search on products
        3. Build augmented prompt
        4. Call LLM (or fallback to rule-based)
        5. Return answer + suggested books
        """
        # Get last user message
        last_query = ''
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_query = msg.get('content', '')
                break

        if not last_query:
            return {'answer': 'Xin lỗi, tôi không hiểu câu hỏi của bạn.', 'suggested_books': []}

        curated_response = self._build_curated_response(last_query)
        if curated_response is not None:
            if user_id and curated_response.get('suggested_books'):
                try:
                    graph_service.log_search(
                        user_id,
                        last_query,
                        [book['book_id'] for book in curated_response['suggested_books'] if book.get('book_id')]
                    )
                except Exception:
                    pass
            return curated_response

        # 1. Graph context
        graph_context = []
        if user_id:
            try:
                history = graph_service.get_user_interaction_history(user_id)
                graph_context = history[:5]
            except Exception as e:
                logger.warning(f"Could not get graph context: {e}")

        # 2. Search products
        detected_type = self._detect_book_type(last_query)
        vector_results = vector_store.search(last_query, k=15)
        keyword_results = vector_store.keyword_search(last_query, k=15)

        # Merge and deduplicate (prefer vector results, skip knowledge docs)
        seen_ids = set()
        all_results = []
        for r in vector_results + keyword_results:
            bid = r.get('book_id')
            if bid and bid not in seen_ids and r.get('book_type') != 'faq':
                seen_ids.add(bid)
                all_results.append(r)

        # Filter by detected book type - boost matching type to front
        if detected_type and any(r.get('book_type') == detected_type for r in all_results):
            all_results = (
                [r for r in all_results if r.get('book_type') == detected_type] +
                [r for r in all_results if r.get('book_type') != detected_type]
            )

        top_books = all_results[:6]

        # 3. Build context string
        context_parts = []
        if top_books:
            context_parts.append("Sản phẩm có sẵn:")
            for b in top_books[:5]:
                price_str = f"{b.get('price', 0):,.0f}đ" if b.get('price') else "Liên hệ"
                context_parts.append(
                    f"- {b['title']} (Loại: {b.get('book_type', 'sách')}, Giá: {price_str}): "
                    f"{b.get('description', '')[:100]}"
                )

        if graph_context:
            recently_viewed = [str(g['book_id']) for g in graph_context[:3]]
            context_parts.append(f"\nKhách hàng gần đây đã xem/mua sách ID: {', '.join(recently_viewed)}")

        context_str = '\n'.join(context_parts)

        # 4. Call LLM (always returns a string — falls back to rule-based on error)
        answer = self._call_llm(last_query, context_str, messages)

        # 7. Log search to graph
        if user_id and top_books:
            book_ids = [b['book_id'] for b in top_books if b.get('book_id')]
            try:
                graph_service.log_search(user_id, last_query, book_ids)
            except Exception:
                pass

        return {
            'answer': answer,
            'suggested_books': top_books[:4],
            'detected_type': detected_type,
        }

    def _call_llm(self, query: str, context: str, conversation_history: list) -> str:
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if not api_key:
            return self._rule_based_response(query, context)
        if time.time() < self._llm_backoff_until:
            return self._rule_based_response(query, context)

        llm_timeout = max(int(getattr(settings, 'GEMINI_REQUEST_TIMEOUT_SECONDS', 8)), 1)
        cooldown_seconds = max(int(getattr(settings, 'GEMINI_COOLDOWN_SECONDS', 60)), 5)
        history = []
        for msg in conversation_history[-5:]:
            role = 'user' if msg.get('role') == 'user' else 'model'
            history.append({'role': role, 'parts': [msg.get('content', '')]})

        prompt = f"Ngữ cảnh sản phẩm:\n{context}\n\nCâu hỏi của khách hàng: {query}"
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self._send_gemini_request, api_key, history, prompt, llm_timeout)
        try:
            answer = future.result(timeout=llm_timeout)
            return answer or self._rule_based_response(query, context)
        except FuturesTimeoutError:
            self._llm_backoff_until = max(self._llm_backoff_until, time.time() + cooldown_seconds)
            logger.warning("Gemini request timed out after %ss; falling back to rule-based response", llm_timeout)
            future.cancel()
            return self._rule_based_response(query, context)
        except Exception as e:
            error_message = str(e).lower()
            if '429' in error_message or 'quota' in error_message or 'rate limit' in error_message:
                self._llm_backoff_until = max(self._llm_backoff_until, time.time() + cooldown_seconds)
            logger.error(f"Gemini API error: {e}")
            return self._rule_based_response(query, context)
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _send_gemini_request(self, api_key: str, history: list, prompt: str, llm_timeout: int) -> str:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=getattr(settings, 'GEMINI_MODEL', 'gemini-3.1-flash-lite-preview'),
            system_instruction=(
                "Bạn là trợ lý tư vấn sách thông minh của Bookstore Việt Nam. "
                "Hãy trả lời bằng tiếng Việt, thân thiện, ngắn gọn và hữu ích. "
                "Dựa vào ngữ cảnh sản phẩm để gợi ý sách phù hợp. "
                "Nếu gợi ý sách, hãy đề cập tác giả và đặc điểm nổi bật. "
                "Giới hạn câu trả lời trong 150 từ."
            )
        )
        chat = model.start_chat(history=history)
        try:
            response = chat.send_message(prompt, request_options={'timeout': llm_timeout})
        except TypeError:
            response = chat.send_message(prompt)

        answer = (getattr(response, 'text', '') or '').strip()
        if not answer:
            raise ValueError('Empty response from Gemini')
        return answer

    def _rule_based_response(self, query: str, context: str = '') -> str:
        """Fallback rule-based response when LLM is unavailable."""
        q = query.lower()
        q_norm = _remove_accents(query)
        has_products = 'Sản phẩm có sẵn' in context

        def match(kw): return kw in q or _remove_accents(kw) in q_norm

        if any(match(kw) for kw in ['giá', 'bao nhiêu', 'rẻ', 'đắt', 'price', 'cost']):
            if has_products:
                return "Dưới đây là một số sách với mức giá phù hợp cho bạn tham khảo! Bạn có thể xem chi tiết từng cuốn để chọn được cuốn ưng ý nhất."
            return "Vui lòng xem danh sách sách để biết giá chi tiết. Bookstore có nhiều mức giá từ bình dân đến cao cấp!"

        if any(match(kw) for kw in ['gợi ý', 'hay', 'nên đọc', 'tốt nhất', 'đề xuất', 'recommend']):
            if has_products:
                return "Tôi đã tìm thấy một số sách được đánh giá cao! Hãy xem qua những gợi ý bên dưới nhé."
            return "Hãy cho tôi biết bạn quan tâm đến thể loại sách nào để tôi gợi ý phù hợp hơn!"

        if any(match(kw) for kw in ['giao hàng', 'shipping', 'vận chuyển', 'ship']):
            return (
                "Hiện hệ thống checkout hỗ trợ 3 phương thức giao hàng:\n"
                "- Standard: 5-7 ngày\n"
                "- Express: 2-3 ngày\n"
                "- Overnight: giao nhanh trong ngày hôm sau"
            )

        if any(match(kw) for kw in ['đổi trả', 'return', 'hoàn tiền', 'refund', 'trả hàng', 'chinh sach']):
            return (
                "Chính sách đổi trả:\n"
                "- Đổi/trả trong vòng 7 ngày nếu sách bị lỗi in hoặc giao sai tựa\n"
                "- Sách không có lỗi từ nhà xuất bản không được đổi trả\n"
                "- Liên hệ support@bookstore.vn để được hỗ trợ"
            )

        if any(match(kw) for kw in ['thanh toán', 'payment', 'trả tiền', 'cod', 'chuyển khoản']):
            return (
                "Ở giao diện checkout hiện tại, Bookstore hỗ trợ:\n"
                "- Credit Card\n"
                "- Debit Card\n"
                "- PayPal\n"
                "- Cash on Delivery (COD)"
            )

        if any(match(kw) for kw in ['khuyến mãi', 'giảm giá', 'discount', 'voucher', 'coupon']):
            return (
                "Bookstore có hỗ trợ nhập mã giảm giá ở bước checkout.\n"
                "Nếu mã còn hiệu lực, hệ thống sẽ tự áp dụng vào đơn hàng.\n"
                "Hiện dữ liệu mẫu chưa có sẵn một mã cố định để chatbot giới thiệu trực tiếp."
            )

        if any(match(kw) for kw in ['thành viên', 'membership', 'hội viên', 'điểm tích lũy']):
            return (
                "Chương trình thành viên Bookstore:\n"
                "- Tích điểm với mỗi đơn hàng (1.000đ = 1 điểm)\n"
                "- Hạng Bạc: từ 100 điểm - giảm 5%\n"
                "- Hạng Vàng: từ 500 điểm - giảm 10%\n"
                "- Hạng Kim Cương: từ 2000 điểm - giảm 15%"
            )

        if any(match(kw) for kw in ['liên hệ', 'contact', 'hotline', 'điện thoại', 'email']):
            return (
                "Thông tin liên hệ Bookstore:\n"
                "- Email: support@bookstore.vn\n"
                "- Hotline: 1800-xxxx (miễn phí, 8h-22h)\n"
                "- Website: www.bookstore.vn\n"
                "- Fanpage: facebook.com/bookstore.vn"
            )

        if has_products:
            return "Tôi đã tìm thấy một số sách phù hợp! Hãy xem các gợi ý bên dưới nhé."

        return "Xin lỗi, tôi không tìm thấy thông tin phù hợp. Bạn có thể mô tả rõ hơn không?"


rag_service = RAGService()
