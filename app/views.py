from django.http.response import JsonResponse
from django.shortcuts import redirect, render,HttpResponseRedirect
from django.views import View 
from django.contrib import messages
from app.forms import CustomerRegistrationForm, CustomerProfileForm
from app.models import Customer,Product,Cart,OrderPlaced,Review
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

@login_required(login_url='login')    
def rateus(request):
    if request.method=="POST":
        user = request.user
        comment = request.POST['comment']
        rate = request.POST['rate']
        review = Review(user=user,comment=comment,rate=rate)
        review.save()
    rate = Review.objects.filter(user=request.user)
    if rate:
      context = {'rate':str(rate[0].rate),'comment':rate[0].comment,'user':rate[0].user,'time':rate[0].created_at}   
      return render(request,'app/rateus.html',context)
    return render(request,'app/rateus.html')

@login_required(login_url='login')        
def editrateus(request):
    if request.method=='POST':
        user = request.user
        comment = request.POST['comment']
        rate = request.POST['rate']
        review = Review.objects.get(user=user)
        review.comment = comment 
        review.rate = rate
        review.save()
        
    rate = Review.objects.filter(user=request.user)
    context = {'rate':str(rate[0].rate),'comment':rate[0].comment}
    return render(request,'app/editrateus.html',context)

class ProductView(View):
 def get(self,request):
  topwears = Product.objects.filter(category='TW')
  bottomwears = Product.objects.filter(category='BW')
  mobiles = Product.objects.filter(category='M')
  cart_count = Cart.objects.all().count()
  context = {'topwears':topwears,'bottomwears':bottomwears,'mobiles':mobiles,'cart_count':cart_count}    
  return render(request, 'app/home.html',context)

class ProductDetailView(View):
 def get(self,request,pk):
  product = Product.objects.get(pk=pk)
  item_already_in_cart = False
  if request.user.is_authenticated:
   item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
  cart_count = Cart.objects.all().count()
  return render(request, 'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'cart_count':cart_count})

def add_to_cart(request):
 if request.user.is_authenticated:
   user = request.user
   product_id = request.GET.get('prod_id')
   product = Product.objects.get(id=product_id)
   Cart(user=user,product=product).save()
   return redirect('/cart')
 else:
   return HttpResponseRedirect('/accounts/login/')


def autocomplete(request):
    if request.is_ajax():
        username_query = request.GET.get('username_query', '')
        usernames = (Product.objects.filter(title__istartswith=username_query).values_list('title', flat=True))
        data = {
            'usernames': usernames,
        }
        return JsonResponse(data)

def show_cart(request):
 if request.user.is_authenticated:
  user = request.user
  cart = Cart.objects.filter(user=user)
  amount = 0.0
  shipping_amount = 70.0
  cart_product = [p for p in Cart.objects.all() if p.user == user]
  if cart_product:
   for p in cart_product:
    tempamount = (p.quantity * p.product.discounted_price)
    amount += tempamount
    totalamount = amount + shipping_amount 
   cart_count = Cart.objects.all().count()
   return render(request,'app/addtocart.html',{'carts':cart,'amount':amount,'totalamount':totalamount,'cart_count':cart_count})
  else:
   cart_count = Cart.objects.all().count()
   return render(request,'app/emptycart.html',{'cart_count':cart_count})
 else:
  return HttpResponseRedirect('/accounts/login/')

def plus_cart(request):
 if request.user.is_authenticated:
   if request.method == 'GET':
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity+=1
    c.save()
    amount = 0.0
    shipping_amount = 70.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
      for p in cart_product:
       tempamount = (p.quantity * p.product.discounted_price)
       amount += tempamount

      data = {
         'quantity':c.quantity,
         'amount':amount,
         'totalamount':amount + shipping_amount
         }
      return JsonResponse(data)
 else:
   return HttpResponseRedirect('/accounts/login')


def minus_cart(request):
 if request.user.is_authenticated:
   if request.method == 'GET':
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity-=1
    c.save()
    amount = 0.0
    shipping_amount = 70.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
      for p in cart_product:
       tempamount = (p.quantity * p.product.discounted_price)
       amount += tempamount

      data = {
         'quantity':c.quantity,
         'amount':amount,
         'totalamount':amount + shipping_amount
         }
      return JsonResponse(data)
 else:
   return HttpResponseRedirect('/accounts/login')

def remove_cart(request):
 if request.user.is_authenticated:
  if request.method == 'GET':
   prod_id = request.GET['prod_id']
   c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
   c.delete()
   amount = 0.0
   shipping_amount = 70.0
   cart_product = [p for p in Cart.objects.all() if p.user == request.user]
   if cart_product:
    for p in cart_product:
     tempamount = (p.quantity * p.product.discounted_price)
     amount += tempamount

    data = {
      'amount':amount,
      'totalamount':amount + shipping_amount
       }
    return JsonResponse(data)
 else:
  return HttpResponseRedirect('/accounts/login/') 



def buy_now(request):
 if request.user.is_authenticated:
  cart_count = Cart.objects.all().count()
  return render(request, 'app/buynow.html',{'cart_count':cart_count})
 else:
  return HttpResponseRedirect('/accounts/login/')


def address(request):
 if request.user.is_authenticated:
  add = Customer.objects.filter(user=request.user)
  cart_count = Cart.objects.all().count()
  return render(request, 'app/address.html',{'add':add,'active':'btn-primary','cart_count':cart_count})
 else:
  return HttpResponseRedirect('/accounts/login/')

def orders(request):
 if request.user.is_authenticated:
  user = request.user
  op = OrderPlaced.objects.filter(user=user)
  cart_count = Cart.objects.all().count()
  return render(request, 'app/orders.html',{'order_placed':op,'cart_count':cart_count})
 else:
  return HttpResponseRedirect('/accounts/login/')

def mobile(request, data=None):
 if data == None:
  mobiles = Product.objects.filter(category='M')
 elif data == 'Sony' or data == 'Apple':
  mobiles = Product.objects.filter(category='M').filter(brand=data)
 elif data == 'below':
  mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=300)
 elif data == 'above':
  mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=300)
 cart_count = Cart.objects.all().count()
 return render(request, 'app/mobile.html',{'mobiles':mobiles,'cart_count':cart_count})

def topwear(request, data=None):
 if data == None:
  topwears = Product.objects.filter(category='TW')
 elif data == 'Lava' or data == 'lica':
  topwears = Product.objects.filter(category='TW').filter(brand=data)
 elif data == 'below':
  topwears = Product.objects.filter(category='TW').filter(discounted_price__lt=300)
 elif data == 'above':
  topwears = Product.objects.filter(category='TW').filter(discounted_price__gt=300)
 cart_count = Cart.objects.all().count()
 return render(request, 'app/topwear.html',{'topwears':topwears,'cart_count':cart_count})

def bottomwear(request, data=None):
  
 if data == None:
  bottomwears = Product.objects.filter(category='BW')
 elif data == 'Sony' or data == 'Lyra':
  bottomwears = Product.objects.filter(category='BW').filter(brand=data)
 elif data == 'below':
  bottomwears = Product.objects.filter(category='BW').filter(discounted_price__lt=300)
 elif data == 'above':
  bottomwears = Product.objects.filter(category='BW').filter(discounted_price__gt=300)
 cart_count = Cart.objects.all().count()
 return render(request, 'app/bottomwear.html',{'bottomwears':bottomwears,'cart_count':cart_count})




class CustomerRegistrationView(View):
 def get(self,request):
  form = CustomerRegistrationForm()
  return render(request, 'app/customerregistration.html',{'form':form})
 def post(self,request):
  form = CustomerRegistrationForm(request.POST)
  if form.is_valid():
   form.save()
   messages.success(request, 'Registered successfully')
   form = CustomerRegistrationForm()
  return render(request, 'app/customerregistration.html',{'form':form})


def checkout(request):
 if request.user.is_authenticated:
  user = request.user
  cart_items = Cart.objects.filter(user=user)
  add = Customer.objects.filter(user=user)
  cart_count = Cart.objects.all().count()
  amount = 0.0
  shipping_amount = 70.0
  totalamount = 0.0
  cart_product = [p for p in Cart.objects.all() if p.user == request.user]
  if cart_product:
   for p in cart_product:
    tempamount = (p.quantity * p.product.discounted_price)
    amount += tempamount
   totalamount = amount + shipping_amount
   return render(request, 'app/checkout.html',{'add':add,'cart_items':cart_items,'totalamount':totalamount,'cart_count':cart_count}) 
 
 else:
  return HttpResponseRedirect('/accounts/login/') 

def payment_done(request):
 if request.user.is_authenticated:
  user = request.user
  custid = request.GET.get('custid')
  customer = Customer.objects.get(id=custid)
  cart = Cart.objects.filter(user=user)
  for c in cart:
   OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
   c.delete()
  return redirect('/orders')
 else:
  return HttpResponseRedirect('/accounts/login/')


class ProfileView(View):
 def get(self,request):
  if request.user.is_authenticated:
   form = CustomerProfileForm()
   cart_count = Cart.objects.all().count()
   return render(request,'app/profile.html',{'form':form,'active':'btn-primary','cart_count':cart_count})
  else:
   return HttpResponseRedirect('/accounts/login/')
 
 def post(self,request):
  if request.user.is_authenticated:
   form = CustomerProfileForm(request.POST,request.FILES) 
   if form.is_valid():
      usr = request.user
      name = form.cleaned_data['name']
      mobile = form.cleaned_data['mobile']
      locality = form.cleaned_data['locality']
      city = form.cleaned_data['city']
      state = form.cleaned_data['state']
      zipcode = form.cleaned_data['zipcode']
      image = form.cleaned_data['image']
      reg = Customer(user=usr,name=name,mobile=mobile,locality=locality,city=city,state=state,zipcode=zipcode,image=image)
      reg.save()
      messages.success(request,'Profile updated!')
   return HttpResponseRedirect('/profile/')
  else:
   return HttpResponseRedirect('/accounts/login/')
  
def search(request):
   query=request.GET['query']
   if len(query)>78:
        allPosts=Product.objects.none()
   else:
        allPostsTitle= Product.objects.filter(title__icontains=query)
        allPostsAuthor= Product.objects.filter(brand__icontains=query)
        allPostsdesc = Product.objects.filter(category__icontains=query)
        allPosts=  allPostsTitle.union(allPostsAuthor,allPostsdesc)

   params={'allPosts': allPosts,'query': query}
   return render(request, 'app/search.html', params)                                                  