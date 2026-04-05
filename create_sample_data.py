"""
Script to create sample data for all microservices
Run this after all services are up and running
"""

import requests
import time
import random
import string
import jwt
import datetime

# Generate a service-level JWT token for internal seed requests
SHARED_SECRET = "super-secret-jwt-key"
_token_payload = {
    "sub": "seed-script",
    "role": "service",
    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
}
SERVICE_TOKEN = jwt.encode(_token_payload, SHARED_SECRET, algorithm="HS256")
AUTH_HEADERS = {"Authorization": f"Bearer {SERVICE_TOKEN}"}

# Service URLs
# When run from host: uses localhost (requires ports to be exposed)
# When run inside Docker (via run_seed.bat): uses internal hostnames
import os
STAFF_SERVICE = os.getenv("STAFF_SERVICE_URL", "http://staff-service:8001")
MANAGER_SERVICE = os.getenv("MANAGER_SERVICE_URL", "http://manager-service:8002")
CUSTOMER_SERVICE = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8003")
CATALOG_SERVICE = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8004")
BOOK_SERVICE = os.getenv("BOOK_SERVICE_URL", "http://book-service:8005")
CART_SERVICE = os.getenv("CART_SERVICE_URL", "http://cart-service:8006")
ORDER_SERVICE = os.getenv("ORDER_SERVICE_URL", "http://order-service:8007")
COMMENT_RATE_SERVICE = os.getenv("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8010")

def wait_for_services():
    """Wait for all services to be ready"""
    print("Waiting for services to be ready...")
    services = [
        STAFF_SERVICE, MANAGER_SERVICE, CUSTOMER_SERVICE, CATALOG_SERVICE,
        BOOK_SERVICE, CART_SERVICE, ORDER_SERVICE, COMMENT_RATE_SERVICE
    ]

    for service in services:
        while True:
            try:
                response = requests.get(service, timeout=10)
                print(f"✓ {service} is ready")
                break
            except Exception as e:
                print(f"  Waiting for {service}... (Error: {e})")
                time.sleep(2)

    print("\nAll services are ready!\n")


def create_staff():
    """Create sample staff members"""
    print("Creating staff members...")

    # Staff model only has: name, email, password, role
    staff_data = [
        {
            "name": "John Staff",
            "email": "john.staff@bookstore.com",
            "password": "password123",
            "role": "staff"
        },
        {
            "name": "Sarah Staff",
            "email": "sarah.staff@bookstore.com",
            "password": "password123",
            "role": "staff"
        },
        {
            "name": "Mike Staff",
            "email": "mike.staff@bookstore.com",
            "password": "password123",
            "role": "staff"
        }
    ]

    staff_ids = []
    for staff in staff_data:
        try:
            response = requests.post(f"{STAFF_SERVICE}/api/staff/", json=staff, headers=AUTH_HEADERS)
            if response.status_code == 201:
                staff_id = response.json()['id']
                staff_ids.append(staff_id)
                print(f"  ✓ Created staff: {staff['name']} (ID: {staff_id})")
            else:
                # Already exists - fetch existing ID
                list_response = requests.get(f"{STAFF_SERVICE}/api/staff/", headers=AUTH_HEADERS)
                if list_response.status_code == 200:
                    existing = [s for s in list_response.json() if s.get('email') == staff['email']]
                    if existing:
                        staff_id = existing[0]['id']
                        staff_ids.append(staff_id)
                        print(f"  ~ Staff already exists: {staff['name']} (ID: {staff_id})")
                    else:
                        print(f"  ✗ Failed to create staff: {staff['name']} - {response.text}")
                else:
                    print(f"  ✗ Failed to create staff: {staff['name']} - {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating staff: {e}")

    return staff_ids


def create_managers():
    """Create sample managers"""
    print("\nCreating managers...")

    manager_data = [
        {
            "name": "Jane Manager",
            "email": "jane.manager@bookstore.com",
            "password": "password123",
            "phone": "2234567890",
            "department": "Operations"
        },
        {
            "name": "Bob Manager",
            "email": "bob.manager@bookstore.com",
            "password": "password123",
            "phone": "2234567891",
            "department": "Sales"
        }
    ]

    for manager in manager_data:
        try:
            response = requests.post(f"{MANAGER_SERVICE}/api/managers/", json=manager, headers=AUTH_HEADERS)
            if response.status_code == 201:
                print(f"  ✓ Created manager: {manager['name']}")
            else:
                # Already exists - check and skip gracefully
                list_response = requests.get(f"{MANAGER_SERVICE}/api/managers/", headers=AUTH_HEADERS)
                if list_response.status_code == 200:
                    existing = [m for m in list_response.json() if m.get('email') == manager['email']]
                    if existing:
                        print(f"  ~ Manager already exists: {manager['name']} (ID: {existing[0]['id']})")
                    else:
                        print(f"  ✗ Failed to create manager: {manager['name']} - {response.text}")
                else:
                    print(f"  ✗ Failed to create manager: {manager['name']} - {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating manager: {e}")


def create_customers():
    """Create sample customers"""
    print("\nCreating customers...")

    # Skip if customers already exist
    try:
        check = requests.get(f"{CUSTOMER_SERVICE}/api/customers/", headers=AUTH_HEADERS)
        if check.status_code == 200:
            existing = check.json()
            if len(existing) >= 10:
                print(f"  ~ Customers already seeded ({len(existing)} found). Skipping.")
                return [c['id'] for c in existing]
    except Exception:
        pass

    customer_data = []
    first_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Victor", "Trent", "Peggy", "Walter"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    for i in range(10):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        customer_data.append({
            "name": f"{fname} {lname}",
            "email": f"{fname.lower()}.{lname.lower()}{i}@example.com",
            "password": "password123"
        })

    customer_ids = []
    for customer in customer_data:
        try:
            response = requests.post(f"{CUSTOMER_SERVICE}/api/customers/", json=customer, headers=AUTH_HEADERS)
            if response.status_code == 201:
                customer_id = response.json()['id']
                customer_ids.append(customer_id)
                print(f"  ✓ Created customer: {customer['name']} (ID: {customer_id})")
            else:
                # Already exists - fetch existing ID
                list_response = requests.get(f"{CUSTOMER_SERVICE}/api/customers/", headers=AUTH_HEADERS)
                if list_response.status_code == 200:
                    existing = [c for c in list_response.json() if c.get('email') == customer['email']]
                    if existing:
                        customer_id = existing[0]['id']
                        customer_ids.append(customer_id)
                        print(f"  ~ Customer already exists: {customer['name']} (ID: {customer_id})")
                    else:
                        print(f"  ✗ Failed to create customer: {customer['name']} - {response.text}")
                else:
                    print(f"  ✗ Failed to create customer: {customer['name']} - {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating customer: {e}")

    return customer_ids


def create_books():
    """Create sample books"""
    print("\nCreating books...")

    # Skip if books already exist (idempotent — prevent duplicates on re-run)
    try:
        check = requests.get(f"{BOOK_SERVICE}/api/books/", headers=AUTH_HEADERS)
        if check.status_code == 200:
            existing_books = check.json()
            if len(existing_books) >= 50:
                print(f"  ~ Books already seeded ({len(existing_books)} found). Skipping.")
                return [b['id'] for b in existing_books]
    except Exception:
        pass

    book_data = []
    adjectives = ["Great", "Silent", "Hidden", "Dark", "Bright", "Lost", "Golden", "Crimson", "Last", "First", "Fallen", "Rising", "Broken", "Crystal", "Forgotten", "Secret", "Mystic", "Ancient", "Eternal", "Frozen"]
    nouns = ["Gatsby", "Empire", "Mountain", "River", "King", "Queen", "Knight", "Dragon", "Shadow", "Light", "Echo", "Whisper", "Storm", "Flame", "Sword", "Crown", "Throne", "Soul", "Heart", "Star"]
    genres = ["Sci-Fi", "Fantasy", "Mystery", "Romance", "Thriller", "Horror", "Historical", "Biography", "Business", "Self-Help"]
    authors = ["John Smith", "Jane Doe", "Emily Brontë", "George Orwell", "J.K. Rowling", "J.R.R. Tolkien", "Isaac Asimov", "Agatha Christie", "Stephen King", "Dan Brown", "Haruki Murakami", "Neil Gaiman", "Margaret Atwood"]

    # Add the famous 8 books first to ensure catalog consistency
    classic_books = [
        {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "9780743273565", "price": 15.99, "stock": 50, "description": "A classic American novel set in the Jazz Age"},
        {"title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "9780061120084", "price": 18.99, "stock": 45, "description": "A gripping tale of racial injustice"},
        {"title": "1984", "author": "George Orwell", "isbn": "9780451524935", "price": 16.99, "stock": 60, "description": "A dystopian social science fiction novel"},
        {"title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "9780141439518", "price": 14.99, "stock": 40, "description": "A romantic novel of manners"},
        {"title": "The Hobbit", "author": "J.R.R. Tolkien", "isbn": "9780547928227", "price": 19.99, "stock": 55, "description": "A fantasy novel and children's book"},
        {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "isbn": "9780590353427", "price": 22.99, "stock": 70, "description": "The first novel in the Harry Potter series"},
        {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "isbn": "9780316769174", "price": 17.99, "stock": 35, "description": "A story about teenage rebellion"},
        {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "isbn": "9780544003415", "price": 29.99, "stock": 30, "description": "An epic high-fantasy novel"}
    ]
    book_data.extend(classic_books)

    # Generate 42 more random books to make it 50
    for i in range(42):
        author = random.choice(authors)
        genre = random.choice(genres)
        book_data.append({
            "title": f"The {random.choice(adjectives)} {random.choice(nouns)}",
            "author": author,
            "isbn": f"978{random.randint(1000000000, 9999999999)}",
            "price": round(random.uniform(9.99, 49.99), 2),
            "stock": random.randint(15, 120),
            "description": f"An amazing {genre.lower()} book written by {author}. Highly recommended for {genre.lower()} lovers!"
        })

    book_ids = []
    for book in book_data:
        try:
            response = requests.post(f"{BOOK_SERVICE}/api/books/", json=book, headers=AUTH_HEADERS)
            if response.status_code == 201:
                book_id = response.json()['id']
                book_ids.append(book_id)
                print(f"  ✓ Created book: {book['title']} (ID: {book_id})")
            else:
                # Already exists - fetch existing ID by ISBN
                list_response = requests.get(f"{BOOK_SERVICE}/api/books/", headers=AUTH_HEADERS)
                if list_response.status_code == 200:
                    existing = [b for b in list_response.json() if b.get('isbn') == book['isbn']]
                    if existing:
                        book_id = existing[0]['id']
                        book_ids.append(book_id)
                        print(f"  ~ Book already exists: {book['title']} (ID: {book_id})")
                    else:
                        print(f"  ✗ Failed to create book: {book['title']} - {response.text}")
                else:
                    print(f"  ✗ Failed to create book: {book['title']} - {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating book: {e}")

    return book_ids


def create_ratings_and_reviews(customer_ids, book_ids):
    """Create sample ratings and reviews (separate endpoints)"""
    print("\nCreating ratings and reviews...")

    if not customer_ids or not book_ids:
        print("  ⚠ Skipping ratings/reviews - no customers or books available")
        return

    # Randomly assign ratings and reviews
    ratings_data = []
    reviews_data = []
    for _ in range(30):
        c_id = random.choice(customer_ids)
        b_id = random.choice(book_ids)
        score = random.randint(3, 5)
        # Avoid duplicate ratings by just catching the exception in the POST if any
        ratings_data.append({
            "customer_id": c_id,
            "book_id": b_id,
            "score": score
        })
        
        if random.random() > 0.5: # 50% chance to leave a review alongside a rating
            reviews_data.append({
                "customer_id": c_id,
                "book_id": b_id,
                "comment": random.choice([
                    "Absolutely loved this book! A timeless classic.",
                    "One of the best books I've ever read. Highly recommend!",
                    "Very thought-provoking and relevant even today.",
                    "A beautiful story with wonderful characters.",
                    "Couldn't put it down. Read it in one sitting!",
                    "Good, but started a bit slow.",
                    "The ending blew my mind!",
                    "A masterpiece."
                ])
            })

    for rating in ratings_data:
        try:
            requests.post(f"{COMMENT_RATE_SERVICE}/api/ratings/", json=rating, headers=AUTH_HEADERS)
            print(f"  ✓ Created rating for book ID {rating['book_id']}")
        except Exception:
            pass

    for review in reviews_data:
        try:
            response = requests.post(f"{COMMENT_RATE_SERVICE}/api/reviews/", json=review, headers=AUTH_HEADERS)
            if response.status_code == 201:
                print(f"  ✓ Created review for book ID {review['book_id']}")
            else:
                print(f"  ✗ Failed to create review for book ID {review['book_id']} - {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating review: {e}")


def create_cart_items(customer_ids, book_ids):
    """Create sample cart items"""
    print("\nCreating cart items...")

    if not customer_ids or not book_ids:
        print("  ⚠ Skipping cart items - no customers or books available")
        return

    # Step 1: Create carts via POST /api/carts/ with {customer_id}
    # Step 2: Add items via POST /api/cart-items/ with {cart_id, book_id, quantity}

    cart_assignments = []
    # Create 5 carts with random items
    for c_id in random.sample(customer_ids, min(5, len(customer_ids))):
        num_items = random.randint(1, 4)
        items = []
        for _ in range(num_items):
            items.append({
                "book_id": random.choice(book_ids),
                "quantity": random.randint(1, 3)
            })
        cart_assignments.append({
            "customer_id": c_id,
            "items": items
        })

    for assignment in cart_assignments:
        customer_id = assignment["customer_id"]
        # Create the cart (200 = already exists, 201 = newly created, both are OK)
        try:
            cart_response = requests.post(f"{CART_SERVICE}/api/carts/", json={"customer_id": customer_id}, headers=AUTH_HEADERS)
            if cart_response.status_code in (200, 201):
                cart_id = cart_response.json()['id']
                action = "Created" if cart_response.status_code == 201 else "Found existing"
                print(f"  ✓ {action} cart (ID: {cart_id}) for customer {customer_id}")
            else:
                print(f"  ✗ Failed to create cart for customer {customer_id} - {cart_response.text}")
                continue
        except Exception as e:
            print(f"  ✗ Error creating cart: {e}")
            continue

        # Add items to the cart using customer_id (not cart_id)
        for item in assignment["items"]:
            try:
                item_payload = {"customer_id": customer_id, "book_id": item["book_id"], "quantity": item["quantity"]}
                item_response = requests.post(f"{CART_SERVICE}/api/cart-items/", json=item_payload, headers=AUTH_HEADERS)
                if item_response.status_code == 201:
                    print(f"    ✓ Added book {item['book_id']} (qty: {item['quantity']}) to cart {cart_id}")
                else:
                    print(f"    ✗ Failed to add book {item['book_id']} to cart - {item_response.text}")
            except Exception as e:
                print(f"    ✗ Error adding cart item: {e}")


def create_orders(customer_ids, book_ids):
    """Create sample orders"""
    print("\nCreating orders...")

    if not customer_ids or not book_ids:
        print("  ⚠ Skipping orders - no customers or books available")
        return

    # Order creation via POST /api/orders/create/
    # Required: customer_id, payment_method, shipping_address
    # Optional: discount_code, shipping_method
    order_data = []
    # Create 8 random orders
    for _ in range(8):
        c_id = random.choice(customer_ids)
        order_data.append({
            "customer_id": c_id,
            "payment_method": random.choice(["credit_card", "cash", "paypal", "cash_on_delivery"]),
            "shipping_address": f"{random.randint(100, 999)} Random Street, City {random.choice(['A', 'B', 'C'])}",
            "shipping_method": random.choice(["standard", "express", "overnight"])
        })

    for order in order_data:
        try:
            response = requests.post(f"{ORDER_SERVICE}/api/orders/create/", json=order, headers=AUTH_HEADERS)
            if response.status_code == 201:
                print(f"  ✓ Created order for customer {order['customer_id']}")
            else:
                print(f"  ✗ Failed to create order for customer {order['customer_id']} - {response.text}")
        except Exception as e:
            print(f"  ✗ Error creating order: {e}")


def main():
    """Main function to create all sample data"""
    print("=" * 60)
    print("BOOKSTORE MICROSERVICES - SAMPLE DATA CREATION")
    print("=" * 60)
    print()

    # Wait for services to be ready
    wait_for_services()

    # Create data in order
    staff_ids = create_staff()
    create_managers()
    customer_ids = create_customers()
    book_ids = create_books()
    create_ratings_and_reviews(customer_ids, book_ids)
    create_cart_items(customer_ids, book_ids)
    create_orders(customer_ids, book_ids)

    print()
    print("=" * 60)
    print("SAMPLE DATA CREATION COMPLETED!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Staff members: {len(staff_ids)}")
    print(f"  - Customers: {len(customer_ids)}")
    print(f"  - Books: {len(book_ids)}")
    print()
    print("You can now access the application at http://localhost:8000")
    print()


if __name__ == "__main__":
    main()
