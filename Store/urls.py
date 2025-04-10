from django.urls import path
from . import views

urlpatterns = [
    # Authentication paths
    path('', views.landing, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile-related paths
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    # Product-related paths
    path('home/', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('update_cart/', views.update_cart, name='update_cart'),

    # Order-related paths
    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('track-orders/', views.track_orders, name='track_orders'),
    path('order/cod/', views.order_COD, name='order_COD'),
    path('order/online/', views.order_online, name='order_online'),

    # Search
    path('search/', views.search_view, name='search'),
]
