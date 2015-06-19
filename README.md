# Przygoda | [![Code Health](https://landscape.io/github/VirrageS/przygoda/master/landscape.svg?style=flat&badge_auth_token=2d1ada759c4f46399a06205375c04926)](https://landscape.io/github/VirrageS/przygoda/master) | [![Circle CI](https://circleci.com/gh/VirrageS/przygoda.svg?style=shield&&circle-token=bbdd9a0c1379c15241b877d9678c64538730b6d5)](https://circleci.com/gh/VirrageS/przygoda) | [![Build Status](https://magnum.travis-ci.com/VirrageS/przygoda.svg?token=cnzFxz77oBFevu6Vrpep&branch=master)](https://magnum.travis-ci.com/VirrageS/przygoda)
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

	MacBook-Air-Janusz:przygoda VirrageS$ virtualenv env
	MacBook-Air-Janusz:przygoda VirrageS$ source env/bin/activate
	(env)MacBook-Air-Janusz:przygoda VirrageS$ pip install -r requirements.txt

## Tworzenie bazy danych
Tworzymy bazę danych do naszej aplikacji. Pamiętaj: za każdym razem jak wykonujemy
komende `db.create_all()` stara baza danych jest nadpisywana.

Aby utworzyć bazę danych wpisujemy:

	MacBook-Air-Janusz:przygoda VirrageS$
	MacBook-Air-Janusz:przygoda VirrageS$ source env/bin/activate
	(env)MacBook-Air-Janusz:przygoda VirrageS$ python shell.py
	>>> from app import db
	>>> db.create_all()
	>>> exit()

Rekomendowane użycie: za pierwszym razem odpalenia aplikacji,
po dodaniu noweg modułu lub modyfikacji istniejącego modułu (oczywiście
jeżeli te moduły dziedziczą po `db.Model`).

## Odpalanie aplikacji
Jeżeli nie jesteśmy w wirtualnym środowisku musimy wpisać:

	MacBook-Air-Janusz:przygoda VirrageS$
	MacBook-Air-Janusz:przygoda VirrageS$ source env/bin/activate
	(env)MacBook-Air-Janusz:przygoda VirrageS$

Teraz odpalamy naszą aplikację dzięki `python run.py`.

	(env)MacBook-Air-Janusz:przygoda VirrageS$ python run.py
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader

Teraz pozostało w przeglądarce wpisać [http://127.0.0.1:5000]
i powinniśmy zostać przekierowani do naszej aplikacji.


# Testowanie

Testowanie odbywa się automatycznie po `git push` przez Travis CI (na górze widać
aktualny status). Manualnie możemy to zrobić:

	(env)MacBook-Air-Janusz:przygoda VirrageS$ python setup.py test


## Ogólne

Testy umieszczamy folderze `tests`. Trzeba pamiętać aby dodać test do `__init__.py`
tak żeby mógł być przetestowany. Testy powinny mieć porządne nazwy funkcji i najlepiej
dokumentację.

## Przykład:

```python
class UserTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		self.app = app.test_client()

	def test_user_username(self):
		u = User(username='john', password='a', email='john@example.com')
		assert u.username == 'john'

	def test_user_password(self):
		u = User(username='john', password='a', email='john@example.com')
		assert u.password == 'a'

	def test_user_email(self):
		u = User(username='john', password='a', email='john@example.com')
		assert u.email == 'john@example.com'
```
