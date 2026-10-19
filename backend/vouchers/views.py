from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from io import BytesIO
from .models import VoucherTransaction, VoucherItem, VoucherCanvassSupplier, VoucherReferenceLibrary
from .serializers import (
    VoucherTransactionListSerializer,
    VoucherTransactionDetailSerializer,
    VoucherItemSerializer,
    VoucherCanvassSupplierSerializer,
    VoucherReferenceLibrarySerializer
)
from .excel_service import generate_voucher_workbook

class VoucherReferenceLibraryViewSet(viewsets.ModelViewSet):
    """
    CRUD Viewset for Voucher Reference Libraries (Transaction types, suppliers, signatories, terms)
    """
    queryset = VoucherReferenceLibrary.objects.all()
    serializer_class = VoucherReferenceLibrarySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        active_only = self.request.query_params.get('active_only')
        if active_only and active_only.lower() in ['true', '1']:
            qs = qs.filter(is_active=True)
        return qs

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

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        """Generate and download or preview Voucher & Appendices PDF"""
        voucher = self.get_object()
        sheet_param = request.query_params.get('sheet', '').strip()
        is_preview = request.query_params.get('preview') == 'true'

        from vouchers.excel_service import build_voucher_cells, TEMPLATE_PATH, generate_voucher_workbook
        from pds.excel_to_pdf import convert_template_cells_to_pdf, convert_workbook_to_pdf

        target_sheet = sheet_param if sheet_param else None
        cell_map = build_voucher_cells(voucher)
        pdf_bytes = convert_template_cells_to_pdf(TEMPLATE_PATH, cell_map, sheet_name=target_sheet)

        if not pdf_bytes:
            # Fallback to workbook conversion if direct copy COM export failed
            wb = generate_voucher_workbook(voucher)
            pdf_bytes = convert_workbook_to_pdf(wb, sheet_name=target_sheet)

        if not pdf_bytes:
            return Response(
                {"detail": "PDF conversion is unavailable or Excel COM failed. Please use Excel export."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        suffix = f"_{sheet_param}" if sheet_param else ""
        filename = f"Voucher_{voucher.transaction_code}{suffix}.pdf"
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        disposition = 'inline' if is_preview else 'attachment'
        response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
        return response

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        voucher = self.get_object()
        voucher.compute_totals()
        return Response(VoucherTransactionDetailSerializer(voucher).data)
