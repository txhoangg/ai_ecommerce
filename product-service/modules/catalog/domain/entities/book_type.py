from dataclasses import dataclass, field
from typing import Dict, Any


class BookType:
    FICTION = 'fiction'
    TEXTBOOK = 'textbook'
    NEWSPAPER = 'newspaper'
    MAGAZINE = 'magazine'
    MANGA = 'manga'
    SCIENCE = 'science'
    SELF_HELP = 'self_help'
    DICTIONARY = 'dictionary'
    CHILDREN = 'children'
    EBOOK = 'ebook'
    AUDIOBOOK = 'audiobook'
    ENCYCLOPEDIA = 'encyclopedia'

    ALL_TYPES = [
        FICTION, TEXTBOOK, NEWSPAPER, MAGAZINE, MANGA,
        SCIENCE, SELF_HELP, DICTIONARY, CHILDREN,
        EBOOK, AUDIOBOOK, ENCYCLOPEDIA,
    ]

    NAMES_VI = {
        FICTION: 'Sách văn học',
        TEXTBOOK: 'Sách giáo khoa',
        NEWSPAPER: 'Báo',
        MAGAZINE: 'Tạp chí',
        MANGA: 'Manga/Truyện tranh',
        SCIENCE: 'Sách khoa học',
        SELF_HELP: 'Sách kỹ năng sống',
        DICTIONARY: 'Từ điển',
        CHILDREN: 'Sách thiếu nhi',
        EBOOK: 'eBook',
        AUDIOBOOK: 'Sách audio',
        ENCYCLOPEDIA: 'Bách khoa toàn thư',
    }

    ICONS = {
        FICTION: '📚',
        TEXTBOOK: '📖',
        NEWSPAPER: '📰',
        MAGAZINE: '📄',
        MANGA: '🎌',
        SCIENCE: '🔬',
        SELF_HELP: '💡',
        DICTIONARY: '📘',
        CHILDREN: '🧸',
        EBOOK: '💻',
        AUDIOBOOK: '🎧',
        ENCYCLOPEDIA: '🌍',
    }

    ATTRIBUTE_SCHEMAS: Dict[str, Dict[str, Any]] = {
        FICTION: {
            'author': {'type': 'string', 'required': True, 'label': 'Tác giả'},
            'genre': {'type': 'string', 'required': False, 'label': 'Thể loại'},
            'pages': {'type': 'integer', 'required': False, 'label': 'Số trang'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
            'series': {'type': 'string', 'required': False, 'label': 'Series'},
        },
        TEXTBOOK: {
            'subject': {'type': 'string', 'required': True, 'label': 'Môn học'},
            'grade_level': {'type': 'string', 'required': True, 'label': 'Lớp/Cấp'},
            'edition': {'type': 'string', 'required': False, 'label': 'Phiên bản'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
        },
        NEWSPAPER: {
            'publication_date': {'type': 'string', 'required': True, 'label': 'Ngày xuất bản'},
            'edition_number': {'type': 'string', 'required': False, 'label': 'Số ấn bản'},
            'region': {'type': 'string', 'required': False, 'label': 'Khu vực'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
        },
        MAGAZINE: {
            'issue_number': {'type': 'string', 'required': True, 'label': 'Số phát hành'},
            'publication_date': {'type': 'string', 'required': False, 'label': 'Ngày phát hành'},
            'frequency': {'type': 'string', 'required': False, 'label': 'Tần suất'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
        },
        MANGA: {
            'volume': {'type': 'integer', 'required': False, 'label': 'Tập'},
            'artist': {'type': 'string', 'required': True, 'label': 'Họa sĩ'},
            'genre': {'type': 'string', 'required': False, 'label': 'Thể loại'},
            'publisher_label': {'type': 'string', 'required': False, 'label': 'Nhãn xuất bản'},
        },
        SCIENCE: {
            'field': {'type': 'string', 'required': True, 'label': 'Lĩnh vực'},
            'level': {'type': 'string', 'required': False, 'label': 'Cấp độ'},
            'edition': {'type': 'string', 'required': False, 'label': 'Phiên bản'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
        },
        SELF_HELP: {
            'topic': {'type': 'string', 'required': True, 'label': 'Chủ đề'},
            'target_audience': {'type': 'string', 'required': False, 'label': 'Đối tượng'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
        },
        DICTIONARY: {
            'language_pair': {'type': 'string', 'required': True, 'label': 'Cặp ngôn ngữ'},
            'edition': {'type': 'string', 'required': False, 'label': 'Phiên bản'},
            'entries_count': {'type': 'integer', 'required': False, 'label': 'Số từ mục'},
        },
        CHILDREN: {
            'age_range': {'type': 'string', 'required': True, 'label': 'Độ tuổi'},
            'illustrations': {'type': 'boolean', 'required': False, 'label': 'Có hình minh họa'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
        },
        EBOOK: {
            'file_format': {'type': 'string', 'required': True, 'label': 'Định dạng file'},
            'file_size_mb': {'type': 'float', 'required': False, 'label': 'Dung lượng (MB)'},
            'drm_protected': {'type': 'boolean', 'required': False, 'label': 'Bảo vệ DRM'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
        },
        AUDIOBOOK: {
            'duration_hours': {'type': 'float', 'required': True, 'label': 'Thời lượng (giờ)'},
            'narrator': {'type': 'string', 'required': False, 'label': 'Người đọc'},
            'file_format': {'type': 'string', 'required': False, 'label': 'Định dạng'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
        },
        ENCYCLOPEDIA: {
            'volumes': {'type': 'integer', 'required': False, 'label': 'Số tập'},
            'topics_covered': {'type': 'string', 'required': False, 'label': 'Chủ đề bao gồm'},
            'language': {'type': 'string', 'required': False, 'label': 'Ngôn ngữ'},
            'edition': {'type': 'string', 'required': False, 'label': 'Phiên bản'},
        },
    }

    @classmethod
    def get_attribute_schema(cls, type_key: str) -> Dict[str, Any]:
        return cls.ATTRIBUTE_SCHEMAS.get(type_key, {})

    @classmethod
    def is_valid_type(cls, type_key: str) -> bool:
        return type_key in cls.ALL_TYPES

    @classmethod
    def get_name_vi(cls, type_key: str) -> str:
        return cls.NAMES_VI.get(type_key, type_key)

    @classmethod
    def get_icon(cls, type_key: str) -> str:
        return cls.ICONS.get(type_key, '')
