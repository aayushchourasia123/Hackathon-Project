from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.predictor, name="predictor"),
    path('result', views.FormInfo, name="FormInfo"),
    path('transactions/', views.all_transactions, name="all_transactions"),
    path('transaction-history/', views.transaction_history, name="transaction_history"),
    path('account-analysis/', views.account_analysis, name="account_analysis"),
    path('merchant-analysis/', views.merchant_analysis, name="merchant_analysis"),
    path('dataset-loader/', views.dataset_loader, name="dataset_loader"),
    path('api/chart-data/', views.get_chart_data, name="chart_data"),
]
