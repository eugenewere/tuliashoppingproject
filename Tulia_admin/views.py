from django.contrib import messages
# from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

# from clare_project.Tulia_admin.forms import *
# from clare_project.Tulia_admin.models import *
from Tulia_admin.utils import render_to_pdf
# e76f0fd3301e2ec842482c7c83efaba62b09915f252e66bac27140861b8a7bf6
#


from Tulia.forms import *
from Tulia_admin.forms import *
from Tulia_admin.models import *

login_required()
def home(request):
    revenues = Order_payment.objects.all()
    checkouts = Checkout.objects.filter(status__exact='PENDING').order_by('-created_at')

    context ={
        'revenue':sum(i.amount for i in revenues),
        'products':Product.objects.all().count(),
        'all_orders':Order_Product.objects.filter(checkout__isnull=False, checkout__status='PAID').count(),
        'pending_orders':Order_Product.objects.filter(checkout__isnull=False, checkout__status='PENDING').count(),
        'buyer_orders': checkouts,
    }
    return render(request, 'tulia/home/index.html', context)

def deleteproducts(request, product_id):
    product = Product.objects.filter(id=product_id)
    product.delete()
    messages.success(request, 'Product Deleted Successfully')

    return redirect('TuliaAdmin:products')
@csrf_exempt
# @login_required()
def product_featured(request):
    if request.is_ajax():
        product_id = request.POST.get('product_id')
        product = Product.objects.filter(id=product_id).first()
        if product.feat_product == "FEATURED":
            Product.objects.filter(id=product_id).update(feat_product="NORMAL")
            context = {
                'results': 'normal_success'
            }
        elif product.feat_product == "NORMAL":
            Product.objects.filter(id=product_id).update(feat_product="FEATURED")
            context = {
                'results': 'featured_success'
            }
        return JsonResponse(context)

def products(request):
    brands = Brand.objects.all()
    categories = Category.objects.all()
    user = request.user.id
    seller = Seller.objects.filter(user_ptr_id=user).first()
    products = Product.objects.filter(seller=seller).order_by('-created_at')
    variants = Variant.objects.all()

    context = {
        'seller': Seller.objects.all(),
        'products': products,
        'sellerz': seller,

        'brands': brands,
        'categories': categories,
        # 'variantOptions':variantOptions,
        'variants': variants,
    }

    return render(request, 'tulia/product/product.html', context)

def addproducts(request):
    user = request.user.id
    seller = Seller.objects.filter(user_ptr_id=user).first()
    if request.method == 'POST' and request.is_ajax():
        name = request.POST.get('name')
        bran = request.POST.get('product_brand')
        sdesc = request.POST.get('short_description')
        ldesc = request.POST.get('long_description')
        img = request.FILES.get('featured_url')
        vat = request.POST.get('vat_status')
        categor = request.POST.get('category')
        invtry = request.POST.get('quantity')
        brand = Brand.objects.filter(id=bran).first()
        category = Category.objects.filter(id=categor).first()
        images = request.FILES.getlist('other_images[]')
        cost = request.POST.get('unit_cost')
        form = ProductForm(request.POST, request.FILES)
        print(form)

        if form.is_valid():
            new_product = Product.objects.create(
                name=name,
                unit_cost=cost,
                product_brand=brand,
                short_description=sdesc,
                long_description=ldesc,
                seller=seller,
                featured_url=img,
                vat_status=vat,
                category=category,
                status='VERIFIED'
            )
            Inventory.objects.create(
                product=new_product,
                quantity=invtry,
            )
            for upload in images:
                image_file = {
                    'image': upload,
                }
                image_form = ImagesForm({'product': new_product.id}, image_file)
                image_form.save()

            for variant_option_id in request.POST.getlist('variant_options[]'):
                variant_option = Variant_Option.objects.filter(id=int(variant_option_id)).first()

                if variant_option is not None:
                    Product_Variant_Options.objects.create(
                        product=new_product,
                        variant_options=variant_option
                    )
            data = {
                'results': 'success',
                'success': 'Product Added Successfully added'
            }
            return JsonResponse(data, safe=False)
        else:
            form1 = ProductForm(request.POST, request.FILES)
            print(ProductForm)
            data = {
                'results': 'error',
                'error': 'Error Adding The Product',
                'form': form1,
            }
            return render(request,'tulia/product/error.html', data)
    return redirect('TuliaAdmin:products')

# @login_required()
def category(request):
    independent_categories = []
    categories = Category.objects.all()
    for category in categories:
        if not category.is_child:
            independent_categories.append(category)

    context = {
        'categories': set(independent_categories),
    }
    return render(request, 'tulia/product/category.html', context)
# @login_required()
def addcategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        category = request.POST['name']
        if not Category.objects.filter(name__exact=category):
            if form.is_valid():
                form.save()
                messages.success(request, 'Category Added Successfully')
            else:
                messages.error(request, 'Category Not Added')
        else:
            messages.error(request, 'Category Exists')
    return redirect('TuliaAdmin:category')
# @login_required()
def deletecategory(request, category_id):
    category = Category.objects.filter(id=category_id)
    category.delete()
    return redirect('TuliaAdmin:category')
# @login_required()
def editcategory(request, category_id):
    category = Category.objects.filter(id=category_id).first()
    categoryform = CategoryForm(request.POST, instance=category)
    if categoryform.is_valid():
        categoryform.save()
        messages.success(request, "Category updated successfully")
    else:
        messages.error(request, "Error Updating Category")
    return redirect('TuliaAdmin:category')
# @login_required()
def view_sub_category(request, category_id):
    sub_categories = Category.objects.filter(parent_id=category_id)
    categories = Category.objects.all()
    context = {
        "categories": categories,
        "sub_categories": sub_categories,
        # 'brand_count':new_brand_count,

    }
    return render(request, 'tulia/product/subcategory.html', context)





def brand(request):
    brands = Brand.objects.all()
    categories = Category.objects.all()

    context = {
        'brands': brands,
        'categories': categories,
    }
    return render(request, 'tulia/product/brand.html', context)

def add_brand(request):
    if request.method == 'POST':
        brand_form = AddBrandForm(request.POST)

        if brand_form.is_valid():
            brand_form.save()
            messages.success(request, 'Brand Added Successfully')
            return redirect('TuliaAdmin:brand')
        else:
            messages.error(request, 'Brand Not Added')
            return redirect('TuliaAdmin:brand')


    return redirect('TuliaAdmin:brand')

def brand_edit(request, brand_id):
    if request.method == 'POST':
        brand = Brand.objects.get(id=brand_id)
        form = AddBrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand Update Successful')
            return redirect('TuliaAdmin:brand')
        else:
            messages.error(request, 'Form Invalid')
            return redirect('TuliaAdmin:brand')

def brand_delete(request, brand_id):
    brand = Brand.objects.filter(id=brand_id).first()
    brand.delete()
    messages.success(request, 'Brand Deleted Successfully')
    return redirect('TuliaAdmin:brand')





def carousel(request):
    carousels = Carousel.objects.all()
    context = {
        'carousels': carousels,

        'seller': Seller.objects.filter(status='VERIFIED'),
        'products': Product.objects.filter(status='VERIFIED')

    }
    return render(request, 'tulia/product/carousel.html', context)


def addcarousel(request):
    if request.method == 'POST':
        carouselForm = CarouselImageForm(request.POST, request.FILES)
        if carouselForm.is_valid():
            carouselForm.save()
            messages.success(request, 'Advertisment Image Added Successfully')
            return redirect('TuliaAdmin:carousel')
        else:
            messages.error(request, 'Advertisment Image not Added ')
            return redirect('TuliaAdmin:carousel')
    return redirect('TuliaAdmin:carousel')

def carousel_delete(request, carousel_id):
    carousel = Carousel.objects.filter(id=carousel_id).first()
    carousel.delete()
    messages.success(request, 'Advertisment Image Deleted Succesfully')

    return redirect('TuliaAdmin:carousel')

def carousel_edit(request, carousel_id):
    carousel = Carousel.objects.filter(id=carousel_id).first()
    form = CarouselImageForm(request.POST, request.FILES, instance=carousel)
    if form.is_valid():
        form.save()
        messages.success(request, 'Advertisment Image Updated Succesfully')

    return redirect('TuliaAdmin:carousel')


def variants(request):
    user = request.user.id
    seller = Seller.objects.filter(user_ptr_id=user).first()
    variants = Variant.objects.filter(seller=seller).all()
    variant_options = Variant_Option.objects.filter(seller=seller).order_by("variant")
    context = {
        'variants': variants,
        'variant_options': variant_options,
        'seller': seller,
    }
    return render(request, 'tulia/product/variants.html', context)


def variant_delete(request, variant_id):
    variant = Variant.objects.filter(id=variant_id).first()
    variant.delete()
    messages.success(request, 'Variant Deleted Successfully')
    return redirect('TuliaAdmin:variants')


def variant_edit(request,  variant_id):
    if request.method == 'POST':
        variant = Variant.objects.filter(id=variant_id).first()
        variant_form = VariantUpdateForm(request.POST, instance=variant)
        print(variant_form)
        if variant_form.is_valid():
            variant_form.save()
            messages.success(request, 'Variant Update Successful')
            return redirect('TuliaAdmin:variants')
        else:
            messages.error(request, 'Variant Error Updating')
            return redirect('TuliaAdmin:variants')
    return redirect('TuliaAdmin:variants')


def addvariants(request):
    user = request.user.id
    seller = Seller.objects.filter(user_ptr_id=user).first()
    if request.method == 'POST':

        variant_form = VariantForm(request.POST)
        if variant_form.is_valid():
            variant_form.save()
            messages.success(request, 'Variant Added Successfully')
            return redirect('TuliaAdmin:variants')
        else:
            messages.error(request, 'Error Adding Variants')
            return redirect('TuliaAdmin:variants')

    return redirect('TuliaAdmin:variants')

def variants_options(request):
    user = request.user.id
    seller = Seller.objects.filter(user_ptr_id=user).first()

    if request.method == 'POST':
        variantOptions = VariantOptionForm(request.POST)
        if variantOptions.is_valid():
            variantOptions.save()
            messages.success(request, 'Variant Options Added Successfully')
            return redirect('TuliaAdmin:variants')
        else:
            messages.error(request, 'Variant Option Not Added')
    return redirect('TuliaAdmin:variants')


def variants_options_edit(request, variant_option_id):
    if request.method == 'POST':
        variant_option = Variant_Option.objects.filter(id=variant_option_id).first()
        variant_option_form = VariantUpdateOptionForm(request.POST, instance=variant_option)
        if variant_option_form.is_valid():
            variant_option_form.save()
            messages.success(request, 'Variant Options Update Successful')
            return redirect('TuliaAdmin:variants')
        else:
            messages.success(request, 'Variant Options Error Updating')
            return redirect('TuliaAdmin:variants')


def variants_options_delete(request, variant_option_id):
    variantOption = Variant_Option.objects.filter(id=variant_option_id).first()
    variantOption.delete()
    messages.success(request, 'Variant Option Deleted Successfully')
    return redirect('TuliaAdmin:variants')





@login_required()
def view_regions(request):
    user=request.user.id
    seller =Seller.objects.filter(id=user).first()
    if request.method == 'POST':
        region=request.POST['name']
        region_cost = request.POST['region_cost']

        Region.objects.create(
            name=region,
            region_cost=region_cost,
            seller=seller,
        )
        messages.success(request, 'A Region And Its Respective Cost Has Been Added')
        return redirect("TuliaAdmin:view-regions")



    regions = Region.objects.filter(seller=seller)
    sellers = Seller.objects.all()

    context = {
        'regions': regions,
        'sellers': sellers,
    }
    return render(request, 'tulia/region/region.html', context)

@login_required()
def edit_regions(request, region_id):
    if request.method == 'POST':
        region = request.POST['name']
        region_cost = request.POST['region_cost']
        Region.objects.filter(id=region_id).update(
            name=region,
            region_cost=region_cost,
        )
        messages.success(request, 'Region Update Successful')
        return redirect("TuliaAdmin:view-regions")


@login_required()
def delete_regions(request, region_id):
    region = Region.objects.filter(id=region_id).first()
    region.delete()
    messages.success(request, 'Region Deleted Successfully')
    return redirect("TuliaAdmin:view-regions")


def orders(request):
    checkouts = Checkout.objects.filter(status__exact='PENDING').order_by('-created_at')
    context={
        'buyer_orders': checkouts,
    }
    return render(request, 'tulia/orders/new_orders.html', context)


def buyerOrders(request, reference_code):

    buyer_orders = []
    admin_orders = []
    user = request.user.id


    seller = Seller.objects.filter(user_ptr_id=user).first()

    orders = Order_Product.objects.filter(
        checkout__reference_code__exact=reference_code,
        product__seller=seller,
    ).order_by('-created_at')
    # print(orders)
    # for order in orders:
    #     buyer_orders.append(order)

    orderss = Order_Product.objects.filter(checkout__reference_code__exact=reference_code, checkout__isnull=False, checkout__status__iexact='PENDING',).order_by('-created_at')



    context = {
        # 'buyer':buyer,
        'orders':orders,
        'admin_orders':orderss
    }

    return render(request, 'tulia/orders/buyer_orders.html', context)

def edit_payments(request, Order_payment_id):
    orderPay = Order_payment.objects.filter(id=Order_payment_id).first()
    dbcheckout = Checkout.objects.filter(order_payment=orderPay).first()

    if request.method == "POST":

        dbamount = orderPay.amount
        dbpayrefcode =  orderPay.payment_refrence
        dbbalance =orderPay.balance
        dbshipping = dbcheckout.shipping_cost

        amount = request.POST.get("amount")
        # ref_code = request.POST.get("ref_code")
        payment_reference = request.POST.get("payment_reference")
        shippingcost = request.POST.get("shipping_cost")


        if shippingcost is not None:
            shipping_cost = shippingcost
        else:
            shipping_cost = dbshipping



        if dbpayrefcode == payment_reference:
            newUpdatedpayref = payment_reference
        else:
            newUpdatedpayref = dbpayrefcode

        form_checkout = Checkout.objects.filter(order_payment = orderPay).first()

        UpdatedShipping = float(shipping_cost)
        newUpdatedAmmount = float(dbamount) + float(amount)
        balance = float(dbbalance) - float(amount)
        new_amount = float(UpdatedShipping) + float(newUpdatedAmmount)
        newpayref = newUpdatedpayref
        negativebalance = float(form_checkout.total) - float(newUpdatedAmmount)


        if float(newUpdatedAmmount) >= float(form_checkout.total) :
            Order_payment.objects.filter(id=orderPay.id).update(
                checkout_id=form_checkout.id,
                amount=float(new_amount),
                payment_refrence=newpayref,
                balance= float(negativebalance),
            )
            checkout=Checkout.objects.filter(id=form_checkout.id).update(
                status='PAID',
                shipping_cost=float(UpdatedShipping),
                amount_paid=float(new_amount),
            )
            orders = Order_Product.objects.filter(checkout=form_checkout.id)
            for order in orders:
                product_inventory_count = order.product.inventory_qty
                order_quantity = order.quantity
                remaining_quantity = product_inventory_count - order_quantity
                print(product_inventory_count, order_quantity, remaining_quantity)
                Inventory.objects.filter(product_id=order.product.id).update(
                    quantity=remaining_quantity,
                )

            messages.success(request, 'Order Payment Is Completed')
        else:
            Order_payment.objects.filter(id=orderPay.id).update(
                checkout_id=form_checkout.id,
                amount=float(new_amount),
                payment_refrence=newpayref,
                balance=float(balance),
            )
            Checkout.objects.filter(id=form_checkout.id).update(
                status='PENDING',
                amount_paid=float(new_amount),
                shipping_cost = float(UpdatedShipping)
            )
            messages.info(request, 'Order Payment Is Not Payed Fully')
    return redirect('TuliaAdmin:payments')


def payments(request):
    seller = Seller.objects.filter(user_ptr_id=request.user.id).first()
    if request.method == "POST":

        amount = request.POST.get("amount")
        ref_code = request.POST.get("ref_code")
        payment_reference = request.POST.get("payment_reference")
        shipping_cost = request.POST.get("shipping_cost")
        form_checkout = Checkout.objects.filter(reference_code__iexact=ref_code).first()

        if shipping_cost is not None:
            new_shipping_cost =shipping_cost
        else:
            new_shipping_cost = 0

        balance = float(form_checkout.total) - float(amount)
        new_amount = float(new_shipping_cost) + float(amount)



        if float(amount) >= float(form_checkout.total):
            Order_payment.objects.create(
                checkout_id=form_checkout.id,
                amount=float(new_amount),
                seller=seller,
                payment_refrence=payment_reference,
                balance=float(balance),
            )
            Checkout.objects.filter(id=form_checkout.id).update(
                status='PAID',
                shipping_cost=float(new_shipping_cost),
                amount_paid=amount,
            )


            orders = Order_Product.objects.filter(checkout=form_checkout.id)

            for order in orders:
                print(order)
                product_inventory_count =  order.product.inventory_qty
                order_quantity = order.quantity
                remaining_quantity = (product_inventory_count) - (order_quantity)
                print(product_inventory_count, order_quantity, remaining_quantity)
                Inventory.objects.filter(product=order.product).update(
                    quantity=int(remaining_quantity),
                )
            messages.success(request, 'Order Payment Is Completed')
        else:
            Order_payment.objects.create(
                checkout_id=form_checkout.id,
                amount=float(amount),
                seller=seller,
                payment_refrence=payment_reference,
                balance=float(balance),

            )
            Checkout.objects.filter(id=form_checkout.id).update(
                status='PENDING',
                amount_paid=amount,
                shipping_cost = float(new_shipping_cost)
            )
            messages.info(request, 'Order Payment Is Not Payed Fully')

    paymentsz=[]
    sellerrr = Seller.objects.filter(id=request.user.id).first()
    payments = Order_payment.objects.filter(seller=sellerrr).order_by('-created_at')
    for pay in payments:
        paymentsz.append(pay)

    checkoutsz = []
    checkouts = Checkout.objects.filter(order_payment__payment_refrence__isnull=True, status='PENDING', order_product__product__seller_id=request.user.id,)
    for checkout in checkouts:
        checkoutsz.append(checkout)
    context={
        # 'checkouts':checkoutsz,
        'checkouts':list(set(checkoutsz)),
        'payments':paymentsz
        # 'payments':list(set(paymentsz)),
    }
    return render(request, 'tulia/payments/payment.html', context)

def logout_view(request):
    logout(request)
    return redirect('Shoppy:shoppy-login')


def ListOrders(request):
    user=request.user.id
    import datetime
    month_data = []
    months_choices=[]
    months_choices_int=[]
    for i in range(1,13):
        months_choices.append(( datetime.date(2008, i, 1).strftime('%B')[0:3]))

    labels2 = months_choices

    for z in range(1,13):
        months_choices_int.append((datetime.date(2008, z, 1).strftime('%m')))

    seller = Seller.objects.filter(id=user).first()
    for months_choice in months_choices_int:
        month_data.append(Order_Product.objects.filter(checkout__status='PAID', product__seller=seller,  created_at__month=months_choice).count())
    defaultData2 = month_data
    context2={
        'labels2':labels2,
        'defaultData23':defaultData2,


    }

    month_data = {}
    return JsonResponse(context2)


# offer
@login_required()
def viewAllReports(request):

    return render(request,'tulia/reports/reports.html')
# reports

class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        orders = Order_Product.objects.filter(checkout__isnull=False)
        template = get_template('tulia/invoice.html')
        print(template)
        context = {
            'orders': orders,
        }
        html = template.render(context)
        pdf = render_to_pdf('tulia/invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" % ("12341231")
            content = "inline; filename='%s'" % (filename)
            # download = request.GET.get("download")
            response['Content-Disposition'] = content
            # if download:
            #     content = "attachment; filename='%s'" % (filename)
            return pdf
        return HttpResponse("Not found")

class GenerateProductPDF(View):
    def get(self, request, *args, **kwargs):
        user = request.user.id
        products =Product.objects.filter(seller=user)
        template = get_template('tulia/productspdf.html')
        context = {
            'products': products,
        }
        html = template.render(context)
        pdf = render_to_pdf('tulia/productspdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" % ("12341231")
            content = "inline; filename='%s'" % (filename)
            # download = request.GET.get("download")
            response['Content-Disposition'] = content
            # if download:
            #     content = "attachment; filename='%s'" % (filename)
            return pdf
        return HttpResponse("Not found")

