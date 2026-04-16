import torch
import torch.nn as nn

# All supported book types in this bookstore system
BOOK_TYPES = [
    'fiction',
    'textbook',
    'newspaper',
    'magazine',
    'manga',
    'science',
    'self_help',
    'dictionary',
    'children',
    'ebook',
    'audiobook',
    'encyclopedia',
]
N_TYPES = len(BOOK_TYPES)


class BehaviorLSTM(nn.Module):
    """LSTM model for user behavior analysis.

    Input: sequence of (book_id, event_weight) pairs representing a user's interaction history.
    Output:
        - user_embed: 64-dimensional user embedding capturing reading preferences
        - type_scores: probability distribution over N_TYPES book types
    """

    def __init__(self, max_books: int = 10000, embed_dim: int = 32,
                 hidden_dim: int = 64, n_types: int = N_TYPES):
        super().__init__()
        self.max_books = max_books
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.n_types = n_types

        # Book ID embedding (padded with 0)
        self.book_embed = nn.Embedding(max_books + 1, embed_dim, padding_idx=0)

        # LSTM: input = (book embedding) + (normalized event weight scalar)
        self.lstm = nn.LSTM(embed_dim + 1, hidden_dim, batch_first=True)

        # Output heads
        self.user_proj = nn.Linear(hidden_dim, 64)
        self.type_pred = nn.Linear(hidden_dim, n_types)
        self.dropout = nn.Dropout(0.2)

    def forward(self, book_ids: torch.Tensor, weights: torch.Tensor):
        """
        Args:
            book_ids: LongTensor of shape (batch_size, seq_len)
            weights:  FloatTensor of shape (batch_size, seq_len, 1) - normalized event weights

        Returns:
            user_embed: FloatTensor (batch_size, 64)
            type_scores: FloatTensor (batch_size, N_TYPES) - softmax probabilities
        """
        embeds = self.book_embed(book_ids)           # (batch, seq, embed_dim)
        x = torch.cat([embeds, weights], dim=-1)     # (batch, seq, embed_dim + 1)
        lstm_out, (h_n, _) = self.lstm(x)
        h = h_n[-1]                                  # (batch, hidden_dim)
        h = self.dropout(h)
        user_embed = self.user_proj(h)               # (batch, 64)
        type_scores = torch.softmax(self.type_pred(h), dim=-1)  # (batch, N_TYPES)
        return user_embed, type_scores
