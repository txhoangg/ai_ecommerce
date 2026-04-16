import os
import logging
from collections import defaultdict
from django.conf import settings

logger = logging.getLogger(__name__)


class BehaviorModelTrainer:
    """Trains the BehaviorLSTM model on user interaction sequences."""

    EVENT_WEIGHTS = {
        'view': 1,
        'add_to_cart': 3,
        'purchase': 5,
        'search': 1,
        'rate': 2,
    }

    def __init__(self):
        self.model = None
        self.type_to_idx = None

    def _get_type_to_idx(self):
        from .behavior_model import BOOK_TYPES
        return {t: i for i, t in enumerate(BOOK_TYPES)}

    def _load_or_create_model(self):
        """Load existing model weights or create a fresh model."""
        from .behavior_model import BehaviorLSTM
        import torch

        model = BehaviorLSTM()
        try:
            if os.path.exists(settings.BEHAVIOR_MODEL_PATH):
                state = torch.load(
                    settings.BEHAVIOR_MODEL_PATH,
                    map_location='cpu',
                    weights_only=True,
                )
                model.load_state_dict(state)
                logger.info("Loaded existing behavior model weights.")
        except Exception as e:
            logger.warning(f"Could not load existing model (will train from scratch): {e}")
        return model

    def train(self, interactions: list, epochs: int = 10) -> bool:
        """
        Train the LSTM behavior model on user interaction data.

        Args:
            interactions: list of dicts with keys:
                          user_id, book_id, event_type, book_type
            epochs: number of training epochs

        Returns:
            True if training succeeded, False otherwise.
        """
        import torch
        import torch.nn as nn
        import torch.optim as optim

        if not interactions or len(interactions) < 5:
            logger.info("Not enough interactions to train (need >= 5). Skipping.")
            return False

        self.type_to_idx = self._get_type_to_idx()
        model = self._load_or_create_model()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        # Group interactions by user
        user_sequences = defaultdict(list)
        for inter in interactions:
            uid = inter.get('user_id')
            if uid is not None:
                user_sequences[uid].append(inter)

        if not user_sequences:
            logger.warning("No valid user sequences found in interactions.")
            return False

        logger.info(f"Training on {len(user_sequences)} users, {len(interactions)} interactions, {epochs} epochs.")
        model.train()

        for epoch in range(epochs):
            total_loss = 0.0
            count = 0

            for user_id, seq in user_sequences.items():
                if not seq:
                    continue

                # Truncate to last 20 interactions
                seq = seq[-20:]

                # Build input tensors
                book_ids = torch.tensor(
                    [[s['book_id'] % 10000 for s in seq]],
                    dtype=torch.long,
                )
                weights = torch.tensor(
                    [[[self.EVENT_WEIGHTS.get(s.get('event_type', 'view'), 1) / 5.0]
                      for s in seq]],
                    dtype=torch.float,
                )

                # Determine target: most common book_type in this sequence
                type_counts = defaultdict(int)
                for s in seq:
                    bt = s.get('book_type', 'fiction')
                    if bt in self.type_to_idx:
                        type_counts[bt] += 1
                    else:
                        type_counts['fiction'] += 1

                if not type_counts:
                    continue

                target_type = max(type_counts, key=type_counts.get)
                target_idx = self.type_to_idx.get(target_type, 0)
                target = torch.tensor([target_idx], dtype=torch.long)

                optimizer.zero_grad()
                _, type_scores = model(book_ids, weights)
                loss = criterion(type_scores, target)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                count += 1

            if epoch % max(1, epochs // 5) == 0:
                avg_loss = total_loss / max(count, 1)
                logger.info(f"  Epoch {epoch}/{epochs} - avg loss: {avg_loss:.4f} ({count} users)")

        # Save model
        try:
            import torch
            torch.save(model.state_dict(), settings.BEHAVIOR_MODEL_PATH)
            self.model = model
            logger.info(f"Behavior model saved to {settings.BEHAVIOR_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to save behavior model: {e}")
            return False

        return True
