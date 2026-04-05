import chromadb


class KnowledgeBase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path='/tmp/bookstore_kb')
        self.collection = self.client.get_or_create_collection(name='bookstore_kb')

    def build_from_books(self, books):
        """Build the knowledge base from a list of book dicts."""
        # Clear existing documents
        existing = self.collection.get()
        if existing['ids']:
            self.collection.delete(ids=existing['ids'])

        if not books:
            return

        documents = []
        metadatas = []
        ids = []

        for book in books:
            book_id = book.get('id')
            title = book.get('title', '')
            author = book.get('author', '')
            description = book.get('description', '')
            price = book.get('price', 0)
            stock = book.get('stock', 0)

            text = f"{title} by {author}. {description}"
            documents.append(text)
            metadatas.append({
                'type': 'book',
                'id': str(book_id),
                'title': title,
                'author': author,
                'price': float(price) if price else 0.0,
                'stock': int(stock) if stock else 0,
            })
            ids.append(f"book_{book_id}")

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query_books(self, query_text, n_results=5):
        """Query only book entries (exclude FAQ)."""
        try:
            count = self.collection.count()
            if count == 0:
                return []
            # Count only books
            book_count = len(self.collection.get(where={"type": "book"})['ids'])
            if book_count == 0:
                return []
            n_results = min(n_results, book_count)
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"type": "book"},
            )
        except Exception:
            return []

        output = []
        if not results or not results['ids']:
            return output
        for i, doc_id in enumerate(results['ids'][0]):
            output.append({
                'id': doc_id,
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
            })
        return output

    def query_faq(self, query_text, n_results=5):
        """Query only FAQ entries."""
        try:
            count = self.collection.count()
            if count == 0:
                return []
            faq_count = len(self.collection.get(where={"type": "faq"})['ids'])
            if faq_count == 0:
                return []
            n_results = min(n_results, faq_count)
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"type": "faq"},
            )
        except Exception:
            return []

        output = []
        if not results or not results['ids']:
            return output
        for i, doc_id in enumerate(results['ids'][0]):
            output.append({
                'id': doc_id,
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
            })
        return output

    def query(self, query_text, n_results=5):
        """Query the knowledge base and return list of result dicts."""
        # Guard: n_results cannot exceed the number of documents in the collection
        count = self.collection.count()
        if count == 0:
            return []
        n_results = min(n_results, count)
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )

        output = []
        if not results or not results['ids']:
            return output

        ids = results['ids'][0]
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        for i, doc_id in enumerate(ids):
            output.append({
                'id': doc_id,
                'text': documents[i],
                'metadata': metadatas[i],
                'distance': distances[i],
            })

        return output

    def build_service_faq(self):
        """Add service FAQ documents (payment, shipping, returns, promotions) to the KB."""
        faq_docs = [
            {
                'id': 'faq_payment_1',
                'text': 'Phương thức thanh toán: Bookstore chấp nhận thanh toán qua thẻ tín dụng (Visa, Mastercard), PayPal, tiền mặt khi nhận hàng (Cash on Delivery), và chuyển khoản ngân hàng.',
                'metadata': {'type': 'faq', 'category': 'payment', 'title': 'Phương thức thanh toán'}
            },
            {
                'id': 'faq_payment_2',
                'text': 'Thanh toán an toàn: Tất cả giao dịch được mã hóa SSL 256-bit. Thông tin thẻ của bạn không được lưu trữ trên hệ thống của chúng tôi.',
                'metadata': {'type': 'faq', 'category': 'payment', 'title': 'Bảo mật thanh toán'}
            },
            {
                'id': 'faq_shipping_1',
                'text': 'Giao hàng tiêu chuẩn (Standard): 3-5 ngày làm việc, phí 5 USD. Giao hàng nhanh (Express): 1-2 ngày làm việc, phí 15 USD. Giao hàng hỏa tốc (Overnight): trong ngày, phí 25 USD.',
                'metadata': {'type': 'faq', 'category': 'shipping', 'title': 'Phí và thời gian giao hàng'}
            },
            {
                'id': 'faq_shipping_2',
                'text': 'Theo dõi đơn hàng: Sau khi đặt hàng thành công, bạn sẽ nhận được mã tracking. Truy cập mục "Orders" để theo dõi trạng thái giao hàng theo thời gian thực.',
                'metadata': {'type': 'faq', 'category': 'shipping', 'title': 'Theo dõi đơn hàng'}
            },
            {
                'id': 'faq_return_1',
                'text': 'Chính sách đổi trả: Bạn có thể trả sách trong vòng 30 ngày kể từ ngày nhận hàng nếu sách bị lỗi in, hư hỏng khi vận chuyển, hoặc giao sai tựa. Sách nguyên vẹn, chưa qua sử dụng.',
                'metadata': {'type': 'faq', 'category': 'return', 'title': 'Chính sách đổi trả'}
            },
            {
                'id': 'faq_return_2',
                'text': 'Quy trình hoàn tiền: Sau khi nhận được sách trả lại và kiểm tra, chúng tôi sẽ hoàn tiền trong 5-7 ngày làm việc qua phương thức thanh toán ban đầu.',
                'metadata': {'type': 'faq', 'category': 'return', 'title': 'Hoàn tiền'}
            },
            {
                'id': 'faq_promo_1',
                'text': 'Mã giảm giá (Discount Code): Nhập mã khuyến mãi tại bước thanh toán để được giảm giá. Mỗi mã có thời hạn sử dụng và điều kiện áp dụng riêng. Kiểm tra mục Promotions để xem mã hiện có.',
                'metadata': {'type': 'faq', 'category': 'promotion', 'title': 'Mã giảm giá'}
            },
            {
                'id': 'faq_promo_2',
                'text': 'Chương trình khuyến mãi: Bookstore thường xuyên có các đợt sale theo mùa, giảm giá thành viên, và ưu đãi đặc biệt cho khách hàng thân thiết. Đăng ký tài khoản để nhận thông báo sớm nhất.',
                'metadata': {'type': 'faq', 'category': 'promotion', 'title': 'Chương trình khuyến mãi'}
            },
            {
                'id': 'faq_account_1',
                'text': 'Đăng ký tài khoản: Tạo tài khoản miễn phí để lưu lịch sử mua hàng, theo dõi đơn hàng, nhận gợi ý sách cá nhân hóa và tham gia các chương trình khuyến mãi dành riêng cho thành viên.',
                'metadata': {'type': 'faq', 'category': 'account', 'title': 'Tài khoản thành viên'}
            },
            {
                'id': 'faq_contact_1',
                'text': 'Liên hệ hỗ trợ: Email support@bookstore.com, hotline 1800-BOOKS (miễn phí), hoặc chat trực tiếp tại website. Thời gian hỗ trợ: 8:00 - 22:00 mỗi ngày kể cả cuối tuần.',
                'metadata': {'type': 'faq', 'category': 'support', 'title': 'Liên hệ hỗ trợ'}
            },
        ]

        existing_faq_ids = [d['id'] for d in faq_docs]
        try:
            existing = self.collection.get(ids=existing_faq_ids)
            ids_to_delete = existing['ids']
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
        except Exception:
            pass

        self.collection.add(
            documents=[d['text'] for d in faq_docs],
            metadatas=[d['metadata'] for d in faq_docs],
            ids=[d['id'] for d in faq_docs],
        )
        return len(faq_docs)

    def get_stats(self):
        return {'total_documents': self.collection.count()}
