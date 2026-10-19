from rest_framework import serializers
from .models import VoucherTransaction, VoucherItem, VoucherCanvassSupplier, VoucherReferenceLibrary
from decimal import Decimal

class VoucherReferenceLibrarySerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = VoucherReferenceLibrary
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class VoucherCanvassSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherCanvassSupplier
        fields = '__all__'
        read_only_fields = ['id', 'voucher']


class VoucherItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherItem
        fields = '__all__'
        read_only_fields = ['id', 'voucher', 'total_cost']


class VoucherTransactionListSerializer(serializers.ModelSerializer):
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = VoucherTransaction
        fields = [
            'id', 'transaction_code', 'transaction_type', 'transaction_type_display',
            'status', 'status_display', 'liquidation_code', 'liquidation_month',
            'ada_number', 'ada_date', 'ors_number', 'ors_date',
            'payee_supplier_name', 'cheque_number', 'cheque_date',
            'total_amount', 'dv_gross_amount', 'dv_net_amount',
            'items_count', 'created_at', 'updated_at'
        ]


class VoucherTransactionDetailSerializer(serializers.ModelSerializer):
    items = VoucherItemSerializer(many=True, required=False)
    canvass_suppliers = VoucherCanvassSupplierSerializer(many=True, required=False)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = VoucherTransaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        suppliers_data = validated_data.pop('canvass_suppliers', [])
        voucher = VoucherTransaction.objects.create(**validated_data)

        for idx, item_data in enumerate(items_data, start=1):
            item_data['item_number'] = item_data.get('item_number', idx)
            VoucherItem.objects.create(voucher=voucher, **item_data)

        for supplier_data in suppliers_data:
            VoucherCanvassSupplier.objects.create(voucher=voucher, **supplier_data)

        voucher.compute_totals()
        return voucher

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        suppliers_data = validated_data.pop('canvass_suppliers', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for idx, item_data in enumerate(items_data, start=1):
                item_data['item_number'] = item_data.get('item_number', idx)
                VoucherItem.objects.create(voucher=instance, **item_data)

        if suppliers_data is not None:
            instance.canvass_suppliers.all().delete()
            for supplier_data in suppliers_data:
                VoucherCanvassSupplier.objects.create(voucher=instance, **supplier_data)

        instance.compute_totals()
        return instance
