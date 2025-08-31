from django.core.management.base import BaseCommand
from Predictor.data_loader import load_training_dataset

class Command(BaseCommand):
    help = 'Load the training dataset into the database'

    def handle(self, *args, **options):
        self.stdout.write('Loading training dataset...')
        
        if load_training_dataset():
            self.stdout.write(
                self.style.SUCCESS('Successfully loaded training dataset!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to load training dataset.')
            )
