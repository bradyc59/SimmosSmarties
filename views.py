from django.http import HttpResponse, HttpResponseRedirect
from .models import Product, CaUser, ShoppingBasket, ShoppingBasketItems, OrderItems, Order
from .forms import *
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .permissions import admin_required
from django.contrib import messages


def index(request):
    all_p = Product.objects.all()
    categories = ProductCategory.objects.all()
    names = Product.objects.order_by().values('names').disticnt()
    featured = Product.objects.filter(featured=1).all()
    on_sale = Product.objects.filter(on_sale=1).all()

    num_featured = len(featured)
    num_on_sale = len(on_sale)

    return render(request, 'index.html', {
        'products': all_p,
        'featured': featured,
        'num_featured': num_featured,
        'on_sale': on_sale,
        'num_on_sale': num_on_sale,
        'categories': categories,
        'names': names
    })


@login_required
@admin_required
def editproduct(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        featured = request.POST.get('featured')
        if featured == 'on':
            featured = True
        else:
            featured = False
        on_sale = request.POST.get('on_sale')
        if on_sale == 'on':
            on_sale = True
        else:
            on_sale = False
        sale_price = request.POST.get('sale_price')
        if sale_price == None or sale_price == '':
            sale_price = 0

        product = Product.objects.filter(id=product_id).first()
        product.featured = featured
        product.on_sale = on_sale
        product.sale_price = sale_price
        product.save()

        messages.success(request, "Product edited.")
        return redirect('/product/' + str(product.id))



def register(request):
    return HttpResponse("Hello, welcome to Simmos Smarties")


@login_required
def all_products(request):
    all_p = Product.objects.all()
    return render(request, 'all_products.html', {'products': all_p})


@login_required
def remove_from_basket(request, product_id):
    if request.method == 'POST':
        product = Product.objects.filter(pk=product_id).first()
        sbi = ShoppingBasketItems.objects.filter(product=product).first()
        sbi.delete()
        return redirect('/basket/')


def product_single(request, product_id):
    single_product = Product.objects.filter(id=product_id).first()

    if single_product is None:
        e = 'We couldn\'t find a product with that ID.'
        return render(request, '404.html', {'error_message': e})

    names_products = Product.objects.filter(names=single_product.names).exclude(id=product_id).all()[:4]

    return render(request, 'single_product.html', {'product': single_product, 'names_products': names_products})


def products_by_category(request, category_name):
    category = ProductCategory.objects.filter(name__iexact=category_name).first()
    products = Product.objects.filter(category=category)

    if products is None or len(products) < 1:
        error_msg = 'We don\'t have any products under the category name "' + category_name + '".'

        return render(request, '404.html', {'error_message': error_msg})

    return render(request, 'products_by_category.html', {'products': products, 'category': category})


def products_by_names(request, names):
    products = Product.objects.filter(names__iexact=names).all()
    names = names.capitalize()

    if products is None or len(products) < 1:
        error_msg = 'We don\'t have any products under the names"' + names + '".'

        return render(request, '404.html', {'error_message': error_msg})

    return render(request, 'products_by_names.html', {'products': products, 'names': names})


@login_required
@admin_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    product.delete()

    messages.success(request, "Product deleted.")
    return redirect('/products/')


@login_required
def checkout(request):
    user = request.user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user).first()
    sbi = ShoppingBasketItems.objects.filter(basket=shopping_basket).all()

    if not sbi:
        return redirect('/')

    basket_total = 0
    subtotal = 0
    for product in sbi:
        subtotal = sum(int(product.quantity) * float(product.product.price) for product in sbi)
        subtotal = float("{:.2f}".format(subtotal))
        basket_total += product.quantity

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.user_id = request.user.id
            new_order.save()

            for product in sbi:
                oi = OrderItems(quantity=product.quantity, product=product.product, order=new_order).save()

            shopping_basket.delete()

            return render(request, 'thanks.html', {'order': new_order, 'sbi': sbi, 'subtotal': subtotal})
    else:
        form = CheckoutForm()
        return render(request, 'checkout.html', {'basket': sbi, 'subtotal': subtotal, 'basket_total': basket_total, 'form': form})


@login_required
def basket(request):
    user = request.user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user).first()
    sbi = ShoppingBasketItems.objects.filter(basket=shopping_basket).all()

    basket_total = 0
    subtotal = 0
    for product in sbi:
        if product.product.on_sale:
            subtotal += float(product.quantity) * float(product.product.sale_price)
        else:
            subtotal += float(product.quantity) * float(product.product.price)
    subtotal = float("{:.2f}".format(subtotal))
    for product in sbi:
        basket_total += product.quantity

    return render(request, 'basket.html', {'basket': sbi, 'subtotal': subtotal, 'basket_total': basket_total})


@login_required
@admin_required
def addproduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_product = form.save()
            return redirect('/product/' + str(new_product.id))
        return redirect('/products/')
    else:
        form = ProductForm()
        return render(request, 'form.html', {'form': form})


@login_required
@admin_required
def orders(request):
    orders = Order.objects.all()
    no_orders = len(orders)

    return render(request, 'orders.html', {'orders': orders, 'no_orders': no_orders})


@login_required
def thanks(request):
    return render(request, 'thanks.html')


class CaUserSignupView(CreateView):
    model = CaUser
    form_class = CaSignupForm
    template_name = 'causer_signup.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')


class AdminSignupView(CreateView):
    model = CaUser
    form_class = AdminSignupForm
    template_name = 'admin_signup.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')


class Login(LoginView):
    template_name = 'login.html'


@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def add_to_basket(request, product_id):
    if request.method == 'POST':
        user = request.user
        shopping_basket = ShoppingBasket.objects.filter(user_id=user).first()
        if not shopping_basket:
            shopping_basket = ShoppingBasket(user_id=user).save()
            shopping_basket = ShoppingBasket.objects.filter(user_id=user).first()

        product = Product.objects.get(pk=product_id)
        sbi = ShoppingBasketItems.objects.filter(basket=shopping_basket, product_id=product.id).first()
        if sbi is None:
            sbi = ShoppingBasketItems(basket=shopping_basket, product_id=product.id).save()
        else:
            sbi.quantity = sbi.quantity + 1
            sbi.save()
        #     request, 'single_product.html', {'product': product, 'added': True}
        messages.success(request, "Product added to basket.")
        return redirect('/product/' + str(product.id))
    return redirect('/')
