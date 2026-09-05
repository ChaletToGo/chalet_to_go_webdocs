"""Print edition, generated only from the shared editorial catalogs.

No reader state, form inputs, or calculator output enters the document.
"""
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from PIL import Image as PILImage, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, KeepTogether, Flowable

from .financials import amount, budget_context, product_context
from .i18n import catalog, LOCALES

ASSETS = Path(__file__).parent / 'static' / 'images'
FONT_DIR = Path(reportlab.__file__).parent / 'fonts'
pdfmetrics.registerFont(TTFont('Editorial', str(FONT_DIR / 'Vera.ttf')))
pdfmetrics.registerFont(TTFont('EditorialBold', str(FONT_DIR / 'VeraBd.ttf')))
pdfmetrics.registerFontFamily('Editorial', normal='Editorial', bold='EditorialBold')
FOREST, MOSS, CLAY = [colors.HexColor(c) for c in ('#0E2A20','#556B4E','#C76A3D')]
LINE = colors.HexColor('#D6D3CA')
WIDTH = A4[0] - 36*mm
STYLES = {
    'body': ParagraphStyle('body', fontName='Editorial', fontSize=10, leading=15, textColor=FOREST, spaceAfter=9),
    'intro': ParagraphStyle('intro', fontName='Editorial', fontSize=12, leading=18, textColor=FOREST, spaceAfter=15),
    'title': ParagraphStyle('title', fontName='EditorialBold', fontSize=27, leading=32, textColor=FOREST, spaceAfter=17, keepWithNext=True),
    'heading': ParagraphStyle('heading', fontName='EditorialBold', fontSize=13, leading=18, textColor=FOREST, spaceBefore=10, spaceAfter=8, keepWithNext=True),
    'small': ParagraphStyle('small', fontName='Editorial', fontSize=8, leading=12, textColor=MOSS, spaceAfter=9),
    'eyebrow': ParagraphStyle('eyebrow', fontName='EditorialBold', fontSize=8, leading=12, textColor=MOSS, spaceAfter=12, keepWithNext=True),
}

def paragraph(text, style='body'):
    # Normalize whitespace unsupported by some PDF extractors; retain accents.
    text = str(text).replace('\u202f',' ').replace('\u00a0',' ').replace('–','-').replace('—','-').replace('‑','-')
    return Paragraph(escape(text), STYLES[style])

def photo(filename, height=58*mm, width=WIDTH, crop=True):
    with PILImage.open(ASSETS / filename) as original:
        image = ImageOps.exif_transpose(original).convert('RGB')
        if crop:
            image = ImageOps.fit(image, (int(width*2.3),int(height*2.3)), centering=(.5,.35))
        else:
            image.thumbnail((int(width*2.3),int(height*2.3)))
            height = width * image.height / image.width
        stream = BytesIO()
        image.save(stream, 'JPEG', quality=88)
    stream.seek(0)
    return Image(stream, width=width, height=height)

class Bar(Flowable):
    def __init__(self, fractions, width=WIDTH):
        super().__init__()
        self.width, self.height, self.fractions = width, 12, fractions

    def draw(self):
        self.canv.setFillColor(LINE)
        self.canv.rect(0,3,self.width,6,fill=1,stroke=0)
        x = 0
        for fraction,color in zip(self.fractions,(MOSS,CLAY)):
            self.canv.setFillColor(color)
            self.canv.rect(x,3,self.width*fraction,6,fill=1,stroke=0)
            x += self.width*fraction

def table(rows, widths):
    result = Table([[paragraph(cell,'small') for cell in row] for row in rows], colWidths=widths, repeatRows=1, hAlign='LEFT')
    result.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAE7DF')),
        ('VALIGN',(0,0),(-1,-1),'TOP'), ('LINEBELOW',(0,0),(-1,-1),.4,LINE),
        ('TOPPADDING',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    return result

@lru_cache(maxsize=7)
def build_pdf(locale):
    if locale not in LOCALES:
        raise ValueError('Unsupported locale')
    data = catalog(locale)
    ui, finance = data['ui'], data['finance']
    money = lambda value: 'CHF ' + amount(value,locale)
    story = []
    for page in data['pages']:
        if story:
            story.append(PageBreak())
        story.extend([paragraph('CHALET TO GO / ' + page.get('eyebrow',ui['edition']), 'eyebrow'), paragraph(page['title'],'title')])
        layout = page['layout']
        if layout == 'cover':
            story.extend([paragraph(' '.join(ui[f'cover_deck_{n}'] for n in (1,2,3)),'intro'), photo(page['image'],135*mm), Spacer(1,12*mm), paragraph(ui['slogan'],'heading'), paragraph(ui['edition']+' / 2026 / '+LOCALES[locale],'small')])
            continue
        story.append(paragraph(page['intro'],'intro'))
        if layout == 'projection':
            # Explicit static allowlist: calculator prompts and methods are excluded.
            story.extend([paragraph(finance['prices_title'],'heading'),paragraph(finance['currency_note'])])
            for product in product_context():
                story.append(KeepTogether([paragraph(product['name']+' / '+money(product['price']),'heading'),
                    paragraph(finance['production']+': '+money(product['production'])+' · '+finance['balance']+': '+money(product['balance'])),
                    Bar([product['production_width']/100,product['balance_width']/100])]))
            story.extend([paragraph(finance['production_share']+' / '+finance['balance']+' · CHF 0 - '+amount(100000,locale),'small'),paragraph(finance['balance_note'],'small'),
                paragraph(finance['scenarios_title'],'heading'),paragraph(finance['scenarios_note']),
                table([[finance['model'],'1 ×','5 ×','15 ×']]+[[p['name']]+[amount(v,locale) for v in p['scenarios']] for p in product_context()],[WIDTH/4]*4),
                paragraph(finance['balance']+' · CHF. '+finance['supplied'],'small')])
            continue
        if page.get('image') and layout not in ('swiss','village','closing'):
            story.extend([photo(page['image']), Spacer(1,5*mm)])
        if page.get('body'):
            story.append(paragraph(page['body']))
        for date,title,text in page.get('timeline',[]):
            story.extend([paragraph(date+' / '+title,'heading'),paragraph(text)])
        for index,(src,alt,caption) in enumerate(page.get('images',[])):
            story.append(KeepTogether([photo(src,height=58*mm),paragraph(caption,'small')]))
        for index,(_,title,subtitle,text) in enumerate(page.get('models',[])):
            price = money(product_context()[index]['price']) if index < 3 else finance['by_quote']
            story.extend([paragraph(title+' / '+price,'heading'),paragraph(subtitle+' - '+text)])
        if layout == 'collection':
            story.extend([paragraph(finance['export']+' / B2B','heading'),paragraph(finance['series']+' - '+finance['by_contract'])])
        for title,text in page.get('steps',[]):
            story.extend([paragraph(title,'heading'),paragraph(text)])
        for first,second,text in page.get('features',[]):
            story.extend([paragraph(first+' / '+second,'heading'),paragraph(text)])
        for key in ('risk','concept'):
            if key+'_title' in page:
                story.extend([paragraph(page[key+'_title'],'heading'),paragraph(page[key+'_body'])])
        if 'portrait' in page:
            portrait=page['portrait']
            story.append(KeepTogether([paragraph('Marc Mathys / '+portrait['title'],'heading'),
                Table([[photo(portrait['image'],width=32*mm,crop=False),paragraph(portrait['body'])]],colWidths=[40*mm,WIDTH-40*mm],style=[('VALIGN',(0,0),(-1,-1),'TOP')])]))
        if layout == 'plan':
            budget=budget_context()
            story.extend([paragraph(finance['budget_title'],'heading'),paragraph(finance['budget_note']),paragraph(money(budget['total']),'title'),
                paragraph(finance['setup_title']+': '+money(budget['setup'])+' · '+finance['reserve_title']+': '+money(budget['working_capital']),'small')])
            for item in budget['items']:
                story.append(KeepTogether([paragraph(finance[item['key']]+' / '+money(item['amount']),'small'),Bar([item['percentage']/100]),Spacer(1,3*mm)]))
            story.extend([paragraph(finance['budget_share']+' · 0-100%. '+finance['scope_note'],'small')])
            story.extend([PageBreak(),paragraph('CHALET TO GO / '+page['eyebrow'],'eyebrow'),paragraph(page['section'],'title'),paragraph(page['intro'],'intro')])
            for period,unit,title,text in page['milestones']:
                story.append(KeepTogether([paragraph(period+' '+unit+' / '+title,'heading'),paragraph(text),Spacer(1,9*mm)]))
            story.append(paragraph(ui['plan_note'],'small'))
        if layout in ('swiss','village','closing'):
            story.extend([Spacer(1,5*mm),photo(page['image'],height=50*mm)])
        if layout == 'closing':
            story.extend([Spacer(1,6*mm),paragraph(ui['sources'],'small')])

    output=BytesIO()
    def furniture(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.line(18*mm,18*mm,A4[0]-18*mm,18*mm)
        canvas.setFont('Editorial',8)
        canvas.setFillColor(MOSS)
        canvas.drawString(18*mm,12*mm,'CHALET TO GO / '+locale.upper())
        canvas.drawRightString(A4[0]-18*mm,12*mm,str(doc.page))
        canvas.restoreState()
    document=SimpleDocTemplate(output,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=24*mm,
        title='Chalet to Go - '+ui['magazine'],author='Chalet to Go',lang=locale)
    document.build(story,onFirstPage=furniture,onLaterPages=furniture)
    return output.getvalue()
