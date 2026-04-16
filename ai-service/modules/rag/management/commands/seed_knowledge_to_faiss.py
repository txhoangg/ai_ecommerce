import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

# Knowledge documents seeded with IDs starting at 9000000 to avoid collision with book IDs
KNOWLEDGE_DOCS = [
    {
        'id': 9000001,
        'title': 'Chính sách giao hàng',
        'content': (
            'Bookstore hỗ trợ giao hàng toàn quốc. '
            'Giao hàng tiêu chuẩn: 3-5 ngày làm việc, phí 30.000đ. '
            'Giao hàng nhanh (24h): 1-2 ngày làm việc, phí 50.000đ. '
            'Giao hàng hỏa tốc (trong ngày, nội thành): phí 80.000đ. '
            'Miễn phí giao hàng cho đơn hàng từ 200.000đ trở lên. '
            'Theo dõi đơn hàng qua email hoặc ứng dụng Bookstore. '
            'Đối tác vận chuyển: GHN, GHTK, ViettelPost.'
        ),
        'type': 'faq',
    },
    {
        'id': 9000002,
        'title': 'Chính sách đổi trả và hoàn tiền',
        'content': (
            'Khách hàng được đổi/trả hàng trong vòng 7 ngày kể từ ngày nhận hàng. '
            'Điều kiện đổi trả: sách bị lỗi in, giao sai tựa, hư hỏng trong vận chuyển. '
            'Sách không có lỗi từ nhà xuất bản không được đổi trả (trừ trường hợp đặc biệt). '
            'Hoàn tiền trong 3-5 ngày làm việc sau khi xác nhận đổi trả. '
            'Hình thức hoàn tiền: chuyển khoản ngân hàng hoặc ví điện tử. '
            'Liên hệ support@bookstore.vn hoặc hotline 1800-xxxx để yêu cầu đổi trả.'
        ),
        'type': 'faq',
    },
    {
        'id': 9000003,
        'title': 'Phương thức thanh toán',
        'content': (
            'Bookstore hỗ trợ nhiều phương thức thanh toán: '
            'Thanh toán khi nhận hàng (COD) - áp dụng toàn quốc. '
            'Chuyển khoản ngân hàng: Vietcombank, Techcombank, MB Bank. '
            'Ví điện tử: Momo, ZaloPay, VNPay, ShopeePay. '
            'Thẻ tín dụng/ghi nợ: Visa, Mastercard, JCB. '
            'Trả góp 0%: áp dụng cho đơn từ 1.000.000đ với thẻ tín dụng liên kết. '
            'Điểm thành viên: dùng điểm tích lũy để thanh toán một phần đơn hàng.'
        ),
        'type': 'faq',
    },
    {
        'id': 9000004,
        'title': 'Chương trình thành viên và tích điểm',
        'content': (
            'Chương trình thành viên Bookstore có 4 hạng: Đồng, Bạc, Vàng, Kim Cương. '
            'Tích điểm: mỗi 1.000đ mua sách = 1 điểm thưởng. '
            'Hạng Đồng: 0-99 điểm - không có ưu đãi thêm. '
            'Hạng Bạc: 100-499 điểm - giảm 5% toàn bộ đơn hàng. '
            'Hạng Vàng: 500-1999 điểm - giảm 10% + ưu tiên giao hàng. '
            'Hạng Kim Cương: 2000+ điểm - giảm 15% + giao hàng miễn phí + quà tặng sinh nhật. '
            'Đổi điểm: 100 điểm = 10.000đ giảm giá. '
            'Điểm có hiệu lực 12 tháng kể từ ngày tích.'
        ),
        'type': 'faq',
    },
    {
        'id': 9000005,
        'title': 'Thông tin liên hệ và hỗ trợ',
        'content': (
            'Bookstore - Hệ thống sách trực tuyến hàng đầu Việt Nam. '
            'Email hỗ trợ: support@bookstore.vn. '
            'Hotline: 1800-xxxx (miễn phí, 8h00-22h00 tất cả các ngày). '
            'Chat trực tuyến trên website: www.bookstore.vn. '
            'Fanpage: facebook.com/bookstore.vn. '
            'Địa chỉ: 123 Đường Sách, Quận 1, TP. Hồ Chí Minh. '
            'Thời gian làm việc: 8h00-22h00, kể cả cuối tuần và ngày lễ. '
            'Phản hồi khiếu nại trong vòng 24 giờ.'
        ),
        'type': 'faq',
    },
    {
        'id': 9000006,
        'title': 'Câu hỏi thường gặp về mua sách',
        'content': (
            'Hỏi: Làm thế nào để tìm sách? '
            'Đáp: Dùng thanh tìm kiếm, tìm theo tên sách, tác giả, thể loại hoặc ISBN. '
            'Hỏi: Sách có đảm bảo chất lượng không? '
            'Đáp: 100% sách chính hãng từ NXB uy tín, có tem chống hàng giả. '
            'Hỏi: Có thể đặt trước sách sắp ra mắt không? '
            'Đáp: Có, đặt trước được giảm thêm 10% so với giá bìa. '
            'Hỏi: Bookstore có bán sách nước ngoài không? '
            'Đáp: Có, chúng tôi nhập khẩu sách tiếng Anh, Nhật, Hàn, Pháp và nhiều ngôn ngữ khác. '
            'Hỏi: Tôi có thể mua sách cho thư viện trường/công ty không? '
            'Đáp: Có, liên hệ B2B@bookstore.vn để được tư vấn giá sỉ và hóa đơn VAT.'
        ),
        'type': 'faq',
    },
    {
        'id': 9000007,
        'title': 'Thể loại và danh mục sách',
        'content': (
            'Bookstore phân loại sách thành các thể loại chính: '
            'Văn học - tiểu thuyết, truyện ngắn, thơ trong và ngoài nước. '
            'Sách thiếu nhi - truyện tranh, sách tô màu, sách giáo dục sớm. '
            'Manga - truyện tranh Nhật Bản các thể loại shounen, shoujo, seinen. '
            'Sách giáo khoa - đầy đủ các cấp Tiểu học, THCS, THPT. '
            'Kỹ năng sống - self-help, phát triển bản thân, tài chính cá nhân. '
            'Khoa học - vật lý, hóa học, sinh học, thiên văn, công nghệ. '
            'Tạp chí - Forbes, Elle, Đẹp, Time, National Geographic. '
            'Từ điển - Anh-Việt, Việt-Anh, chuyên ngành các lĩnh vực. '
            'Sách điện tử (ebook) và sách nói (audiobook) cũng có sẵn.'
        ),
        'type': 'faq',
    },
]


class Command(BaseCommand):
    help = 'Seed bookstore knowledge documents (FAQs, policies) into FAISS vector index'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-seed even if knowledge docs are already indexed',
        )

    def handle(self, *args, **options):
        from modules.rag.services.vector_store import vector_store

        self.stdout.write(self.style.NOTICE("Seeding knowledge documents to FAISS..."))

        success_count = 0
        fail_count = 0

        for doc in KNOWLEDGE_DOCS:
            try:
                # Skip if already indexed and not forced
                if not options.get('force') and doc['id'] in vector_store.metadata:
                    self.stdout.write(f"  Skipping '{doc['title']}' (already indexed)")
                    continue

                vector_store.add_knowledge_doc(
                    doc_id=doc['id'],
                    title=doc['title'],
                    content=doc['content'],
                    doc_type=doc['type'],
                )
                success_count += 1
                self.stdout.write(f"  Seeded: {doc['title']}")
            except Exception as e:
                fail_count += 1
                self.stdout.write(self.style.WARNING(f"  Failed to seed '{doc['title']}': {e}"))
                logger.error(f"seed_knowledge error for doc {doc['id']}: {e}")

        stats = vector_store.get_stats()
        self.stdout.write(self.style.SUCCESS(
            f"Knowledge seeding complete: {success_count} added, {fail_count} failed. "
            f"Total in FAISS index: {stats['total_vectors']}"
        ))
