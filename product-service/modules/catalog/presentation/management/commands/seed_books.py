from django.core.management.base import BaseCommand
from modules.catalog.infrastructure.models.book_type_model import BookTypeModel
from modules.catalog.infrastructure.models.category_model import CategoryModel
from modules.catalog.infrastructure.models.publisher_model import PublisherModel
from modules.catalog.infrastructure.models.book_model import BookModel
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Seed initial book types and sample books'

    def handle(self, *args, **options):
        self._seed_book_types()
        self._seed_publishers()
        self._seed_categories()
        self._seed_books()
        self.stdout.write(self.style.SUCCESS('Seed completed successfully.'))

    def _seed_book_types(self):
        if BookTypeModel.objects.count() >= 12:
            self.stdout.write('Book types already seeded, skipping.')
            return

        types = [
            {
                'type_key': 'fiction', 'name': 'Fiction', 'name_vi': 'Sách văn học', 'icon': '📚',
                'description': 'Tiểu thuyết, truyện ngắn, văn học',
                'attribute_schema': {'author': 'str', 'genre': 'str', 'pages': 'int', 'language': 'str', 'series': 'str'}
            },
            {
                'type_key': 'textbook', 'name': 'Textbook', 'name_vi': 'Sách giáo khoa', 'icon': '🎓',
                'description': 'Sách học sinh, sách giáo khoa các cấp',
                'attribute_schema': {'subject': 'str', 'grade_level': 'str', 'edition': 'str', 'language': 'str'}
            },
            {
                'type_key': 'newspaper', 'name': 'Newspaper', 'name_vi': 'Báo', 'icon': '📰',
                'description': 'Báo hàng ngày, báo tin tức',
                'attribute_schema': {'publication_date': 'str', 'edition_number': 'str', 'region': 'str', 'language': 'str'}
            },
            {
                'type_key': 'magazine', 'name': 'Magazine', 'name_vi': 'Tạp chí', 'icon': '📖',
                'description': 'Tạp chí chuyên đề, định kỳ',
                'attribute_schema': {'issue_number': 'str', 'publication_date': 'str', 'frequency': 'str', 'language': 'str'}
            },
            {
                'type_key': 'manga', 'name': 'Manga/Comic', 'name_vi': 'Manga/Truyện tranh', 'icon': '🎌',
                'description': 'Manga Nhật Bản, truyện tranh',
                'attribute_schema': {'volume': 'int', 'artist': 'str', 'genre': 'str', 'publisher_label': 'str'}
            },
            {
                'type_key': 'science', 'name': 'Science', 'name_vi': 'Sách khoa học', 'icon': '🔬',
                'description': 'Khoa học tự nhiên, nghiên cứu',
                'attribute_schema': {'field': 'str', 'level': 'str', 'edition': 'str', 'language': 'str'}
            },
            {
                'type_key': 'self_help', 'name': 'Self-help', 'name_vi': 'Sách kỹ năng sống', 'icon': '💡',
                'description': 'Phát triển bản thân, kỹ năng sống',
                'attribute_schema': {'topic': 'str', 'target_audience': 'str', 'language': 'str'}
            },
            {
                'type_key': 'dictionary', 'name': 'Dictionary', 'name_vi': 'Từ điển', 'icon': '📝',
                'description': 'Từ điển các ngôn ngữ và chuyên ngành',
                'attribute_schema': {'language_pair': 'str', 'edition': 'str', 'entries_count': 'int'}
            },
            {
                'type_key': 'children', 'name': "Children's Book", 'name_vi': 'Sách thiếu nhi', 'icon': '🧒',
                'description': 'Sách dành cho trẻ em và thiếu niên',
                'attribute_schema': {'age_range': 'str', 'illustrations': 'bool', 'language': 'str'}
            },
            {
                'type_key': 'ebook', 'name': 'eBook', 'name_vi': 'Sách điện tử', 'icon': '💻',
                'description': 'Sách định dạng điện tử PDF, EPUB',
                'attribute_schema': {'file_format': 'str', 'file_size_mb': 'float', 'drm_protected': 'bool', 'language': 'str'}
            },
            {
                'type_key': 'audiobook', 'name': 'Audiobook', 'name_vi': 'Sách audio', 'icon': '🎧',
                'description': 'Sách phát thanh, sách nói',
                'attribute_schema': {'duration_hours': 'float', 'narrator': 'str', 'file_format': 'str', 'language': 'str'}
            },
            {
                'type_key': 'encyclopedia', 'name': 'Encyclopedia', 'name_vi': 'Bách khoa toàn thư', 'icon': '🌐',
                'description': 'Bách khoa toàn thư, sách tra cứu',
                'attribute_schema': {'volumes': 'int', 'topics_covered': 'str', 'language': 'str', 'edition': 'str'}
            },
        ]
        for t in types:
            BookTypeModel.objects.get_or_create(type_key=t['type_key'], defaults=t)
        self.stdout.write(f'  Seeded {len(types)} book types')

    def _seed_publishers(self):
        if PublisherModel.objects.count() >= 5:
            return
        publishers = [
            {'name': 'NXB Kim Đồng', 'email': 'info@nxbkimdong.vn', 'phone': '024-3825-1234', 'website': 'https://nxbkimdong.com.vn'},
            {'name': 'NXB Trẻ', 'email': 'info@nxbtre.vn', 'phone': '028-3930-5678', 'website': 'https://nxbtre.com.vn'},
            {'name': 'NXB Giáo Dục', 'email': 'info@nxbgd.vn', 'phone': '024-3869-0101', 'website': 'https://nxbgiaoduc.vn'},
            {'name': 'NXB Thế Giới', 'email': 'info@nxbthegoi.vn', 'phone': '024-3825-9999', 'website': ''},
            {'name': 'Nhã Nam', 'email': 'info@nhanam.vn', 'phone': '024-3926-1234', 'website': 'https://nhanam.vn'},
        ]
        for p in publishers:
            PublisherModel.objects.get_or_create(name=p['name'], defaults=p)
        self.stdout.write(f'  Seeded {len(publishers)} publishers')

    def _seed_categories(self):
        if CategoryModel.objects.count() >= 5:
            return
        categories = [
            ('Văn học', None), ('Giáo dục', None), ('Báo & Tạp chí', None),
            ('Truyện tranh & Manga', None), ('Khoa học & Kỹ thuật', None),
            ('Kỹ năng sống', None), ('Từ điển & Tra cứu', None),
            ('Thiếu nhi', None), ('Sách điện tử', None), ('Bách khoa', None),
        ]
        for name, parent in categories:
            slug = slugify(name, allow_unicode=True)
            CategoryModel.objects.get_or_create(slug=slug, defaults={'name': name, 'description': ''})
        self.stdout.write(f'  Seeded {len(categories)} categories')

    def _seed_books(self):
        if BookModel.objects.count() >= 38:
            self.stdout.write('Books already seeded, skipping.')
            return

        def get_type(key):
            return BookTypeModel.objects.get(type_key=key)

        def get_pub(name):
            return PublisherModel.objects.filter(name__icontains=name).first()

        def get_cat(name):
            return CategoryModel.objects.filter(name__icontains=name).first()

        books_data = [
            # Fiction
            {'title': 'Dế Mèn Phiêu Lưu Ký', 'book_type': get_type('fiction'), 'price': 65000, 'stock': 150,
             'author': 'Tô Hoài',
             'description': 'Tác phẩm nổi tiếng của nhà văn Tô Hoài về cuộc phiêu lưu của chú dế dũng cảm qua nhiều vùng đất kỳ thú.',
             'isbn': '978-604-2-15678-1', 'category': get_cat('Văn học'), 'publisher': get_pub('Kim Đồng'),
             'attributes': {'genre': 'Thiếu nhi', 'pages': 192, 'language': 'Tiếng Việt'}},
            {'title': 'Số Đỏ', 'book_type': get_type('fiction'), 'price': 72000, 'stock': 80,
             'author': 'Vũ Trọng Phụng',
             'description': 'Tiểu thuyết trào phúng kiệt tác, phản ánh xã hội Việt Nam thời Pháp thuộc với hình tượng Xuân Tóc Đỏ.',
             'isbn': '978-604-2-15679-2', 'category': get_cat('Văn học'), 'publisher': get_pub('Trẻ'),
             'attributes': {'genre': 'Văn học hiện thực', 'pages': 268, 'language': 'Tiếng Việt'}},
            {'title': 'Chí Phèo', 'book_type': get_type('fiction'), 'price': 45000, 'stock': 120,
             'author': 'Nam Cao',
             'description': 'Truyện ngắn hiện thực phê phán về số phận bi thảm của người nông dân trong xã hội cũ.',
             'isbn': '978-604-2-15680-3', 'category': get_cat('Văn học'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'genre': 'Văn học hiện thực', 'pages': 128, 'language': 'Tiếng Việt'}},
            {'title': 'Cho Tôi Xin Một Vé Đi Tuổi Thơ', 'book_type': get_type('fiction'), 'price': 55000, 'stock': 200,
             'author': 'Nguyễn Nhật Ánh',
             'description': 'Cuốn sách đưa người đọc trở về thế giới tuổi thơ đầy ắp kỷ niệm và mộng mơ.',
             'isbn': '978-604-2-15681-4', 'category': get_cat('Văn học'), 'publisher': get_pub('Trẻ'),
             'attributes': {'genre': 'Văn học thiếu nhi', 'pages': 218, 'language': 'Tiếng Việt'}},
            {'title': 'Mắt Biếc', 'book_type': get_type('fiction'), 'price': 68000, 'stock': 180,
             'author': 'Nguyễn Nhật Ánh',
             'description': 'Câu chuyện tình yêu đầu đời trong sáng, buồn man mác của Ngạn và Hà Lan.',
             'isbn': '978-604-2-15682-5', 'category': get_cat('Văn học'), 'publisher': get_pub('Trẻ'),
             'attributes': {'genre': 'Văn học lãng mạn', 'pages': 296, 'language': 'Tiếng Việt'}},
            # Textbook
            {'title': 'Toán 12 - Tập 1', 'book_type': get_type('textbook'), 'price': 38000, 'stock': 500,
             'author': 'Bộ Giáo Dục và Đào Tạo',
             'description': 'Sách giáo khoa Toán lớp 12 tập 1 theo chương trình mới của Bộ GD&ĐT.',
             'isbn': '978-604-0-34561-4', 'category': get_cat('Giáo dục'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'subject': 'Toán học', 'grade_level': 'Lớp 12', 'edition': '2024', 'language': 'Tiếng Việt'}},
            {'title': 'Vật Lý 11', 'book_type': get_type('textbook'), 'price': 35000, 'stock': 400,
             'author': 'Bộ Giáo Dục và Đào Tạo',
             'description': 'Sách giáo khoa Vật lý lớp 11 với các kiến thức cơ bản về cơ học, nhiệt học, quang học.',
             'isbn': '978-604-0-34562-5', 'category': get_cat('Giáo dục'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'subject': 'Vật lý', 'grade_level': 'Lớp 11', 'edition': '2024', 'language': 'Tiếng Việt'}},
            {'title': 'Ngữ Văn 10 - Tập 1', 'book_type': get_type('textbook'), 'price': 32000, 'stock': 600,
             'author': 'Bộ Giáo Dục và Đào Tạo',
             'description': 'Sách giáo khoa Ngữ Văn lớp 10 tập 1 với các tác phẩm văn học tiêu biểu.',
             'isbn': '978-604-0-34563-6', 'category': get_cat('Giáo dục'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'subject': 'Ngữ văn', 'grade_level': 'Lớp 10', 'edition': '2024', 'language': 'Tiếng Việt'}},
            # Newspaper
            {'title': 'Báo Tuổi Trẻ - Số Cuối Tuần', 'book_type': get_type('newspaper'), 'price': 8000, 'stock': 200,
             'author': 'Tòa soạn Báo Tuổi Trẻ',
             'description': 'Báo Tuổi Trẻ ấn bản cuối tuần với nhiều chuyên mục đặc sắc về xã hội, kinh tế, giải trí.',
             'isbn': '', 'category': get_cat('Báo'), 'publisher': get_pub('Trẻ'),
             'attributes': {'publication_date': '2024-01-06', 'edition_number': 'Số 1/2024', 'region': 'TP.HCM', 'language': 'Tiếng Việt'}},
            {'title': 'Báo Thanh Niên', 'book_type': get_type('newspaper'), 'price': 6000, 'stock': 200,
             'author': 'Tòa soạn Báo Thanh Niên',
             'description': 'Nhật báo Thanh Niên - tiếng nói của giới trẻ Việt Nam.',
             'isbn': '', 'category': get_cat('Báo'), 'publisher': None,
             'attributes': {'publication_date': '2024-01-06', 'edition_number': 'Số 6/1', 'region': 'Toàn quốc', 'language': 'Tiếng Việt'}},
            # Magazine
            {'title': 'Tạp Chí Kiến Thức Ngày Nay', 'book_type': get_type('magazine'), 'price': 22000, 'stock': 100,
             'author': 'Ban biên tập KTNN',
             'description': 'Tạp chí khoa học phổ thông hàng đầu Việt Nam với các bài viết về khoa học, lịch sử, địa lý.',
             'isbn': '', 'category': get_cat('Báo'), 'publisher': None,
             'attributes': {'issue_number': 'Số 850', 'publication_date': '2024-01-01', 'frequency': 'Nửa tháng', 'language': 'Tiếng Việt'}},
            {'title': 'Forbes Việt Nam', 'book_type': get_type('magazine'), 'price': 65000, 'stock': 50,
             'author': 'Forbes Media',
             'description': 'Tạp chí kinh tế Forbes ấn bản tiếng Việt, cập nhật xu hướng kinh doanh và danh sách tỷ phú.',
             'isbn': '', 'category': get_cat('Báo'), 'publisher': None,
             'attributes': {'issue_number': 'Số 125', 'publication_date': '2024-01-01', 'frequency': 'Hàng tháng', 'language': 'Tiếng Việt'}},
            # Manga
            {'title': 'Thám Tử Lừng Danh Conan - Tập 1', 'book_type': get_type('manga'), 'price': 28000, 'stock': 300,
             'author': 'Gosho Aoyama',
             'description': 'Manga trinh thám nổi tiếng: thám tử nhí Conan phá các vụ án bí ẩn.',
             'isbn': '978-604-2-98765-1', 'category': get_cat('Truyện tranh'), 'publisher': get_pub('Kim Đồng'),
             'attributes': {'volume': 1, 'genre': 'Trinh thám', 'publisher_label': 'Shogakukan'}},
            {'title': 'One Piece - Tập 1', 'book_type': get_type('manga'), 'price': 28000, 'stock': 250,
             'author': 'Eiichiro Oda',
             'description': 'Hành trình của Monkey D. Luffy và băng hải tặc Mũ Rơm trở thành Vua Hải Tặc.',
             'isbn': '978-604-2-98766-2', 'category': get_cat('Truyện tranh'), 'publisher': get_pub('Kim Đồng'),
             'attributes': {'volume': 1, 'genre': 'Phiêu lưu', 'publisher_label': 'Shueisha'}},
            {'title': 'Naruto - Tập 1', 'book_type': get_type('manga'), 'price': 25000, 'stock': 220,
             'author': 'Masashi Kishimoto',
             'description': 'Câu chuyện về ninja Naruto Uzumaki và hành trình trở thành Hokage.',
             'isbn': '978-604-2-98767-3', 'category': get_cat('Truyện tranh'), 'publisher': get_pub('Kim Đồng'),
             'attributes': {'volume': 1, 'genre': 'Hành động', 'publisher_label': 'Shueisha'}},
            {'title': 'Doraemon - Tập 1', 'book_type': get_type('manga'), 'price': 22000, 'stock': 350,
             'author': 'Fujiko F. Fujio',
             'description': 'Chú mèo máy Doraemon đến từ tương lai giúp đỡ cậu bé Nobita bằng những vật dụng kỳ diệu.',
             'isbn': '978-604-2-98768-4', 'category': get_cat('Truyện tranh'), 'publisher': get_pub('Kim Đồng'),
             'attributes': {'volume': 1, 'genre': 'Hài hước', 'publisher_label': 'Shogakukan'}},
            # Science
            {'title': 'Lược Sử Thời Gian', 'book_type': get_type('science'), 'price': 120000, 'stock': 80,
             'author': 'Stephen Hawking',
             'description': 'Cuốn sách khoa học kinh điển về nguồn gốc và số phận của vũ trụ.',
             'isbn': '978-604-2-56789-1', 'category': get_cat('Khoa học'), 'publisher': get_pub('Nhã Nam'),
             'attributes': {'field': 'Vật lý thiên văn', 'level': 'Phổ thông', 'edition': '3', 'language': 'Tiếng Việt'}},
            {'title': 'Sapiens: Lược Sử Loài Người', 'book_type': get_type('science'), 'price': 189000, 'stock': 150,
             'author': 'Yuval Noah Harari',
             'description': 'Cuốn sách kể lại lịch sử toàn diện của loài người từ thời tiền sử đến hiện đại.',
             'isbn': '978-604-2-56790-2', 'category': get_cat('Khoa học'), 'publisher': get_pub('Thế Giới'),
             'attributes': {'field': 'Lịch sử, Nhân học', 'level': 'Phổ thông', 'edition': '2', 'language': 'Tiếng Việt'}},
            # Self-help
            {'title': 'Đắc Nhân Tâm', 'book_type': get_type('self_help'), 'price': 88000, 'stock': 500,
             'author': 'Dale Carnegie',
             'description': 'Cuốn sách kỹ năng giao tiếp và ứng xử bán chạy nhất mọi thời đại.',
             'isbn': '978-604-2-11111-1', 'category': get_cat('Kỹ năng'), 'publisher': get_pub('Trẻ'),
             'attributes': {'topic': 'Kỹ năng giao tiếp', 'target_audience': 'Người đi làm', 'language': 'Tiếng Việt'}},
            {'title': 'Nhà Giả Kim', 'book_type': get_type('self_help'), 'price': 79000, 'stock': 400,
             'author': 'Paulo Coelho',
             'description': 'Tiểu thuyết triết học về chàng trai người Tây Ban Nha theo đuổi giấc mơ của mình.',
             'isbn': '978-604-2-11112-2', 'category': get_cat('Kỹ năng'), 'publisher': get_pub('Nhã Nam'),
             'attributes': {'topic': 'Phát triển bản thân', 'target_audience': 'Mọi lứa tuổi', 'language': 'Tiếng Việt'}},
            {'title': 'Mindset - Tư Duy Thành Công', 'book_type': get_type('self_help'), 'price': 95000, 'stock': 300,
             'author': 'Carol S. Dweck',
             'description': 'Khám phá sức mạnh của tư duy phát triển và cách thay đổi tư duy để đạt thành công.',
             'isbn': '978-604-2-11113-3', 'category': get_cat('Kỹ năng'), 'publisher': get_pub('Nhã Nam'),
             'attributes': {'topic': 'Tư duy & Tâm lý', 'target_audience': 'Mọi lứa tuổi', 'language': 'Tiếng Việt'}},
            # Dictionary
            {'title': 'Từ Điển Anh-Việt Oxford', 'book_type': get_type('dictionary'), 'price': 350000, 'stock': 60,
             'author': 'Oxford University Press',
             'description': 'Từ điển Anh-Việt Oxford phiên bản cập nhật với hơn 150,000 từ và cụm từ.',
             'isbn': '978-604-2-77777-1', 'category': get_cat('Từ điển'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'language_pair': 'Anh-Việt', 'edition': '2023', 'entries_count': 150000}},
            {'title': 'Từ Điển Việt-Anh Toàn Thư', 'book_type': get_type('dictionary'), 'price': 280000, 'stock': 45,
             'author': 'Bùi Phụng',
             'description': 'Từ điển Việt-Anh đầy đủ với hơn 120,000 từ, thành ngữ và cách dùng thực tế.',
             'isbn': '978-604-2-77778-2', 'category': get_cat('Từ điển'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'language_pair': 'Việt-Anh', 'edition': '2022', 'entries_count': 120000}},
            {'title': 'Từ Điển Tiếng Việt', 'book_type': get_type('dictionary'), 'price': 195000, 'stock': 80,
             'author': 'Hoàng Phê',
             'description': 'Từ điển tiếng Việt phổ thông, giải thích nghĩa và cách dùng của hơn 40,000 từ.',
             'isbn': '978-604-2-77779-3', 'category': get_cat('Từ điển'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'language_pair': 'Việt-Việt', 'edition': '2021', 'entries_count': 40000}},
            # Children
            {'title': 'Hoàng Tử Bé', 'book_type': get_type('children'), 'price': 58000, 'stock': 200,
             'author': 'Antoine de Saint-Exupéry',
             'description': 'Tác phẩm kinh điển về tình bạn, tình yêu và những điều quan trọng trong cuộc sống.',
             'isbn': '978-604-2-33333-1', 'category': get_cat('Thiếu nhi'), 'publisher': get_pub('Nhã Nam'),
             'attributes': {'age_range': '8-12 tuổi', 'illustrations': True, 'language': 'Tiếng Việt'}},
            {'title': 'Không Gia Đình', 'book_type': get_type('children'), 'price': 75000, 'stock': 160,
             'author': 'Hector Malot',
             'description': 'Câu chuyện cảm động về cậu bé Rémi và hành trình tìm kiếm gia đình.',
             'isbn': '978-604-2-33334-2', 'category': get_cat('Thiếu nhi'), 'publisher': get_pub('Kim Đồng'),
             'attributes': {'age_range': '10-15 tuổi', 'illustrations': False, 'language': 'Tiếng Việt'}},
            {'title': 'Totto-Chan: Cô Bé Bên Cửa Sổ', 'book_type': get_type('children'), 'price': 82000, 'stock': 220,
             'author': 'Tetsuko Kuroyanagi',
             'description': 'Hồi ký tuổi thơ đầy ắp kỷ niệm về một ngôi trường đặc biệt tại Nhật Bản.',
             'isbn': '978-604-2-33335-3', 'category': get_cat('Thiếu nhi'), 'publisher': get_pub('Nhã Nam'),
             'attributes': {'age_range': '8-14 tuổi', 'illustrations': False, 'language': 'Tiếng Việt'}},
            # eBook — gán đúng category "Sách điện tử"
            {'title': 'Clean Code (eBook)', 'book_type': get_type('ebook'), 'price': 150000, 'stock': 9999,
             'author': 'Robert C. Martin',
             'description': 'Hướng dẫn viết code sạch, dễ bảo trì - bắt buộc với mọi lập trình viên.',
             'isbn': '978-0-13-235088-4', 'category': get_cat('Sách điện tử'), 'publisher': None,
             'attributes': {'file_format': 'PDF', 'file_size_mb': 8.5, 'drm_protected': False, 'language': 'English'}},
            {'title': 'Python Crash Course (eBook)', 'book_type': get_type('ebook'), 'price': 120000, 'stock': 9999,
             'author': 'Eric Matthes',
             'description': 'Hướng dẫn học Python từ căn bản đến nâng cao với các dự án thực tế.',
             'isbn': '978-1-59327-928-8', 'category': get_cat('Sách điện tử'), 'publisher': None,
             'attributes': {'file_format': 'PDF/EPUB', 'file_size_mb': 12.0, 'drm_protected': False, 'language': 'English'}},
            {'title': 'Atomic Habits (eBook)', 'book_type': get_type('ebook'), 'price': 89000, 'stock': 9999,
             'author': 'James Clear',
             'description': 'Phương pháp xây dựng thói quen tốt và loại bỏ thói quen xấu một cách khoa học.',
             'isbn': '978-0-7352-1129-2', 'category': get_cat('Sách điện tử'), 'publisher': None,
             'attributes': {'file_format': 'PDF/EPUB', 'file_size_mb': 5.2, 'drm_protected': False, 'language': 'Tiếng Việt'}},
            # Audiobook
            {'title': 'Đắc Nhân Tâm (Audio)', 'book_type': get_type('audiobook'), 'price': 99000, 'stock': 9999,
             'author': 'Dale Carnegie',
             'description': 'Phiên bản audio của Đắc Nhân Tâm do diễn viên chuyên nghiệp đọc diễn cảm.',
             'isbn': '', 'category': get_cat('Kỹ năng'), 'publisher': get_pub('Trẻ'),
             'attributes': {'duration_hours': 8.5, 'narrator': 'Minh Châu', 'file_format': 'MP3', 'language': 'Tiếng Việt'}},
            # Encyclopedia
            {'title': 'Bách Khoa Toàn Thư Việt Nam - Bộ 4 Tập', 'book_type': get_type('encyclopedia'), 'price': 1200000, 'stock': 20,
             'author': 'Hội đồng Quốc gia',
             'description': 'Bộ bách khoa toàn thư Việt Nam đầy đủ và toàn diện nhất về khoa học, lịch sử, địa lý và văn hóa.',
             'isbn': '978-604-0-99999-1', 'category': get_cat('Bách khoa'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'volumes': 4, 'topics_covered': 'Khoa học, Lịch sử, Địa lý, Văn hóa', 'language': 'Tiếng Việt', 'edition': '3'}},
            {'title': 'Bách Khoa Thế Giới Động Vật', 'book_type': get_type('encyclopedia'), 'price': 450000, 'stock': 35,
             'author': 'David Burnie',
             'description': 'Bộ bách khoa toàn thư về thế giới động vật với hơn 2,000 loài được minh họa chi tiết.',
             'isbn': '978-604-0-99998-2', 'category': get_cat('Bách khoa'), 'publisher': get_pub('Thế Giới'),
             'attributes': {'volumes': 1, 'topics_covered': 'Động vật, Sinh học', 'language': 'Tiếng Việt', 'edition': '2'}},
            {'title': 'Bách Khoa Toàn Thư Khoa Học', 'book_type': get_type('encyclopedia'), 'price': 320000, 'stock': 40,
             'author': 'DK Publishing',
             'description': 'Bách khoa toàn thư khoa học với hình ảnh sinh động, phù hợp cho học sinh và gia đình.',
             'isbn': '978-604-0-99997-3', 'category': get_cat('Bách khoa'), 'publisher': get_pub('Giáo Dục'),
             'attributes': {'volumes': 1, 'topics_covered': 'Khoa học tự nhiên', 'language': 'Tiếng Việt', 'edition': '1'}},
        ]

        count = 0
        updated = 0
        for data in books_data:
            existing = BookModel.objects.filter(title=data['title']).first()
            if existing:
                # Update author and description if empty
                changed = False
                if not existing.author and data.get('author'):
                    existing.author = data['author']
                    changed = True
                if not existing.description and data.get('description'):
                    existing.description = data['description']
                    changed = True
                if changed:
                    existing.save()
                    updated += 1
            else:
                try:
                    BookModel.objects.create(**data)
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Skip {data['title']}: {e}"))
        self.stdout.write(f'  Seeded {count} new books, updated {updated} existing books')
