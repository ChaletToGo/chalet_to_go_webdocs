# Magazine languages

Each JSON catalog includes all editorial pages, alt text, captions and reader controls. Asset paths, chapter IDs, product names and the Chalet to Go brand remain stable across languages. `pt-BR` is the editorial source; update all seven catalogs together. Romansh uses Rumantsch Grischun and needs native editorial review before external publication.

Selection order: valid `?lang=` choice, saved HttpOnly cookie, country, browser language, English. Automatic choices do not create a preference cookie. The language menu keeps the active chapter and offers automatic detection again.

Country mapping: BR → pt-BR, CH → en, IT → it, FR → fr, DE → de, PT → pt-PT. Other detected countries default to English. Swiss visitors can select English, Romansh, German, Italian or French; both Portuguese variants remain accessible as well.

Production: set `TRUST_COUNTRY_HEADER=true` only behind a controlled proxy passing Cloudflare's overwritten `CF-IPCountry` header, with direct origin access restricted. Enable Cloudflare IP Geolocation. The application does not query external location services or request GPS. Local development and requests without country information use `Accept-Language`; this is a language fallback and does not establish the user's physical country. IP country can be inaccurate with VPNs; a saved manual choice always takes priority.

Responses use `Content-Language`, `Vary` and `Cache-Control: private, no-store` to prevent caching one visitor's language for another. Explicit query links work without JavaScript. The UI strings use plain text; translated HTML is not executed.
