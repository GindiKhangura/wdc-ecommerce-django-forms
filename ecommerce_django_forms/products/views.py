from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotFound

from products.forms import ProductForm
from products.models import Product, Category, ProductImage


def products(request):
    # Get all products from the DB
    products = Product.objects.filter(active=True)

    # Get up to 4 featured products from the DB
    featured_products = products.filter(featured=True)[:4]

    # This is done for you. The request.session is a dictionary that contains
    # data that will be stored as long as the user is authenticated.
    # We are just initializing an empty list for the products_in_cart, that will
    # be use later on.
    request.session.setdefault('products_in_cart', [])
    request.session.save()

    # Render 'products.html' template sending products and featured products
    # as context
    return render(request, 'products.html', context={'products': products, 'featured_products': featured_products})


def create_product(request):
    if request.method == 'GET':
        # Create an empty instance of ProductFrom() and render "create_product.html"
        # sending the form as context under "product_form" key
        product_form = ProductForm()
        return render(request, 'create_product.html', context={'product_form': product_form})
    elif request.method == 'POST':
        # Create an instance of ProductFrom initializing it with the product
        # data that come in request.POST
        product_form = ProductForm(request.POST)
        if product_form.is_valid():

            # Create the product object while saving the form
            product = product_form.save()

            # Inside product_form.cleaned_data you will find the already
            # validated data for the product. Use the images urls there to
            # create a ProductImage object for each one.

            urls = []
            for i in range(1, 4):
                url = product_form.cleaned_data['image_{}'.format(i)]
                if url:
                    urls.append(url)

            for url in urls:
                ProductImage.objects.create(
                    product=product,
                    url=url
                )

            # Redirect to products view
            return redirect('products')

        # If form is not valid, re-render the 'create_product.html' sending the
        # product_form as context, which will have all the error messages included
        return render(request, 'create_product.html', context={'product_form': product_form})


def edit_product(request, product_id):
    # Get the product with given product_id from the DB
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'GET':
        # Create an instance of ProductForm sending the product in the "instance"
        # parameter. This will initialize all the fields in the form with the
        # data from our product.
        product_form = ProductForm(instance=product)

        # Render the 'edit_product.html' template sending the product and the
        # product_form as context
        return render(request, 'edit_product.html', context={'product_form': product_form, 'product': product})
    elif request.method == 'POST':
        # Create an instance of ProductForm sending the new data that come in
        # request.POST, and also the product inside the "instance" parameter
        product_form = ProductForm(request.POST, instance=product)
        if product_form.is_valid():
            product = product_form.save()

            urls = [request.POST.get(url) for url in ['image_{}'.format(i) for i in range(1,4)] if request.POST.get(url)]

            # Delete unneeded images.
            product_images = product.productimage_set.all()
            product_images.exclude(url__in=urls).delete()

            # Create needed images.
            # Calling bulk_create() would be better if we know which ones we need to create.
            for url in urls:
                product_images.get_or_create(product=product, url=url)

            return redirect('products')

        return render(request, 'edit_product.html', context={'product_form': product_form, 'product': product})


def delete_product(request, product_id):
    # Get the product with given product_id from the DB
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'GET':
        # Render the 'delete_product.html' template sending the product as context
        return render(request, 'delete_product.html', context={'product': product})
    elif request.method == "POST":
        # Delete the product and redirect to 'products' view
        product.delete()
        return redirect('products')


def toggle_featured(request, product_id):
    # Get the product with given product_id from the DB
    product = get_object_or_404(Product, id=product_id)

    # Toggle the boolean product.featured and save the product
    product.featured = not product.featured
    product.save()

    # Redirect to 'products' view
    return redirect('products')


def cart(request):
    # Get all the products ids from the products that have been added to the cart.
    # You can find this ids in the request.session dictionary, under the
    # 'products_in_cart' key. This was explained and initialized in the 'products' view
    products_ids = request.session['products_in_cart']

    # Get all the products from the DB with the ids above
    products_in_cart = Product.objects.filter(id__in=products_ids)

    # Render the 'cart.html' template sending the products_in_cart as context
    return render(request, 'cart.html', context={'products_in_cart': products_in_cart})


def add_to_cart(request):
    # Get the product_id that come in request.POST and add it to the
    # list under 'products_in_cart' key of request.session dictionary.
    # Do a .save() to the request.session. This is the way that Django recognizes
    # that something changes in the session.

    request.session['products_in_cart'].append(request.POST.get('product_id'))
    request.session.save()

    # Redirect to 'products' view
    return redirect('products')


def remove_from_cart(request):
    # Get the product_id that come in request.POST and remove it from the list
    # under 'products_in_cart' of request.session dictionary.
    # Do a .save() to the request.session.

    request.session['products_in_cart'].remove(request.POST.get('product_id'))
    request.session.save()

    # Redirect to 'cart' view
    return redirect('cart')
