"""
خريطة رموز التداول المدعومة في yfinance
"""

# خريطة الرموز المالية
SYMBOL_MAPPING = {
    # الذهب
    'GOLD': 'GC=F',
    'XAUUSD': 'GC=F', 
    'XAU': 'GC=F',
    
    # الفضة
    'SILVER': 'SI=F',
    'XAGUSD': 'SI=F',
    'XAG': 'SI=F',
    
    # النفط
    'OIL': 'CL=F',
    'CRUDE': 'CL=F',
    'WTI': 'CL=F',
    'WTIUSD': 'CL=F',
    'BRENT': 'BZ=F',
    
    # المؤشرات الأمريكية
    'US30': '^DJI',      # داو جونز
    'DJ30': '^DJI',
    'DOW': '^DJI',
    'DJIA': '^DJI',
    
    'US500': '^GSPC',    # S&P 500
    'SPX': '^GSPC',
    'SP500': '^GSPC',
    
    'US100': '^IXIC',    # ناسداك
    'NAS100': '^IXIC',
    'NASDAQ': '^IXIC',
    'NDX': '^IXIC',
    
    # المؤشرات الأوروبية
    'DAX': '^GDAXI',     # داكس الألماني
    'DE30': '^GDAXI',
    
    'UK100': '^FTSE',    # فوتسي البريطاني
    'FTSE': '^FTSE',
    
    'FR40': '^FCHI',     # كاك الفرنسي
    'CAC': '^FCHI',
    
    # المؤشرات الآسيوية
    'JP225': '^N225',    # نيكي الياباني
    'NIKKEI': '^N225',
    
    'HK50': '^HSI',      # هانغ سنغ
    'HSI': '^HSI',
    
    # العملات الرقمية الرئيسية
    'BTC': 'BTC-USD',
    'BITCOIN': 'BTC-USD',
    'BTCUSD': 'BTC-USD',
    
    'ETH': 'ETH-USD',
    'ETHEREUM': 'ETH-USD',
    'ETHUSD': 'ETH-USD',
    
    'ADA': 'ADA-USD',
    'XRP': 'XRP-USD',
    'LTC': 'LTC-USD',
    'BCH': 'BCH-USD',
    'DOT': 'DOT-USD',
    'LINK': 'LINK-USD',
    'BNB': 'BNB-USD',
    'SOL': 'SOL-USD',
    'AVAX': 'AVAX-USD',
    'MATIC': 'MATIC-USD',
    'ATOM': 'ATOM-USD',
    'NEAR': 'NEAR-USD',
    'FTM': 'FTM-USD',
    'ALGO': 'ALGO-USD',
    'VET': 'VET-USD',
    'ICP': 'ICP-USD',
    'FIL': 'FIL-USD',
    'THETA': 'THETA-USD',
    'TRX': 'TRX-USD',
    'EOS': 'EOS-USD',
    'XLM': 'XLM-USD',
    'AAVE': 'AAVE-USD',
    'MKR': 'MKR-USD',
    'COMP': 'COMP-USD',
    'UNI': 'UNI-USD',
    'SUSHI': 'SUSHI-USD',
    'CRV': 'CRV-USD',
    '1INCH': '1INCH-USD',
    'YFI': 'YFI-USD',
    'SNX': 'SNX-USD',
    'REN': 'REN-USD',
    'KSM': 'KSM-USD',
    'ZIL': 'ZIL-USD',
    'QTUM': 'QTUM-USD',
    'ICX': 'ICX-USD',
    'OMG': 'OMG-USD',
    'LRC': 'LRC-USD',
    'ZRX': 'ZRX-USD',
    'BAT': 'BAT-USD',
    'REP': 'REP-USD',
    'GNT': 'GNT-USD',
    
    # أزواج الفوركس الرئيسية
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    'USDJPY': 'USDJPY=X',
    'USDCHF': 'USDCHF=X',
    'AUDUSD': 'AUDUSD=X',
    'USDCAD': 'USDCAD=X',
    'NZDUSD': 'NZDUSD=X',
    
    # أزواج الفوركس الفرعية
    'EURJPY': 'EURJPY=X',
    'GBPJPY': 'GBPJPY=X',
    'EURGBP': 'EURGBP=X',
    'EURAUD': 'EURAUD=X',
    'EURCAD': 'EURCAD=X',
    'EURCHF': 'EURCHF=X',
    'GBPAUD': 'GBPAUD=X',
    'GBPCAD': 'GBPCAD=X',
    'GBPCHF': 'GBPCHF=X',
    'AUDCAD': 'AUDCAD=X',
    'AUDCHF': 'AUDCHF=X',
    'AUDJPY': 'AUDJPY=X',
    'CADJPY': 'CADJPY=X',
    'CHFJPY': 'CHFJPY=X',
    'NZDJPY': 'NZDJPY=X',
    'NZDCAD': 'NZDCAD=X',
    'NZDCHF': 'NZDCHF=X',
    
    # الأسهم الأمريكية الشائعة
    'AAPL': 'AAPL',      # Apple
    'MSFT': 'MSFT',      # Microsoft
    'GOOGL': 'GOOGL',    # Google
    'AMZN': 'AMZN',      # Amazon
    'TSLA': 'TSLA',      # Tesla
    'META': 'META',      # Meta (Facebook)
    'NVDA': 'NVDA',      # NVIDIA
    'JPM': 'JPM',        # JPMorgan Chase
    'JNJ': 'JNJ',        # Johnson & Johnson
    'V': 'V',            # Visa
    'PG': 'PG',          # Procter & Gamble
    'HD': 'HD',          # Home Depot
    'MA': 'MA',          # Mastercard
    'UNH': 'UNH',        # UnitedHealth
    'BAC': 'BAC',        # Bank of America
    'DIS': 'DIS',        # Disney
    'ADBE': 'ADBE',      # Adobe
    'CRM': 'CRM',        # Salesforce
    'NFLX': 'NFLX',      # Netflix
    'XOM': 'XOM',        # Exxon Mobil
    'KO': 'KO',          # Coca-Cola
    'PEP': 'PEP',        # PepsiCo
    'INTC': 'INTC',      # Intel
    'AMD': 'AMD',        # AMD
    'CSCO': 'CSCO',      # Cisco
    'VZ': 'VZ',          # Verizon
    'PFE': 'PFE',        # Pfizer
    'T': 'T',            # AT&T
    'MRK': 'MRK',        # Merck
    'ABBV': 'ABBV',      # AbbVie
    'CVX': 'CVX',        # Chevron
    'WMT': 'WMT',        # Walmart
    'LLY': 'LLY',        # Eli Lilly
    'AVGO': 'AVGO',      # Broadcom
    'TMO': 'TMO',        # Thermo Fisher
    'ACN': 'ACN',        # Accenture
    'COST': 'COST',      # Costco
    'DHR': 'DHR',        # Danaher
    'NEE': 'NEE',        # NextEra Energy
    'TXN': 'TXN',        # Texas Instruments
    'LIN': 'LIN',        # Linde
    'HON': 'HON',        # Honeywell
    'QCOM': 'QCOM',      # Qualcomm
    'UPS': 'UPS',        # United Parcel Service
    'LOW': 'LOW',        # Lowe's
    'SBUX': 'SBUX',      # Starbucks
    'MDT': 'MDT',        # Medtronic
    'CAT': 'CAT',        # Caterpillar
    'DE': 'DE',          # Deere & Company
    'GS': 'GS',          # Goldman Sachs
    'AXP': 'AXP',        # American Express
    'BLK': 'BLK',        # BlackRock
    'BKNG': 'BKNG',      # Booking Holdings
    'GILD': 'GILD',      # Gilead Sciences
    'MMM': 'MMM',        # 3M
    'MDLZ': 'MDLZ',      # Mondelez International
    'CI': 'CI',          # Cigna
    'SO': 'SO',          # Southern Company
    'DUK': 'DUK',        # Duke Energy
    'PLD': 'PLD',        # Prologis
    'AMT': 'AMT',        # American Tower
    'CCI': 'CCI',        # Crown Castle
    'EQIX': 'EQIX',      # Equinix
    'WELL': 'WELL',      # Welltower
    'PSA': 'PSA',        # Public Storage
    'O': 'O',            # Realty Income
    'SPG': 'SPG',        # Simon Property Group
    'VTR': 'VTR',        # Ventas
    'HCP': 'HCP',        # HCP Inc.
    'EXR': 'EXR',        # Extended Stay America
    'AVB': 'AVB',        # AvalonBay Communities
    'EQR': 'EQR',        # Equity Residential
    'MAA': 'MAA',        # Mid-America Apartment Communities
    'UDR': 'UDR',        # UDR Inc.
    'ESS': 'ESS',        # Essex Property Trust
    'CPT': 'CPT',        # Camden Property Trust
    'AIV': 'AIV',        # Aimco
    'BXP': 'BXP',        # Boston Properties
    'KIM': 'KIM',        # Kimco Realty
    'REG': 'REG',        # Regency Centers
    'FRT': 'FRT',        # Federal Realty Investment Trust
    'MAC': 'MAC',        # Macerich
    'SLG': 'SLG',        # SL Green Realty
    'BEP': 'BEP',        # Brookfield Renewable Partners
    'NEP': 'NEP',        # NextEra Energy Partners
    'AEP': 'AEP',        # American Electric Power
    'EXC': 'EXC',        # Exelon
    'XEL': 'XEL',        # Xcel Energy
    'SRE': 'SRE',        # Sempra Energy
    'D': 'D',            # Dominion Energy
    'PCG': 'PCG',        # PG&E Corporation
    'ED': 'ED',          # Consolidated Edison
    'FE': 'FE',          # FirstEnergy
    'ETR': 'ETR',        # Entergy
    'AEE': 'AEE',        # Ameren
    'LNT': 'LNT',        # Alliant Energy
    'NI': 'NI',          # NiSource
    'PNW': 'PNW',        # Pinnacle West Capital
    'ES': 'ES',          # Eversource Energy
    'WEC': 'WEC',        # WEC Energy Group
    'CNP': 'CNP',        # CenterPoint Energy
    'ATO': 'ATO',        # Atmos Energy
    'CMS': 'CMS',        # CMS Energy
    'PEG': 'PEG',        # Public Service Enterprise Group
    'IDA': 'IDA',        # IDACORP
    'NJR': 'NJR',        # New Jersey Resources
    'SWX': 'SWX',        # Southwest Gas
    'OGE': 'OGE',        # OGE Energy
    'UIL': 'UIL',        # UIL Holdings
    'AVA': 'AVA',        # Avista
    'NWE': 'NWE',        # NorthWestern Energy
    'BKH': 'BKH',        # Black Hills
    'SR': 'SR',          # Spire
    'MDU': 'MDU',        # MDU Resources Group
    'GXP': 'GXP',        # Great Plains Energy
    'AGR': 'AGR',        # Avangrid
    'EIX': 'EIX',        # Edison International
    'PPL': 'PPL',        # PPL Corporation
    'ALE': 'ALE',        # ALLETE
    'HE': 'HE',          # Hawaiian Electric Industries
    'NVE': 'NVE',        # NV Energy
    'POR': 'POR',        # Portland General Electric
    'SCG': 'SCG',        # SCANA Corporation
    'VST': 'VST',        # Vistra Energy
    'CEG': 'CEG',        # Constellation Energy
    'NEE-PR': 'NEE-PR',  # NextEra Energy Partners Preferred
    'AEP-PA': 'AEP-PA',  # American Electric Power Preferred A
    'D-PA': 'D-PA',      # Dominion Energy Preferred A
    'SO-PA': 'SO-PA',    # Southern Company Preferred A
    'DUK-PA': 'DUK-PA',  # Duke Energy Preferred A
    'XEL-PA': 'XEL-PA',  # Xcel Energy Preferred A
    'EXC-PA': 'EXC-PA',  # Exelon Preferred A
    'SRE-PA': 'SRE-PA',  # Sempra Energy Preferred A
    'PCG-PA': 'PCG-PA',  # PG&E Corporation Preferred A
    'ED-PA': 'ED-PA',    # Consolidated Edison Preferred A
    'FE-PA': 'FE-PA',    # FirstEnergy Preferred A
    'ETR-PA': 'ETR-PA',  # Entergy Preferred A
    'AEE-PA': 'AEE-PA',  # Ameren Preferred A
    'LNT-PA': 'LNT-PA',  # Alliant Energy Preferred A
    'NI-PA': 'NI-PA',    # NiSource Preferred A
    'PNW-PA': 'PNW-PA',  # Pinnacle West Capital Preferred A
    'ES-PA': 'ES-PA',    # Eversource Energy Preferred A
    'WEC-PA': 'WEC-PA',  # WEC Energy Group Preferred A
    'CNP-PA': 'CNP-PA',  # CenterPoint Energy Preferred A
    'ATO-PA': 'ATO-PA',  # Atmos Energy Preferred A
    'CMS-PA': 'CMS-PA',  # CMS Energy Preferred A
    'PEG-PA': 'PEG-PA',  # Public Service Enterprise Group Preferred A
}

def get_correct_symbol(symbol):
    """
    تحويل الرمز إلى الرمز الصحيح المدعوم في yfinance
    """
    symbol = symbol.upper().strip()
    
    # إزالة العلامات الخاصة
    symbol = symbol.replace('$', '')
    
    # البحث في خريطة الرموز
    if symbol in SYMBOL_MAPPING:
        return SYMBOL_MAPPING[symbol]
    
    # إذا لم يجد الرمز، إرجاع الرمز الأصلي
    return symbol

def determine_market_type(symbol):
    """
    تحديد نوع السوق بناءً على الرمز
    """
    symbol = symbol.upper()
    
    # العملات الرقمية
    if any(crypto in symbol for crypto in ['BTC', 'ETH', 'ADA', 'XRP', 'LTC', 'BCH', 'DOT', 'LINK', 'BNB', 'SOL']):
        return 'crypto'
    elif '-USD' in symbol:
        return 'crypto'
    
    # المؤشرات والسلع
    elif any(index in symbol for index in ['^', 'US30', 'US500', 'US100', 'DAX', 'FTSE', 'CAC', 'NIKKEI', 'HSI']):
        return 'index'
    elif symbol in ['GC=F', 'SI=F', 'CL=F', 'BZ=F'] or any(commodity in symbol for commodity in ['GOLD', 'SILVER', 'OIL', 'CRUDE', 'WTI', 'BRENT']):
        return 'commodity'
    
    # الفوركس
    elif '=X' in symbol or any(curr in symbol for curr in ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']):
        return 'forex'
    
    # الأسهم (افتراضي)
    else:
        return 'stock'

# الفريمات الزمنية المدعومة
TIMEFRAMES = {
    '1m': {'period': '1d', 'interval': '1m', 'name': 'دقيقة واحدة'},
    '5m': {'period': '5d', 'interval': '5m', 'name': 'خمس دقائق'},
    '15m': {'period': '5d', 'interval': '15m', 'name': 'ربع ساعة'},
    '30m': {'period': '5d', 'interval': '30m', 'name': 'نصف ساعة'},
    '1h': {'period': '5d', 'interval': '1h', 'name': 'ساعة واحدة'},
    '4h': {'period': '1mo', 'interval': '1h', 'name': 'أربع ساعات'},
    '1d': {'period': '3mo', 'interval': '1d', 'name': 'يوم واحد'},
    '1w': {'period': '1y', 'interval': '1wk', 'name': 'أسبوع واحد'},
    '1M': {'period': '2y', 'interval': '1mo', 'name': 'شهر واحد'}
}

def get_timeframe_config(timeframe):
    """
    الحصول على إعدادات الفريم الزمني
    """
    timeframe = timeframe.lower()
    
    if timeframe in TIMEFRAMES:
        return TIMEFRAMES[timeframe]
    else:
        # افتراضي - ساعة واحدة
        return TIMEFRAMES['1h']