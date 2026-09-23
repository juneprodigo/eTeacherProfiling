"""
pds/address_views.py — High-performance cascading Philippine Address API
Reads PSGC standard geographic data and provides filtered cascading lists.
"""
import os
import json
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

DATA_DIR = Path(__file__).resolve().parent / 'data'

# In-memory caches
_REGIONS = None
_PROVINCES = None
_MUNICIPALITIES = None
_BARANGAYS_BY_CITY = None

# Common Philippine Postal Zip Codes
ZIP_CODE_LOOKUP = {
    # Cagayan (Region II)
    'tuguegarao': '3500',
    'tuguegarao city': '3500',
    'abulug': '3517',
    'alcala': '3507',
    'allacapan': '3523',
    'amulung': '3505',
    'aparri': '3515',
    'baggao': '3506',
    'ballesteros': '3516',
    'buguey': '3511',
    'calayan': '3520',
    'camalaniugan': '3510',
    'claveria': '3519',
    'enrile': '3501',
    'gattaran': '3508',
    'gonzaga': '3513',
    'iguig': '3504',
    'lal-lo': '3509',
    'lasam': '3524',
    'pamplona': '3522',
    'peñablanca': '3502',
    'penablanca': '3502',
    'piat': '3527',
    'rizal': '3526',
    'sanchez-mira': '3518',
    'santa ana': '3514',
    'santa praxedes': '3521',
    'santa teresita': '3512',
    'santo niño': '3525',
    'santo nino': '3525',
    'solana': '3503',
    'tuao': '3528',
    # Isabela
    'ilagan': '3300',
    'city of ilagan': '3300',
    'cauayan': '3305',
    'cauayan city': '3305',
    'santiago': '3311',
    'santiago city': '3311',
    'alicia': '3306',
    'angadanan': '3307',
    'aurora': '3316',
    'benito soliven': '3331',
    'burgos': '3322',
    'cabagan': '3328',
    'cabatuan': '3315',
    'cordon': '3312',
    'dinapigue': '3336',
    'divilacan': '3335',
    'echague': '3309',
    'gamu': '3301',
    'jones': '3313',
    'luna': '3304',
    'maconacon': '3333',
    'mallig': '3323',
    'naguilian': '3302',
    'palanan': '3334',
    'quezon': '3324',
    'quirino': '3321',
    'ramon': '3319',
    'reina mercedes': '3303',
    'roxas': '3320',
    'san agustin': '3314',
    'san guillermo': '3308',
    'san isidro': '3310',
    'san manuel': '3317',
    'san mariano': '3332',
    'san mateo': '3318',
    'san pablo': '3329',
    'santa maria': '3330',
    'tumauini': '3325',
    # Nueva Vizcaya
    'bayombong': '3700',
    'solano': '3709',
    'bambang': '3702',
    'bagabag': '3711',
    'aritao': '3704',
    'dupax del norte': '3706',
    'dupax del sur': '3707',
    'kayapa': '3708',
    'kasibu': '3703',
    'santa fe': '3705',
    'villoverde': '3710',
    # Quirino
    'cabarroguis': '3400',
    'diffun': '3401',
    'saguday': '3402',
    'aglipay': '3403',
    'maddela': '3404',
    'nagtipunan': '3405',
    # Batanes
    'basco': '3900',
    'itbayat': '3905',
    'ivana': '3902',
    'mahatao': '3901',
    'sabtang': '3903',
    'uyugan': '3904',
    # Metro Manila (NCR)
    'manila': '1000',
    'quezon city': '1100',
    'caloocan': '1400',
    'makati': '1200',
    'pasig': '1600',
    'taguig': '1630',
    'paranaque': '1700',
    'parañaque': '1700',
    'las pinas': '1740',
    'las piñas': '1740',
    'muntinlupa': '1770',
    'mandaluyong': '1550',
    'marikina': '1800',
    'pasay': '1300',
    'malabon': '1470',
    'navotas': '1485',
    'valenzuela': '1440',
    'san juan': '1500',
    'pateros': '1620',
    # Key Major Cities
    'baguio': '2600',
    'baguio city': '2600',
    'la trinidad': '2601',
    'san fernando': '2500',
    'angeles': '2009',
    'angeles city': '2009',
    'cebu city': '6000',
    'mandaue': '6014',
    'lapu-lapu': '6015',
    'iloilo city': '5000',
    'bacolod': '6100',
    'davao city': '8000',
    'cagayan de oro': '9000',
    'general santos': '9500',
    'zamboanga city': '7000',
}


def _load_data():
    global _REGIONS, _PROVINCES, _MUNICIPALITIES, _BARANGAYS_BY_CITY
    if _REGIONS is not None:
        return

    try:
        with open(DATA_DIR / 'regions.json', 'r', encoding='utf-8') as f:
            _REGIONS = json.load(f)
    except Exception:
        _REGIONS = []

    try:
        with open(DATA_DIR / 'provinces.json', 'r', encoding='utf-8') as f:
            _PROVINCES = json.load(f)
    except Exception:
        _PROVINCES = []

    try:
        with open(DATA_DIR / 'municipalities.json', 'r', encoding='utf-8') as f:
            _MUNICIPALITIES = json.load(f)
    except Exception:
        _MUNICIPALITIES = []

    try:
        with open(DATA_DIR / 'barangays.json', 'r', encoding='utf-8') as f:
            raw_brgys = json.load(f)
            _BARANGAYS_BY_CITY = {}
            for b in raw_brgys:
                # Key by normalized citymun name
                city_key = b.get('citymun', '').strip().lower()
                if city_key not in _BARANGAYS_BY_CITY:
                    _BARANGAYS_BY_CITY[city_key] = []
                _BARANGAYS_BY_CITY[city_key].append({
                    'code': b.get('code'),
                    'name': b.get('name')
                })
    except Exception:
        _BARANGAYS_BY_CITY = {}


class RegionListView(APIView):
    """List all Philippine administrative regions."""
    permission_classes = [AllowAny]

    def get(self, request):
        _load_data()
        return Response(_REGIONS)


class ProvinceListView(APIView):
    """List provinces, optionally filtered by region name or designation."""
    permission_classes = [AllowAny]

    def get(self, request):
        _load_data()
        region_filter = request.query_params.get('region', '').strip().lower()

        if not region_filter:
            return Response(_PROVINCES)

        # Region might be 'Region II' or 'Cagayan Valley'
        target_designation = region_filter
        for r in _REGIONS:
            if r.get('name', '').lower() == region_filter or r.get('designation', '').lower() == region_filter:
                target_designation = r.get('designation', '').lower()
                break

        filtered = [
            p for p in _PROVINCES
            if p.get('region', '').strip().lower() == target_designation
        ]
        return Response(filtered)


class MunicipalityListView(APIView):
    """List municipalities/cities, optionally filtered by province."""
    permission_classes = [AllowAny]

    def get(self, request):
        _load_data()
        prov_filter = request.query_params.get('province', '').strip().lower()

        results = []
        for m in _MUNICIPALITIES:
            m_prov = m.get('province', '').strip().lower()
            if not prov_filter or m_prov == prov_filter:
                name = m.get('name', '')
                normalized_name = name.lower()
                zip_val = ZIP_CODE_LOOKUP.get(normalized_name, '')
                results.append({
                    'name': name,
                    'province': m.get('province'),
                    'city': m.get('city', False),
                    'zip_code': zip_val
                })

        return Response(results)


class BarangayListView(APIView):
    """List barangays for a specific city or municipality."""
    permission_classes = [AllowAny]

    def get(self, request):
        _load_data()
        city_param = request.query_params.get('city', '').strip().lower()
        if not city_param:
            return Response([])

        # Direct match or partial match on citymun key
        # Many PSGC keys have format like "Tuguegarao City Capital" or "Aparri"
        matches = []
        if city_param in _BARANGAYS_BY_CITY:
            matches = _BARANGAYS_BY_CITY[city_param]
        else:
            # Try fuzzy matching keys (e.g. user sends "Tuguegarao City", key might be "tuguegarao city capital" or "tuguegarao")
            clean_city = city_param.replace('city of ', '').replace(' city', '').strip()
            for key, brgys in _BARANGAYS_BY_CITY.items():
                if key == clean_city or clean_city in key or key in clean_city:
                    matches = brgys
                    break

        # Sort barangays by name
        sorted_brgys = sorted(matches, key=lambda x: x['name'])
        return Response(sorted_brgys)
