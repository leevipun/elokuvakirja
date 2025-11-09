# Elokuva-Arkisto - Kurssivaatimuksien Arviointi

Tämä dokumentti arvioi sovelluksen täyttämät ja täyttämättömät vaatimukset kurssin eri arvosanaluokille (3, 4 ja 5).

---

## 📋 ARVOSANA 3 - PERUSVAATIMUKSET

### Sovelluksen Perusvaatimukset

| Vaatimus                                                | Status  | Huomautukset                                                 |
| ------------------------------------------------------- | ------- | ------------------------------------------------------------ |
| ✅ Käyttäjä pystyy luomaan tunnuksen                    | TÄYTTÄÄ | `register` route toteutettu, salasanat hashittu Werkzeug:lla |
| ✅ Käyttäjä pystyy kirjautumaan sisään                  | TÄYTTÄÄ | `login` route toteutettu, password check toteutettu          |
| ✅ Käyttäjä pystyy lisäämään elokuvia                   | TÄYTTÄÄ | `/add` route, `add_movie()` funktio toteutettu               |
| ✅ Käyttäjä pystyy muokkaamaan elokuvia                 | TÄYTTÄÄ | `/edit/<movie_id>` route, owner- ja non-owner edit logic     |
| ✅ Käyttäjä pystyy poistamaan elokuvia                  | TÄYTTÄÄ | `/delete/<movie_id>` route, owner-only deletion              |
| ✅ Käyttäjä näkee lisätyt tietokohteet                  | TÄYTTÄÄ | `/` route näyttää elokuvat, pagination toteutettu            |
| ✅ Käyttäjä pystyy etsimään elokuvia                    | TÄYTTÄÄ | `/search` route, suodatus nimen/genren/vuoden perusteella    |
| ✅ Käyttäjäsivu näyttää tilastoja                       | TÄYTTÄÄ | `/dashboard` route, käyttäjä-dashboard toteutettu            |
| ✅ Käyttäjä pystyy valitsemaan luokittelun              | TÄYTTÄÄ | Categories, platforms, directors - dropdown + custom add     |
| ✅ Käyttäjä pystyy lisäämään toissijaisia tietokohteita | TÄYTTÄÄ | Arvioinnnit, suosikki-merkkaus, review-teksti                |

### Tekniset Perusvaatimukset

| Vaatimus                  | Status  | Huomautukset                                |
| ------------------------- | ------- | ------------------------------------------- |
| ✅ Flask-sovellus         | TÄYTTÄÄ | Käyttää Flask 3.1.2                         |
| ✅ SQLite-tietokanta      | TÄYTTÄÄ | `database.db` SQLite3                       |
| ✅ HTML-pohjainen UI      | TÄYTTÄÄ | 8 HTML-pohjaa templates/-kansiossa          |
| ✅ Ei JavaScript-koodia   | TÄYTTÄÄ | Puhtaasti HTML/CSS, ei JS:ää                |
| ✅ SQL suoraan            | TÄYTTÄÄ | Parametroidut SQL-kyselyt, ei ORM:ää        |
| ✅ Vain Flask + Werkzeug  | TÄYTTÄÄ | Ei muita app-spesifisiä kirjastoja          |
| ✅ Itse tehty CSS         | TÄYTTÄÄ | `static/styles.css` 1200+ riviä omaa CSS:ää |
| ✅ Koodi englanniksi      | TÄYTTÄÄ | Kaikki funktionimet, muuttujat englanniksi  |
| ✅ Tietokanta englanniksi | TÄYTTÄÄ | Kaikki taulut ja sarakkeet englanniksi      |
| ✅ Git versionhallinta    | TÄYTTÄÄ | 20+ committi, `.git` kansio olemassa        |

### Turvallisuus

| Vaatimus                             | Status  | Huomautukset                                                        |
| ------------------------------------ | ------- | ------------------------------------------------------------------- |
| ✅ Salasanat hashataan               | TÄYTTÄÄ | `werkzeug.security.generate_password_hash` + `check_password_hash`  |
| ✅ Käyttäjän oikeudet tarkastetaan   | TÄYTTÄÄ | Login-check, owner-check elokuvan poistossa                         |
| ✅ Lomakkeiden oikeudet tarkastetaan | TÄYTTÄÄ | Owner vs non-owner edit logic                                       |
| ✅ Syötteet tarkastetaan             | TÄYTTÄÄ | `.strip()`, None-check, validaatio                                  |
| ✅ Parametroidut SQL-kyselyt         | TÄYTTÄÄ | Kaikki kyselyt käyttävät `?` parametreja                            |
| ✅ Sivupohjat (render_template)      | TÄYTTÄÄ | Kaikki vastaukset käyttävät Jinja2 pohjia                           |
| ✅ CSRF-suoja                        | TÄYTTÄÄ | `secrets.token_hex()`, CSRF token verification kaikissa lomakkeissa |

### Versionhallinta & Dokumentaatio

| Vaatimus                            | Status  | Huomautukset                                |
| ----------------------------------- | ------- | ------------------------------------------- |
| ✅ README.md                        | TÄYTTÄÄ | Kattava README asennus- ja käyttöohjeilla   |
| ✅ Säännölliset commitit            | TÄYTTÄÄ | 20 committi viimeisten kahden viikon aikana |
| ✅ Englanninkieliset commit-viestit | TÄYTTÄÄ | Kaikki commit-viestit englanniksi           |

**ARVOSANA 3 STATUS: ✅ KAIKKI VAATIMUKSET TÄYTETTY**

---

## 📈 ARVOSANA 4 - LISÄVAATIMUKSET

### Toimivuus ja Käytettävyys

| Vaatimus                             | Status  | Huomautukset                                                   |
| ------------------------------------ | ------- | -------------------------------------------------------------- |
| ✅ Helppo ja looginen käyttöliittymä | TÄYTTÄÄ | Intuitiivinen navigaatio, selkeät nappulat                     |
| ✅ CSS toteutettu hyvin              | TÄYTTÄÄ | 1200+ riviä omaa CSS:ää, gradientit, hover-efektit, responsive |
| ✅ Ei CSS-kirjastoja                 | TÄYTTÄÄ | Kaikki CSS käsin kirjoitettu, ei Bootstrap/Tailwind            |

### Versionhallinta

| Vaatimus                             | Status  | Huomautukset                                              |
| ------------------------------------ | ------- | --------------------------------------------------------- |
| ✅ Ei sinne kuulumattomia tiedostoja | TÄYTTÄÄ | `.gitignore` asetettu, `__pycache__/` ja `.venv/` ignored |
| ✅ Hyvät commitit                    | TÄYTTÄÄ | Commitit koherentteja, hyviä viestejä, loogisia pakkausta |

### Ohjelmointityyli

| Vaatimus                                | Status  | Huomautukset                                               |
| --------------------------------------- | ------- | ---------------------------------------------------------- |
| ✅ Kuvaavat muuttuja- ja funktionimen   | TÄYTTÄÄ | `get_movies()`, `search_movies()`, `pagination_info` jne.  |
| ✅ 4-välilyönnin sisennys               | TÄYTTÄÄ | Johdonmukainen 4 välilyönnin sisennys                      |
| ✅ Ei liian pitkiä rivejä               | TÄYTTÄÄ | Rivit noudattavat kohtuullista pituutta (max ~100 merkkiä) |
| ✅ snake_case nimeäminen                | TÄYTTÄÄ | `get_total_movies_count()`, `add_to_favorites()` jne.      |
| ✅ Välit oikein operaattorien ympärillä | TÄYTTÄÄ | `total_pages = ceil(...)`, `name = text.strip()`           |
| ✅ Ei ylimääräisiä sulkeita if/while    | TÄYTTÄÄ | `if user:` eikä `if (user):`                               |

### Tietokanta-asiat

| Vaatimus                          | Status  | Huomautukset                                                      |
| --------------------------------- | ------- | ----------------------------------------------------------------- |
| ✅ Kuvaavasti nimetyt taulut      | TÄYTTÄÄ | `movies`, `users`, `categories`, `user_ratings`, `user_favorites` |
| ✅ Kuvaavasti nimetyt sarakkeet   | TÄYTTÄÄ | `created_at`, `owner_id`, `watch_date`, `watched_with`            |
| ✅ REFERENCES-määre käytetty      | TÄYTTÄÄ | `owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE`         |
| ✅ Ei SELECT \*                   | TÄYTTÄÄ | Kaikki kyselyt listaavat sarakkeet eksplisiittisesti              |
| ✅ SQL:n ominaisuuksia järkevästi | TÄYTTÄÄ | GROUP BY, LEFT JOIN, aggregaaatiot (AVG, COUNT)                   |

### Vertaisarviointi ja Palaute

| Vaatimus                        | Status   | Huomautukset                                  |
| ------------------------------- | -------- | --------------------------------------------- |
| ✅ Ensimmäinen vertaisarviointi | TÄYTTÄÄ  | Suoritettu opiskelijakaverin projektin kanssa |
| ✅ Toinen vertaisarviointi      | TÄYTTÄÄ  | Suoritettu opiskelijakaverin projektin kanssa |
| 🟡 Kurssipalaute annettu        | OSITTAIN | Palautejärjestelmästä riippuu                 |

**ARVOSANA 4 STATUS: ✅ KAIKKI VAATIMUKSET TÄYTETTY**

---

## 🏆 ARVOSANA 5 - EDISTYNEET VAATIMUKSET

### Ohjelmointityyli - Pylint

| Vaatimus                   | Status       | Huomautukset                                          |
| -------------------------- | ------------ | ----------------------------------------------------- |
| ❌ Pylint-raportti annettu | **EI TÄYTÄ** | Pylint-raporttia (pylint-report.md) ei vielä olemassa |

**Pylint-raportin luomisen vaiheet:**

```bash
# Asennetaan pylint (tai tarkistetaan että se on asennettu)
pip install pylint

# Ajetaan pylint sovellukselle
pylint app.py movies.py users.py categories.py platforms.py directors.py review.py db.py > pylint-report.txt

# Luodaan pylint-report.md selostuksella jokaisesta ilmoituksesta
```

### Toimivuus ja Käytettävyys

| Vaatimus                                    | Status       | Huomautukset                                                                   |
| ------------------------------------------- | ------------ | ------------------------------------------------------------------------------ |
| ✅ Käyttäjän tekstissä rivinvaihdot näkyvät | TÄYTTÄÄ      | Review-kenttä käyttää `<textarea>` jota renderöidään HTML:ssa                  |
| ✅ Kuvissa alt-attribuutti                  | TÄYTTÄÄ      | Sovelluksessa ei kuvia, vaan emoji-ikoneita                                    |
| ❌ Lomakkeissa label-elementti              | **EI TÄYTÄ** | Label-elementit puuttuvat monista lomakkeista, käytetään vain `<label>` teksti |

**Label-elementtien lisääminen:**

- `add.html`, `edit.html`, `edit_owner.html`: Label-elementit puuttuvat
- `login.html`, `register.html`: Osittain käytössä, mutta voisi parantaa

### Suuren Tietomäärän Käsittely

| Vaatimus                       | Status  | Huomautukset                                                  |
| ------------------------------ | ------- | ------------------------------------------------------------- |
| ✅ Sivutus toteutettu          | TÄYTTÄÄ | Pagination 20 elokuvaa per sivu, `get_movies(page, per_page)` |
| ✅ Testaus suurella datalla    | TÄYTTÄÄ | `seed.py` 1000 elokuvalla, 5000 arvioinnilla testattu         |
| ✅ Indeksit tietokannassa      | TÄYTTÄÄ | 13 indeksia `schema.sql`:ssa                                  |
| ✅ Raportointi suorituskyvystä | TÄYTTÄÄ | README.md sisältää yksityiskohtaisen performance-raportin     |

**Suorituskykyraportin sisältö:**

- ✅ Seed-data (1000 elokuvaa, 5000 arviointia)
- ✅ Tietokannan indeksit (13 kpl)
- ✅ Sivutus (20 per sivu)
- ✅ Latausajat (150-250ms per sivu)
- ✅ Indeksien hyöty (50-72% nopeampi)
- ✅ Testattavat ominaisuudet listattu

**ARVOSANA 5 STATUS: 🟡 OSITTAIN TÄYTETTY**

---

## 📊 YHTEENVETO

### Saavutetut Arvosanatasot

| Arvosana | Vaatimukset            | Status          |
| -------- | ---------------------- | --------------- |
| **3**    | Perusvaatimukset       | ✅ **TÄYTTÄÄ**  |
| **4**    | Lisävaatimukset        | ✅ **TÄYTTÄÄ**  |
| **5**    | Edistyneet vaatimukset | 🟡 **OSITTAIN** |

### Puuttuvat Vaatimukset Arvosanalle 5

1. **Pylint-raportti** (kriittinen)

   - Tarvitaan: `pylint-report.md` tiedosto
   - Selostus jokaisen Pylint-ilmoituksen ratkaisusta

2. **Label-elementit lomakkeissa** (parantaminen)
   - Tarvitaan: HTML label-elementit lomakkeissa
   - Helpottaa saavutettavuutta

### Korjausmahdollisuudet

#### Helppo ratkaista (30 min):

- [ ] Label-elementit lisätä `add.html`, `edit.html`, `edit_owner.html`

#### Kriittinen ratkaista (20 min):

- [ ] Ajaa `pylint app.py movies.py users.py categories.py platforms.py directors.py review.py db.py`
- [ ] Luoda `pylint-report.md` selostuksella

---

## 🚀 SUOSITUKSET

### Arvosanan 5 Saavuttamiseksi

**Vaihe 1: Pylint-raportti (KRIITTINEN)**

```bash
# 1. Aja pylint
pylint app.py movies.py users.py categories.py platforms.py directors.py review.py db.py --max-line-length=120 > pylint_output.txt

# 2. Luo pylint-report.md malliin:
# - Lista kaikista Pylint-ilmoituksista
# - Selostus MIKSI asiaa ei ole korjattu
# - Ryhmittele samankaltaiset ilmoitukset
```

**Vaihe 2: Label-elementit (PARANTAMINEN)**

Päivitä HTML-lomakkeet:

```html
<!-- Ennen: -->
<input type="text" name="title" />

<!-- Jälkeen: -->
<label for="title">Movie Title:</label>
<input type="text" id="title" name="title" />
```

---

## 📝 MUISTIINPANOT

### Vahvuudet

✅ Pehmeä aloitus perusvaatimuksille  
✅ Kattava CSS-toteutus  
✅ Hyvä tietokanta-suunnittelu indekseillä  
✅ Toimiva pagination suurelle datamäärälle  
✅ Turvallisuus toteutettu (CSRF, hashing, parameterized queries)  
✅ Git-historia hyvä ja järkevä

### Parannettavaa

🟡 Pylint-raportti puuttuu (arvosana 5 edellytys)  
🟡 Label-elementit voisi parantaa  
🟡 HTML accessibility-tasoa voisi kohentaa

### Koodin Laatu

- Muuttujanimet: **Erinomainen** (descriptive)
- SQL-kyselyt: **Erinomainen** (parametroidut, no SELECT \*)
- CSS: **Erinomainen** (itse tehty, responsive, hyvä design)
- Tietokannan rakenne: **Erinomainen** (normalisoitu, indeksit)
- Turvallisuus: **Erinomainen** (CSRF, hashing, input validation)

---

**Arviointi päivitetty:** 2025-11-09  
**Arvioija:** Automated Evaluation System  
**Seuraava tarkistus:** Pylint-raportin jälkeen
