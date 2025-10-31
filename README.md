Elokuva-"Päiväkirja"

Sovelluksen toiminnot
Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan elokuvia.
Käyttäjä näkee sovellukseen lisätyt elokuvat.
Käyttäjä pystyy etsimään elokuvia nimen, ohjaajan ja genren avulla.
Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät ilmoitukset.
Käyttäjä pystyy valitsemaan elokuvalle yhden tai useamman luokittelun (esim. elokuvan genre, toistoalusta, ohjaaja).
Sovelluksen asennus
Asenna flask-kirjasto:

$ pip install flask

Asenna load_dotenv-kirjasto:
pip install load_dotenv

Lisää tiedosto .env,

joka sisältää muuttujan SECRET_KEY ja sillä arvon

Luo tietokannan taulut ja lisää alkutiedot:

$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql

Voit käynnistää sovelluksen näin:

$ flask run
