def format_mga(montant, show_symbol=True):
    try:
        montant = float(montant or 0)
        sign = "-" if montant < 0 else ""
        formatted = f"{abs(montant):,.0f}".replace(",", " ")
        return f"{sign}{formatted} Ar" if show_symbol else f"{sign}{formatted}"
    except:
        return "0 Ar"

def format_pourcentage(v):
    try: return f"{float(v):.1f}%"
    except: return "0.0%"

def format_date(date_str, fmt="%d/%m/%Y"):
    from datetime import datetime
    try:
        s = str(date_str)[:19]
        for f in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try: return datetime.strptime(s, f).strftime(fmt)
            except: continue
        return s[:10]
    except: return str(date_str)[:10]
