from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from phonenumber_field.phonenumber import PhoneNumber


from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@csrf_exempt
def register_order(request):
    try:
        data = request.data

        if 'products' not in data:
            return Response({"error": "products: Обязательное поле."}, status=status.HTTP_400_BAD_REQUEST)
        if data['products'] is None:
            return Response({"error": "products: Это поле не может быть пустым."}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(data['products'], list):
            return Response({"error": "products: Ожидался list со значениями, но был получен 'str'."}, status=status.HTTP_400_BAD_REQUEST)
        if len(data['products']) == 0:
            return Response({"error": "products: Этот список не может быть пустым."}, status=status.HTTP_400_BAD_REQUEST)

        required_fields = ['firstname', 'lastname', 'phonenumber', 'address']
        missing_fields = [
            field for field in required_fields if field not in data]
        if missing_fields:
            return Response({"error": f"{', '.join(missing_fields)}: Обязательное поле."}, status=status.HTTP_400_BAD_REQUEST)

        for field in required_fields:
            if data[field] is None:
                return Response({"error": f"{field}: Это поле не может быть пустым."}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(data[field], str):
                return Response({"error": f"{field}: Not a valid string."}, status=status.HTTP_400_BAD_REQUEST)
            if data[field].strip() == '':
                return Response({"error": f"{field}: Это поле не может быть пустым."}, status=status.HTTP_400_BAD_REQUEST)

        from phonenumber_field.phonenumber import PhoneNumber
        phone = data['phonenumber'].strip()
        try:
            parsed_phone = PhoneNumber.from_string(phone)
            if not parsed_phone.is_valid():
                raise ValueError("Invalid phone number")
        except Exception:
            return Response(
                {"error": "phonenumber: Введен некорректный номер телефона."},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item_data in data['products']:
            try:
                product = Product.objects.get(id=item_data['product'])
            except Product.DoesNotExist:
                return Response(
                    {"error": f'products: Недопустимый первичный ключ "{item_data["product"]}"'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(
            firstname=data['firstname'].strip(),
            lastname=data['lastname'].strip(),
            phonenumber=phone,
            address=data['address'].strip()
        )

        # Создание позиций заказа
        for item_data in data['products']:
            product = Product.objects.get(id=item_data['product'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data.get('quantity', 1)
            )

        return Response({})

    except Exception as e:
        return Response({"error": str(e)}, status=400)
