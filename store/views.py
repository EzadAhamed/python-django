from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate
from .auth_utils import frontend_login, frontend_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import uuid
import json
import random

from .models import (
    Product, Category, Cart, CartItem,
    Order, OrderItem, Wishlist, Review, Subscriber
)


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


def home(request):
    featured = Product.objects.filter(is_featured=True)[:6]
    new_arrivals = Product.objects.filter(is_new_arrival=True)[:8]
    bestsellers = Product.objects.filter(is_bestseller=True)[:4]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
        'categories': categories,
    })


def shop(request):
    products = Product.objects.filter(stock__gt=0)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', '-created_at')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_map = {
        'price_asc': 'price', 'price_desc': '-price',
        'name': 'name', 'newest': '-created_at'
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'query': query,
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        body = request.POST.get('body')
        if rating and title and body:
            Review.objects.update_or_create(
                product=product, user=request.user,
                defaults={'rating': rating, 'title': title, 'body': body}
            )
            messages.success(request, 'Review submitted!')
            return redirect('product_detail', slug=slug)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related': related,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'in_wishlist': in_wishlist,
        'sizes': product.get_sizes(),
    })


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, stock__gt=0)
    return render(request, 'store/category.html', {
        'category': category,
        'products': products,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    size = request.POST.get('size', 'M')
    quantity = int(request.POST.get('quantity', 1))

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, size=size)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    messages.success(request, f'"{product.name}" added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
    })


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        item.delete()
    else:
        item.quantity = quantity
        item.save()
    return redirect('cart')


def checkout(request):
    cart = get_or_create_cart(request)
    items = cart.items.all()
    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Email address is required to place an order.')
            return redirect('checkout')

        otp = str(random.randint(100000, 999999))
        request.session['pending_otp'] = otp
        request.session['otp_action'] = 'checkout'
        request.session['pending_checkout_data'] = request.POST.dict()

        send_mail(
            'Zavi Luxe Order Verification',
            f'Your OTP to confirm your order is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return redirect('verify_otp')

    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi"
    ]
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'items': items,
        'states': states,
    })


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_confirmation.html', {'order': order})


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user)
    return render(request, 'store/orders.html', {'orders': user_orders})


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'items': items})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        messages.info(request, 'Removed from wishlist.')
    else:
        messages.success(request, 'Added to wishlist!')
    return redirect(request.META.get('HTTP_REFERER', 'shop'))


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            frontend_login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'store/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if not email:
            messages.error(request, 'Email address is mandatory.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            otp = str(random.randint(100000, 999999))
            request.session['pending_otp'] = otp
            request.session['otp_action'] = 'register'
            request.session['pending_register_data'] = {
                'username': username,
                'email': email,
                'password': password1,
                'first_name': first_name,
                'last_name': last_name
            }
            
            send_mail(
                'Verify your Zavi Luxe Account Registration',
                f'Your OTP for account creation is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return redirect('verify_otp')
    return render(request, 'store/register.html')


def logout_view(request):
    frontend_logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


@login_required
def profile(request):
    user_orders = Order.objects.filter(user=request.user)[:5]
    return render(request, 'store/profile.html', {'orders': user_orders})


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    contact_success = False
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', 'No Subject')
        message = request.POST.get('message', '')

        full_name = f"{first_name} {last_name}".strip()
        email_subject = f"New Inquiry: {subject}"
        email_body = f"You have received a new inquiry from {full_name} ({email}).\n\nSubject: {subject}\n\nMessage:\n{message}"

        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Sending to the host
            fail_silently=False,
        )
        contact_success = True
    return render(request, 'store/contact.html', {'contact_success': contact_success})


def returns_exchange(request):
    return render(request, 'store/returns_exchange.html')


def shipping(request):
    return render(request, 'store/shipping.html')


def size_guide(request):
    return render(request, 'store/size_guide.html')


def cancel_order(request, order_number):
    # Work with the frontend dual-auth user
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to manage your orders.')
        return redirect('login')
    order = get_object_or_404(Order, order_number=order_number)
    # Ownership check using pk to avoid SimpleLazyObject comparison issues
    if not order.user or order.user.pk != request.user.pk:
        messages.error(request, 'You do not have permission to cancel this order.')
        return redirect('orders')
    if order.can_cancel:
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order_number} has been cancelled successfully.')
    else:
        messages.error(request, f'Order #{order_number} cannot be cancelled — it has already been shipped or delivered.')
    return redirect('orders')


def request_return(request, order_number):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to manage your orders.')
        return redirect('login')
    order = get_object_or_404(Order, order_number=order_number)
    if not order.user or order.user.pk != request.user.pk:
        messages.error(request, 'You do not have permission to request a return for this order.')
        return redirect('orders')
    if order.can_return:
        order.status = 'return_requested'
        order.save()
        send_mail(
            f'Return Request — Order #{order_number}',
            f'Hi {order.first_name},\n\nYour return request for order #{order_number} has been received. Our team will contact you within 24 hours to arrange the pickup.\n\nThank you for shopping with Zavi Luxe.',
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=True,
        )
        messages.success(request, f'Return request for order #{order_number} submitted. We\'ll contact you within 24 hours.')
    else:
        messages.error(request, f'Return window for order #{order_number} has expired or the order is not yet delivered.')
    return redirect('orders')


def search_view(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ) if query else Product.objects.none()
    return render(request, 'store/search.html', {'products': products, 'query': query})

def otp_verify_view(request):
    if 'pending_otp' not in request.session:
        messages.error(request, 'No pending OTP verification request found.')
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '')
        expected_otp = request.session.get('pending_otp')
        action = request.session.get('otp_action')

        if entered_otp == expected_otp:
            if action == 'register':
                data = request.session.get('pending_register_data')
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name']
                )
                frontend_login(request, user)
                messages.success(request, 'Account created successfully! Welcome to Zavi Luxe.')
            elif action == 'checkout':
                data = request.session.get('pending_checkout_data')
                cart = get_or_create_cart(request)
                items = cart.items.all()
                if not items:
                    messages.error(request, 'Your cart is empty.')
                    return redirect('cart')

                order_number = 'ZL' + uuid.uuid4().hex[:8].upper()
                total_cart = cart.get_total()
                shipping = 0 if total_cart >= 2999 else 99

                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    order_number=order_number,
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    email=data.get('email'),
                    phone=data.get('phone'),
                    address=data.get('address'),
                    city=data.get('city'),
                    state=data.get('state'),
                    pincode=data.get('pincode'),
                    country=data.get('country', 'India'),
                    total_amount=total_cart + shipping,
                    payment_method=data.get('payment_method', 'COD'),
                    notes=data.get('notes', ''),
                )
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        price=item.product.price,
                        quantity=item.quantity,
                        size=item.size,
                    )
                cart.items.all().delete()
                
                request.session.pop('pending_otp', None)
                request.session.pop('otp_action', None)
                request.session.pop('pending_checkout_data', None)
                
                send_mail(
                    'Order Confirmation - Zavi Luxe',
                    f'Thank you for your order {order.first_name}!\n\nYour order #{order_number} has been placed successfully for a total amount of ₹{order.total_amount}.\n\nWe will notify you once it is shipped.',
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=False,
                )
                
                messages.success(request, f'Order #{order_number} placed successfully!')
                return redirect('order_confirmation', order_number=order_number)

            
            request.session.pop('pending_otp', None)
            request.session.pop('otp_action', None)
            request.session.pop('pending_register_data', None)
            request.session.pop('pending_login_user_id', None)
            request.session.pop('pending_checkout_data', None)
            
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            
    return render(request, 'store/otp_verify.html')



def subscribe_newsletter(request):
    if request.method == 'POST':
        # Could be form data or JSON
        try:
            data = json.loads(request.body)
            email = data.get('email')
        except json.JSONDecodeError:
            email = request.POST.get('email')

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required.'}, status=400)

        # Check if already subscribed
        if Subscriber.objects.filter(email=email).exists():
            return JsonResponse({'status': 'info', 'message': 'You are already subscribed!'})

        # Save and send email
        Subscriber.objects.create(email=email)
        
        try:
            send_mail(
                'Welcome to Zavi Luxe!',
                'Thank you for subscribing to our newsletter! You will now receive exclusive updates and offers.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
        except Exception:
            pass # Fail silently if email backend fails

        return JsonResponse({'status': 'success', 'message': 'Successfully subscribed!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
