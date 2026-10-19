from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from io import BytesIO
from .models import VoucherTransaction, VoucherItem, VoucherCanvassSupplier
from .serializers import (
    VoucherTransactionListSerializer,
    VoucherTransactionDetailSerializer,
    VoucherItemSerializer,
    VoucherCanvassSupplierSerializer
)
from .excel_service import generate_voucher_workbook

class VoucherTransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD Viewset for Voucher Preparation transactions following flowchart
    """
    queryset = VoucherTransaction.objects.all().prefetch_related('items', 'canvass_suppliers')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return VoucherTransactionListSerializer
        return VoucherTransactionDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def export_excel(self, request, pk=None):
        """Export filled Appendix & Voucher excel forms"""
        voucher = self.get_object()
        wb = generate_voucher_workbook(voucher)

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"Voucher_{voucher.transaction_code}.xlsx"
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        voucher = self.get_object()
        voucher.compute_totals()
        return Response(VoucherTransactionDetailSerializer(voucher).data)
