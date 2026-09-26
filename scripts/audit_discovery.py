"""Public discovery preflight. A successful probe is NOT proof of a real bot visit."""
import json
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from urllib.error import HTTPError, URLError

ORIGIN = 'https://www.chalettogo.com'
BOTS = ['Googlebot', 'bingbot', 'OAI-SearchBot', 'Claude-SearchBot', 'PerplexityBot']

def fetch(path):
    try:
        with urlopen(Request(ORIGIN + path, headers={'User-Agent': 'ChaletToGo-DiscoveryAudit/1.0'}), timeout=20) as r:
            return {'status': r.status, 'url': r.url,
                    'robots_header': r.headers.get('X-Robots-Tag', ''),
                    'challenge': r.headers.get('cf-mitigated', '')}, r.read().decode('utf-8')
    except (HTTPError, URLError) as exc:
        return {'error': str(exc)}, ''

if __name__ == '__main__':
    result, robots_text = fetch('/robots.txt')
    parser = RobotFileParser()
    parser.parse(robots_text.splitlines())
    report = {'robots': result, 'rules': {
        bot: parser.can_fetch(bot, ORIGIN + '/?lang=en') if robots_text else None for bot in BOTS},
        'pages': {path: fetch(path)[0] for path in ['/?lang=en', '/sobre?lang=en', '/llms.txt', '/sitemap.xml']},
        'limitation': 'Robots rules and ordinary HTTP requests only. Verify real crawler IPs and security events in Cloudflare; this does not prove index inclusion or AI recommendations.'}
    print(json.dumps(report, indent=2, ensure_ascii=False))
