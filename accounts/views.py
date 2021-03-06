from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.forms import inlineformset_factory
from .filters import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .decorators import *
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url = 'login')
@admin_only
def home(request):

    customers = Customer.objects.all()
    products = Order.objects.all()

    total_orders = products.count()
    delivered = products.filter(status='delivered').count()
    pending = products.filter(status='pending').count()
    context = {'customers':customers,'products':products, 'total_orders': total_orders, 'delivered':delivered, 'pending':pending}

    return render(request,'accounts/dashboard.html', context)

@unauthenticated_user
def loginPage(request):

    
     if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "Username and password is incorrect")
        

     return render(request,'accounts/login.html')

def logoutPage(request):
    logout(request)
    return redirect('login')

@login_required(login_url = 'login')
@allowed_user(allowed_roles=['user'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    print(orders)
    
    total_orders = orders.count()
    delivered = orders.filter(status='delivered').count()
    pending = orders.filter(status='pending').count()
  
    contexts = {'order' : orders, 'total_orders': total_orders, 'delivered':delivered, 'pending':pending}
    return render(request, 'accounts/user.html', contexts)

@unauthenticated_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            

            messages.success(request, "Account Created for " + username)
            return redirect('login')


    context = {'form': form}
    return render(request,'accounts/register.html', context)

@login_required(login_url = 'login')
@allowed_user(allowed_roles=['user'])
def accountSettings(request):

    customer = request.user.customer
    form = CustomerForm(instance=customer)


    if request.method == 'POST':
        form = CustomerForm(request.POST,request.FILES,instance=customer)

        if form.is_valid():
            form.save()

    context = {'form' : form}
    return render(request,'accounts/account_settings.html', context)


@login_required(login_url = 'login')
def products(request):
    products = Product.objects.all()
    return render(request,'accounts/products.html', {'products':products})


@login_required(login_url = 'login')
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    order = customer.order_set.all()
    order_count = order.count()
    MyFilter = OrderFilter(request.GET, queryset=order)
    order = MyFilter.qs
    context = {'customer':customer, 'order':order, 'order_count':order_count, 'myfilter':MyFilter}
    return render(request,'accounts/customer.html', context)

@login_required(login_url = 'login')
def createOrder(request, pk):


    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product','status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)

    #form = OrderForm(initial = {'customer':customer})

    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')


    context = {'formset' : formset}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url = 'login')
def updateOrder(request, pk):

    order = Order.objects.get(id=pk)

    form = OrderForm(instance = order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form':form}

    return render(request, 'accounts/order_form.html', context)

@login_required(login_url = 'login')
def deleteOrder(request, pk):
    
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')
        

    context = {'item': order}

    return render(request, 'accounts/delete.html', context)

