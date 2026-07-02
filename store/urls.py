from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('search/', views.search_view, name='search'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.orders, name='orders'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.otp_verify_view, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Info Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('returns-exchange/', views.returns_exchange, name='returns_exchange'),
    path('shipping/', views.shipping, name='shipping'),
    path('size-guide/', views.size_guide, name='size_guide'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe'),

    # Order Actions
    path('orders/cancel/<str:order_number>/', views.cancel_order, name='cancel_order'),
    path('orders/return/<str:order_number>/', views.request_return, name='request_return'),
]

