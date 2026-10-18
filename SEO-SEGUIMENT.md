# Seguiment de millores SEO — portantveus.cat

Basat en l'auditoria SEO (puntuació inicial **64/100**). Darrera actualització: **2026-10-18**.

Llegenda: ✅ fet · 🟡 parcial / falta una dada · ⬜ pendent · 👤 depèn d'una decisió o dada vostra

## Resum

| Bloc | Estat |
|---|---|
| Crítics (3) | ✅ 3/3 |
| Avisos (6) | ✅ 4 · 🟡 2 (falten dades: xarxes, botigues, fitxa tècnica) |
| Oportunitats (5) | ✅ 4 · ⬜ 1 (esdeveniments) |
| Comprovacions externes | ⬜ 3 (fer-les després de publicar) |

---

## 1. Problemes crítics

### ✅ 1.1 Una pàgina per llibre
- Noves URL: `/llibres/aran-i-les-paraules-magiques/`, `/llibres/onada-de-contes/`, `/llibres/el-ratoli-oli/`, `/llibres/el-xup-xup-de-laris/`, `/llibres/pi-pa-pipa/`.
- Cada pàgina té: títol i descripció propis, canonical, OG/Twitter amb imatge pròpia 1200×630 (`img/og-*.jpg`), H1 amb el títol, sinopsi, fitxa tècnica, autoria enllaçada, bloc "On el pots trobar:", enllaços als altres llibres i molles de pa.
- Schema: `Book` complet + `BreadcrumbList`.
- Les targetes de la portada enllacen a cada fitxa (títol + "Fitxa del llibre i on trobar-lo →") i el peu de la portada llista tot el catàleg.
- `sitemap.xml` ara té 8 URL (portada + 5 llibres + 2 autors).

### ✅ 1.2 Imatges pesades
Totes convertides a WebP i redimensionades a la mida de visualització (a `img/`):

| Imatge | Abans | Ara |
|---|---|---|
| Logo capçalera (LCP) | 516 KB, 2293×567 PNG | 25 KB, 1040×257 WebP |
| Logo petit nav | 126 KB, 450×300 | 3 KB, 126×84 |
| 5 fotos de llibres | ~3,8 MB, 4160×2774 JPG | 20–39 KB cadascuna (800 px) + versió 1400 px via `srcset` |
| 3 fotos d'equip | ~560 KB | ~60 KB cadascuna (600×800) |
| **Total imatges portada** | **~4,9 MB** | **~0,35 MB** |

- El logo de capçalera té `fetchpriority="high"` i `preload`.

### ✅ 1.3 width/height a totes les imatges
- Les 10 imatges de la portada i totes les de les pàgines noves tenen `width` i `height` (verificat amb script: 0 imatges sense mida).

---

## 2. Avisos

### ✅ 2.1 Títol de la portada
- Abans: `Portantveus | Editorial` (23 caràcters).
- Ara: `Portantveus · Editorial en català de contes i àlbums il·lustrats` (64). Mateix text a `og:title` i `twitter:title`.

### 🟡 2.2 Camps del schema Book
- ✅ Afegits: `image`, `description`, `url`, `genre`, `@id`, autor i il·lustrador enllaçats a les seves pàgines (`Person` amb `@id`), editorial enllaçada a l'`Organization`.
- 👤 **Falten dades** (el generador ja els suporta; només cal omplir `_dades/llibres.json`):
  - [ ] `data_publicacio` (datePublished)
  - [ ] `format` (bookFormat: tapa dura / tova)
  - [ ] `pagines` (numberOfPages)
  - [ ] `edat_min` / `edat_max` (typicalAgeRange + audience)
  - [ ] `on_comprar` (offers) — veure 2.4

### ✅ 2.3 Títols coherents entre schema i pàgina
Forma única fixada a `_dades/llibres.json` i aplicada a schema, H3, textos alternatius i fitxes:
- `L'onada de contes` (abans "L'Onada de Contes" a l'schema)
- `El xup-xup de l'Aris. Com es cuina un germanet` (amb subtítol a tot arreu)
- `Pi, pa, pipa! Començo a llegir de mica en mica` (sense "!" final; "Pi, Pa, Pipa!" de la sinopsi normalitzat)

### 🟡 2.4 Enllaços per comprar i xarxes socials
- ✅ Cada fitxa té un bloc "On el pots trobar" amb l'ISBN i un `mailto:` amb l'assumpte de la comanda ja omplert (alternativa mentre no hi hagi botigues).
- ✅ Enllaços interns nous: portada → llibres → autors → altres llibres.
- 👤 **Falten dades:**
  - [ ] URL de les llibreries/botigues on es venen → `on_comprar` a cada llibre (es mostren com a botons i generen `offers`).
  - [ ] URL reals de les xarxes (Instagram, etc. — a la portada només hi ha "@portantveus") → `editorial.xarxes` (genera `sameAs`) i convertir "@portantveus" de la secció de contacte en enllaç.

### ✅ 2.5 Pàgina 404
- Nou `404.html` en català, amb el logo, botó a l'inici i enllaços a tots els llibres i al contacte. Enllaços absoluts perquè funcioni a qualsevol ruta. `noindex`.

### ✅ 2.6 Posicionament coherent  👤 (revisar)
Decisió presa: **editorial independent en català de contes, àlbums il·lustrats i primeres lectures per a infants i joves**, oberta a la novel·la.
- Title, meta description, OG, eyebrow i H1 (text ocult) diuen el mateix.
- El text de "El projecte" ara diu: *"El nostre catàleg se centra en el conte infantil i juvenil, l'àlbum il·lustrat i les primeres lectures, i està obert a la novel·la de tots els gèneres."*
- L'etiqueta "Conte juvenil" de L'Aran es manté (encaixa amb "infants i joves").
- [ ] Confirmar que aquest enfocament us va bé.

---

## 3. Oportunitats

### ✅ 3.1 Pàgines d'autor
- `/autors/anna-godoy-lopez/` i `/autors/ivan-godoy-lopez/` amb `Person` schema, foto, bio i llistat dels seus llibres.
- Els noms de l'equip a la portada i l'autoria de cada llibre hi enllacen.
- [ ] 👤 Ampliar les bios (ara són curtes) i afegir xarxes personals (`xarxes` de cada autor → `sameAs`).

### ⬜ 3.2 Secció d'esdeveniments / notícies
- No hi ha dades d'actes concrets. Quan n'hi hagi (data, lloc, títol, descripció), es pot afegir una llista `esdeveniments` al JSON i pàgines amb `Event` schema.
- [ ] 👤 Passar el primer esdeveniment (presentació, club de lectura, concert...).

### ✅ 3.3 Google Fonts retallades
- Abans: 2 famílies, 9 pesos + itàlica. Ara: Poppins 500/600/700/800 + Inter 400 (5 pesos, els únics que es fan servir).

### ✅ 3.4 Jerarquia d'encapçalaments
- Contacte: els `h4` (Adreça, Originals…, Premsa…, Xarxes socials) passen a `h3`. Ja no hi ha salt H2 → H4.

### ✅ 3.5 Organization schema ampliat
- Afegit: `address` (08737 Torrelles de Foix, Barcelona, ES), `founder` (Anna Godoy López, Arnau Güell Soler), `member` (Anna i Ivan, enllaçats a les pàgines d'autor), logo nou optimitzat.
- [ ] 👤 Adreça completa (carrer), si es vol mostrar. A la portada el bloc "Adreça" comença amb un `<br>` buit.

---

## 4. Altres correccions fetes de passada
- ✅ HTML trencat a dues sinopsis (`<p class="sinopsis-text"</em>` i `</em>` solt) corregit.
- ✅ Errata a la sinopsi de Pi, pa, pipa!: "per teixi" → "per teixir".
- ⬜ 👤 La sinopsi de L'Aran acaba amb *"L'Aran i els regals màgics."* — sembla un altre títol o un text que s'ha quedat enganxat. Revisar.

- ✅ (2026-10-18) Fitxes d'autor i de llibre: les rutes eren absolutes (`/img/...`, `/llibres/...`) i en previsualització local (servidor d'IntelliJ a `/portantveus/`) no carregaven ni les fotos de l'equip, ni les imatges dels contes, ni els enllaços a les fitxes. Ara el generador escriu rutes relatives (`../../img/...`). Les fotos d'autor són les mateixes del grup editorial (`img/equip-3.webp` per a l'Anna i `img/equip-1.webp` per a l'Ivan). Verificat servint el lloc sota un subdirectori: totes les imatges carreguen i els enllaços autor → llibre → autor funcionen.
- ℹ️ `404.html` manté rutes absolutes a propòsit: GitHub Pages la serveix des de qualsevol URL i les relatives s'hi trencarien. Només es veu bé publicada o servida des de l'arrel.

- ✅ (2026-10-18) *Sota la pluja, un mort i mig*: sinopsi definitiva (2 paràgrafs), autora «Teresa Juvé i Acero», gènere «Novel·la detectivesca» i col·lecció «Jaume Plagumà» (a la fitxa, a la targeta de la portada i a l'schema com a `isPartOf` → `BookSeries`). Per ara no hi ha pàgina d'autora: s'ha esborrat `autors/teresa-juve/`, l'autora té `"pagina": false` al JSON i el seu nom surt com a text, sense enllaç. Quan es vulgui la pàgina, només cal treure aquest camp i tornar a generar.

## 5. Comprovacions després de publicar
- [ ] GitHub Pages → Settings → Pages: **Enforce HTTPS** activat.
- [ ] `www.portantveus.cat` redirigeix a `portantveus.cat` (DNS a Cloudflare: CNAME `www` → `arnaug.github.io`).
- [ ] PageSpeed Insights de la portada i d'una fitxa (confirmar LCP i CLS).
- [ ] Google Search Console: enviar el `sitemap.xml` nou i demanar indexació de les 5 fitxes.
- [ ] Validar l'schema amb el [Rich Results Test](https://search.google.com/test/rich-results) a una fitxa de llibre.

## 6. Neteja pendent
- [ ] Esborrar del repo les imatges originals que ja no es fan servir (~7 MB): `foto_*.JPG`, `foto_equip*.jpg`, `logo_portantveus_registre.png`, `logo_curt_junt.png`, `Logo_portantveus.png`, `LOGO CURT_JUNT*.jpg`, `logo portanveus revisat_*.jpg`, `logo_portantveus_transparent.png`, `logo_portantveus_def.jpeg`. Ja no afecten la velocitat (no es carreguen), però fan el repo més pesat. Es poden guardar fora del repo com a originals.

---

## Com mantenir-ho

Tota la informació dels llibres i autors és a **`_dades/llibres.json`** (font única). Després d'editar-lo:

```bash
python3 tools/generar.py
```

Això regenera les fitxes de llibre, les pàgines d'autor, el `sitemap.xml` i el JSON-LD de la portada (entre els marcadors `<!-- GEN:jsonld -->` d'`index.html`; no l'editeu a mà). Els camps buits no es mostren ni s'afegeixen a l'schema.

**Afegir un llibre nou:** afegir l'entrada al JSON, posar les imatges a `img/` (`llibre-<clau>-800.webp`, `llibre-<clau>-1400.webp`, `og-<clau>.jpg` de 1200×630), executar el generador i afegir la targeta a `index.html` (secció `#projectes`) i al peu.

Exemple de camps opcionals:
```json
"data_publicacio": "2024-04-23",
"format": "Tapa dura",
"pagines": 32,
"edat_min": 3,
"edat_max": 6,
"on_comprar": [{"nom": "Llibreria X", "url": "https://...", "preu": "15.00"}]
```
