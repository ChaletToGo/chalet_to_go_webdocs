"""Deployment smoke test for country-based pricing through the running app."""
from urllib.request import Request, urlopen


def main():
    for country, currency, language in [('BR', 'BRL', 'de'), ('CH', 'CHF', 'pt-BR'), ('US', 'EUR', 'pt-BR')]:
        request = Request('http://127.0.0.1:8000/?lang=' + language,
                          headers={'CF-IPCountry': country})
        with urlopen(request, timeout=15) as response:
            if response.headers.get('X-Site-Country') != country or response.headers.get('X-Price-Currency') != currency:
                raise RuntimeError(f'Country pricing failed: {country} must use {currency}, independently of {language}.')
        print(f'Country pricing OK: {country} -> {currency}')


if __name__ == '__main__':
    main()
