"""
attendance/dtr_exporter.py — CS Form No. 48 (Daily Time Record) Exporters
Generates official Civil Service Form 48 in both Excel (.xlsx) and PDF formats.
"""
import io
import calendar
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from django.template.loader import render_to_string
from django.conf import settings
from .models import AttendanceShiftSetting, DailyTimeRecord


def get_month_records(teacher, year, month):
    """Fetches and structures daily records for the full month (days 1 to last day)."""
    _, last_day = calendar.monthrange(year, month)
    existing_records = {
        r.date.day: r
        for r in DailyTimeRecord.objects.filter(
            teacher=teacher,
            date__year=year,
            date__month=month
        )
    }

    days_data = []
    for day in range(1, last_day + 1):
        dt = datetime.date(year, month, day)
        rec = existing_records.get(day)
        is_weekend = dt.weekday() in [5, 6]  # Saturday or Sunday

        days_data.append({
            'day': day,
            'date': dt,
            'is_weekend': is_weekend,
            'day_name': dt.strftime('%a'),
            'am_in': rec.am_time_in.strftime('%I:%M') if rec and rec.am_time_in else '',
            'am_out': rec.am_time_out.strftime('%I:%M') if rec and rec.am_time_out else '',
            'pm_in': rec.pm_time_in.strftime('%I:%M') if rec and rec.pm_time_in else '',
            'pm_out': rec.pm_time_out.strftime('%I:%M') if rec and rec.pm_time_out else '',
            'tardy_minutes': rec.tardy_minutes if rec else 0,
            'undertime_minutes': rec.undertime_minutes if rec else 0,
            'hours_rendered': float(rec.total_hours_rendered) if rec else 0.0,
            'status': rec.status if rec else ('Weekend' if is_weekend else ''),
            'remarks': rec.remarks if rec else '',
        })

    return days_data, last_day


def generate_dtr_excel(teacher, year, month):
    """
    Builds an openpyxl Excel spreadsheet styled precisely as Civil Service Form No. 48.
    """
    days_data, last_day = get_month_records(teacher, year, month)
    month_name = calendar.month_name[month]
    full_name = teacher.user.get_full_name() or teacher.user.username
    position = teacher.position or teacher.user.get_role_display()
    emp_id = teacher.employee_id or f'EMP-{teacher.id:04d}'

    wb = Workbook()
    ws = wb.active
    ws.title = f"CS_Form_48_{month_name[:3]}_{year}"
    ws.views.sheetView[0].showGridLines = True

    # Styling constants
    font_header_title = Font(name="Calibri", size=13, bold=True, color="1E293B")
    font_doc_no = Font(name="Calibri", size=9, italic=True, bold=True, color="475569")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_regular = Font(name="Calibri", size=9.5, color="1E293B")
    font_small = Font(name="Calibri", size=8.5, color="475569")
    font_weekend = Font(name="Calibri", size=9, italic=True, color="64748B")

    fill_header = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_table_hdr = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
    fill_weekend = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_total = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

    thin_border_side = Side(style='thin', color='94A3B8')
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_bottom_thick = Border(bottom=Side(style='medium', color='1E293B'))

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    # Row 1: Document Form Number
    ws.merge_cells('A1:G1')
    ws['A1'] = "Civil Service Form No. 48"
    ws['A1'].font = font_doc_no
    ws['A1'].alignment = Alignment(horizontal='left')

    # Row 2: Title
    ws.merge_cells('A2:G2')
    ws['A2'] = "DAILY TIME RECORD"
    ws['A2'].font = font_header_title
    ws['A2'].alignment = align_center

    # Row 3: Subtitle / Agency
    ws.merge_cells('A3:G3')
    ws['A3'] = "DEPARTMENT OF EDUCATION — CAGAYAN EAST ELEMENTARY SCHOOL (CES)"
    ws['A3'].font = font_small
    ws['A3'].alignment = align_center

    # Row 5: Name
    ws['A5'] = "Name:"
    ws['A5'].font = font_bold
    ws.merge_cells('B5:E5')
    ws['B5'] = full_name.upper()
    ws['B5'].font = Font(name="Calibri", size=11, bold=True, underline="single", color="0F172A")

    ws['F5'] = "Employee ID:"
    ws['F5'].font = font_bold
    ws['G5'] = emp_id
    ws['G5'].font = font_bold

    # Row 6: Month & Year
    ws['A6'] = "For the Month of:"
    ws['A6'].font = font_regular
    ws.merge_cells('B6:E6')
    ws['B6'] = f"{month_name} 1 - {last_day}, {year}"
    ws['B6'].font = font_bold

    ws['F6'] = "Position:"
    ws['F6'].font = font_regular
    ws['G6'] = position
    ws['G6'].font = font_regular

    # Row 7: Official hours
    ws.merge_cells('A7:G7')
    ws['A7'] = "Official hours for arrival and departure: Regular Days 8:00 AM - 12:00 PM / 1:00 PM - 5:00 PM"
    ws['A7'].font = font_small
    ws['A7'].alignment = align_center

    # Row 9-10: Table Headers
    # Header Row 1
    ws.row_dimensions[9].height = 20
    ws.row_dimensions[10].height = 20

    ws.merge_cells('A9:A10')
    ws['A9'] = "Day"
    ws['A9'].font = font_bold
    ws['A9'].fill = fill_table_hdr
    ws['A9'].alignment = align_center
    ws['A9'].border = border_cell

    ws.merge_cells('B9:C9')
    ws['B9'] = "A. M."
    ws['B9'].font = font_bold
    ws['B9'].fill = fill_table_hdr
    ws['B9'].alignment = align_center
    ws['B9'].border = border_cell

    ws['B10'] = "Arrival"
    ws['B10'].font = font_bold
    ws['B10'].fill = fill_table_hdr
    ws['B10'].alignment = align_center
    ws['B10'].border = border_cell

    ws['C10'] = "Departure"
    ws['C10'].font = font_bold
    ws['C10'].fill = fill_table_hdr
    ws['C10'].alignment = align_center
    ws['C10'].border = border_cell

    ws.merge_cells('D9:E9')
    ws['D9'] = "P. M."
    ws['D9'].font = font_bold
    ws['D9'].fill = fill_table_hdr
    ws['D9'].alignment = align_center
    ws['D9'].border = border_cell

    ws['D10'] = "Arrival"
    ws['D10'].font = font_bold
    ws['D10'].fill = fill_table_hdr
    ws['D10'].alignment = align_center
    ws['D10'].border = border_cell

    ws['E10'] = "Departure"
    ws['E10'].font = font_bold
    ws['E10'].fill = fill_table_hdr
    ws['E10'].alignment = align_center
    ws['E10'].border = border_cell

    ws.merge_cells('F9:F10')
    ws['F9'] = "Under / Tardy\n(Mins)"
    ws['F9'].font = font_bold
    ws['F9'].fill = fill_table_hdr
    ws['F9'].alignment = align_center
    ws['F9'].border = border_cell

    ws.merge_cells('G9:G10')
    ws['G9'] = "Remarks / Status"
    ws['G9'].font = font_bold
    ws['G9'].fill = fill_table_hdr
    ws['G9'].alignment = align_center
    ws['G9'].border = border_cell

    # Fill Table Rows
    current_row = 11
    total_hours_sum = 0.0
    total_tardy_sum = 0
    total_undertime_sum = 0
    days_present_count = 0

    for d in days_data:
        ws.row_dimensions[current_row].height = 18
        day_cell = ws.cell(row=current_row, column=1, value=d['day'])
        day_cell.alignment = align_center
        day_cell.border = border_cell

        c_am_in = ws.cell(row=current_row, column=2, value=d['am_in'])
        c_am_out = ws.cell(row=current_row, column=3, value=d['am_out'])
        c_pm_in = ws.cell(row=current_row, column=4, value=d['pm_in'])
        c_pm_out = ws.cell(row=current_row, column=5, value=d['pm_out'])

        tardy_under = ""
        combined_lost = d['tardy_minutes'] + d['undertime_minutes']
        if combined_lost > 0:
            tardy_under = f"{combined_lost}m"

        c_lost = ws.cell(row=current_row, column=6, value=tardy_under)
        c_remarks = ws.cell(row=current_row, column=7, value=d['status'] or d['remarks'])

        for c in [c_am_in, c_am_out, c_pm_in, c_pm_out, c_lost]:
            c.alignment = align_center
            c.border = border_cell
        c_remarks.alignment = align_left
        c_remarks.border = border_cell

        if d['is_weekend']:
            day_cell.font = font_weekend
            for c in [day_cell, c_am_in, c_am_out, c_pm_in, c_pm_out, c_lost, c_remarks]:
                c.fill = fill_weekend
                c.font = font_weekend
            if not d['am_in'] and not d['pm_in']:
                c_remarks.value = d['day_name'].upper()
        else:
            day_cell.font = font_bold
            for c in [c_am_in, c_am_out, c_pm_in, c_pm_out, c_lost, c_remarks]:
                c.font = font_regular

        if d['am_in'] or d['pm_in']:
            days_present_count += 1
            total_hours_sum += d['hours_rendered']
            total_tardy_sum += d['tardy_minutes']
            total_undertime_sum += d['undertime_minutes']

        current_row += 1

    # Totals Row
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=5)
    c_tot_label = ws.cell(row=current_row, column=1, value=f"TOTAL DAYS PRESENT: {days_present_count}  |  HOURS RENDERED: {total_hours_sum:.2f} hrs")
    c_tot_label.font = font_bold
    c_tot_label.alignment = align_center
    c_tot_label.fill = fill_total

    c_tot_lost = ws.cell(row=current_row, column=6, value=f"{total_tardy_sum + total_undertime_sum}m")
    c_tot_lost.font = font_bold
    c_tot_lost.alignment = align_center
    c_tot_lost.fill = fill_total

    c_tot_rem = ws.cell(row=current_row, column=7, value="")
    c_tot_rem.fill = fill_total

    for col in range(1, 8):
        ws.cell(row=current_row, column=col).border = border_cell

    current_row += 2

    # Certification clause (Official CSC Form 48 text)
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row + 1, end_column=7)
    c_cert = ws.cell(
        row=current_row, column=1,
        value="I certify on my honor that the above is a true and correct report of the hours of work performed, "
              "record of which was made daily at the time of arrival and departure from office."
    )
    c_cert.font = Font(name="Calibri", size=8.5, italic=True, color="334155")
    c_cert.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    current_row += 4

    # Signatures
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
    c_emp_sig = ws.cell(row=current_row, column=1, value=full_name.upper())
    c_emp_sig.font = Font(name="Calibri", size=10, bold=True)
    c_emp_sig.alignment = align_center

    ws.merge_cells(start_row=current_row, start_column=5, end_row=current_row, end_column=7)
    c_head_sig = ws.cell(row=current_row, column=5, value="SCHOOL HEAD / PRINCIPAL")
    c_head_sig.font = Font(name="Calibri", size=10, bold=True)
    c_head_sig.alignment = align_center

    current_row += 1
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
    ws.cell(row=current_row, column=1, value="Signature of Employee").font = font_small
    ws.cell(row=current_row, column=1).alignment = align_center

    ws.merge_cells(start_row=current_row, start_column=5, end_row=current_row, end_column=7)
    ws.cell(row=current_row, column=5, value="In Charge / Authorized Officer").font = font_small
    ws.cell(row=current_row, column=5).alignment = align_center

    # Column Widths
    col_widths = {
        'A': 7,   # Day
        'B': 12,  # AM In
        'C': 12,  # AM Out
        'D': 12,  # PM In
        'E': 12,  # PM Out
        'F': 14,  # Under / Tardy
        'G': 24,  # Remarks
    }
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def generate_dtr_pdf(teacher, year, month):
    """
    Renders Civil Service Form No. 48 into a clean PDF using WeasyPrint or xhtml2pdf.
    """
    days_data, last_day = get_month_records(teacher, year, month)
    month_name = calendar.month_name[month]
    full_name = teacher.user.get_full_name() or teacher.user.username
    position = teacher.position or teacher.user.get_role_display()
    emp_id = teacher.employee_id or f'EMP-{teacher.id:04d}'

    total_hours = sum(d['hours_rendered'] for d in days_data)
    total_tardy = sum(d['tardy_minutes'] for d in days_data)
    total_undertime = sum(d['undertime_minutes'] for d in days_data)
    days_present = sum(1 for d in days_data if d['am_in'] or d['pm_in'])

    context = {
        'teacher': teacher,
        'full_name': full_name,
        'position': position,
        'emp_id': emp_id,
        'month_name': month_name,
        'month': month,
        'year': year,
        'last_day': last_day,
        'days_data': days_data,
        'total_hours': f"{total_hours:.2f}",
        'total_tardy': total_tardy,
        'total_undertime': total_undertime,
        'days_present': days_present,
    }

    html_content = render_to_string('attendance/dtr_pdf.html', context)

    # 1. Attempt WeasyPrint
    try:
        import weasyprint
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        return pdf_bytes
    except Exception as e_wp:
        print("WeasyPrint DTR PDF generation fallback:", e_wp)

    # 2. Resilient fallback: xhtml2pdf
    try:
        from xhtml2pdf import pisa
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
        if pisa_status.err:
            raise Exception("xhtml2pdf rendering error")
        return pdf_buffer.getvalue()
    except Exception as e_pisa:
        print("xhtml2pdf DTR PDF generation failed:", e_pisa)
        raise e_pisa
