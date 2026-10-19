from django.db import models
from django.conf import settings
from decimal import Decimal

class VoucherTransaction(models.Model):
    """
    Main Voucher Preparation Transaction following DepEd / Naguilian Elementary School workflow.
    """
    TRANSACTION_TYPES = [
        ('SUPPLIES', 'Purchase of Supplies'),
        ('REPAIR', 'Repair and Maintenance'),
        ('CATERING', 'Catering'),
        ('TRAVEL', 'Travel'),
        ('TRAINING', 'Training'),
        ('UTILITIES', 'Electricity / Internet'),
        ('LOAD', 'Load'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_CANVASS', 'Pending Canvass / Quotations'),
        ('AWARDED', 'Canvass Awarded'),
        ('PO_ISSUED', 'PO Issued'),
        ('INSPECTED', 'Inspected & Accepted'),
        ('VOUCHER_READY', 'Disbursement Voucher Ready'),
        ('COMPLETED', 'Completed / Liquidated'),
    ]

    # Liquidation & Accounting Header
    transaction_code = models.CharField(max_length=50, unique=True, help_text="Unique transaction code e.g. TR-2026-001")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='SUPPLIES')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    liquidation_code = models.CharField(max_length=100, blank=True, default='')
    liquidation_month = models.CharField(max_length=50, blank=True, default='', help_text="e.g. October 2026")
    ada_number = models.CharField(max_length=100, blank=True, default='')
    ada_date = models.DateField(null=True, blank=True)
    ors_number = models.CharField(max_length=100, blank=True, default='', help_text="ORS / BURS No.")
    ors_date = models.DateField(null=True, blank=True)

    # Primary Payee / Supplier (e.g. Vicky's Hardware or Selected Winning Bidder)
    payee_supplier_name = models.CharField(max_length=255, blank=True, default='')
    payee_address = models.TextField(blank=True, default='')
    payee_tin = models.CharField(max_length=100, blank=True, default='')
    cheque_number = models.CharField(max_length=100, blank=True, default='')
    cheque_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # RIS (Requisition and Issue Slip) - Appendix 63
    ris_number = models.CharField(max_length=100, blank=True, default='')
    ris_date1 = models.DateField(null=True, blank=True, help_text="Requisition Date")
    ris_date2 = models.DateField(null=True, blank=True, help_text="Issue/Approval Date")
    ris_purpose = models.TextField(blank=True, default='')
    ris_requested_by = models.CharField(max_length=150, blank=True, default='AMALIA I. CONSIGNA')
    ris_approved_by = models.CharField(max_length=150, blank=True, default='JUDY S. MOLINA')
    ris_issued_by = models.CharField(max_length=150, blank=True, default='DIVINA D. NOBLEZA')
    ris_received_by = models.CharField(max_length=150, blank=True, default='JENNY LYN A. TABUADA')

    # PR (Purchase Request) - Appendix 60
    pr_number = models.CharField(max_length=100, blank=True, default='')
    pr_date = models.DateField(null=True, blank=True)
    pr_purpose = models.TextField(blank=True, default='')
    pr_requested_by = models.CharField(max_length=150, blank=True, default='DIVINA D. NOBLEZA')
    pr_approved_by = models.CharField(max_length=150, blank=True, default='JUDY S. MOLINA')

    # PO (Purchase Order) - Appendix 61
    po_number = models.CharField(max_length=100, blank=True, default='')
    po_date = models.DateField(null=True, blank=True)
    po_mode_of_procurement = models.CharField(max_length=100, default='SMALL VALUE')
    po_place_of_delivery = models.CharField(max_length=255, default='NAGUILIAN ELEMENTARY SCHOOL')
    po_delivery_term = models.CharField(max_length=100, default='1-2 DAY/S OF DELIVERY')
    po_payment_term = models.CharField(max_length=100, default='Check')

    # IAR (Inspection and Acceptance Report) - Appendix 62
    iar_number = models.CharField(max_length=100, blank=True, default='')
    iar_date = models.DateField(null=True, blank=True)
    iar_invoice_number = models.CharField(max_length=100, blank=True, default='')
    iar_invoice_date = models.DateField(null=True, blank=True)
    iar_inspection_officer = models.CharField(max_length=150, blank=True, default='JENNY LYN A. TABUADA')
    iar_property_custodian = models.CharField(max_length=150, blank=True, default='DIVINA D. NOBLEZA')

    # DV (Disbursement Voucher)
    dv_number = models.CharField(max_length=100, blank=True, default='')
    dv_date = models.DateField(null=True, blank=True)
    dv_mode_of_payment = models.CharField(max_length=50, default='MDSCheck', help_text="MDSCheck, Commercial Check, ADA, Others")
    dv_gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    dv_tax_rate1 = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.05'), help_text="5% VAT/Expanded")
    dv_tax_rate2 = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.01'), help_text="1% Withholding")
    dv_tax_amount1 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    dv_tax_amount2 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    dv_net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Amount Due")
    
    # Signatories & Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='vouchers_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_code} - {self.get_transaction_type_display()} ({self.payee_supplier_name or 'No Payee'})"

    def compute_totals(self):
        """Auto calculate total item costs, canvasses, and DV tax breakdown"""
        items = self.items.all()
        gross = sum((Decimal(str(item.quantity or 0)) * Decimal(str(item.unit_cost_1 or 0)) for item in items), Decimal('0.00'))
        self.dv_gross_amount = gross
        self.total_amount = gross

        # Tax computation (5% and 1%)
        rate1 = Decimal(str(self.dv_tax_rate1 or 0))
        rate2 = Decimal(str(self.dv_tax_rate2 or 0))
        self.dv_tax_amount1 = (gross * rate1).quantize(Decimal('0.01'))
        self.dv_tax_amount2 = (gross * rate2).quantize(Decimal('0.01'))
        total_tax = self.dv_tax_amount1 + self.dv_tax_amount2
        self.dv_net_amount = gross - total_tax
        self.save(update_fields=['dv_gross_amount', 'total_amount', 'dv_tax_amount1', 'dv_tax_amount2', 'dv_net_amount'])


class VoucherItem(models.Model):
    """
    Individual items under a Voucher Transaction.
    Holds specs and unit costs from Canvass 1 (Winner/PR), Canvass 2, Canvass 3.
    """
    voucher = models.ForeignKey(VoucherTransaction, on_delete=models.CASCADE, related_name='items')
    item_code = models.CharField(max_length=50, blank=True, default='')
    item_number = models.PositiveIntegerField(default=1)
    classification = models.CharField(max_length=100, blank=True, default='', help_text="e.g. Office Supplies, Semi-Expendable")
    unit = models.CharField(max_length=50, default='pcs')
    description = models.TextField(help_text="Item / Article Description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))

    # Canvass 1 / PR estimated cost
    unit_cost_1 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Supplier 1 Unit Price")
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Canvass 2 Unit Price
    unit_cost_2 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Supplier 2 Unit Price")
    # Canvass 3 Unit Price
    unit_cost_3 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Supplier 3 Unit Price")

    class Meta:
        ordering = ['item_number', 'id']

    def save(self, *args, **kwargs):
        qty = Decimal(str(self.quantity or 0))
        cost = Decimal(str(self.unit_cost_1 or 0))
        self.total_cost = (qty * cost).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_number}. {self.description[:30]} ({self.quantity} {self.unit})"


class VoucherCanvassSupplier(models.Model):
    """
    Quotations / Canvass bidders (up to 3 bidders for AOQ / Canvass 1, 2, 3)
    """
    voucher = models.ForeignKey(VoucherTransaction, on_delete=models.CASCADE, related_name='canvass_suppliers')
    supplier_slot = models.PositiveSmallIntegerField(choices=[(1, 'Canvass 1 (Awardee)'), (2, 'Canvass 2'), (3, 'Canvass 3')], default=1)
    supplier_name = models.CharField(max_length=255)
    supplier_address = models.CharField(max_length=255, blank=True, default='')
    canvass_date = models.DateField(null=True, blank=True)
    is_awardee = models.BooleanField(default=False)

    class Meta:
        unique_together = ('voucher', 'supplier_slot')
        ordering = ['supplier_slot']

    def __str__(self):
        return f"Slot {self.supplier_slot}: {self.supplier_name}"
