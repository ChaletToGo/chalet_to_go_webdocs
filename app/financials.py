"""Documented budget amounts; not a validated financing requirement."""
STARTUP_BUDGET = (
    ('legal', 25_000), ('premises', 120_000), ('equipment', 130_000),
    ('prototype', 70_000), ('showroom', 45_000), ('marketing', 35_000),
    ('working_capital', 150_000),
)
PRODUCTS = (
    {'name':'Basic','price':40_000,'production':15_000},
    {'name':'Standard','price':65_000,'production':25_000},
    {'name':'Premium','price':100_000,'production':39_000},
)


def budget_context():
    total = sum(amount for _,amount in STARTUP_BUDGET)
    return {'total':total,'setup':total-150_000,'working_capital':150_000,
            'items':[{'key':key,'amount':amount,'percentage':amount/total*100}
                     for key,amount in STARTUP_BUDGET]}


def product_context():
    return [{**p,'balance':p['price']-p['production'],
             'ratio':(p['price']-p['production'])/p['price']*100,
             'production_width':p['production']/100_000*100,
             'balance_width':(p['price']-p['production'])/100_000*100,
             'scenarios':[(p['price']-p['production'])*units for units in (1,5,15)]}
            for p in PRODUCTS]


def amount(value, locale):
    separator = ',' if locale == 'en' else '’' if locale == 'rm' else '\u202f' if locale in ('fr','pt-PT') else '.'
    return f'{value:,.0f}'.replace(',',separator)
