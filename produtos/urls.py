from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    # path('create-checkout-session/<int:id>', views.create_checkout_session, name="create_checkout_session"),
    path('create_payment/<int:id>', views.create_payment, name="create_payment"),
    path('success/', views.success, name="success"),
    path('error/', views.error, name="error"),
    path('stripe_webhook/', views.stripe_webhook, name="stripe_webhook"),
]
