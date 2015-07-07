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

Jeżeli nie masz `pip` to użyj komend:

	MacBook-Air-Janusz:przygoda VirrageS$ apt-get update
	MacBook-Air-Janusz:przygoda VirrageS$ sudo apt-get install python3-pip python3-dev

I zainstaluj `pip3`:

	MacBook-Air-Janusz:przygoda VirrageS$ sudo pip3 install virtualenv

Teraz czas na wszystkie biblioteki:

	MacBook-Air-Janusz:przygoda VirrageS$ virtualenv env
	MacBook-Air-Janusz:przygoda VirrageS$ source env/bin/activate
	(env)MacBook-Air-Janusz:przygoda VirrageS$ pip3 install -r requirements.txt

## Tworzenie bazy danych

Tworzymy bazę danych do naszej aplikacji. Pamiętaj: za każdym razem jak wykonujemy
komende `db.create_all()` stara baza danych jest nadpisywana.

Aby utworzyć bazę danych wpisujemy:

	MacBook-Air-Janusz:przygoda VirrageS$
	MacBook-Air-Janusz:przygoda VirrageS$ source env/bin/activate
	(env)MacBook-Air-Janusz:przygoda VirrageS$ python3 shell.py
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

Teraz odpalamy naszą aplikację dzięki `python3 run.py`.

	(env)MacBook-Air-Janusz:przygoda VirrageS$ python3 run.py
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader

Teraz pozostało w przeglądarce wpisać [http://127.0.0.1:5000]
i powinniśmy zostać przekierowani do naszej aplikacji.


# Testowanie

Testowanie odbywa się automatycznie po `git push` przez Travis CI (na górze widać
aktualny status). Manualnie możemy to zrobić:

	(env)MacBook-Air-Janusz:przygoda VirrageS$ python3 -m unittest discover

# Server

## SSH

## Użytkownik

## Security

## Koniec

## Aplikacja

Na początku ściągamy wszystkie potrzebne nam biblioteki i narzędzia

	sudo apt-get update
	sudo apt-get install python3-pip python3-dev nginx

Następnie instalujemy virtualne środowisko

	sudo pip3 install virtualenv

Teraz musimy ściągnąć nasz projekt

	git clone https://github.com/VirrageS/przygoda
	cd ~/przygoda

Instalujemy w nim virtualne środowisko i aktywujemy je

	virtualenv env
	source env/bin/activate

Instalujemy wszystko czego potrzebujemy

	pip3 install gunicorn flask
	pip3 install -r requirements.txt

Dezaktywujemy virtualne środowisko i przechodzimy do dalszej części

	deactivate

## Gunicorn

Tworzymy skrypt, który będzie ciągle próbował utrzymać stabliność

	sudo nano /etc/init/przygoda.conf

i umieszczamy w nim

```text
description "Gunicorn application server running przygoda"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid virrages
setgid www-data

env PATH=/home/virrages/przygoda/env/bin
chdir /home/virrages/przygoda
exec gunicorn --workers 3 --bind unix:przygoda.sock -m 007 run:app
```

Teraz startujemy nasz skrypt, który powinnien zostać poprawnie odpalony

	sudo start przygoda

## Nginx

Na początku usuwamy default'owe strony, których nie będziemy potrzebować ani używać

	sudo rm -rf /etc/nginx/sites-enabled/default
	sudo rm -rf /etc/nginx/sites-available/default

Tworzymy nową konfigurację strony

	sudo nano /etc/nginx/sites-available/przygoda

i umieszczamy w niej:

```text
server {
    listen 80;
    server_name 104.131.76.86;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/virrages/przygoda/przygoda.sock;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

Przenosimy konfigurację z dostępnych także do aktywnych stron

	sudo ln -s /etc/nginx/sites-available/przygoda /etc/nginx/sites-enabled

Sprawdzamy czy nasza konfiguracja nginx'a jest poprawna

	sudo nginx -t

Teraz restartujemy nginx'a i powinno już wszystko działać

	sudo service nginx restart
