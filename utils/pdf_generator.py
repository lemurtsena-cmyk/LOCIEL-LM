import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable)
from utils.formatters import format_mga

FACTURES_DIR = os.environ.get("APP_FACTURES_DIR", "factures")
os.makedirs(FACTURES_DIR, exist_ok=True)

def generer_facture(vente, details):
    num = vente["numero_facture"] or f"FAC-{vente[\'id\']}"
    filename = os.path.join(FACTURES_DIR, f"{num}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm)

    primary = colors.HexColor("#2563eb")
    light   = colors.HexColor("#f3f4f6")
    green   = colors.HexColor("#16a34a")
    dark    = colors.HexColor("#1f2937")

    def sty(name, **kw):
        return ParagraphStyle(name, fontName="Helvetica",
                              fontSize=10, **kw)

    story = []
    # En-tête
    hd = [[
        Paragraph("GESTION BOUTIQUE PRO",
            sty("t", fontSize=20, textColor=primary,
                fontName="Helvetica-Bold")),
        Paragraph(f"<b>FACTURE</b><br/>"
            f"<font color=\'#2563eb\' size=\'14\'>{num}</font>",
            sty("r", alignment=TA_RIGHT,
                fontName="Helvetica-Bold", fontSize=12))
    ]]
    ht = Table(hd, colWidths=[10*cm, 7*cm])
    ht.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(ht)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Votre partenaire de confiance",
        sty("s", textColor=colors.HexColor("#6b7280"))))
    story.append(HRFlowable(width="100%", thickness=2,
        color=primary, spaceAfter=0.5*cm))

    date_str = str(vente["date_vente"])[:16] if vente["date_vente"] \
               else datetime.now().strftime("%d/%m/%Y %H:%M")
    client_nom = vente.get("client_nom") or "Client de passage"
    client_tel = vente.get("client_tel") or "-"

    info = [[
        Paragraph(
            f"<b>DATE:</b> {date_str}<br/>"
            f"<b>PAIEMENT:</b> {vente.get(\'mode_paiement\',\'especes\').upper()}<br/>"
            f"<b>STATUT:</b> {vente.get(\'statut\',\'\').upper()}",
            sty("i", leading=18)),
        Paragraph(
            f"<b>CLIENT:</b> {client_nom}<br/>"
            f"<b>TEL:</b> {client_tel}",
            sty("ir", leading=18, alignment=TA_RIGHT))
    ]]
    it = Table(info, colWidths=[9*cm, 8*cm])
    it.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), light),
        ("ROWPADDING",(0,0),(-1,-1), 10)]))
    story.append(it)
    story.append(Spacer(1, 0.5*cm))

    td = [["#","Code","Designation","Qte","Prix Unit.","Sous-Total"]]
    for i, d in enumerate(details, 1):
        td.append([str(i), d.get("produit_code") or "-",
            d.get("produit_nom",""), str(d["quantite"]),
            format_mga(d["prix_unitaire"]),
            format_mga(d["sous_total"])])

    dt = Table(td, colWidths=[1*cm,2.5*cm,6*cm,1.5*cm,3*cm,3*cm])
    dt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), primary),
        ("TEXTCOLOR",(0,0),(-1,0), colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1), 10),
        ("ROWPADDING",(0,0),(-1,-1), 8),
        ("ALIGN",(3,1),(-1,-1),"RIGHT"),
        ("GRID",(0,0),(-1,-1), 0.5, colors.HexColor("#d1d5db")),
        *[("BACKGROUND",(0,i),(-1,i), light)
          for i in range(2,len(td),2)],
        ("FONTNAME",(5,1),(5,-1),"Helvetica-Bold"),
        ("TEXTCOLOR",(5,1),(5,-1), green),
    ]))
    story.append(dt)
    story.append(Spacer(1, 0.5*cm))

    total  = vente.get("total", 0)
    remise = vente.get("remise", 0)
    paye   = vente.get("montant_paye", 0)
    reste  = total - paye

    rows = []
    rows.append(["Sous-Total:", format_mga(total + remise)])
    if remise > 0:
        rows.append(["Remise:", f"-{format_mga(remise)}"])
    rows.append(["TOTAL TTC:", format_mga(total)])
    rows.append(["Paye:", format_mga(paye)])
    if reste > 0:
        rows.append(["Reste a Payer:", format_mga(reste)])
    elif paye > total:
        rows.append(["Monnaie Rendue:", format_mga(paye - total)])

    tt = Table(rows, colWidths=[6*cm,4*cm], hAlign="RIGHT")
    tt.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"RIGHT"),
        ("FONTSIZE",(0,0),(-1,-1), 10),
        ("ROWPADDING",(0,0),(-1,-1), 6),
        ("FONTNAME",(0,-3),(-1,-3),"Helvetica-Bold"),
        ("FONTSIZE",(0,-3),(-1,-3), 13),
        ("TEXTCOLOR",(1,-3),(1,-3), green),
        ("BACKGROUND",(0,-3),(-1,-3), colors.HexColor("#f0fdf4")),
        ("LINEABOVE",(0,-3),(-1,-3), 2, primary),
    ]))
    story.append(tt)
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1,
        color=colors.HexColor("#d1d5db")))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Merci pour votre confiance !  •  Conservez cette facture.",
        sty("f", fontSize=9, textColor=colors.HexColor("#9ca3af"),
            alignment=TA_CENTER)))
    doc.build(story)
    return filename
