import re
from rest_framework import serializers
from .models import Order, OrderItem, Product


class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False  # ✅ ДОБАВИТЬ
    )

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(
        many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname',
                  'phonenumber', 'address', 'products']

    def validate_phonenumber(self, value):
        if not re.match(r'^\+7[0-9]{10}$', value):
            raise serializers.ValidationError(
                "Введен некорректный номер телефона.")
        return value

    def create(self, validated_data):
        products_data = validated_data.pop('products')

        if not products_data:
            raise serializers.ValidationError(
                'Заказ должен содержать хотябы один товар')
        order = Order.objects.create(**validated_data)

        order_items = []
        for item_data in products_data:
            product = item_data['product']
            price = product.price
            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=price
            ))

        OrderItem.objects.bulk_create(order_items)

        return order
