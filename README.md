Elokuva-"Päiväkirja"

Sovelluksen toiminnot
Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan elokuvia.
Käyttäjä näkee sovellukseen lisätyt elokuvat.
Käyttäjä pystyy etsimään elokuvia nimen, ohjaajan ja genren avulla.
Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät ilmoitukset.
Käyttäjä pystyy valitsemaan elokuvalle yhden tai useamman luokittelun (esim. elokuvan genre, toistoalusta, ohjaaja).

Sovelluksen ideana on, että käyttäjät voivat lisätä katsomiaan elokuvia. Jokainen elokuva voidaan lisätä vain kerran. Jos elokuva on jo lisätty voi käyttäjä merkitä elokuvan katsotuksi ja arvostella sen. Vain elokuvan lisännyt käyttäjä voi poistaa kyseisen elokuvan. Elokuvasta näytetään tietoja mm arvostelujen keskiarvo kaikille käyttäjille. Käyttäjät voivat muokata osittain jo olemassa olevaa elokuvaan muun muassa lisätä ja poistaa "streaming platform" tietoja, jotta tämä tieto olisi aina ajantasalla uusille katselijoille.

## Sovelluksen asennus

Asenna flask-kirjasto:

```
$ pip install flask
```

Asenna pylint-kirjasto (koodin laadun tarkistamista varten):

```
$ pip install pylint
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```
