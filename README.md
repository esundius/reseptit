# Reseptit

## Sovelluksen toiminnot

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan reseptejä.
* Käyttäjä näkee sovellukseen lisätyt reseptit.
* Käyttäjä pystyy etsimään reseptejä hakusanalla.
* Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
* Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkuruoka, intialainen, vegaaninen). (ei vielä implementoitu)
* Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```bash
pip install flask
```

Luo tietokannan taulut:

```bash
sqlite3 database.db < schema.sql
```

Halutessasi voit lisätä ison määrän testidataa tietokantaan:

```bash
python seed.py
```

Voit käynnistää sovelluksen näin:

```bash
flask run
```
