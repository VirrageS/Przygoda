# Przygoda [![Build Status](https://travis-ci.org/VirrageS/Przygoda.svg?branch=master)](https://travis-ci.org/VirrageS/przygoda)
Aplikacja Przygoda jest najlepszym sposobem na znajdowanie miłośników rowerów

# Instalacja

## Clone GitHub project
Klonujemy nasze repozytorium:

	MacBook-Air-Janusz:Desktop VirrageS$
	MacBook-Air-Janusz:Desktop VirrageS$ git clone https://github.com/VirrageS/przygoda
	MacBook-Air-Janusz:Desktop VirrageS$ cd przygoda
	MacBook-Air-Janusz:przygoda VirrageS$

## Inicjacja wirtualnego środowiska i bibliotek
Teraz instalujemy wirtualne środowisko pythona.

Wybierz jedną z opcji instalacji:

	MacBook-Air-Janusz:przygoda VirrageS$ sudo pip install virtualenv

lub:

	MacBook-Air-Janusz:przygoda VirrageS$ sudo easy_install virtualenv

Teraz czas na wszystkie biblioteki:

	MacBook-Air-Janusz:przygoda VirrageS$ virtualenv flaskenv
	MacBook-Air-Janusz:przygoda VirrageS$ source flaskenv/bin/activate
	(flaskenv)MacBook-Air-Janusz:przygoda VirrageS$ pip install -r requirements.txt

## Tworzenie bazy danych
Tworzymy bazę danych do naszej aplikacji. Pamiętaj: za każdym razem jak wykonujemy
komende `db.create_all()` stara baza danych jest nadpisywana.

Aby utworzyć bazę danych wpisujemy:

	MacBook-Air-Janusz:przygoda VirrageS$
	MacBook-Air-Janusz:przygoda VirrageS$ source flaskenv/bin/activate
	(flaskenv)MacBook-Air-Janusz:przygoda VirrageS$ python shell.py
	>>> from app import db
	>>> db.create_all()
	>>> exit()

Rekomendowane użycie: za pierwszym razem odpalenia aplikacji,
po dodaniu noweg modułu lub modyfikacji istniejącego modułu (oczywiście
jeżeli te moduły dziedziczą po `db.Model`).

## Odpalanie aplikacji
Jeżeli nie jesteśmy w wirtualnym środowisku musimy wpisać:

	MacBook-Air-Janusz:przygoda VirrageS$
	MacBook-Air-Janusz:przygoda VirrageS$ source flaskenv/bin/activate
	(flaskenv)MacBook-Air-Janusz:przygoda VirrageS$

Teraz odpalamy naszą aplikację dzięki `python run.py`.

	(flaskenv)MacBook-Air-Janusz:przygoda VirrageS$ python run.py
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader

Teraz pozostało w przeglądarce wpisać [http://127.0.0.1:5000]
i powinniśmy zostać przekierowani do naszej aplikacji.


# Testowanie

Testowanie odbywa się w pliku `tests.py` umieszczamy w nim wszystkie unit_test,
które chcemy przetestować. Testy powinny mieć porządne nazwy funkcji i najlepiej
dokumentację.

## Przykład:

```python
def test_add_user_to_database(self):
	u = User(username='john', password='a', email='john@example.com')
	db.session.add(u)
	db.session.commit()
	u = User.query.filter_by(username='john').first()
	assert u.username == 'john'
	assert u.password == 'a'
	assert u.email == 'john@example.com'

	u = User(username='johner', password='a', email='susan@examplee.com')
	db.session.add(u)
	db.session.commit()
	u = User.query.filter_by(username='johner').first()
	assert u.username != 'john'
	assert u.username == 'johner'
```
