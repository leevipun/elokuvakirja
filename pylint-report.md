# Pylint-raportin yhteenveto ja korjausehdotukset

Tämä dokumentti käy läpi Pylintin antamat ilmoitukset ja miten ne korjataan. Raportti osoittaa pääasiassa koodin tyylillisiä ja rakenteellisia huomautuksia, ei toiminnallisia virheitä. Korjaukset parantavat koodin ylläpidettävyyttä ja yhtenäisyyttä.

```
******\******* Module users
users.py:11:19: C0303: Trailing whitespace (trailing-whitespace)
******\******* Module movies
movies.py:8:0: C0303: Trailing whitespace (trailing-whitespace)
movies.py:60:0: C0303: Trailing whitespace (trailing-whitespace)
movies.py:66:0: C0303: Trailing whitespace (trailing-whitespace)
movies.py:303:0: C0303: Trailing whitespace (trailing-whitespace)
movies.py:455:0: C0303: Trailing whitespace (trailing-whitespace)
movies.py:547:0: C0303: Trailing whitespace (trailing-whitespace)
movies.py:558:0: C0303: Trailing whitespace (trailing-whitespace)
movies.py:569:0: C0303: Trailing whitespace (trailing-whitespace)
movies.py:64:9: R1716: Simplify chained comparison between the operands (chained-comparison)
movies.py:403:11: W1309: Using an f-string that does not have any interpolated variables (f-string-without-interpolation)
movies.py:544:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
movies.py:555:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
movies.py:2:0: C0411: standard import "math.ceil" should be placed before first party import "db" (wrong-import-order)
******\******* Module seed
seed.py:88:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:106:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:112:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:118:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:128:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:137:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:146:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:155:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:164:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:173:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:182:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:186:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:189:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:192:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:195:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:205:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:212:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:221:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:225:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:228:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:232:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:242:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:254:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:256:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:265:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:269:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:272:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:276:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:280:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:291:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:293:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:303:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:309:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:319:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:328:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:344:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:332:14: W1309: Using an f-string that does not have any interpolated variables (f-string-without-interpolation)
seed.py:10:0: C0411: standard import "os" should be placed before third party import "werkzeug.security.generate_password_hash" (wrong-import-order)
******\******* Module app
app.py:61:0: C0303: Trailing whitespace (trailing-whitespace)
app.py:64:0: C0303: Trailing whitespace (trailing-whitespace)
app.py:536:0: C0303: Trailing whitespace (trailing-whitespace)
app.py:538:0: C0303: Trailing whitespace (trailing-whitespace)
app.py:540:0: C0303: Trailing whitespace (trailing-whitespace)
app.py:545:0: C0303: Trailing whitespace (trailing-whitespace)
app.py:546:41: C0303: Trailing whitespace (trailing-whitespace)
app.py:351:0: R0911: Too many return statements (10/8) (too-many-return-statements)
```

## 1. Trailing Whitespace -ilmoitukset (C0303)

**Esimerkki:**

```
app.py:540:0: C0303: Trailing whitespace (trailing-whitespace)
seed.py:328:0: C0303: Trailing whitespace (trailing-whitespace)
```

Nämä ilmoitukset tarkoittavat, että rivin lopussa on ylimääräinen välilyönti tai tab-merkki.

**Korjaus:**

- Poista rivin loppuun jääneet välilyönnit

## 2. Import-järjestys (C0411)

**Esimerkki:**

```
seed.py:10:0: C0411: standard import "os" should be placed before third party import "werkzeug.security.generate_password_hash" (wrong-import-order)
```

Tämä ilmoitus kertoo, että importit eivät ole oikeassa järjestyksessä. Pylint (ja yleinen Python-tyyliohjeistus) suosittelee seuraavaa järjestystä: 1. Pythonin vakiokirjastot (esim. os, sys, datetime) 2. Kolmannen osapuolen kirjastot (esim. werkzeug, flask, requests) 3. Sovelluksen omat moduulit (esim. from .models import User)

Lisäksi jokaisen ryhmän välissä tulee olla tyhjä rivi.

**Korjaus:**

- Siirrä os import ylimmäksi ja lisää tyhjät rivit ryhmien väliin.

## 3. f-string ilman interpolaatioita (W1309)

**Esimerkki:**

```
seed.py:332:14: W1309: Using an f-string that does not have any interpolated variables (f-string-without-interpolation)
```

Tämä tarkoittaa, että käytät f-stringiä (f"teksti") vaikka tekstissä ei ole {} sisällä muuttujia.

**Korjaus:**

- Poista f-etuliite, jos muuttujia ei tarvita.
- Jos tarkoitus oikeasti oli lisätä muuttujia, lisää ne f-stringiin.

**Esimerkki:**

```
# Huono
msg = f"Seed completed."

# Hyvä (koska ei interpolointia)
msg = "Seed completed."
```

## 4. Liian monta return-lausetta (R0911)

**Esimerkki:**

```
app.py:351:0: R0911: Too many return statements (10/8) (too-many-return-statements)
```

Funktiossa on liikaa return-kohtia, mikä tekee logiikasta vaikeammin seurattavan ja ylläpidettävän.

Usein tämä liittyy pitkään if/elif/else -rakenteeseen tai tarkistuksiin, joita voisi lyhentää.

**Korjaus:**

- Yhdistä ehdollisia haaroja.
- Palauta arvoja vain lopussa, käytä väliaikaisia muuttujia.
- Pilko funktio pienempiin funktioihin, jos se tekee monta eri asiaa.
