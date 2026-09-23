from django import template
from datetime import date, datetime

register = template.Library()

@register.filter(name='na')
def na(val, default='N/A'):
    if val is None or str(val).strip() == '':
        return default
    return val

@register.filter(name='pds_date')
def pds_date(val, default='N/A'):
    if not val:
        return default
    if isinstance(val, (date, datetime)):
        return val.strftime('%d/%m/%Y')
    try:
        # Try parsing string date YYYY-MM-DD
        d = datetime.strptime(str(val)[:10], '%Y-%m-%d')
        return d.strftime('%d/%m/%Y')
    except Exception:
        return str(val)

@register.filter(name='pds_yn')
def pds_yn(val):
    if val is True:
        return 'YES'
    if val is False:
        return 'NO'
    return 'N/A'
