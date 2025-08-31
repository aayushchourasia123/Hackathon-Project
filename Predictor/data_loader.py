import pandas as pd
import os
from .models import Transaction
from django.conf import settings

def load_training_dataset():
    """
    Load the training dataset that the model was trained on.
    This will populate the database with historical transactions for analysis.
    """
    try:
        # Path to your training dataset (adjust this path as needed)
        dataset_path = os.path.join(settings.BASE_DIR, 'saved_models', 'AIML_Dataset.csv')
        
        if not os.path.exists(dataset_path):
            # Try alternative paths
            alternative_paths = [
                os.path.join(settings.BASE_DIR, 'saved_models', 'fraud_detection_dataset.csv'),
                os.path.join(settings.BASE_DIR, 'data', 'AIML_Dataset.csv'),
                os.path.join(settings.BASE_DIR, 'dataset', 'AIML_Dataset.csv'),
            ]
            
            for path in alternative_paths:
                if os.path.exists(path):
                    dataset_path = path
                    break
            else:
                print("Training dataset not found. Please ensure your dataset is in the saved_models folder.")
                return False
        
        print(f"Loading training dataset from: {dataset_path}")
        
        # Read the CSV file
        df = pd.read_csv(dataset_path)
        print(f"Dataset loaded with {len(df)} rows")
        
        # Check if data already exists to avoid duplicates
        existing_count = Transaction.objects.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} transactions. Skipping data load.")
            return True
        
        # Process and save transactions
        saved_count = 0
        for index, row in df.iterrows():
            try:
                # Handle missing or NaN values
                step = int(row.get('step', 1)) if pd.notna(row.get('step')) else 1
                type_val = str(row.get('type', 'TRANSFER')) if pd.notna(row.get('type')) else 'TRANSFER'
                amount = float(row.get('amount', 0.0)) if pd.notna(row.get('amount')) else 0.0
                nameOrig = str(row.get('nameOrig', f'Account_{index}')) if pd.notna(row.get('nameOrig')) else f'Account_{index}'
                oldbalanceOrg = float(row.get('oldbalanceOrg', 0.0)) if pd.notna(row.get('oldbalanceOrg')) else 0.0
                newbalanceOrig = float(row.get('newbalanceOrig', 0.0)) if pd.notna(row.get('newbalanceOrig')) else 0.0
                nameDest = str(row.get('nameDest', f'Account_{index}')) if pd.notna(row.get('nameDest')) else f'Account_{index}'
                oldbalanceDest = float(row.get('oldbalanceDest', 0.0)) if pd.notna(row.get('oldbalanceDest')) else 0.0
                newbalanceDest = float(row.get('newbalanceDest', 0.0)) if pd.notna(row.get('newbalanceDest')) else 0.0
                isFraud = bool(row.get('isFraud', False)) if pd.notna(row.get('isFraud')) else False
                isFlaggedFraud = bool(row.get('isFlaggedFraud', False)) if pd.notna(row.get('isFlaggedFraud')) else False
                
                # Create transaction record
                transaction = Transaction.objects.create(
                    step=step,
                    type=type_val,
                    amount=amount,
                    nameOrig=nameOrig,
                    oldbalanceOrg=oldbalanceOrg,
                    newbalanceOrig=newbalanceOrig,
                    nameDest=nameDest,
                    oldbalanceDest=oldbalanceDest,
                    newbalanceDest=newbalanceDest,
                    isFraud=isFraud,
                    isFlaggedFraud=isFlaggedFraud
                )
                saved_count += 1
                
                # Progress indicator for large datasets
                if saved_count % 1000 == 0:
                    print(f"Processed {saved_count} transactions...")
                    
            except Exception as e:
                print(f"Error saving row {index}: {e}")
                continue
        
        print(f"Successfully loaded {saved_count} transactions from training dataset!")
        return True
        
    except Exception as e:
        print(f"Error loading training dataset: {str(e)}")
        return False

def get_dataset_info():
    """
    Get information about the loaded dataset for display purposes.
    """
    try:
        total_transactions = Transaction.objects.count()
        fraud_count = Transaction.objects.filter(isFraud=True).count()
        valid_count = Transaction.objects.filter(isFraud=False).count()
        
        # Get transaction type distribution
        type_counts = {}
        for transaction_type in ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']:
            count = Transaction.objects.filter(type=transaction_type).count()
            if count > 0:
                type_counts[transaction_type] = count
        
        # Get total amount
        total_amount = sum([float(t.amount) for t in Transaction.objects.all()])
        
        return {
            'total_transactions': total_transactions,
            'fraud_count': fraud_count,
            'valid_count': valid_count,
            'fraud_percentage': round((fraud_count / total_transactions * 100), 2) if total_transactions > 0 else 0,
            'type_distribution': type_counts,
            'total_amount': round(total_amount, 2),
            'dataset_loaded': total_transactions > 0
        }
    except Exception as e:
        return {
            'error': str(e),
            'dataset_loaded': False
        }
