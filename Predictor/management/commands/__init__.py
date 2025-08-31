# Empty file to make this a Python package
```

```python:Predictor/management/commands/load_dataset.py
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
```

## 5. Now you can use the system in two ways:

### Option 1: Automatic Loading (Recommended)
The system will automatically detect and load your training dataset when it starts up. Just make sure your CSV file is in the `saved_models` folder.

### Option 2: Manual Loading
Run this command to manually load the dataset:
```bash
python manage.py load_dataset
```

## What This Gives You:

✅ **Pre-loaded Training Data**: Your model's training dataset is automatically loaded  
✅ **Immediate Analysis**: Users can see real transaction analysis right away  
✅ **Dataset Statistics**: Shows total transactions, fraud count, fraud percentage  
✅ **Professional Demo**: Demonstrates the system's capabilities with real data  
✅ **No Upload Required**: Users can immediately explore transaction history and analysis  

## File Structure:
```
saved_models/
├── rf_model.joblib
├── AIML Dataset.csv  ← Your training dataset here
└── other model files...
```

Now when users visit your system, they'll immediately see:
- A banner showing your training dataset is loaded
- Statistics about total transactions and fraud cases
- The ability to analyze real historical transactions
- Professional-looking analysis with actual data

This makes your fraud detection system look much more professional and demonstrates its real-world capabilities!

