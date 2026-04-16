# AI-ECOMMERCE Bookstore

Hệ thống bookstore/e-commerce theo kiến trúc microservices, trong đó `product-service` quản lý catalog sách và `ai-service` cung cấp recommendation, knowledge base, RAG chat và phân tích hành vi người dùng.

Phiên bản hiện tại của dự án tập trung vào kiến trúc đang được sử dụng để triển khai và demo, với `product-service` là trung tâm dữ liệu sản phẩm và `ai-service` là thành phần mở rộng cho các tính năng AI.

## 1. Tổng quan hệ thống

Dự án gồm 2 nhóm thành phần chính:

- Nghiệp vụ e-commerce:
  - `api-gateway`
  - `staff-service`
  - `manager-service`
  - `customer-service`
  - `cart-service`
  - `order-service`
  - `ship-service`
  - `pay-service`
  - `comment-rate-service`
  - `product-service`
- AI:
  - `ai-service`
- Hạ tầng:
  - `MySQL`
  - `PostgreSQL`
  - `RabbitMQ`
  - `Neo4j`

Luồng tổng quát:

- Người dùng thao tác trên giao diện `api-gateway`.
- Gateway gọi sang các microservice nghiệp vụ qua HTTP.
- `product-service` là nguồn dữ liệu sách trung tâm.
- `ai-service` đồng bộ dữ liệu từ `product-service`, tạo vector index, knowledge base, recommendation và chatbot.
- `order-service` phối hợp với `pay-service` và `ship-service` qua `RabbitMQ`.

## 2. Kiến trúc service

### Các service đang hoạt động

| Service | Port | Vai trò |
|---|---:|---|
| `api-gateway` | `8000` | Giao diện web Django, quản lý session, gọi các service backend |
| `staff-service` | `8001` | Đăng nhập staff, thông tin nhân viên |
| `manager-service` | `8002` | Báo cáo, dashboard manager |
| `customer-service` | `8003` | Đăng ký/đăng nhập khách hàng |
| `cart-service` | `8006` | Giỏ hàng |
| `order-service` | `8007` | Đơn hàng, saga với payment/shipping |
| `ship-service` | `8008` | Vận chuyển |
| `pay-service` | `8009` | Thanh toán |
| `comment-rate-service` | `8010` | Đánh giá, nhận xét |
| `product-service` | `8012` | Catalog sách, tồn kho, thông tin sản phẩm |
| `ai-service` | `8013` | RAG chat, FAISS, graph recommendation, behavior model |

### Database và middleware

| Thành phần | Port | Ghi chú |
|---|---:|---|
| `mysql` | `3307` | Dùng cho gateway, staff, cart, ship, comment-rate |
| `postgres` | `5432` | Dùng cho manager, customer, order, pay, product, ai |
| `rabbitmq` | `5672`, `15672` | Message broker cho saga |
| `neo4j` | `7474`, `7687` | Lưu graph interaction và recommendation |

## 3. Tính năng chính

### E-commerce

- Danh sách sách, chi tiết sách, tìm kiếm, lọc theo danh mục
- Đăng ký/đăng nhập customer
- Đăng nhập staff và manager
- Quản lý sách cho staff
- Quản lý đơn hàng
- Đánh giá và bình luận sách
- Dashboard staff và manager

### AI

- Recommendation theo hành vi người dùng
- Recommendation theo graph interaction
- Semantic search bằng vector store
- Knowledge base cho chính sách và FAQ
- Chatbot tư vấn sách có RAG
- Deep model LSTM cho user behavior analysis

## 4. AI stack

`ai-service` hiện tại có đầy đủ các thành phần AI để demo:

- `FAISS` để lưu vector index
- `SentenceTransformer` model `paraphrase-multilingual-MiniLM-L12-v2` để tạo embedding
- `Neo4j` để lưu interaction graph
- `PyTorch` + `LSTM` cho behavior model
- `Gemini` để sinh câu trả lời chat khi có API key
- Rule-based fallback khi LLM chậm hoặc không có API key

### Knowledge base

Knowledge base được seed vào vector store, gồm các nhóm nội dung:

- Chính sách giao hàng
- Đổi trả và hoàn tiền
- Phương thức thanh toán
- Chương trình thành viên
- Thông tin liên hệ
- FAQ mua sách
- Danh mục và thể loại sách

### RAG chat

Pipeline chat của `ai-service`:

1. Lấy câu hỏi mới nhất từ người dùng
2. Lấy graph context nếu người dùng đã đăng nhập
3. Tìm kiếm vector + keyword trên catalog sách
4. Bổ sung knowledge/doc context
5. Gọi Gemini nếu có API key
6. Fallback sang rule-based response nếu cần

## 5. Seed dữ liệu

Script seed tạo dữ liệu mẫu cho hệ thống:

- Khoảng `50` sách trong `product-service`
- `10` customer
- `3` staff
- `2` manager
- Ratings, reviews, orders mẫu
- Đồng bộ products vào FAISS
- Seed knowledge docs vào FAISS
- Train behavior model

## 6. Hướng dẫn chạy dự án

### Yêu cầu

- Docker
- Docker Compose
- Windows PowerShell hoặc terminal có hỗ trợ `docker compose`

### Bước 1: Chuẩn bị biến môi trường

Nếu muốn dùng Gemini cho chatbot, tạo file `.env` tại root repo và thêm:

```env
GEMINI_API_KEY=your_api_key_here
```

Nếu không có `GEMINI_API_KEY`, chatbot vẫn hoạt động với fallback rule-based.

### Bước 2: Build và chạy hệ thống

Từ thư mục `AI-ECOMMERCE`, chạy:

```powershell
docker compose up --build
```

Nếu bạn muốn dọn các container cũ không còn nằm trong compose:

```powershell
docker compose up --build --remove-orphans
```

### Bước 3: Seed dữ liệu và khởi tạo AI

Có thể chạy file batch:

```powershell
.\run_seed.bat
```

Hoặc chạy tay từng bước:

```powershell
docker compose cp create_sample_data.py api-gateway:/tmp/create_sample_data.py
docker compose exec api-gateway python /tmp/create_sample_data.py
docker compose exec ai-service python manage.py sync_products_to_faiss
docker compose exec ai-service python manage.py seed_knowledge_to_faiss
docker compose exec ai-service python manage.py train_behavior_model --epochs 10
```

## 7. Các màn hình demo chính

Sau khi chạy xong, truy cập:

- Trang chủ: `http://localhost:8000/`
- Login: `http://localhost:8000/login/`
- Danh sách sách: `http://localhost:8000/books/`
- Recommend: `http://localhost:8000/books/recommendations/`
- Chat AI: `http://localhost:8000/chat/`
- Dashboard staff: `http://localhost:8000/staff/dashboard/`
- Dashboard manager: `http://localhost:8000/manager/dashboard/`

## 8. Health check

Một số endpoint hữu ích để kiểm tra nhanh:

- `http://localhost:8012/health/` -> `product-service`
- `http://localhost:8013/health/` -> `ai-service`

## 9. Cấu trúc thư mục

```text
AI-ECOMMERCE/
|-- api-gateway/
|-- staff-service/
|-- manager-service/
|-- customer-service/
|-- cart-service/
|-- order-service/
|-- ship-service/
|-- pay-service/
|-- comment-rate-service/
|-- product-service/
|-- ai-service/
|-- create_sample_data.py
|-- run_seed.bat
|-- docker-compose.yml
|-- init-mysql.sql
|-- init-postgres.sql
```

## 10. Điểm nổi bật để bảo vệ đồ án

Dự án này có thể bảo vệ theo 5 ý chính:

- Có trên `10` sản phẩm trong hệ thống
- Có `AI Service - Deep Model` bằng `PyTorch LSTM`
- Có `AI Service - Knowledge Base` bằng `FAISS + knowledge documents`
- Có `AI Service - RAG + Chat`
- Có tính thực tiễn cao vì là bài toán bookstore/e-commerce có dashboard và demo rõ ràng

## 11. Ghi chú

- `product-service` là nguồn dữ liệu sách chính thức.
- `ai-service` đã được tích hợp trực tiếp với `product-service`.
- Repo hiện tại không còn các service legacy bị trùng lặp.
- Nếu thay đổi code trong service, nên rebuild lại service tương ứng bằng `docker compose up --build <service-name>`.
