from django.core.management.base import BaseCommand
from django.db import transaction

from modules.catalog.infrastructure.models import (
    BookTypeModel, CategoryModel, PublisherModel, BookModel
)
from modules.catalog.domain.entities.book_type import BookType


BOOK_TYPE_DEFINITIONS = [
    {
        'type_key': BookType.FICTION,
        'name': 'Fiction',
        'name_vi': 'Sách văn học',
        'description': 'Sách văn học, tiểu thuyết, truyện ngắn',
        'icon': '📚',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.FICTION],
    },
    {
        'type_key': BookType.TEXTBOOK,
        'name': 'Textbook',
        'name_vi': 'Sách giáo khoa',
        'description': 'Sách giáo khoa và tài liệu học tập chính thức',
        'icon': '📖',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.TEXTBOOK],
    },
    {
        'type_key': BookType.NEWSPAPER,
        'name': 'Newspaper',
        'name_vi': 'Báo',
        'description': 'Báo và ấn phẩm tin tức hàng ngày',
        'icon': '📰',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.NEWSPAPER],
    },
    {
        'type_key': BookType.MAGAZINE,
        'name': 'Magazine',
        'name_vi': 'Tạp chí',
        'description': 'Tạp chí và ấn phẩm định kỳ',
        'icon': '📄',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.MAGAZINE],
    },
    {
        'type_key': BookType.MANGA,
        'name': 'Manga',
        'name_vi': 'Manga/Truyện tranh',
        'description': 'Manga Nhật Bản và truyện tranh',
        'icon': '🎌',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.MANGA],
    },
    {
        'type_key': BookType.SCIENCE,
        'name': 'Science',
        'name_vi': 'Sách khoa học',
        'description': 'Sách khoa học, kỹ thuật và công nghệ',
        'icon': '🔬',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.SCIENCE],
    },
    {
        'type_key': BookType.SELF_HELP,
        'name': 'Self Help',
        'name_vi': 'Sách kỹ năng sống',
        'description': 'Sách phát triển bản thân và kỹ năng sống',
        'icon': '💡',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.SELF_HELP],
    },
    {
        'type_key': BookType.DICTIONARY,
        'name': 'Dictionary',
        'name_vi': 'Từ điển',
        'description': 'Từ điển và tài liệu tra cứu ngôn ngữ',
        'icon': '📘',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.DICTIONARY],
    },
    {
        'type_key': BookType.CHILDREN,
        'name': 'Children',
        'name_vi': 'Sách thiếu nhi',
        'description': 'Sách dành cho trẻ em và thiếu nhi',
        'icon': '🧸',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.CHILDREN],
    },
    {
        'type_key': BookType.EBOOK,
        'name': 'eBook',
        'name_vi': 'eBook',
        'description': 'Sách điện tử định dạng kỹ thuật số',
        'icon': '💻',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.EBOOK],
    },
    {
        'type_key': BookType.AUDIOBOOK,
        'name': 'Audiobook',
        'name_vi': 'Sách audio',
        'description': 'Sách nói và audio book',
        'icon': '🎧',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.AUDIOBOOK],
    },
    {
        'type_key': BookType.ENCYCLOPEDIA,
        'name': 'Encyclopedia',
        'name_vi': 'Bách khoa toàn thư',
        'description': 'Bách khoa toàn thư và tài liệu tham khảo tổng hợp',
        'icon': '🌍',
        'attribute_schema': BookType.ATTRIBUTE_SCHEMAS[BookType.ENCYCLOPEDIA],
    },
]

PUBLISHER_DEFINITIONS = [
    {'name': 'NXB Kim Đồng', 'email': 'contact@kimdong.vn', 'phone': '024-3822-3460', 'address': 'Hà Nội', 'website': 'https://kimdong.com.vn'},
    {'name': 'NXB Trẻ', 'email': 'info@nxbtre.com.vn', 'phone': '028-3930-5809', 'address': 'TP. Hồ Chí Minh', 'website': 'https://nxbtre.com.vn'},
    {'name': 'NXB Giáo Dục Việt Nam', 'email': 'contact@nxbgd.vn', 'phone': '024-3869-7641', 'address': 'Hà Nội', 'website': 'https://nxbgd.vn'},
    {'name': 'NXB Hội Nhà Văn', 'email': 'nxbhv@hoinhavanvn.org.vn', 'phone': '024-3943-4905', 'address': 'Hà Nội', 'website': ''},
    {'name': 'NXB Khoa Học Kỹ Thuật', 'email': 'contact@nxbkhkt.vn', 'phone': '024-3825-2536', 'address': 'Hà Nội', 'website': ''},
    {'name': 'Alphabooks', 'email': 'info@alphabooks.vn', 'phone': '024-3512-4098', 'address': 'Hà Nội', 'website': 'https://alphabooks.vn'},
    {'name': 'First News', 'email': 'firstnews@firstnews.vn', 'phone': '028-3811-7701', 'address': 'TP. Hồ Chí Minh', 'website': 'https://firstnews.vn'},
    {'name': 'NXB Thế Giới', 'email': 'info@nxbthegioi.vn', 'phone': '024-3825-3841', 'address': 'Hà Nội', 'website': ''},
]

CATEGORY_DEFINITIONS = [
    {'name': 'Văn học Việt Nam', 'slug': 'van-hoc-viet-nam', 'description': 'Tác phẩm văn học của các tác giả Việt Nam'},
    {'name': 'Văn học nước ngoài', 'slug': 'van-hoc-nuoc-ngoai', 'description': 'Tác phẩm văn học quốc tế dịch sang tiếng Việt'},
    {'name': 'Sách giáo khoa THPT', 'slug': 'sach-giao-khoa-thpt', 'description': 'Sách giáo khoa bậc Trung học Phổ thông'},
    {'name': 'Sách giáo khoa THCS', 'slug': 'sach-giao-khoa-thcs', 'description': 'Sách giáo khoa bậc Trung học Cơ sở'},
    {'name': 'Tin tức hàng ngày', 'slug': 'tin-tuc-hang-ngay', 'description': 'Báo và tin tức hàng ngày'},
    {'name': 'Tạp chí kinh tế', 'slug': 'tap-chi-kinh-te', 'description': 'Tạp chí về kinh tế và tài chính'},
    {'name': 'Tạp chí thời trang', 'slug': 'tap-chi-thoi-trang', 'description': 'Tạp chí thời trang và làm đẹp'},
    {'name': 'Manga Nhật Bản', 'slug': 'manga-nhat-ban', 'description': 'Truyện tranh manga từ Nhật Bản'},
    {'name': 'Khoa học tự nhiên', 'slug': 'khoa-hoc-tu-nhien', 'description': 'Sách về khoa học tự nhiên và vũ trụ'},
    {'name': 'Kỹ năng sống', 'slug': 'ky-nang-song', 'description': 'Sách phát triển bản thân và kỹ năng mềm'},
    {'name': 'Ngoại ngữ', 'slug': 'ngoai-ngu', 'description': 'Từ điển và tài liệu học ngoại ngữ'},
    {'name': 'Thiếu nhi', 'slug': 'thieu-nhi', 'description': 'Sách và truyện dành cho trẻ em'},
    {'name': 'Công nghệ thông tin', 'slug': 'cong-nghe-thong-tin', 'description': 'Sách về lập trình và công nghệ thông tin'},
    {'name': 'Triết học & Tâm lý', 'slug': 'triet-hoc-tam-ly', 'description': 'Sách về triết học và tâm lý học'},
]


def get_book_seeds(publishers, categories, book_types):
    pub = {p.name: p for p in publishers}
    cat = {c.slug: c for c in categories}
    bt = {b.type_key: b for b in book_types}

    return [
        # ── FICTION ────────────────────────────────────────────────────────
        {
            'title': 'Dế Mèn Phiêu Lưu Ký',
            'book_type': bt[BookType.FICTION],
            'category': cat.get('van-hoc-viet-nam'),
            'publisher': pub.get('NXB Kim Đồng'),
            'description': 'Truyện dài nổi tiếng của nhà văn Tô Hoài kể về hành trình phiêu lưu của chú Dế Mèn.',
            'price': '45000.00',
            'stock': 150,
            'isbn': '',
            'image_url': 'https://salt.tikicdn.com/cache/400x400/ts/product/45/3a/d5/de-men-phieu-luu-ky.jpg',
            'attributes': {'author': 'Tô Hoài', 'genre': 'Thiếu nhi/Phiêu lưu', 'pages': 208, 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Số Đỏ',
            'book_type': bt[BookType.FICTION],
            'category': cat.get('van-hoc-viet-nam'),
            'publisher': pub.get('NXB Hội Nhà Văn'),
            'description': 'Tiểu thuyết trào phúng nổi tiếng của Vũ Trọng Phụng, phê phán xã hội thực dân nửa phong kiến.',
            'price': '55000.00',
            'stock': 80,
            'isbn': '',
            'image_url': 'https://salt.tikicdn.com/cache/400x400/ts/product/so-do-vu-trong-phung.jpg',
            'attributes': {'author': 'Vũ Trọng Phụng', 'genre': 'Trào phúng/Hiện thực', 'pages': 280, 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Chí Phèo',
            'book_type': bt[BookType.FICTION],
            'category': cat.get('van-hoc-viet-nam'),
            'publisher': pub.get('NXB Hội Nhà Văn'),
            'description': 'Truyện ngắn kinh điển của Nam Cao về người nông dân bị xã hội đẩy vào con đường tha hóa.',
            'price': '40000.00',
            'stock': 120,
            'isbn': '',
            'image_url': '',
            'attributes': {'author': 'Nam Cao', 'genre': 'Hiện thực', 'pages': 176, 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Nhà Thờ Đức Bà Paris',
            'book_type': bt[BookType.FICTION],
            'category': cat.get('van-hoc-nuoc-ngoai'),
            'publisher': pub.get('NXB Văn Học') or pub.get('NXB Trẻ'),
            'description': 'Tiểu thuyết lãng mạn kinh điển của Victor Hugo đặt trong bối cảnh thành phố Paris thế kỷ 15.',
            'price': '85000.00',
            'stock': 60,
            'isbn': '',
            'image_url': '',
            'attributes': {'author': 'Victor Hugo', 'genre': 'Lãng mạn/Lịch sử', 'pages': 512, 'language': 'Tiếng Việt (bản dịch)'},
        },

        # ── TEXTBOOK ───────────────────────────────────────────────────────
        {
            'title': 'Toán 12',
            'book_type': bt[BookType.TEXTBOOK],
            'category': cat.get('sach-giao-khoa-thpt'),
            'publisher': pub.get('NXB Giáo Dục Việt Nam'),
            'description': 'Sách giáo khoa Toán lớp 12 theo chương trình chuẩn của Bộ Giáo dục và Đào tạo.',
            'price': '28000.00',
            'stock': 500,
            'isbn': '',
            'image_url': '',
            'attributes': {'subject': 'Toán học', 'grade_level': 'Lớp 12', 'edition': '2024', 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Vật lý 11',
            'book_type': bt[BookType.TEXTBOOK],
            'category': cat.get('sach-giao-khoa-thpt'),
            'publisher': pub.get('NXB Giáo Dục Việt Nam'),
            'description': 'Sách giáo khoa Vật lý lớp 11 theo chương trình giáo dục phổ thông mới.',
            'price': '26000.00',
            'stock': 450,
            'isbn': '',
            'image_url': '',
            'attributes': {'subject': 'Vật lý', 'grade_level': 'Lớp 11', 'edition': '2024', 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Hóa học 10',
            'book_type': bt[BookType.TEXTBOOK],
            'category': cat.get('sach-giao-khoa-thpt'),
            'publisher': pub.get('NXB Giáo Dục Việt Nam'),
            'description': 'Sách giáo khoa Hóa học lớp 10 theo chương trình giáo dục phổ thông mới.',
            'price': '25000.00',
            'stock': 400,
            'isbn': '',
            'image_url': '',
            'attributes': {'subject': 'Hóa học', 'grade_level': 'Lớp 10', 'edition': '2024', 'language': 'Tiếng Việt'},
        },

        # ── NEWSPAPER ──────────────────────────────────────────────────────
        {
            'title': 'Báo Tuổi Trẻ',
            'book_type': bt[BookType.NEWSPAPER],
            'category': cat.get('tin-tuc-hang-ngay'),
            'publisher': None,
            'description': 'Nhật báo Tuổi Trẻ - tờ báo có lượng phát hành lớn nhất Việt Nam.',
            'price': '6000.00',
            'stock': 200,
            'isbn': '',
            'image_url': 'https://tuoitre.vn/favicon.ico',
            'attributes': {'publication_date': '2024-01-15', 'edition_number': '7489', 'region': 'Toàn quốc', 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Báo Thanh Niên',
            'book_type': bt[BookType.NEWSPAPER],
            'category': cat.get('tin-tuc-hang-ngay'),
            'publisher': None,
            'description': 'Nhật báo Thanh Niên - tờ báo uy tín hàng đầu Việt Nam dành cho giới trẻ.',
            'price': '6000.00',
            'stock': 180,
            'isbn': '',
            'image_url': '',
            'attributes': {'publication_date': '2024-01-15', 'edition_number': '8901', 'region': 'Toàn quốc', 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Báo VnExpress In',
            'book_type': bt[BookType.NEWSPAPER],
            'category': cat.get('tin-tuc-hang-ngay'),
            'publisher': None,
            'description': 'Phiên bản in của báo điện tử VnExpress.',
            'price': '7000.00',
            'stock': 100,
            'isbn': '',
            'image_url': '',
            'attributes': {'publication_date': '2024-01-15', 'edition_number': '5012', 'region': 'Toàn quốc', 'language': 'Tiếng Việt'},
        },

        # ── MAGAZINE ───────────────────────────────────────────────────────
        {
            'title': 'Tạp chí Kiến Thức Ngày Nay',
            'book_type': bt[BookType.MAGAZINE],
            'category': cat.get('tap-chi-kinh-te'),
            'publisher': None,
            'description': 'Tạp chí tri thức phổ thông nổi tiếng với nhiều chủ đề đa dạng.',
            'price': '15000.00',
            'stock': 150,
            'isbn': '',
            'image_url': '',
            'attributes': {'issue_number': '1050', 'publication_date': '2024-01-01', 'frequency': 'Bán nguyệt san', 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Tạp chí Đẹp',
            'book_type': bt[BookType.MAGAZINE],
            'category': cat.get('tap-chi-thoi-trang'),
            'publisher': None,
            'description': 'Tạp chí thời trang và làm đẹp hàng đầu Việt Nam.',
            'price': '45000.00',
            'stock': 80,
            'isbn': '',
            'image_url': '',
            'attributes': {'issue_number': '215', 'publication_date': '2024-01-01', 'frequency': 'Nguyệt san', 'language': 'Tiếng Việt'},
        },
        {
            'title': 'Tạp chí Forbes Việt Nam',
            'book_type': bt[BookType.MAGAZINE],
            'category': cat.get('tap-chi-kinh-te'),
            'publisher': None,
            'description': 'Phiên bản Việt Nam của tạp chí kinh tế danh tiếng Forbes.',
            'price': '60000.00',
            'stock': 70,
            'isbn': '',
            'image_url': '',
            'attributes': {'issue_number': '133', 'publication_date': '2024-01-01', 'frequency': 'Nguyệt san', 'language': 'Tiếng Việt'},
        },

        # ── MANGA ──────────────────────────────────────────────────────────
        {
            'title': 'Thám Tử Lừng Danh Conan - Tập 1',
            'book_type': bt[BookType.MANGA],
            'category': cat.get('manga-nhat-ban'),
            'publisher': pub.get('NXB Kim Đồng'),
            'description': 'Manga trinh thám nổi tiếng của tác giả Gosho Aoyama về thám tử nhí Conan Edogawa.',
            'price': '22000.00',
            'stock': 300,
            'isbn': '',
            'image_url': 'https://salt.tikicdn.com/cache/400x400/ts/product/conan-tap-1.jpg',
            'attributes': {'volume': 1, 'artist': 'Gosho Aoyama', 'genre': 'Trinh thám', 'publisher_label': 'Shonen Sunday'},
        },
        {
            'title': 'One Piece - Tập 1: Tôi Sẽ Trở Thành Vua Hải Tặc!',
            'book_type': bt[BookType.MANGA],
            'category': cat.get('manga-nhat-ban'),
            'publisher': pub.get('NXB Kim Đồng'),
            'description': 'Tập đầu tiên của bộ manga huyền thoại One Piece của tác giả Eiichiro Oda.',
            'price': '22000.00',
            'stock': 250,
            'isbn': '',
            'image_url': '',
            'attributes': {'volume': 1, 'artist': 'Eiichiro Oda', 'genre': 'Phiêu lưu/Hài', 'publisher_label': 'Weekly Shonen Jump'},
        },
        {
            'title': 'Naruto - Tập 1: Uzumaki Naruto',
            'book_type': bt[BookType.MANGA],
            'category': cat.get('manga-nhat-ban'),
            'publisher': pub.get('NXB Kim Đồng'),
            'description': 'Tập đầu tiên của bộ manga ninja huyền thoại Naruto của tác giả Masashi Kishimoto.',
            'price': '22000.00',
            'stock': 220,
            'isbn': '',
            'image_url': '',
            'attributes': {'volume': 1, 'artist': 'Masashi Kishimoto', 'genre': 'Hành động/Phiêu lưu', 'publisher_label': 'Weekly Shonen Jump'},
        },

        # ── SCIENCE ────────────────────────────────────────────────────────
        {
            'title': 'Lược Sử Thời Gian',
            'book_type': bt[BookType.SCIENCE],
            'category': cat.get('khoa-hoc-tu-nhien'),
            'publisher': pub.get('NXB Trẻ'),
            'description': 'Tác phẩm nổi tiếng của Stephen Hawking giải thích những khám phá lớn trong vật lý và vũ trụ học.',
            'price': '95000.00',
            'stock': 90,
            'isbn': '',
            'image_url': 'https://salt.tikicdn.com/cache/400x400/ts/product/luoc-su-thoi-gian.jpg',
            'attributes': {'field': 'Vật lý/Vũ trụ học', 'level': 'Phổ thông', 'edition': '2nd', 'language': 'Tiếng Việt (bản dịch)'},
        },
        {
            'title': 'Vũ Trụ Trong Vỏ Hạt Dẻ',
            'book_type': bt[BookType.SCIENCE],
            'category': cat.get('khoa-hoc-tu-nhien'),
            'publisher': pub.get('NXB Trẻ'),
            'description': 'Cuốn sách thứ hai của Stephen Hawking khám phá các lý thuyết vũ trụ học hiện đại.',
            'price': '105000.00',
            'stock': 75,
            'isbn': '',
            'image_url': '',
            'attributes': {'field': 'Vật lý lý thuyết', 'level': 'Phổ thông nâng cao', 'edition': '1st', 'language': 'Tiếng Việt (bản dịch)'},
        },
        {
            'title': 'Sapiens: Lược Sử Loài Người',
            'book_type': bt[BookType.SCIENCE],
            'category': cat.get('khoa-hoc-tu-nhien'),
            'publisher': pub.get('NXB Trẻ'),
            'description': 'Tác phẩm của Yuval Noah Harari khám phá lịch sử tiến hóa và phát triển của loài người.',
            'price': '120000.00',
            'stock': 110,
            'isbn': '',
            'image_url': '',
            'attributes': {'field': 'Nhân chủng học/Lịch sử', 'level': 'Phổ thông', 'edition': '1st', 'language': 'Tiếng Việt (bản dịch)'},
        },

        # ── SELF HELP ──────────────────────────────────────────────────────
        {
            'title': 'Đắc Nhân Tâm',
            'book_type': bt[BookType.SELF_HELP],
            'category': cat.get('ky-nang-song'),
            'publisher': pub.get('First News'),
            'description': 'Cuốn sách kinh điển về kỹ năng giao tiếp và ứng xử của Dale Carnegie.',
            'price': '88000.00',
            'stock': 200,
            'isbn': '',
            'image_url': 'https://salt.tikicdn.com/cache/400x400/ts/product/dac-nhan-tam.jpg',
            'attributes': {'topic': 'Kỹ năng giao tiếp', 'target_audience': 'Người trưởng thành', 'language': 'Tiếng Việt (bản dịch)'},
        },
        {
            'title': 'Nhà Giả Kim',
            'book_type': bt[BookType.SELF_HELP],
            'category': cat.get('ky-nang-song'),
            'publisher': pub.get('NXB Hội Nhà Văn'),
            'description': 'Tác phẩm triết học nổi tiếng của Paulo Coelho về hành trình theo đuổi ước mơ.',
            'price': '79000.00',
            'stock': 180,
            'isbn': '',
            'image_url': '',
            'attributes': {'topic': 'Phát triển bản thân/Triết học', 'target_audience': 'Mọi lứa tuổi', 'language': 'Tiếng Việt (bản dịch)'},
        },
        {
            'title': 'Nghĩ Giàu Làm Giàu',
            'book_type': bt[BookType.SELF_HELP],
            'category': cat.get('ky-nang-song'),
            'publisher': pub.get('First News'),
            'description': 'Cuốn sách kinh điển của Napoleon Hill về tư duy làm giàu và thành công.',
            'price': '92000.00',
            'stock': 160,
            'isbn': '',
            'image_url': '',
            'attributes': {'topic': 'Tài chính/Thành công', 'target_audience': 'Người trưởng thành', 'language': 'Tiếng Việt (bản dịch)'},
        },

        # ── DICTIONARY ─────────────────────────────────────────────────────
        {
            'title': 'Từ Điển Anh - Việt',
            'book_type': bt[BookType.DICTIONARY],
            'category': cat.get('ngoai-ngu'),
            'publisher': pub.get('NXB Khoa Học Kỹ Thuật'),
            'description': 'Từ điển Anh-Việt toàn diện với hơn 100.000 mục từ và cụm từ.',
            'price': '145000.00',
            'stock': 250,
            'isbn': '',
            'image_url': '',
            'attributes': {'language_pair': 'Anh-Việt', 'edition': '3rd', 'entries_count': 100000},
        },
        {
            'title': 'Từ Điển Việt - Anh',
            'book_type': bt[BookType.DICTIONARY],
            'category': cat.get('ngoai-ngu'),
            'publisher': pub.get('NXB Khoa Học Kỹ Thuật'),
            'description': 'Từ điển Việt-Anh với hơn 80.000 mục từ, thành ngữ và tục ngữ.',
            'price': '135000.00',
            'stock': 200,
            'isbn': '',
            'image_url': '',
            'attributes': {'language_pair': 'Việt-Anh', 'edition': '2nd', 'entries_count': 80000},
        },
        {
            'title': 'Từ Điển Toán Học Anh - Việt',
            'book_type': bt[BookType.DICTIONARY],
            'category': cat.get('ngoai-ngu'),
            'publisher': pub.get('NXB Giáo Dục Việt Nam'),
            'description': 'Từ điển chuyên ngành Toán học Anh-Việt dành cho học sinh, sinh viên và nhà nghiên cứu.',
            'price': '75000.00',
            'stock': 120,
            'isbn': '',
            'image_url': '',
            'attributes': {'language_pair': 'Anh-Việt (Toán học)', 'edition': '1st', 'entries_count': 25000},
        },

        # ── CHILDREN ───────────────────────────────────────────────────────
        {
            'title': 'Hoàng Tử Bé',
            'book_type': bt[BookType.CHILDREN],
            'category': cat.get('thieu-nhi'),
            'publisher': pub.get('NXB Kim Đồng'),
            'description': 'Truyện cổ tích nổi tiếng thế giới của Antoine de Saint-Exupéry về chú hoàng tử nhỏ.',
            'price': '48000.00',
            'stock': 300,
            'isbn': '',
            'image_url': 'https://salt.tikicdn.com/cache/400x400/ts/product/hoang-tu-be.jpg',
            'attributes': {'age_range': '6-12 tuổi', 'illustrations': True, 'language': 'Tiếng Việt (bản dịch)'},
        },
        {
            'title': 'Pinocchio',
            'book_type': bt[BookType.CHILDREN],
            'category': cat.get('thieu-nhi'),
            'publisher': pub.get('NXB Kim Đồng'),
            'description': 'Truyện cổ tích kinh điển của Carlo Collodi về chú bé gỗ Pinocchio.',
            'price': '42000.00',
            'stock': 250,
            'isbn': '',
            'image_url': '',
            'attributes': {'age_range': '4-10 tuổi', 'illustrations': True, 'language': 'Tiếng Việt (bản dịch)'},
        },
        {
            'title': 'Alice Lạc Vào Xứ Sở Thần Tiên',
            'book_type': bt[BookType.CHILDREN],
            'category': cat.get('thieu-nhi'),
            'publisher': pub.get('NXB Kim Đồng'),
            'description': 'Tác phẩm kinh điển của Lewis Carroll về cuộc phiêu lưu kỳ diệu của cô bé Alice.',
            'price': '50000.00',
            'stock': 200,
            'isbn': '',
            'image_url': '',
            'attributes': {'age_range': '7-14 tuổi', 'illustrations': True, 'language': 'Tiếng Việt (bản dịch)'},
        },

        # ── EBOOK ──────────────────────────────────────────────────────────
        {
            'title': 'Clean Code (eBook)',
            'book_type': bt[BookType.EBOOK],
            'category': cat.get('cong-nghe-thong-tin'),
            'publisher': pub.get('NXB Khoa Học Kỹ Thuật'),
            'description': 'Phiên bản eBook của cuốn sách Clean Code của Robert C. Martin về cách viết code sạch.',
            'price': '75000.00',
            'stock': 9999,
            'isbn': '',
            'image_url': '',
            'attributes': {'file_format': 'PDF', 'file_size_mb': 5.2, 'drm_protected': False, 'language': 'Tiếng Anh'},
        },
        {
            'title': 'Design Patterns (eBook)',
            'book_type': bt[BookType.EBOOK],
            'category': cat.get('cong-nghe-thong-tin'),
            'publisher': pub.get('NXB Khoa Học Kỹ Thuật'),
            'description': 'Phiên bản eBook của cuốn sách Design Patterns của Gang of Four.',
            'price': '80000.00',
            'stock': 9999,
            'isbn': '',
            'image_url': '',
            'attributes': {'file_format': 'EPUB', 'file_size_mb': 3.8, 'drm_protected': False, 'language': 'Tiếng Anh'},
        },
        {
            'title': 'Python Crash Course (eBook)',
            'book_type': bt[BookType.EBOOK],
            'category': cat.get('cong-nghe-thong-tin'),
            'publisher': pub.get('NXB Khoa Học Kỹ Thuật'),
            'description': 'Phiên bản eBook hướng dẫn lập trình Python cho người mới bắt đầu.',
            'price': '65000.00',
            'stock': 9999,
            'isbn': '',
            'image_url': '',
            'attributes': {'file_format': 'PDF', 'file_size_mb': 8.1, 'drm_protected': False, 'language': 'Tiếng Anh'},
        },

        # ── AUDIOBOOK ──────────────────────────────────────────────────────
        {
            'title': 'Đắc Nhân Tâm - Audiobook',
            'book_type': bt[BookType.AUDIOBOOK],
            'category': cat.get('ky-nang-song'),
            'publisher': pub.get('First News'),
            'description': 'Phiên bản audio của cuốn sách Đắc Nhân Tâm, được đọc bởi diễn viên chuyên nghiệp.',
            'price': '55000.00',
            'stock': 9999,
            'isbn': '',
            'image_url': '',
            'attributes': {'duration_hours': 8.5, 'narrator': 'Nguyễn Văn A', 'file_format': 'MP3', 'language': 'Tiếng Việt'},
        },
        {
            'title': 'The 7 Habits of Highly Effective People - Audiobook',
            'book_type': bt[BookType.AUDIOBOOK],
            'category': cat.get('ky-nang-song'),
            'publisher': pub.get('Alphabooks'),
            'description': 'Phiên bản audio của cuốn sách 7 thói quen của người thành đạt của Stephen Covey.',
            'price': '60000.00',
            'stock': 9999,
            'isbn': '',
            'image_url': '',
            'attributes': {'duration_hours': 13.0, 'narrator': 'Stephen R. Covey', 'file_format': 'MP3', 'language': 'Tiếng Anh'},
        },

        # ── ENCYCLOPEDIA ───────────────────────────────────────────────────
        {
            'title': 'Bách Khoa Toàn Thư Việt Nam',
            'book_type': bt[BookType.ENCYCLOPEDIA],
            'category': None,
            'publisher': pub.get('NXB Giáo Dục Việt Nam'),
            'description': 'Bộ bách khoa toàn thư đầu tiên và toàn diện nhất về Việt Nam, bao gồm nhiều lĩnh vực.',
            'price': '850000.00',
            'stock': 30,
            'isbn': '',
            'image_url': '',
            'attributes': {'volumes': 4, 'topics_covered': 'Lịch sử, Địa lý, Văn hóa, Khoa học', 'language': 'Tiếng Việt', 'edition': '1st'},
        },
        {
            'title': 'Encyclopedia Britannica (Bản Tiếng Anh)',
            'book_type': bt[BookType.ENCYCLOPEDIA],
            'category': None,
            'publisher': pub.get('NXB Thế Giới'),
            'description': 'Phiên bản rút gọn của bộ bách khoa toàn thư Britannica nổi tiếng thế giới.',
            'price': '1200000.00',
            'stock': 15,
            'isbn': '',
            'image_url': '',
            'attributes': {'volumes': 2, 'topics_covered': 'Science, History, Arts, Geography, Technology', 'language': 'Tiếng Anh', 'edition': '15th'},
        },
    ]


class Command(BaseCommand):
    help = 'Seed the database with initial book data for all 12 book types'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Starting seed process...'))

        with transaction.atomic():
            publishers = self._seed_publishers()
            categories = self._seed_categories()
            book_types = self._seed_book_types()
            self._seed_books(publishers, categories, book_types)

        self.stdout.write(self.style.SUCCESS('Seed completed successfully!'))

    def _seed_book_types(self):
        self.stdout.write('  Seeding book types...')
        book_types = []
        for bt_def in BOOK_TYPE_DEFINITIONS:
            obj, created = BookTypeModel.objects.get_or_create(
                type_key=bt_def['type_key'],
                defaults={
                    'name': bt_def['name'],
                    'name_vi': bt_def['name_vi'],
                    'description': bt_def['description'],
                    'icon': bt_def['icon'],
                    'attribute_schema': bt_def['attribute_schema'],
                }
            )
            if created:
                self.stdout.write(f'    Created book type: {obj.name_vi}')
            else:
                obj.name = bt_def['name']
                obj.name_vi = bt_def['name_vi']
                obj.description = bt_def['description']
                obj.icon = bt_def['icon']
                obj.attribute_schema = bt_def['attribute_schema']
                obj.save()
            book_types.append(obj)
        self.stdout.write(f'  Book types: {len(book_types)} records')
        return book_types

    def _seed_publishers(self):
        self.stdout.write('  Seeding publishers...')
        publishers = []
        for pub_def in PUBLISHER_DEFINITIONS:
            obj, created = PublisherModel.objects.get_or_create(
                name=pub_def['name'],
                defaults={
                    'email': pub_def['email'],
                    'phone': pub_def['phone'],
                    'address': pub_def['address'],
                    'website': pub_def['website'],
                }
            )
            if created:
                self.stdout.write(f'    Created publisher: {obj.name}')
            publishers.append(obj)
        self.stdout.write(f'  Publishers: {len(publishers)} records')
        return publishers

    def _seed_categories(self):
        self.stdout.write('  Seeding categories...')
        categories = []
        for cat_def in CATEGORY_DEFINITIONS:
            obj, created = CategoryModel.objects.get_or_create(
                slug=cat_def['slug'],
                defaults={
                    'name': cat_def['name'],
                    'description': cat_def['description'],
                }
            )
            if created:
                self.stdout.write(f'    Created category: {obj.name}')
            categories.append(obj)
        self.stdout.write(f'  Categories: {len(categories)} records')
        return categories

    def _seed_books(self, publishers, categories, book_types):
        self.stdout.write('  Seeding books...')
        seeds = get_book_seeds(publishers, categories, book_types)
        created_count = 0
        skipped_count = 0

        for book_def in seeds:
            existing = BookModel.objects.filter(
                title=book_def['title'],
                book_type=book_def['book_type'],
            ).first()

            if existing:
                skipped_count += 1
                continue

            BookModel.objects.create(
                title=book_def['title'],
                book_type=book_def['book_type'],
                category=book_def.get('category'),
                publisher=book_def.get('publisher'),
                description=book_def['description'],
                price=book_def['price'],
                stock=book_def['stock'],
                isbn=book_def.get('isbn', ''),
                image_url=book_def.get('image_url', ''),
                attributes=book_def.get('attributes', {}),
                is_active=True,
            )
            created_count += 1
            self.stdout.write(f'    Created book: {book_def["title"]}')

        self.stdout.write(
            f'  Books: {created_count} created, {skipped_count} skipped (already exist)'
        )
