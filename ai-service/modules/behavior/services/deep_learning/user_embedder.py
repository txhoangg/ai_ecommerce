import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

EVENT_WEIGHTS = {
    'view': 1,
    'add_to_cart': 3,
    'purchase': 5,
    'search': 1,
    'rate': 2,
}


class UserEmbedder:
    """Inference wrapper around BehaviorLSTM for getting user type preferences."""

    def __init__(self):
        self.model = None
        self._load()

    def _load(self):
        try:
            if os.path.exists(settings.BEHAVIOR_MODEL_PATH):
                import torch
                from .behavior_model import BehaviorLSTM
                self.model = BehaviorLSTM()
                state = torch.load(
                    settings.BEHAVIOR_MODEL_PATH,
                    map_location='cpu',
                    weights_only=True,
                )
                self.model.load_state_dict(state)
                self.model.eval()
                logger.info("UserEmbedder: model loaded successfully.")
        except Exception as e:
            logger.warning(f"UserEmbedder load error (will use no-model fallback): {e}")
            self.model = None

    def reload(self):
        """Reload model from disk (call after training)."""
        self.model = None
        self._load()

    def get_preferred_types(self, interaction_history: list) -> list:
        """
        Predict user's preferred book types from interaction history.

        Args:
            interaction_history: list of dicts with keys: book_id, event_type (optional), weight

        Returns:
            List of (book_type, probability) tuples sorted by probability descending, top 3.
        """
        if not self.model or not interaction_history:
            return []

        try:
            import torch
            from .behavior_model import BOOK_TYPES

            seq = interaction_history[-20:]

            book_ids = torch.tensor(
                [[s['book_id'] % 10000 for s in seq]],
                dtype=torch.long,
            )
            weights = torch.tensor(
                [[[EVENT_WEIGHTS.get(s.get('event_type', 'view'), 1) / 5.0]
                  for s in seq]],
                dtype=torch.float,
            )

            with torch.no_grad():
                _, type_scores = self.model(book_ids, weights)

            probs = type_scores[0].tolist()
            result = sorted(zip(BOOK_TYPES, probs), key=lambda x: x[1], reverse=True)
            return result[:3]

        except Exception as e:
            logger.error(f"UserEmbedder predict error: {e}")
            return []

    def get_user_embedding(self, interaction_history: list):
        """
        Get raw 64-dim user embedding tensor.

        Returns numpy array of shape (64,) or None if unavailable.
        """
        if not self.model or not interaction_history:
            return None

        try:
            import torch
            seq = interaction_history[-20:]
            book_ids = torch.tensor(
                [[s['book_id'] % 10000 for s in seq]],
                dtype=torch.long,
            )
            weights = torch.tensor(
                [[[EVENT_WEIGHTS.get(s.get('event_type', 'view'), 1) / 5.0]
                  for s in seq]],
                dtype=torch.float,
            )

            with torch.no_grad():
                user_embed, _ = self.model(book_ids, weights)

            return user_embed[0].numpy()
        except Exception as e:
            logger.error(f"UserEmbedder embedding error: {e}")
            return None


user_embedder = UserEmbedder()
