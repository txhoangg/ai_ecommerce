import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Train the LSTM behavior model using interaction data from Neo4j'

    def add_arguments(self, parser):
        parser.add_argument(
            '--epochs',
            type=int,
            default=10,
            help='Number of training epochs (default: 10)',
        )
        parser.add_argument(
            '--min-interactions',
            type=int,
            default=5,
            help='Minimum interactions required to proceed with training (default: 5)',
        )

    def handle(self, *args, **options):
        epochs = options['epochs']
        min_interactions = options['min_interactions']

        self.stdout.write(self.style.NOTICE(
            f"Starting behavior model training ({epochs} epochs)..."
        ))

        # Step 1: Fetch interactions from Neo4j
        interactions = []
        try:
            from modules.graph.services.graph_service import graph_service
            interactions = graph_service.get_all_interactions()
            self.stdout.write(f"  Fetched {len(interactions)} interactions from Neo4j.")
        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f"  Could not fetch from Neo4j: {e}. Will use empty dataset."
            ))

        if len(interactions) < min_interactions:
            self.stdout.write(self.style.WARNING(
                f"  Only {len(interactions)} interactions found (need >= {min_interactions}). "
                f"Skipping training - model will start with random weights."
            ))
            return

        # Step 2: Train
        try:
            from modules.behavior.services.deep_learning.model_trainer import BehaviorModelTrainer
            trainer = BehaviorModelTrainer()
            success = trainer.train(interactions, epochs=epochs)

            if success:
                self.stdout.write(self.style.SUCCESS(
                    f"Behavior model training complete ({len(interactions)} interactions, {epochs} epochs)."
                ))
                # Reload the shared user_embedder so it picks up the new weights
                try:
                    from modules.behavior.services.deep_learning.user_embedder import user_embedder
                    user_embedder.reload()
                    self.stdout.write("  UserEmbedder reloaded with new model weights.")
                except Exception as e:
                    logger.warning(f"Could not reload user_embedder: {e}")
            else:
                self.stdout.write(self.style.WARNING(
                    "Training returned False. Check logs for details. Continuing startup."
                ))

        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f"Training failed with error: {e}. Continuing startup without trained model."
            ))
            logger.error(f"train_behavior_model error: {e}")
