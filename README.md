# Reseptit

## Sovelluksen toiminnot

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan reseptejä.
* Käyttäjä näkee sovellukseen lisätyt reseptit.
* Käyttäjä pystyy etsimään reseptejä hakusanalla.
* Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
* Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkuruoka, intialainen, vegaaninen).
* Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut:

```
$ sqlite3 database.db < schema.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```