import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail,EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Product, Cart, CartItem, Order, OrderItem
from .forms import UserUpdateForm, ProfileUpdateForm


# Helper Function to Send Emails
def send_order_email(subject, template_name, context, recipient_list):
    message = render_to_string(template_name, context)
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    email.content_subtype = "html"  
    email.fail_silently = False
    email.send()


# Landing Page
def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'store/landing.html')


# Home Page View
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


# Profile View (For Logged-in Users)
@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


# Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['confirm_password']

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, 'Account created successfully!')
        return redirect('login')
    return render(request, 'accounts/signup.html')


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
    return render(request, 'accounts/login.html')


# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('login')


# Product Search View
@login_required
def search_view(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, 'store/search.html', {'results': results, 'query': query})


# Product Detail View
@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})


# Add to Cart View
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


# Cart View
@login_required
def cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart).select_related('product')
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})


# Checkout View
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart).select_related('product')
    total = sum(item.product.price * item.quantity for item in items)

    if not items.exists():
        return redirect('cart')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        request.session['cart_items'] = [
            {'product_id': item.product.id, 'quantity': item.quantity, 'price': float(item.product.price)}
            for item in items
        ]

        request.session['total'] = float(total)
        request.session['payment_method'] = payment_method
        
        if payment_method == 'COD':
            return redirect('order_COD')
        elif payment_method == 'ONLINE':
            return redirect('order_online')
        else:
            messages.error(request, "Invalid payment method selected.")
            return redirect('checkout')
    return render(request, 'store/checkout.html', {'total': total, 'items': items})



# Order Confirmation View
def order_confirmation(request):
    order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    if not order:
        messages.error(request, "No order found!")
        return redirect('home')

    order_items = OrderItem.objects.filter(order=order)

    subject = 'Order Confirmation from EveryDay Store'
    from_email = 'Store@EveryDay.com'
    to_email = [request.user.email]

    text_content = f"Thank you for your order, {request.user.username}!\n\n" \
                   f"Order ID: {order.id}\n" \
                   f"Total Amount: Rs. {order.total}\n" \
                   f"Payment Method: {order.payment_method}\n\n" \
                   "We are processing your order and will notify you once it has shipped. " \
                   "Thank you for shopping with us!"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Order Confirmation</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f2f2f2;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                background-color: white;
                max-width: 600px;
                margin: 40px auto;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .email-header {{
                background-color: #007bff;
                color: white;
                text-align: center;
                padding: 20px;
            }}
            .email-body {{
                padding: 20px;
                color: #333;
            }}
            h2 {{
                color: #007bff;
            }}
            p {{
                line-height: 1.6;
                margin: 10px 0;
            }}
            .order-details {{
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
            }}
            .order-details p {{
                margin: 5px 0;
            }}
            .button {{
                background-color: #007bff;
                color: white;
                padding: 12px 25px;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
                margin-top: 15px;
                transition: background-color 0.3s;
            }}
            .button:hover {{
                background-color: #0056b3;
            }}
            .footer {{
                background-color: #f4f4f4;
                text-align: center;
                padding: 15px;
                font-size: 12px;
                color: #666;
            }}
            .footer a {{
                color: #007bff;
                text-decoration: none;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>Order Confirmation</h1>
            </div>
            <div class="email-body">
                <h2>Hello {request.user.username},</h2>
                <p>Thank you for your order! We appreciate your trust in us and are excited to serve you.</p>
                <div class="order-details">
                    <p><strong>Order ID:</strong> {order.id}</p>
                    <p><strong>Total Amount:</strong> Rs. {order.total}</p>
                    <p><strong>Payment Method:</strong> {order.payment_method}</p>
                </div>
                <p>We are processing your order and will notify you once it has shipped.</p>
                
                
            </div>
            <div class="footer">
                <p>Thank you for shopping with us!<br>Best regards,<br><strong>EveryDay Store</strong></p>
                
            </div>
        </div>
    </body>
</html>
    """

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()

    return render(request, 'store/order_confirm.html', {
        'order': order,
        'items': order_items,
        'total': order.total,
        'payment_method': order.payment_method,
    })




# Edit Profile View
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.pic = profile.pic or 'profile_pics/default_profile.png'
            profile.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})


# Update Cart View
@login_required
def update_cart(request):
    if request.method == "POST":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        empty_cart = True

        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                try:
                    product_id = int(key.split('_')[1])
                    new_quantity = int(value)
                    cart_item = CartItem.objects.get(product_id=product_id, cart=cart)
                    if new_quantity > 0:
                        cart_item.quantity = new_quantity
                        cart_item.save()
                        empty_cart = False
                    else:
                        cart_item.delete()
                except (CartItem.DoesNotExist, ValueError):
                    continue

        return render(request, 'store/cart.html', {'items': None, 'total': 0}) if empty_cart else redirect('cart')
    return redirect('cart')


# Track Orders View
@login_required
def track_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/track_order.html', {'orders': orders})


# Cash on Delivery Order View
@login_required
def order_COD(request):
    total = request.session.get('total', 0)
    cart_items = request.session.get('cart_items', [])
    payment_method = request.session.get('payment_method', 'COD')

    if not cart_items:
        messages.error(request, "No items found for order!")
        return redirect('cart')

    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total=total,
                payment_method=payment_method,
                payment_status='Unpaid',
                status='Pending'
            )

            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                if product.stock < item['quantity']:
                    messages.error(request, f"Not enough stock for {product.name}!")
                    order.delete()
                    return redirect('cart')
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )
                product.stock -= item['quantity']
                product.save()

            CartItem.objects.filter(cart__user=request.user).delete()

           
            context = {
                'user': request.user,
                'order': order,
                'items': cart_items,
                'total': total,
                'payment_method': payment_method
            }
            send_order_email(
                subject=f"Order Confirmation - #{order.id}",
                template_name='emails/email.html',
                context=context,
                recipient_list=[request.user.email]
            )

            del request.session['cart_items']
            del request.session['total']
            del request.session['payment_method']

            messages.success(request, "Order placed successfully! Check your email for confirmation.")
            return redirect('order_confirmation') 
    return render(request, 'emails/Order_COD.html', {'total': total, 'items': cart_items, 'payment_method': payment_method})



# Online Payment Order View
@login_required
def order_online(request):
    total = request.session.get('total', 0)
    cart_items = request.session.get('cart_items', [])
    payment_method = request.session.get('payment_method', 'ONLINE')

    if not cart_items:
        messages.error(request, "No items found for order!")
        return redirect('cart')

    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total=total,
                payment_method=payment_method,
                payment_status='Pending',
                status='Pending'
            )

            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                if product.stock < item['quantity']:
                    messages.error(request, f"Not enough stock for {product.name}!")
                    order.delete()
                    return redirect('cart')
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )
                product.stock -= item['quantity']
                product.save()

            # Clear Cart
            CartItem.objects.filter(cart__user=request.user).delete()

            context = {
                'user': request.user,
                'order': order,
                'items': cart_items,
                'total': total,
                'payment_method': payment_method
            }
            send_order_email(
                subject=f"Order Confirmation - #{order.id}",
                template_name='emails/email.html',
                context=context,
                recipient_list=[request.user.email]
            )

            del request.session['cart_items']
            del request.session['total']
            del request.session['payment_method']

            messages.success(request, "Order placed successfully! Check your email for confirmation.")
            return redirect('order_confirmation')

    return render(request, 'emails/Order_online.html', {'total': total, 'items': cart_items, 'payment_method': payment_method})