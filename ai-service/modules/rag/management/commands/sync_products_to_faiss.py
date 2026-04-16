import logging
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync all products from product-service into the FAISS vector index'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Maximum number of products to sync (default: 1000)',
        )
        parser.add_argument(
            '--page-size',
            type=int,
            default=100,
            help='Products per page when fetching (default: 100)',
        )

    def handle(self, *args, **options):
        # Import here so Django is fully initialized
        from modules.rag.services.vector_store import vector_store

        limit = options['limit']
        page_size = options['page_size']

        self.stdout.write(self.style.NOTICE(
            f"Starting product sync from {settings.PRODUCT_SERVICE_URL} ..."
        ))

        try:
            url = f"{settings.PRODUCT_SERVICE_URL}/products/"
            total_synced = 0
            total_failed = 0
            page = 1

            while True:
                params = {'page': page, 'page_size': page_size}
                try:
                    resp = requests.get(url, params=params, timeout=30)
                except requests.exceptions.ConnectionError:
                    self.stdout.write(self.style.WARNING(
                        "Product service not reachable. Skipping sync."
                    ))
                    return
                except requests.exceptions.Timeout:
                    self.stdout.write(self.style.WARNING(
                        "Request to product service timed out. Skipping sync."
                    ))
                    return

                if resp.status_code != 200:
                    self.stdout.write(self.style.WARNING(
                        f"Product service returned HTTP {resp.status_code}. Skipping sync."
                    ))
                    return

                data = resp.json()
                if isinstance(data, dict):
                    products = data.get('results', [])
                    total_pages = data.get('total_pages', 1)
                else:
                    products = data
                    total_pages = 1

                if not products:
                    break

                for product in products:
                    try:
                        author = product.get('author', '')
                        desc = product.get('description', '')
                        text_extra = f" Tác giả: {author}." if author else ''
                        vector_store.add_book(
                            book_id=int(product['id']),
                            title=product.get('title', ''),
                            author=product.get('author', ''),
                            description=desc + text_extra,
                            book_type=product.get('book_type_key', 'fiction'),
                            category=product.get('category_name', ''),
                            price=float(product.get('price', 0)),
                            attributes=product.get('attributes', {}),
                            is_active=product.get('is_active', True),
                        )
                        total_synced += 1
                    except Exception as e:
                        total_failed += 1
                        logger.warning(f"Failed to index product {product.get('id')}: {e}")

                self.stdout.write(f"  Synced {total_synced} products so far...")

                if total_synced >= limit or page >= total_pages:
                    break

                page += 1

            stats = vector_store.get_stats()
            self.stdout.write(self.style.SUCCESS(
                f"Sync complete: {total_synced} synced, {total_failed} failed. "
                f"Total in FAISS index: {stats['total_vectors']}"
            ))

        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f"Sync failed with unexpected error: {e}. Continuing startup."
            ))
            logger.error(f"sync_products_to_faiss error: {e}")
