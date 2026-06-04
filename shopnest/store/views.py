from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json
import datetime

from .models import *
from .utils import cookieCart, cartData, guestOrder



@login_required(login_url='login')
def store(request):

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()

	context = {
		'products':products,
		'cartItems':cartItems
	}

	return render(request, 'store/store.html', context)



@login_required(login_url='login')
def home(request):

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'items':items,
		'order':order,
		'cartItems':cartItems
	}

	return render(request, 'store/home.html', context)



@login_required(login_url='login')
def cart(request):

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'items':items,
		'order':order,
		'cartItems':cartItems
	}

	return render(request, 'store/cart.html', context)



@login_required(login_url='login')
def checkout(request):

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'items':items,
		'order':order,
		'cartItems':cartItems
	}

	return render(request, 'store/checkout.html', context)



@login_required(login_url='login')
def updateItem(request):

	data = json.loads(request.body)

	productId = data['productId']

	action = data['action']

	print('Action Selected:', action)

	print('Selected Product:', productId)


	customer = request.user.customer

	product = Product.objects.get(id=productId)

	order, created = Order.objects.get_or_create(
		customer=customer,
		complete=False
	)

	orderItem, created = OrderItem.objects.get_or_create(
		order=order,
		product=product
	)


	if action == 'add':

		orderItem.quantity = (orderItem.quantity + 1)

	elif action == 'remove':

		orderItem.quantity = (orderItem.quantity - 1)


	orderItem.save()


	if orderItem.quantity <= 0:
		orderItem.delete()


	return JsonResponse(
		'Product updated successfully',
		safe=False
	)



@login_required(login_url='login')
def processOrder(request):

	transaction_id = datetime.datetime.now().timestamp()

	data = json.loads(request.body)


	if request.user.is_authenticated:

		customer = request.user.customer

		order, created = Order.objects.get_or_create(
			customer=customer,
			complete=False
		)

	else:

		customer, order = guestOrder(request, data)


	total = float(data['form']['total'])

	order.transaction_id = transaction_id


	if total == order.get_cart_total:

		order.complete = True


	order.save()


	if order.shipping == True:

		ShippingAddress.objects.create(

			customer=customer,

			order=order,

			address=data['shipping']['address'],

			city=data['shipping']['city'],

			state=data['shipping']['state'],

			zipcode=data['shipping']['zipcode'],
		)


	return JsonResponse(
		'Order processed successfully!',
		safe=False
	)



def registerPage(request):

	if request.user.is_authenticated:
		return redirect('home')

	if request.method == 'POST':

		username = request.POST.get('username')

		password1 = request.POST.get('password1')

		password2 = request.POST.get('password2')


		if password1 == password2:

			if len(password1) >= 6:

				if User.objects.filter(username=username).exists():

					error = "Username already exists"

					return render(
						request,
						'store/register.html',
						{'error': error}
					)

				else:

					user = User.objects.create_user(
						username=username,
						password=password1
					)

					user.save()

					Customer.objects.create(
						user=user,
						name=user.username,
						email=''
					)

					return redirect('login')

			else:

				error = "Password must contain at least 6 characters"

				return render(
					request,
					'store/register.html',
					{'error': error}
				)

		else:

			error = "Passwords do not match"

			return render(
				request,
				'store/register.html',
				{'error': error}
			)

	return render(request, 'store/register.html')



def loginPage(request):

	if request.user.is_authenticated:
		return redirect('home')

	if request.method == 'POST':

		username = request.POST.get('username')

		password = request.POST.get('password')

		user = authenticate(
			request,
			username=username,
			password=password
		)

		if user is not None:

			login(request, user)

			return redirect('home')

	context = {}

	return render(request, 'store/login.html', context)



def logoutUser(request):

	logout(request)

	return redirect('login')