from rest_framework import serializers
from .models import Order, OrderItem, Product


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname',
                  'phonenumber', 'address', 'products']

    def validate_phonenumber(self, value):
        import re
        if not re.match(r'^\+7[0-9]{10}$', value):
            raise serializers.ValidationError(
                "Введен некорректный номер телефона.")
        return value

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for item_data in products_data:
            OrderItem.objects.create(order=order, **item_data)
        return order
