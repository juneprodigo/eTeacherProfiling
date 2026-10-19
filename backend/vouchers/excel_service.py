import openpyxl
from io import BytesIO
from decimal import Decimal
from django.conf import settings
import os

TEMPLATE_PATH = os.path.join(settings.BASE_DIR, '..', 'frontend', 'src', 'assets', 'BLANK.xlsx')

def generate_voucher_workbook(voucher):
    """
    Loads BLANK.xlsx and populates:
    - DV (Disbursement Voucher)
    - PO (Purchase Order)
    - CANVASS (Canvass of Price 1, 2, 3)
    - PR-A&m (Purchase Request)
    - AOQ (Abstract of Quotation)
    - IAR (Inspection & Acceptance Report)
    - RIS (Requisition and Issue Slip)
    """
    resolved_path = os.path.abspath(TEMPLATE_PATH)
    if not os.path.exists(resolved_path):
        wb = openpyxl.Workbook()
        return wb

    wb = openpyxl.load_workbook(resolved_path, data_only=False)

    items = list(voucher.items.all().order_by('item_number'))
    suppliers = {s.supplier_slot: s for s in voucher.canvass_suppliers.all()}
    sup1 = suppliers.get(1)
    sup2 = suppliers.get(2)
    sup3 = suppliers.get(3)

    winner_name = voucher.payee_supplier_name or (sup1.supplier_name if sup1 else '')

    # 1. Populate DV Sheet
    if 'DV' in wb.sheetnames:
        ws = wb['DV']
        # DV No. & Date
        if voucher.dv_number:
            ws['K6'] = f"No. {voucher.dv_number}"
        if voucher.dv_date:
            ws['K7'] = f"Date: {voucher.dv_date.strftime('%m/%d/%Y')}"
        elif voucher.ors_date:
            ws['K7'] = f"Date: {voucher.ors_date.strftime('%m/%d/%Y')}"

        # Payee
        ws['B11'] = winner_name
        ws['B13'] = voucher.payee_address
        ws['G11'] = voucher.payee_tin
        ws['K11'] = voucher.ors_number or ''
        if voucher.ors_date:
            ws['K12'] = voucher.ors_date.strftime('%m/%d/%Y')

        # Amounts
        ws['E19'] = float(voucher.dv_gross_amount)
        ws['C20'] = float(voucher.dv_tax_rate1)
        ws['C21'] = float(voucher.dv_tax_rate2)
        ws['D20'] = float(voucher.dv_gross_amount * voucher.dv_tax_rate1)
        ws['D21'] = float(voucher.dv_gross_amount * voucher.dv_tax_rate2)
        ws['E22'] = float(voucher.dv_tax_amount1 + voucher.dv_tax_amount2)
        ws['E24'] = float(voucher.dv_net_amount)
        ws['K19'] = float(voucher.dv_net_amount)
        ws['L24'] = float(voucher.dv_net_amount)

        # Mode of payment check
        if voucher.cheque_number:
            ws['B65'] = voucher.cheque_number
        elif voucher.ada_number:
            ws['B65'] = voucher.ada_number

    # 2. Populate RIS Sheet
    if 'RIS' in wb.sheetnames:
        ws = wb['RIS']
        if voucher.ris_number:
            ws['G6'] = voucher.ris_number
        if voucher.ris_purpose:
            ws['C31'] = voucher.ris_purpose
        if voucher.ris_requested_by:
            ws['C35'] = voucher.ris_requested_by
        if voucher.ris_approved_by:
            ws['D35'] = voucher.ris_approved_by
        if voucher.ris_issued_by:
            ws['F35'] = voucher.ris_issued_by
        if voucher.ris_received_by:
            ws['H35'] = voucher.ris_received_by

        start_row = 9
        for i, item in enumerate(items[:20]):
            r = start_row + i
            ws[f'A{r}'] = i + 1
            ws[f'B{r}'] = item.unit
            ws[f'C{r}'] = item.description
            ws[f'D{r}'] = float(item.quantity)
            ws[f'E{r}'] = '✓'
            ws[f'G{r}'] = float(item.quantity)

    # 3. Populate PR-A&m Sheet
    if 'PR-A&m' in wb.sheetnames:
        ws = wb['PR-A&m']
        if voucher.pr_number:
            ws['D7'] = f" PR No.: {voucher.pr_number} "
        if voucher.pr_date:
            ws['G8'] = voucher.pr_date.strftime('%m/%d/%Y')
        if voucher.pr_purpose:
            ws['C30'] = voucher.pr_purpose
        if voucher.pr_requested_by:
            ws['C35'] = voucher.pr_requested_by
        if voucher.pr_approved_by:
            ws['E35'] = voucher.pr_approved_by

        start_row = 11
        for i, item in enumerate(items[:18]):
            r = start_row + i
            ws[f'A{r}'] = i + 1
            ws[f'B{r}'] = i + 1
            ws[f'C{r}'] = item.unit
            ws[f'D{r}'] = item.description
            ws[f'E{r}'] = float(item.quantity)
            ws[f'F{r}'] = float(item.unit_cost_1)
            ws[f'G{r}'] = float(item.total_cost)

    # 4. Populate CANVASS Sheet
    if 'CANVASS' in wb.sheetnames:
        ws = wb['CANVASS']
        if sup1:
            ws['C8'] = sup1.supplier_name
            ws['C9'] = sup1.supplier_address
            if sup1.canvass_date:
                ws['G8'] = sup1.canvass_date.strftime('%m/%d/%Y')
        elif winner_name:
            ws['C8'] = winner_name
            ws['C9'] = voucher.payee_address

        start_row = 11
        for i, item in enumerate(items[:15]):
            r = start_row + i
            ws[f'A{r}'] = i + 1
            ws[f'B{r}'] = float(item.quantity)
            ws[f'C{r}'] = item.unit
            ws[f'D{r}'] = item.description
            ws[f'E{r}'] = float(item.unit_cost_1)
            ws[f'G{r}'] = float(item.total_cost)

    # 5. Populate PO Sheet
    if 'PO' in wb.sheetnames:
        ws = wb['PO']
        ws['B7'] = winner_name
        ws['B8'] = voucher.payee_address
        ws['B9'] = voucher.payee_tin
        if voucher.po_number:
            ws['E7'] = voucher.po_number
        if voucher.po_date:
            ws['E8'] = voucher.po_date.strftime('%m/%d/%Y')
        if voucher.po_mode_of_procurement:
            ws['D9'] = f"Mode of Procurement:   {voucher.po_mode_of_procurement}"
        if voucher.po_place_of_delivery:
            ws['C16'] = voucher.po_place_of_delivery
        if voucher.po_delivery_term:
            ws['D16'] = f"Delivery Term:  {voucher.po_delivery_term}"
        if voucher.po_payment_term:
            ws['D17'] = f"Payment Term:   {voucher.po_payment_term}"

        start_row = 19
        for i, item in enumerate(items[:20]):
            r = start_row + i
            ws[f'A{r}'] = i + 1
            ws[f'B{r}'] = item.unit
            ws[f'C{r}'] = item.description
            ws[f'D{r}'] = float(item.quantity)
            ws[f'E{r}'] = float(item.unit_cost_1)
            ws[f'F{r}'] = float(item.total_cost)

        ws['D56'] = f"ORS/BURS No.: {voucher.ors_number or ''}"
        if voucher.ors_date:
            ws['F57'] = voucher.ors_date.strftime('%m/%d/%Y')
        ws['F59'] = float(voucher.total_amount)

    # 6. Populate IAR Sheet
    if 'IAR' in wb.sheetnames:
        ws = wb['IAR']
        ws['B7'] = winner_name
        if voucher.iar_number:
            ws['D7'] = voucher.iar_number
        if voucher.po_number:
            ws['B8'] = voucher.po_number
        if voucher.po_date:
            ws['C8'] = voucher.po_date.strftime('%m/%d/%Y')
        if voucher.iar_date:
            ws['D8'] = voucher.iar_date.strftime('%m/%d/%Y')
        if voucher.iar_invoice_number:
            ws['D9'] = voucher.iar_invoice_number
        if voucher.iar_invoice_date:
            ws['D10'] = voucher.iar_invoice_date.strftime('%m/%d/%Y')

        if voucher.iar_inspection_officer:
            ws['A46'] = voucher.iar_inspection_officer
        if voucher.iar_property_custodian:
            ws['C46'] = voucher.iar_property_custodian

        start_row = 13
        for i, item in enumerate(items[:20]):
            r = start_row + i
            ws[f'A{r}'] = i + 1
            ws[f'B{r}'] = item.description
            ws[f'C{r}'] = item.unit
            ws[f'D{r}'] = float(item.quantity)

    # 7. Populate AOQ Sheet
    if 'AOQ' in wb.sheetnames:
        ws = wb['AOQ']
        if winner_name:
            ws['C30'] = winner_name

        start_row = 10
        for i, item in enumerate(items[:18]):
            r = start_row + i
            ws[f'A{r}'] = i + 1
            ws[f'B{r}'] = item.description
            ws[f'C{r}'] = float(item.quantity)
            ws[f'D{r}'] = item.unit
            ws[f'E{r}'] = float(item.total_cost)
            if item.unit_cost_2 > 0:
                ws[f'F{r}'] = float(item.quantity * item.unit_cost_2)
            if item.unit_cost_3 > 0:
                ws[f'G{r}'] = float(item.quantity * item.unit_cost_3)

    return wb
