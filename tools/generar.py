#!/usr/bin/env python3
"""Genera les pàgines estàtiques de Portantveus a partir de _dades/llibres.json.

Ús:  python3 tools/generar.py

Genera:
  - llibres/<slug>/index.html   (una pàgina per llibre, amb Book + BreadcrumbList JSON-LD)
  - autors/<slug>/index.html    (una pàgina per autor, amb Person JSON-LD)
  - sitemap.xml
  - El bloc JSON-LD del catàleg i de l'Organization dins d'index.html (entre marcadors GEN)
"""
import hashlib, html, json, re, datetime, pathlib

ARREL = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ARREL / "_dades/llibres.json").read_text(encoding="utf-8"))
ED = D["editorial"]
BASE = ED["url"].rstrip("/")
AUTORS = {a["slug"]: a for a in D["autors"]}
SECCIONS = {x["slug"]: x for x in D.get("seccions", [])}
AVUI = datetime.date.today().isoformat()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400&display=swap" rel="stylesheet" />')

e = lambda s: html.escape(s, quote=True).replace("&#x27;", "'")

def text_pla(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()

def resum(s, n=155):
    s = text_pla(s)
    if len(s) <= n:
        return s
    tall = s[:n].rsplit(" ", 1)[0].rstrip(",;:.")
    return tall + "…"

def isbn_guions(i):
    # 978-84-09-XXXXX-X (prefix d'agència espanyola 84-09, 5 dígits de títol)
    return f"{i[0:3]}-{i[3:5]}-{i[5:7]}-{i[7:12]}-{i[12]}" if len(i) == 13 else i

def jsonld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=2)
            + '\n</script>')

def org_schema():
    a = ED["adreca"]
    o = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{BASE}/#organization",
        "name": ED["nom"],
        "alternateName": "Editorial Portantveus",
        "url": f"{BASE}/",
        "logo": f"{BASE}/img/logo-portantveus.png",
        "image": f"{BASE}/og-image.png",
        "description": "Editorial independent de contes, àlbums il·lustrats, novel·les i primeres lectures per a infants i joves d'autors catalans.",
        "email": ED["email"],
        "address": {"@type": "PostalAddress", "postalCode": a["codi_postal"],
                    "addressLocality": a["localitat"], "addressRegion": a["regio"],
                    "addressCountry": a["pais"]},
        "areaServed": "Catalunya",
        "knowsLanguage": "ca",
        "founder": [{"@id": f"{BASE}/autors/anna-godoy-lopez/#persona"},
                    {"@type": "Person", "name": "Arnau Güell Soler"}],
        "member": [{"@id": f"{BASE}/autors/{s}/#persona"} for s, a in AUTORS.items() if a.get("equip", True)],
    }
    if ED.get("xarxes"):
        o["sameAs"] = ED["xarxes"]
    return o

def te_pagina(a):
    return a.get("pagina", True)

def persona_ref(slug):
    a = AUTORS[slug]
    if not te_pagina(a):
        return {"@type": "Person", "name": a["nom"]}
    return {"@type": "Person", "@id": f"{BASE}/autors/{slug}/#persona",
            "name": a["nom"], "url": f"{BASE}/autors/{slug}/"}

def nom_autor(a):
    """Nom de l'autor enllaçat a la seva pàgina, o com a text si no en té."""
    return f'<a href="/autors/{a["slug"]}/">{e(a["nom"])}</a>' if te_pagina(a) else e(a["nom"])

def paragrafs(txt):
    return "".join(f"<p>{par.strip()}</p>" for par in txt.split("\n\n") if par.strip())

def llibre_schema(b, complet=True):
    url = f"{BASE}/llibres/{b['slug']}/"
    o = {"@type": "Book", "@id": f"{url}#llibre", "name": b["titol"], "url": url,
         "inLanguage": "ca", "genre": b["genere"],
         "image": f"{BASE}/img/llibre-{b['foto']}-1400.webp",
         "author": persona_ref(b["autor"]),
         "publisher": {"@id": f"{BASE}/#organization", "@type": "Organization", "name": ED["nom"]}}
    if b.get("isbn"): o["isbn"] = b["isbn"]
    if b.get("il_lustrador"): o["illustrator"] = persona_ref(b["il_lustrador"])
    if b.get("col_leccio"): o["isPartOf"] = {"@type": "BookSeries", "name": b["col_leccio"]}
    if complet:
        o["@context"] = "https://schema.org"
        o["description"] = b["descripcio"] or text_pla(b["sinopsi"])
    if b.get("data_publicacio"): o["datePublished"] = b["data_publicacio"]
    fmt = (b.get("format") or "").lower()
    if fmt:
        o["bookFormat"] = ("https://schema.org/Hardcover" if "dura" in fmt
                           else "https://schema.org/Paperback")
    if b.get("pagines"): o["numberOfPages"] = b["pagines"]
    if b.get("edat_min") or b.get("edat_max"):
        rang = f"{b.get('edat_min') or ''}-{b.get('edat_max') or ''}"
        o["typicalAgeRange"] = rang
        o["audience"] = {"@type": "PeopleAudience", "suggestedMinAge": b.get("edat_min"),
                         "suggestedMaxAge": b.get("edat_max")}
        o["audience"] = {k: v for k, v in o["audience"].items() if v}
    if b.get("on_comprar"):
        o["offers"] = [{"@type": "Offer", "url": x["url"], "seller": {"@type": "Organization", "name": x["nom"]},
                        "availability": "https://schema.org/InStock",
                        **({"price": x["preu"], "priceCurrency": "EUR"} if x.get("preu") else {})}
                       for x in b["on_comprar"]]
    return o

def cataleg_schema():
    return {"@context": "https://schema.org", "@type": "ItemList", "name": "Catàleg Portantveus",
            "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                 "url": f"{BASE}/llibres/{b['slug']}/",
                                 "item": llibre_schema(b, complet=False)}
                                for i, b in enumerate(D["llibres"])]}

def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                for i, (n, u) in enumerate(items)]}

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--cream:#FFFFFF;--offwhite:#FAF9F7;--ink:#3D3D3D;--sepia:#6B6B6B;--gold:#F5BE60;--orange:#F0821F;--rust:#E15A1D;--red:#D9432A;--muted:#6B6B6B;--border:#ECE7DF}
body{background:var(--cream);color:var(--ink);font-family:'Inter','Poppins',sans-serif;font-size:17px;line-height:1.75}
h1,h2,h3{font-family:'Poppins',sans-serif;font-weight:700;line-height:1.15}
a{color:var(--rust)}
nav{position:sticky;top:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:1rem 3rem;background:rgba(255,255,255,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--border)}
.nav-logo img{height:42px;width:auto;display:block}
.nav-links{display:flex;gap:2.5rem;list-style:none}
.nav-links a{font-family:'Poppins',sans-serif;font-weight:500;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;text-decoration:none;color:var(--muted)}
.nav-links a:hover{color:var(--rust)}
.container{max-width:1100px;margin:0 auto;padding:0 3rem}
.label{font-family:'Poppins',sans-serif;font-weight:600;font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;color:var(--rust)}
.molles{font-family:'Poppins',sans-serif;font-size:.75rem;color:var(--muted);padding:2rem 0 0}
.molles ol{list-style:none;display:flex;flex-wrap:wrap;gap:.4rem}
.molles li+li::before{content:'›';margin-right:.4rem}
.molles a{color:var(--muted);text-decoration:none}.molles a:hover{color:var(--rust)}
.fitxa{display:grid;grid-template-columns:1.1fr 1fr;gap:4rem;padding:3rem 0 5rem;align-items:start}
.fitxa-img{border-radius:18px;overflow:hidden;background:var(--ink);aspect-ratio:3/2}
.fitxa-img img{width:100%;height:100%;object-fit:cover;display:block}
h1.titol{font-size:clamp(2rem,3.6vw,3rem);margin:.6rem 0 .8rem}
.autoria{font-family:'Poppins',sans-serif;font-weight:500;font-size:.85rem;color:var(--sepia);margin-bottom:2rem}
.autoria a{color:var(--ink)}
.sinopsi p{margin-bottom:1rem}
h2.sub{font-size:1.3rem;margin:2.5rem 0 1rem}
dl.dades{display:grid;grid-template-columns:auto 1fr;gap:.5rem 1.5rem;font-size:.95rem}
dl.dades dt{font-family:'Poppins',sans-serif;font-weight:600;font-size:.68rem;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);padding-top:.3rem}
.comprar{background:var(--offwhite);border:1px solid var(--border);border-radius:16px;padding:1.5rem;margin-top:2rem;font-size:.95rem}
.comprar ul{list-style:none;display:flex;flex-wrap:wrap;gap:.8rem;margin-top:.8rem}
.btn{display:inline-block;font-family:'Poppins',sans-serif;font-weight:600;font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;text-decoration:none;color:#fff;background:linear-gradient(135deg,var(--rust),var(--orange));padding:.8rem 1.6rem;border-radius:50px}
.altres{background:var(--offwhite);padding:4rem 0 5rem}
.altres h2{font-size:1.8rem;margin-bottom:2rem}
.graella{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1.8rem}
.mini{display:block;text-decoration:none;color:var(--ink);background:#fff;border:1px solid var(--border);border-radius:14px;overflow:hidden;transition:transform .3s,box-shadow .3s}
.mini:hover{transform:translateY(-4px);box-shadow:0 14px 40px rgba(61,61,61,.12)}
.mini img{width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;display:block}
.mini span{display:block;padding:1rem 1.1rem;font-family:'Poppins',sans-serif;font-weight:600;font-size:.95rem;line-height:1.3}
.mini small{display:block;font-family:'Poppins',sans-serif;font-weight:600;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:var(--rust);margin-bottom:.3rem}
.persona{display:grid;grid-template-columns:320px 1fr;gap:4rem;padding:3rem 0 5rem;align-items:start}
.persona img{width:100%;height:auto;border-radius:16px;display:block}
.persona-inicials{aspect-ratio:3/4;border-radius:16px;background:linear-gradient(135deg,var(--gold),var(--rust));display:flex;align-items:center;justify-content:center;font-family:'Poppins',sans-serif;font-weight:700;font-size:4.5rem;letter-spacing:.06em;color:rgba(255,255,255,.92)}
.persona-bio p{margin-bottom:1rem}
.fitxa-img.paper{background:#FAF9F7;border:1px solid var(--border)}
footer.peu{background:var(--ink);color:rgba(255,255,255,.65);padding:3rem 0;font-size:.9rem}
footer.peu .container{display:flex;justify-content:space-between;gap:2rem;flex-wrap:wrap}
footer.peu a{color:var(--gold);text-decoration:none}
footer.peu small{font-family:'Poppins',sans-serif;font-size:.65rem;letter-spacing:.1em;color:rgba(255,255,255,.35)}
@media (max-width:900px){.fitxa,.persona{grid-template-columns:1fr;gap:2rem}.persona img,.persona-inicials{max-width:320px}}
@media (max-width:600px){nav{padding:1rem 1.5rem}.nav-links{gap:1.1rem}.nav-links a{font-size:.62rem}.container{padding:0 1.25rem}}
.nav-links a{white-space:nowrap}
@media (max-width:480px){nav{padding:.8rem 1rem}.nav-links{gap:.9rem}.nav-links a{letter-spacing:.08em}.nav-links li:first-child{display:none}}
"""

def relatiu(doc, prefix="../../"):
    """Converteix rutes absolutes del lloc (/img/..., /llibres/...) en relatives, perquè les
    pàgines funcionin també en previsualitzacions locals que no serveixen des de l'arrel."""
    doc = re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{prefix}', doc)
    doc = re.sub(r'(srcset="[^"]*)', lambda m: re.sub(r'(^srcset="|, )/(?!/)', lambda n: n.group(1) + prefix, m.group(1)), doc)
    return doc

# ── Versionat d'estàtics (cache busting) ──────────────────────────────────────
# Cada referència a una imatge/icona local rep "?v=<hash del contingut>". Si el fitxer
# canvia, canvia l'URL i navegadors i Cloudflare el tornen a descarregar a l'instant;
# si no canvia, l'URL és la mateixa i es pot fer servir la còpia en cache.
EXT_VERSIONADES = ("webp", "png", "jpg", "jpeg", "gif", "svg", "ico", "css", "js")
_RE_ACTIU = re.compile(
    r'(?P<url>(?:https://portantveus\.cat)?[^\s"\',?#]*\.(?:' + "|".join(EXT_VERSIONADES) + r'))(?:\?v=[0-9a-f]+)?(?=[\s,]|$)')
_hashos = {}

def _hash_fitxer(path):
    if path not in _hashos:
        _hashos[path] = hashlib.sha1(path.read_bytes()).hexdigest()[:10] if path.is_file() else None
    return _hashos[path]

def versionar(doc, fitxer_html):
    """Afegeix ?v=hash a src, srcset, href i content (og:image...) que apuntin a fitxers del lloc."""
    carpeta = fitxer_html.parent
    def una(url):
        if url.startswith("https://portantveus.cat/"):
            fisic = ARREL / url[len("https://portantveus.cat/"):]
        elif url.startswith("/"):
            fisic = ARREL / url.lstrip("/")
        elif "://" in url or url.startswith("//"):
            return None
        else:
            fisic = (carpeta / url).resolve()
        return _hash_fitxer(fisic)
    def atribut(m):
        valor = _RE_ACTIU.sub(lambda u: u.group("url") + (f"?v={h}" if (h := una(u.group("url"))) else ""), m.group(2))
        return f'{m.group(1)}="{valor}"'
    return re.sub(r'\b(src|srcset|href|content)="([^"]*)"', atribut, doc)

def escriure(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(versionar(doc, path), encoding="utf-8")

def pagina(titol, descripcio, canonical, og_img, og_alt, cos, schemas, og_type="website"):
    return relatiu(_pagina(titol, descripcio, canonical, og_img, og_alt, cos, schemas, og_type))

def _pagina(titol, descripcio, canonical, og_img, og_alt, cos, schemas, og_type="website"):
    sch = "\n  ".join(jsonld(s) for s in schemas)
    return f"""<!DOCTYPE html>
<html lang="ca">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(titol)}</title>
  <meta name="description" content="{e(descripcio)}" />
  <meta name="robots" content="index, follow" />
  <meta name="theme-color" content="#E15A1D" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="Portantveus" />
  <meta property="og:title" content="{e(titol)}" />
  <meta property="og:description" content="{e(descripcio)}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{og_img}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{e(og_alt)}" />
  <meta property="og:locale" content="ca_ES" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{e(titol)}" />
  <meta name="twitter:description" content="{e(descripcio)}" />
  <meta name="twitter:image" content="{og_img}" />
  {FONTS}
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
  {sch}
  <style>{CSS}</style>
</head>
<body>
  <nav>
    <a href="/" class="nav-logo"><img src="/img/logo-curt.webp" alt="Portantveus — tornar a l'inici" width="63" height="42" /></a>
    <ul class="nav-links">
      <li><a href="/#projecte">El projecte</a></li>
      <li><a href="/#projectes">Publicacions</a></li>
      <li><a href="/#equip">L'equip</a></li>
      <li><a href="/#contacte">Contacte</a></li>
    </ul>
  </nav>
  <main>
{cos}
  </main>
  <footer class="peu">
    <div class="container">
      <p>Editorial Portantveus · {e(ED['adreca']['codi_postal'])} {e(ED['adreca']['localitat'])} · <a href="mailto:{ED['email']}">{ED['email']}</a></p>
      <small>{datetime.date.today().year} Editorial Portantveus · Editorial independent en llengua catalana</small>
    </div>
  </footer>
</body>
</html>
"""

def targeta(b):
    return (f'<a class="mini" href="/llibres/{b["slug"]}/">'
            f'<img src="/img/llibre-{b["foto"]}-800.webp" alt="{e(b["alt"])}" width="800" height="533" loading="lazy" />'
            f'<span><small>{e(b["genere"])}</small>{e(b["titol"])}</span></a>')

def molles(items):
    lis = "".join(f'<li><a href="{u}">{e(n)}</a></li>' if u else f'<li aria-current="page">{e(n)}</li>'
                  for n, u in items)
    return f'<nav class="molles" aria-label="Ruta de navegació"><ol>{lis}</ol></nav>'

def generar_llibre(b):
    url = f"{BASE}/llibres/{b['slug']}/"
    au = AUTORS[b["autor"]]
    il = AUTORS.get(b.get("il_lustrador") or "")
    sec = SECCIONS.get(b.get("seccio") or "")
    properament = b.get("estat") == "properament"
    credit = f"{b['titol']}, de {au['nom']}" + (f" amb il·lustracions de {il['nom']}" if il else "") + ". "
    desc = b["descripcio"] or resum(credit + b["sinopsi"])
    titol = f"{b['titol']} · {b['genere']} en català | Portantveus"
    if len(titol) > 65:
        titol = f"{b['titol']} | Portantveus"
    dades = []
    if b.get("isbn"): dades.append(("ISBN", isbn_guions(b["isbn"])))
    dades += [("Gènere", e(b["genere"]))]
    if b.get("col_leccio"): dades.append(("Col·lecció", e(b["col_leccio"])))
    if sec: dades.append(("Secció", e(sec["nom"])))
    dades += [("Idioma", "Català"), ("Text" if il else "Autoria", nom_autor(au))]
    if il: dades.append(("Il·lustracions", nom_autor(il)))
    dades.append(("Editorial", "Portantveus"))
    if properament: dades.append(("Estat", "Properament"))
    if b.get("format"): dades.append(("Format", e(b["format"])))
    if b.get("pagines"): dades.append(("Pàgines", str(b["pagines"])))
    mn, mx = b.get("edat_min"), b.get("edat_max")
    if mn and mx: dades.append(("Edat recomanada", f"De {mn} a {mx} anys"))
    elif mn: dades.append(("Edat recomanada", f"A partir de {mn} anys"))
    if b.get("data_publicacio"): dades.append(("Publicació", e(str(b["data_publicacio"]))))
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in dades)
    if b.get("on_comprar"):
        botons = "".join(f'<li><a class="btn" href="{e(x["url"])}" rel="noopener">{e(x["nom"])}</a></li>' for x in b["on_comprar"])
        comprar = f'<div class="comprar"><strong>On el pots trobar:</strong><ul>{botons}</ul></div>'
    elif properament or not b.get("isbn"):
        assumpte = "Avisa'm: " + b["titol"]
        comprar = (f'<div class="comprar"><strong>Properament a les llibreries</strong><p>Vols que t\'avisem quan surti? Escriu-nos a '
                   f'<a href="mailto:{ED["email"]}?subject={e(assumpte)}">{ED["email"]}</a>.</p></div>')
    else:
        comprar = (f'<div class="comprar"><strong>On el pots trobar:</strong><p>Demana\'l a la teva llibreria de confiança '
                   f'amb l\'ISBN <strong>{isbn_guions(b["isbn"])}</strong>, o escriu-nos a '
                   f'<a href="mailto:{ED["email"]}?subject={e("Comanda: " + b["titol"])}">{ED["email"]}</a> i te l\'enviem.</p></div>')
    altres = "".join(targeta(x) for x in D["llibres"] if x["slug"] != b["slug"])
    autoria = (f'Text: {nom_autor(au)} · Il·lustracions: {nom_autor(il)}' if il else nom_autor(au))
    if b.get("col_leccio"): autoria += f' · Col·lecció {e(b["col_leccio"])}'
    cos = f"""    <div class="container">
      {molles([("Inici", "/"), ("Catàleg", "/#projectes")] + ([(sec["nom"], f"/#{sec['slug']}")] if sec else []) + [(b["titol"], None)])}
      <article class="fitxa">
        <div class="fitxa-img{' paper' if b.get('seccio') == 'novella' else ''}">
          <img src="/img/llibre-{b['foto']}-1400.webp" srcset="/img/llibre-{b['foto']}-800.webp 800w, /img/llibre-{b['foto']}-1400.webp 1400w" sizes="(max-width: 900px) 100vw, 560px" alt="{e(b['alt'])}" width="1400" height="934" fetchpriority="high" />
        </div>
        <div>
          <span class="label">{e(b['genere'])}</span>
          <h1 class="titol">{e(b['titol'])}</h1>
          <p class="autoria">{autoria}</p>
          <h2 class="sub">Sinopsi</h2>
          <div class="sinopsi">{paragrafs(b['sinopsi'])}</div>
          <h2 class="sub">Fitxa tècnica</h2>
          <dl class="dades">{dl}</dl>
          {comprar}
        </div>
      </article>
    </div>
    <section class="altres">
      <div class="container">
        <h2>Altres llibres de Portantveus</h2>
        <div class="graella">{altres}</div>
      </div>
    </section>"""
    molla_sec = [(sec["nom"], f"{BASE}/#{sec['slug']}")] if sec else []
    schemas = [llibre_schema(b), breadcrumb([("Inici", f"{BASE}/"), ("Catàleg", f"{BASE}/#projectes")] + molla_sec + [(b["titol"], url)])]
    out = ARREL / "llibres" / b["slug"] / "index.html"
    escriure(out, pagina(titol, desc, url, f"{BASE}/img/og-{b['foto']}.jpg", b["alt"], cos, schemas, "book"))
    return url

def generar_autor(a):
    url = f"{BASE}/autors/{a['slug']}/"
    propis = [b for b in D["llibres"] if a["slug"] in (b["autor"], b.get("il_lustrador"))]
    equip = a.get("equip", True)
    titol = f"{a['nom']} · {a['rol_schema']} | Portantveus"
    bio_pla = text_pla(a["bio"])
    desc = resum((f"{a['nom']}, {a['carrec'].lower()} a l'editorial Portantveus. " if equip else "") + bio_pla)
    person = {"@context": "https://schema.org", "@type": "Person", "@id": f"{url}#persona",
              "name": a["nom"], "url": url, "jobTitle": a["rol_schema"], "description": bio_pla,
              "knowsLanguage": "ca"}
    if a.get("foto"): person["image"] = f"{BASE}/img/{a['foto']}.webp"
    if equip: person["worksFor"] = {"@id": f"{BASE}/#organization", "@type": "Organization", "name": ED["nom"]}
    if a.get("naixement"): person["birthDate"] = a["naixement"]
    if a.get("lloc_naixement"): person["birthPlace"] = {"@type": "Place", "name": a["lloc_naixement"]}
    if a.get("defuncio"): person["deathDate"] = a["defuncio"]
    foto = (f'<img src="/img/{a["foto"]}.webp" alt="{e(a["nom"])}" width="600" height="800" fetchpriority="high" />'
            if a.get("foto") else f'<div class="persona-inicials" aria-hidden="true">{e(a.get("inicials", ""))}</div>')
    bio_html = "".join(f"<p>{par}</p>" for par in a["bio"].split("\n\n"))
    molla = ("L'equip", "/#equip") if equip else ("Catàleg", "/#projectes")
    if a.get("xarxes"): person["sameAs"] = a["xarxes"]
    targetes = "".join(targeta(b) for b in propis)
    cos = f"""    <div class="container">
      {molles([("Inici", "/"), molla, (a["nom"], None)])}
      <article class="persona">
        {foto}
        <div>
          <span class="label">{e(a['carrec'])}</span>
          <h1 class="titol">{e(a['nom'])}</h1>
          <div class="persona-bio">{bio_html}</div>
        </div>
      </article>
    </div>
    <section class="altres">
      <div class="container">
        <h2>Llibres de {e(a['nom'])}</h2>
        <div class="graella">{targetes}</div>
      </div>
    </section>"""
    schemas = [person, breadcrumb([("Inici", f"{BASE}/"), (molla[0], BASE + molla[1]), (a["nom"], url)])]
    out = ARREL / "autors" / a["slug"] / "index.html"
    escriure(out, pagina(titol, desc, url, f"{BASE}/og-image.png", "Portantveus — Editorial en català", cos, schemas, "profile"))
    return url

def actualitzar_index():
    p = ARREL / "index.html"
    src = p.read_text(encoding="utf-8")
    bloc = ("<!-- GEN:jsonld (generat per tools/generar.py, no editar a mà) -->\n  "
            + jsonld(org_schema()) + "\n  " + jsonld(cataleg_schema()) + "\n  <!-- /GEN:jsonld -->")
    nou, n = re.subn(r"<!-- GEN:jsonld.*?<!-- /GEN:jsonld -->", lambda m: bloc, src, flags=re.S)
    if n != 1:
        raise SystemExit("No s'han trobat els marcadors GEN:jsonld a index.html")
    escriure(p, nou)
    p404 = ARREL / "404.html"
    escriure(p404, p404.read_text(encoding="utf-8"))

def sitemap(urls):
    files = [(f"{BASE}/", "1.0")] + [(u, "0.8") for u in urls["llibres"]] + [(u, "0.6") for u in urls["autors"]]
    body = "\n".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{AVUI}</lastmod>\n    <priority>{p}</priority>\n  </url>" for u, p in files)
    (ARREL / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n',
        encoding="utf-8")

if __name__ == "__main__":
    urls = {"llibres": [generar_llibre(b) for b in D["llibres"]],
            "autors": [generar_autor(a) for a in D["autors"] if te_pagina(a)]}
    actualitzar_index()
    sitemap(urls)
    print(f"Generades {len(urls['llibres'])} pàgines de llibre, {len(urls['autors'])} d'autor, sitemap i JSON-LD d'index.html")
