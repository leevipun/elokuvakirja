## (2 tuhatta käyttäjää, 4 miljoonaa elokuvaa, 7 miljoonaa arvostelua)

## Tietoja ajettu 100 käyttäjää myöhemmin 500 tuhatta elokuaa, 500 tuhatta arvostelua johtuen lataus ajoista

**Indeksin ja paginaation avulla:**

elapsed time: 9.0 s
127.0.0.1 - - [09/Nov/2025 21:29:42] "GET /?page=1 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [09/Nov/2025 21:29:42] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 9.06 s
127.0.0.1 - - [09/Nov/2025 21:29:45] "GET /?page=2 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [09/Nov/2025 21:29:45] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 9.06 s
127.0.0.1 - - [09/Nov/2025 21:29:47] "GET /?page=3 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [09/Nov/2025 21:29:47] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 9.06 s
127.0.0.1 - - [09/Nov/2025 21:29:48] "GET /?page=4 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [09/Nov/2025 21:29:48] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 9.07 s
127.0.0.1 - - [09/Nov/2025 21:29:49] "GET /?page=5 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [09/Nov/2025 21:29:49] "GET /static/styles.css HTTP/1.1" 304 -

**Indeksin, mutta ilman paginaatiota:**

elapsed time: 174.1 s
127.0.0.1 - - [09/Nov/2025 21:25:17] "GET / HTTP/1.1" 200 -

**Indeksin, paginaation, sekä uuden taulun avulla**

127.0.0.1 - - [11/Nov/2025 18:02:50] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 0.18 s
127.0.0.1 - - [11/Nov/2025 18:02:52] "GET /?page=1 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [11/Nov/2025 18:02:52] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 0.13 s
127.0.0.1 - - [11/Nov/2025 18:02:54] "GET /?page=2 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [11/Nov/2025 18:02:54] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 0.13 s
127.0.0.1 - - [11/Nov/2025 18:02:55] "GET /?page=3 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [11/Nov/2025 18:02:55] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 0.08 s
127.0.0.1 - - [11/Nov/2025 18:02:57] "GET /?page=4 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [11/Nov/2025 18:02:57] "GET /static/styles.css HTTP/1.1" 304 -
elapsed time: 0.09 s
127.0.0.1 - - [11/Nov/2025 18:02:58] "GET /?page=5 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [11/Nov/2025 18:02:58] "GET /static/styles.css HTTP/1.1" 304 -

**Johtopäätökset**

Voidaan nähdä, että pelkkä indeksien lisääminen tai sivuttaminen (pagination) ei yksin ratkaissut suorituskykyongelmaa. Suurin hidastava tekijä oli se, miten elokuvien keskimääräinen arvosana laskettiin jokaisella kyselykerralla suoraan user_ratings -taulusta. Kun tietokannassa on miljoonia rivejä, tämän tyyppinen aggregointi aiheuttaa merkittävän laskentakustannuksen joka haun yhteydessä.

Ratkaisuksi luotiin erillinen movie_ratings_summary -taulu, johon talletetaan valmiiksi lasketut keskiarvot ja arvostelujen määrät. Taulu päivittyy automaattisesti triggereiden avulla aina, kun käyttäjä lisää tai muuttaa arviota. Tämän ansiosta kyselyn ei tarvitse enää laskea arvoja uudestaan jokaisella haulla, vaan se voi lukea ne suoraan valmiiksi optimoidusta rakenteesta.

Kokonaisuudessaan optimointi muutti tietokantahaun raskaasta ja hitaasta operaatiosta erittäin nopeaksi ja skaalautuvaksi. Tämä ratkaisu toimii myös suurissa tietomäärissä ja kasvaa käyttäjäkunnan mukana ilman merkittävää lisäkustannusta.
