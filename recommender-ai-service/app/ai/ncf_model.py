import torch
import torch.nn as nn
import numpy as np
import os


class NCFModel(nn.Module):
    def __init__(self, num_users, num_items, embedding_size=32):
        super(NCFModel, self).__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_size)
        self.item_embedding = nn.Embedding(num_items, embedding_size)
        self.mlp = nn.Sequential(
            nn.Linear(embedding_size * 2, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

    def forward(self, user_ids, item_ids):
        user_emb = self.user_embedding(user_ids)
        item_emb = self.item_embedding(item_ids)
        x = torch.cat([user_emb, item_emb], dim=-1)
        return self.mlp(x).squeeze(-1)


class BehaviorModelManager:
    def __init__(self, num_users=1000, num_items=1000):
        self.num_users = num_users
        self.num_items = num_items
        self.model_path = '/tmp/ncf_model.pt'
        self.model = None

    def _build_model(self):
        return NCFModel(self.num_users, self.num_items)

    def train(self, interactions):
        """Train NCF model on interactions list of {'customer_id', 'book_id', 'score'}."""
        model = self._build_model()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.MSELoss()

        # Clamp ids to valid range
        user_ids = torch.tensor(
            [min(i['customer_id'], self.num_users - 1) for i in interactions],
            dtype=torch.long
        )
        item_ids = torch.tensor(
            [min(i['book_id'], self.num_items - 1) for i in interactions],
            dtype=torch.long
        )
        scores = torch.tensor(
            [float(i['score']) for i in interactions],
            dtype=torch.float32
        )

        if len(interactions) == 0:
            return {'epochs': 0, 'interactions': 0, 'final_loss': 0.0}

        model.train()
        loss = torch.tensor(0.0)
        for epoch in range(20):
            optimizer.zero_grad()
            preds = model(user_ids, item_ids)
            loss = criterion(preds, scores)
            loss.backward()
            optimizer.step()

        torch.save(model.state_dict(), self.model_path)
        self.model = model
        return {
            'epochs': 20,
            'interactions': len(interactions),
            'final_loss': float(loss.item()),
        }

    def predict(self, customer_id, book_ids):
        """Return dict {book_id: score} for each book_id."""
        if self.model is None:
            if not self.is_trained():
                return {bid: 0.0 for bid in book_ids}
            model = self._build_model()
            model.load_state_dict(torch.load(self.model_path, map_location='cpu', weights_only=True))
            model.eval()
            self.model = model
        else:
            self.model.eval()

        uid = min(customer_id, self.num_users - 1)
        results = {}
        with torch.no_grad():
            for bid in book_ids:
                iid = min(bid, self.num_items - 1)
                u = torch.tensor([uid], dtype=torch.long)
                i = torch.tensor([iid], dtype=torch.long)
                score = self.model(u, i).item()
                results[bid] = score
        return results

    def is_trained(self):
        return os.path.exists(self.model_path)
