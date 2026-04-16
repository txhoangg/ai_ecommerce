from neo4j import GraphDatabase
from django.conf import settings
import logging
import uuid

logger = logging.getLogger(__name__)


class GraphService:
    def __init__(self):
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
            except Exception as e:
                logger.error(f"Neo4j connection failed: {e}")
        return self._driver

    def log_interaction(self, user_id: int, book_id: int, event_type: str):
        """Log user-book interaction to Neo4j graph.
        event_type: 'view'(weight=1), 'add_to_cart'(weight=3), 'purchase'(weight=5),
                    'search'(weight=1), 'rate'(weight=2)
        """
        weights = {'view': 1, 'add_to_cart': 3, 'purchase': 5, 'search': 1, 'rate': 2}
        weight = weights.get(event_type, 1)

        driver = self._get_driver()
        if not driver:
            return

        try:
            with driver.session() as session:
                session.run("""
                    MERGE (u:User {id: $user_id})
                    MERGE (b:Book {id: $book_id})
                    MERGE (u)-[r:INTERACTED]->(b)
                    ON CREATE SET r.weight = $weight, r.event_type = $event_type,
                                  r.last_event = $event_type, r.count = 1
                    ON MATCH SET r.weight = r.weight + $weight, r.count = r.count + 1,
                                 r.last_event = $event_type
                """, user_id=user_id, book_id=book_id, weight=weight, event_type=event_type)
        except Exception as e:
            logger.error(f"Graph log_interaction error: {e}")

    def log_search(self, user_id: int, query: str, result_book_ids: list):
        """Log search query and results to graph."""
        driver = self._get_driver()
        if not driver:
            return
        query_id = uuid.uuid4().hex
        try:
            with driver.session() as session:
                session.run("""
                    MERGE (u:User {id: $user_id})
                    CREATE (q:Query {id: $query_id, text: $query_text, timestamp: datetime()})
                    CREATE (u)-[:SEARCHED]->(q)
                """, user_id=user_id, query_id=query_id, query_text=query)
                for book_id in result_book_ids[:5]:
                    session.run("""
                        MATCH (q:Query {id: $query_id})
                        MERGE (b:Book {id: $book_id})
                        MERGE (q)-[:RETURNED]->(b)
                    """, query_id=query_id, book_id=book_id)
        except Exception as e:
            logger.error(f"Graph log_search error: {e}")

    def get_recommendations(self, user_id: int, limit: int = 10) -> list:
        """Get book recommendations based on graph traversal:
        1. Books purchased by similar users (collaborative filtering)
        2. Fallback to popular books
        """
        driver = self._get_driver()
        if not driver:
            return []

        try:
            with driver.session() as session:
                # Collaborative filtering
                result = session.run("""
                    MATCH (u:User {id: $user_id})-[r1:INTERACTED]->(b:Book)<-[r2:INTERACTED]-(similar:User)
                    WHERE u <> similar
                    WITH u, similar, sum(r1.weight * r2.weight) AS similarity
                    ORDER BY similarity DESC LIMIT 5
                    MATCH (similar)-[r:INTERACTED]->(rec:Book)
                    WHERE NOT (u)-[:INTERACTED]->(rec)
                    RETURN rec.id AS book_id, sum(r.weight) AS score
                    ORDER BY score DESC LIMIT $limit
                """, user_id=user_id, limit=limit)
                book_ids = [record['book_id'] for record in result]

                if len(book_ids) < limit:
                    # Fallback: most popular books
                    result2 = session.run("""
                        MATCH (b:Book)<-[r:INTERACTED]-()
                        WHERE NOT b.id IN $existing
                        RETURN b.id AS book_id, sum(r.weight) AS score
                        ORDER BY score DESC LIMIT $remaining
                    """, existing=book_ids, remaining=limit - len(book_ids))
                    book_ids += [r['book_id'] for r in result2]

                return book_ids
        except Exception as e:
            logger.error(f"Graph get_recommendations error: {e}")
            return []

    def get_similar_books(self, book_id: int, limit: int = 6) -> list:
        """Get books that are frequently co-purchased/co-viewed."""
        driver = self._get_driver()
        if not driver:
            return []
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (b:Book {id: $book_id})<-[r1:INTERACTED]-(u:User)-[r2:INTERACTED]->(similar:Book)
                    WHERE b <> similar
                    RETURN similar.id AS book_id, count(u) AS co_interactions
                    ORDER BY co_interactions DESC LIMIT $limit
                """, book_id=book_id, limit=limit)
                return [r['book_id'] for r in result]
        except Exception as e:
            logger.error(f"Graph get_similar_books error: {e}")
            return []

    def get_trending_books(self, hours: int = 24, limit: int = 10) -> list:
        """Get trending books based on recent interactions."""
        driver = self._get_driver()
        if not driver:
            return []
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (b:Book)<-[r:INTERACTED]-()
                    RETURN b.id AS book_id, sum(r.weight) AS score
                    ORDER BY score DESC LIMIT $limit
                """, limit=limit)
                return [r['book_id'] for r in result]
        except Exception as e:
            logger.error(f"Graph get_trending error: {e}")
            return []

    def get_user_interaction_history(self, user_id: int) -> list:
        """Get user's interaction history for RAG context."""
        driver = self._get_driver()
        if not driver:
            return []
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (u:User {id: $user_id})-[r:INTERACTED]->(b:Book)
                    RETURN b.id AS book_id, r.weight AS weight, r.last_event AS last_event
                    ORDER BY r.weight DESC LIMIT 10
                """, user_id=user_id)
                return [{'book_id': r['book_id'], 'weight': r['weight'], 'last_event': r['last_event']} for r in result]
        except Exception as e:
            logger.error(f"Graph get_history error: {e}")
            return []

    def add_book_to_graph(self, book_id: int, book_type: str, category: str):
        """Register a book node in the graph."""
        driver = self._get_driver()
        if not driver:
            return
        try:
            with driver.session() as session:
                session.run("""
                    MERGE (b:Book {id: $book_id})
                    SET b.book_type = $book_type, b.category = $category
                """, book_id=book_id, book_type=book_type, category=category)
        except Exception as e:
            logger.error(f"Graph add_book error: {e}")

    def get_all_interactions(self) -> list:
        """Fetch all interactions for training (used by behavior model trainer)."""
        driver = self._get_driver()
        if not driver:
            return []
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (u:User)-[r:INTERACTED]->(b:Book)
                    RETURN u.id AS user_id, b.id AS book_id,
                           r.last_event AS event_type, b.book_type AS book_type,
                           r.weight AS weight
                    LIMIT 50000
                """)
                return [
                    {
                        'user_id': r['user_id'],
                        'book_id': r['book_id'],
                        'event_type': r['event_type'] or 'view',
                        'book_type': r['book_type'] or 'fiction',
                        'weight': r['weight'],
                    }
                    for r in result
                ]
        except Exception as e:
            logger.error(f"Graph get_all_interactions error: {e}")
            return []

    def close(self):
        if self._driver:
            self._driver.close()


graph_service = GraphService()
