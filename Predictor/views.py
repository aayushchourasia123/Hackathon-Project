from django.shortcuts import render, get_object_or_404
import os
from joblib import load
import pandas as pd
from .models import Transaction
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
from .data_loader import load_training_dataset, get_dataset_info

model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saved_models', 'rf_model.joblib')
model = load(model_path)

def predictor(request):
    # Load training dataset if not already loaded
    dataset_info = get_dataset_info()
    if not dataset_info['dataset_loaded']:
        print("Loading training dataset...")
        load_training_dataset()
        dataset_info = get_dataset_info()
    
    return render(request, 'main.html', {
        'dataset_info': dataset_info
    })

def FormInfo(request):
    type_val = request.GET['type']
    amount = float(request.GET['amount'])
    oldbalanceOrg = float(request.GET['oldbalanceOrg'])
    newbalanceOrig = float(request.GET['newbalanceOrig'])
    oldbalanceDest = float(request.GET['oldbalanceDest'])
    newbalanceDest = float(request.GET['newbalanceDest'])
    
    # Get name fields with fallbacks if they're missing
    nameOrig = request.GET.get('nameOrig', f'Account_{oldbalanceOrg:.0f}')
    nameDest = request.GET.get('nameDest', f'Account_{oldbalanceDest:.0f}')
    
    balanceDiffOrg = newbalanceOrig - oldbalanceOrg
    balanceDiffDest = newbalanceDest - oldbalanceDest
    
    # Create and save transaction record
    transaction = Transaction.objects.create(
        type=type_val,
        amount=amount,
        nameOrig=nameOrig,
        nameDest=nameDest,
        oldbalanceOrg=oldbalanceOrg,
        newbalanceOrig=newbalanceOrig,
        oldbalanceDest=oldbalanceDest,
        newbalanceDest=newbalanceDest,
        isFraud=False,  # Will be updated after prediction
        isFlaggedFraud=False
    )
    
    data = pd.DataFrame({
        'type': [type_val],
        'amount': [amount],
        'oldbalanceOrg': [oldbalanceOrg],
        'newbalanceOrig': [newbalanceOrig],
        'oldbalanceDest': [oldbalanceDest],
        'newbalanceDest': [newbalanceDest],
        'balanceDiffOrg': [balanceDiffOrg],
        'balanceDiffDest': [balanceDiffDest]
    })
    
    y_pred = model.predict(data)
    
    # Update transaction with fraud prediction
    transaction.isFraud = bool(y_pred[0])
    transaction.save()
    
    print(f"Prediction: {y_pred[0]}")
    print(f"Prediction type: {type(y_pred[0])}")
    
    result = "FRAUD DETECTED!" if y_pred[0] == 1 else "VALID TRANSACTION"
    result_class = "danger" if y_pred[0] == 1 else "success"
    icon = "⚠️" if y_pred[0] == 1 else "✅"
    message = "This transaction has been flagged as potentially fraudulent. Please review carefully." if y_pred[0] == 1 else "This transaction appears to be legitimate and safe to proceed."
    
    # Get updated dataset info
    dataset_info = get_dataset_info()
    
    return render(request, 'main.html', {
        'prediction': result,
        'result_class': result_class,
        'icon': icon,
        'message': message,
        'show_result': True,
        'transaction_id': transaction.transaction_id,
        'dataset_info': dataset_info
    })

def transaction_history(request):
    """View to show transaction history for specific accounts with graphs"""
    account_name = request.GET.get('account', '')
    time_period = request.GET.get('period', '1month')  # 1month, 3months, 6months, 1year
    transactions = []
    
    if account_name:
        # Calculate date range based on time period
        end_date = datetime.now()
        if time_period == '1month':
            start_date = end_date - timedelta(days=30)
        elif time_period == '3months':
            start_date = end_date - timedelta(days=90)
        elif time_period == '6months':
            start_date = end_date - timedelta(days=180)
        elif time_period == '1year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Find all transactions involving this account
        transactions = Transaction.objects.filter(
            (Q(nameOrig__icontains=account_name) | Q(nameDest__icontains=account_name)) &
            Q(timestamp__gte=start_date)
        )
    
    # Prepare data for charts
    chart_data = {}
    if transactions:
        # Monthly transaction amounts
        monthly_data = {}
        for t in transactions:
            month_key = t.timestamp.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'amount': 0, 'count': 0}
            monthly_data[month_key]['amount'] += float(t.amount)
            monthly_data[month_key]['count'] += 1
        
        chart_data = {
            'labels': list(monthly_data.keys()),
            'amounts': [monthly_data[m]['amount'] for m in monthly_data.keys()],
            'counts': [monthly_data[m]['count'] for m in monthly_data.keys()]
        }
    
    # Get dataset info
    dataset_info = get_dataset_info()
    
    return render(request, 'transaction_history.html', {
        'transactions': transactions,
        'account_name': account_name,
        'time_period': time_period,
        'chart_data': json.dumps(chart_data),
        'dataset_info': dataset_info
    })

def account_analysis(request):
    """View to analyze transactions for a single account with comprehensive analysis"""
    account_name = request.GET.get('account', '')
    time_period = request.GET.get('period', '1month')
    transactions = []
    
    if account_name:
        # Calculate date range
        end_date = datetime.now()
        if time_period == '1month':
            start_date = end_date - timedelta(days=30)
        elif time_period == '3months':
            start_date = end_date - timedelta(days=90)
        elif time_period == '6months':
            start_date = end_date - timedelta(days=180)
        elif time_period == '1year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Find all transactions involving this account
        transactions = Transaction.objects.filter(
            (Q(nameOrig__icontains=account_name) | Q(nameDest__icontains=account_name)) &
            Q(timestamp__gte=start_date)
        )
    
    # Calculate comprehensive statistics
    total_amount = 0
    fraud_count = 0
    valid_count = 0
    incoming_amount = 0
    outgoing_amount = 0
    incoming_count = 0
    outgoing_count = 0
    type_distribution = {}
    
    if transactions:
        for t in transactions:
            amount = float(t.amount)
            total_amount += amount
            
            if t.isFraud:
                fraud_count += 1
            else:
                valid_count += 1
            
            # Determine if transaction is incoming or outgoing for this account
            if t.nameOrig == account_name:
                # Account is sender (outgoing)
                outgoing_amount += amount
                outgoing_count += 1
            else:
                # Account is receiver (incoming)
                incoming_amount += amount
                incoming_count += 1
            
            # Count transaction types
            if t.type not in type_distribution:
                type_distribution[t.type] = 0
            type_distribution[t.type] += 1
    
    # Calculate net flow
    net_flow = incoming_amount - outgoing_amount
    
    # Prepare chart data
    chart_data = {}
    if transactions:
        # Transaction type distribution
        chart_data['types'] = list(type_distribution.keys())
        chart_data['type_counts'] = list(type_distribution.values())
        
        # Monthly transaction counts
        monthly_data = {}
        for t in transactions:
            month_key = t.timestamp.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += 1
        
        chart_data['monthly_labels'] = list(monthly_data.keys())
        chart_data['monthly_counts'] = list(monthly_data.values())
    
    # Get dataset info
    dataset_info = get_dataset_info()
    
    return render(request, 'account_analysis.html', {
        'transactions': transactions,
        'account_name': account_name,
        'time_period': time_period,
        'chart_data': json.dumps(chart_data),
        'dataset_info': dataset_info,
        'total_amount': total_amount,
        'fraud_count': fraud_count,
        'valid_count': valid_count,
        'incoming_amount': incoming_amount,
        'outgoing_amount': outgoing_amount,
        'incoming_count': incoming_count,
        'outgoing_count': outgoing_count,
        'net_flow': net_flow,
        'type_distribution': type_distribution
    })

def merchant_analysis(request):
    """View to analyze transactions by merchant/account type"""
    merchant_name = request.GET.get('merchant', '')
    transactions = []
    
    if merchant_name:
        transactions = Transaction.objects.filter(
            Q(nameOrig__icontains=merchant_name) | Q(nameDest__icontains=merchant_name)
        )
    
    # Get dataset info
    dataset_info = get_dataset_info()
    
    return render(request, 'merchant_analysis.html', {
        'transactions': transactions,
        'merchant_name': merchant_name,
        'dataset_info': dataset_info
    })

def all_transactions(request):
    """View to show all transactions with filtering options"""
    transaction_type = request.GET.get('type', '')
    fraud_filter = request.GET.get('fraud', '')
    time_period = request.GET.get('period', '1month')
    
    # Calculate date range
    end_date = datetime.now()
    if time_period == '1month':
        start_date = end_date - timedelta(days=30)
    elif time_period == '3months':
        start_date = end_date - timedelta(days=90)
    elif time_period == '6months':
        start_date = end_date - timedelta(days=180)
    elif time_period == '1year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    transactions = Transaction.objects.filter(timestamp__gte=start_date)
    
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
    
    if fraud_filter == 'fraud':
        transactions = transactions.filter(isFraud=True)
    elif fraud_filter == 'valid':
        transactions = transactions.filter(isFraud=False)
    
    # Get dataset info
    dataset_info = get_dataset_info()
    
    return render(request, 'all_transactions.html', {
        'transactions': transactions,
        'transaction_type': transaction_type,
        'fraud_filter': fraud_filter,
        'time_period': time_period,
        'dataset_info': dataset_info
    })

def dataset_loader(request):
    """View to load dataset from CSV file"""
    if request.method == 'POST':
        try:
            # Get the uploaded file
            csv_file = request.FILES.get('csv_file')
            if csv_file:
                # Read the CSV file
                df = pd.read_csv(csv_file)
                
                # Process and save transactions
                saved_count = 0
                for index, row in df.iterrows():
                    try:
                        # Create transaction record
                        transaction = Transaction.objects.create(
                            step=row.get('step', 1),
                            type=row.get('type', 'TRANSFER'),
                            amount=row.get('amount', 0.0),
                            nameOrig=row.get('nameOrig', f'Account_{index}'),
                            oldbalanceOrg=row.get('oldbalanceOrg', 0.0),
                            newbalanceOrig=row.get('newbalanceOrig', 0.0),
                            nameDest=row.get('nameDest', f'Account_{index}'),
                            oldbalanceDest=row.get('oldbalanceDest', 0.0),
                            newbalanceDest=row.get('newbalanceDest', 0.0),
                            isFraud=row.get('isFraud', False),
                            isFlaggedFraud=row.get('isFlaggedFraud', False)
                        )
                        saved_count += 1
                    except Exception as e:
                        print(f"Error saving row {index}: {e}")
                        continue
                
                return render(request, 'dataset_loader.html', {
                    'success': True,
                    'message': f'Successfully loaded {saved_count} transactions from dataset!',
                    'total_rows': len(df)
                })
            else:
                return render(request, 'dataset_loader.html', {
                    'error': 'No file uploaded'
                })
        except Exception as e:
            return render(request, 'dataset_loader.html', {
                'error': f'Error loading dataset: {str(e)}'
            })
    
    # Get dataset info
    dataset_info = get_dataset_info()
    
    return render(request, 'dataset_loader.html', {
        'dataset_info': dataset_info
    })

def get_chart_data(request):
    """API endpoint to get chart data for AJAX requests"""
    account_name = request.GET.get('account', '')
    time_period = request.GET.get('period', '1month')
    
    # Calculate date range
    end_date = datetime.now()
    if time_period == '1month':
        start_date = end_date - timedelta(days=30)
    elif time_period == '3months':
        start_date = end_date - timedelta(days=90)
    elif time_period == '6months':
        start_date = end_date - timedelta(days=180)
    elif time_period == '1year':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    if account_name:
        transactions = Transaction.objects.filter(
            (Q(nameOrig__icontains=account_name) | Q(nameDest__icontains=account_name)) &
            Q(timestamp__gte=start_date)
        )
        
        # Prepare chart data
        monthly_data = {}
        for t in transactions:
            month_key = t.timestamp.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'amount': 0, 'count': 0}
            monthly_data[month_key]['amount'] += float(t.amount)
            monthly_data[month_key]['count'] += 1
        
        chart_data = {
            'labels': list(monthly_data.keys()),
            'amounts': [monthly_data[m]['amount'] for m in monthly_data.keys()],
            'counts': [monthly_data[m]['count'] for m in monthly_data.keys()]
        }
        
        return JsonResponse(chart_data)
    
    return JsonResponse({'error': 'No account specified'})