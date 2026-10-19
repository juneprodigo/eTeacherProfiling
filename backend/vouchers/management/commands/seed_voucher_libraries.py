from django.core.management.base import BaseCommand
from vouchers.models import VoucherReferenceLibrary

class Command(BaseCommand):
    help = 'Seed initial reference libraries for Voucher Preparation module'

    def handle(self, *args, **options):
        # 1. Transaction Types
        transaction_types = [
            ('SUPPLIES', 'Purchase of Supplies'),
            ('REPAIR', 'Repair and Maintenance'),
            ('CATERING', 'Catering'),
            ('TRAVEL', 'Travel'),
            ('TRAINING', 'Training'),
            ('UTILITIES', 'Electricity / Internet'),
            ('LOAD', 'Load / Communication'),
        ]
        for idx, (code, name) in enumerate(transaction_types, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='TRANSACTION_TYPE',
                code=code,
                defaults={'name': name, 'sort_order': idx}
            )

        # 2. Suppliers
        suppliers = [
            ("Vicky's Hardware", "Centro, Lal-lo, Cagayan", "123-456-789-001"),
            ("Golden Ribbon General Merchandise", "Bulala, Camalaniugan, Cagayan", "234-567-890-002"),
            ("Crown Paper & Office Depot", "Tuguegarao City, Cagayan", "345-678-901-003"),
            ("DepEd Cooperative Canteen", "Naguilian, Lal-lo, Cagayan", "456-789-012-004"),
            ("Cagayan Electric Cooperative II (CAGELCO II)", "Aparri, Cagayan", "000-111-222-005"),
            ("Smart / PLDT Communications", "Tuguegarao City, Cagayan", "111-222-333-006"),
        ]
        for idx, (name, addr, tin) in enumerate(suppliers, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='SUPPLIER',
                name=name,
                defaults={'address': addr, 'tin': tin, 'sort_order': idx}
            )

        # 3. Requested By
        requested_by = [
            ("DIVINA D. NOBLEZA", "Property Custodian-Designate"),
            ("AMALIA I. CONSIGNA", "Disbursing Officer"),
            ("LEE YAN MEI A. VILLANUEVA", "BAC Member"),
            ("FEDELYNE I. PONCE", "BAC Chairman"),
        ]
        for idx, (name, desig) in enumerate(requested_by, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='REQUESTED_BY',
                name=name,
                defaults={'designation': desig, 'sort_order': idx}
            )

        # 4. Approved By
        approved_by = [
            ("JUDY S. MOLINA", "PRINCIPAL II / School Head"),
            ("MICKEL JOHN L. DELOS SANTOS", "Administrative Assistant III"),
            ("JOSE G. TALOSIG", "Accountant / Disbursing Officer"),
        ]
        for idx, (name, desig) in enumerate(approved_by, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='APPROVED_BY',
                name=name,
                defaults={'designation': desig, 'sort_order': idx}
            )

        # 5. Issued By
        issued_by = [
            ("DIVINA D. NOBLEZA", "Property Custodian"),
            ("JUDY S. MOLINA", "PRINCIPAL II"),
            ("AMALIA I. CONSIGNA", "Disbursing Officer"),
        ]
        for idx, (name, desig) in enumerate(issued_by, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='ISSUED_BY',
                name=name,
                defaults={'designation': desig, 'sort_order': idx}
            )

        # 6. Received By
        received_by = [
            ("JENNY LYN A. TABUADA", "Inspection Officer"),
            ("DIVINA D. NOBLEZA", "Property Custodian"),
            ("MARY ANN M. PONCE", "BAC Member"),
            ("AMALIA I. CONSIGNA", "Disbursing Officer"),
        ]
        for idx, (name, desig) in enumerate(received_by, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='RECEIVED_BY',
                name=name,
                defaults={'designation': desig, 'sort_order': idx}
            )

        # 7. Mode of Procurement
        modes = [
            "SMALL VALUE",
            "SHOPPING",
            "PUBLIC BIDDING",
            "DIRECT CONTRACTING",
            "REPEAT ORDER",
            "EMERGENCY CASES",
        ]
        for idx, m in enumerate(modes, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='MODE_OF_PROCUREMENT',
                name=m,
                defaults={'sort_order': idx}
            )

        # 8. Delivery Terms
        delivery_terms = [
            "1-2 DAY/S OF DELIVERY",
            "3-5 CALENDAR DAYS",
            "7 CALENDAR DAYS",
            "15 CALENDAR DAYS",
            "30 CALENDAR DAYS",
            "IMMEDIATE DELIVERY",
        ]
        for idx, dt in enumerate(delivery_terms, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='DELIVERY_TERM',
                name=dt,
                defaults={'sort_order': idx}
            )

        # 9. Payment Terms
        payment_terms = [
            "Check",
            "MDS Check",
            "Commercial Check",
            "ADA (Advice to Debit Account)",
            "Upon Complete Delivery & Inspection",
            "15 Days After Acceptance",
            "30 Days After Acceptance",
        ]
        for idx, pt in enumerate(payment_terms, start=1):
            VoucherReferenceLibrary.objects.get_or_create(
                category='PAYMENT_TERM',
                name=pt,
                defaults={'sort_order': idx}
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Voucher Reference Libraries.'))
