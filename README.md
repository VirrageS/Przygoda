# Przygoda | [![Code Health](https://landscape.io/github/VirrageS/przygoda/master/landscape.svg?style=flat&badge_auth_token=2d1ada759c4f46399a06205375c04926)](https://landscape.io/github/VirrageS/przygoda/master) | [![Circle CI](https://circleci.com/gh/VirrageS/przygoda.svg?style=shield&&circle-token=bbdd9a0c1379c15241b877d9678c64538730b6d5)](https://circleci.com/gh/VirrageS/przygoda) | [![Build Status](https://magnum.travis-ci.com/VirrageS/przygoda.svg?token=cnzFxz77oBFevu6Vrpep&branch=master)](https://magnum.travis-ci.com/VirrageS/przygoda)
Aplikacja Przygoda jest najlepszym sposobem na znajdowanie miłośników rowerów

# Instalacja

## Clone GitHub project

Klonujemy nasze repozytorium:

	MacBook-Air-Janusz:Desktop VirrageS$ sudo apt-get install git
	MacBook-Air-Janusz:Desktop VirrageS$ git clone https://github.com/VirrageS/przygoda
	MacBook-Air-Janusz:Desktop VirrageS$ cd przygoda

## Inicjacja wirtualnego środowiska i bibliotek

Teraz instalujemy wirtualne środowisko pythona.

Jeżeli nie masz `pip` to użyj komend:

	MacBook-Air-Janusz:przygoda VirrageS$ apt-get update
	MacBook-Air-Janusz:przygoda VirrageS$ sudo apt-get install python3-pip python3-dev
	MacBook-Air-Janusz:przygoda VirrageS$ sudo apt-get build-dep python3-psycopg2

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

	local$ ssh root@SERVER_IP_ADDRESS

Poprosi nas o aktualnego użytkownika i hasło (to co dostaliśmy w emailu) a następnie będziemy musieli zmienić hasło.
Jak już to zrobimy przechodzimy dalej.

## Użytkownik

Teraz przyszła kolej na stworzenie użytkownika. Tworzymy go za pomocą

	adduser virrages

Dodajemy mu wszystkie potrzebne przywileje tak aby także był administratorem

	gpasswd -a virrages sudo

## SSH ciągl dalszy

Na naszej lokalnej maszynie tworzymy nowy klucz ssh

	local$ ssh-keygen

Klikamy cały czas `enter` aż będzie wszystko w porządku.
Następnie kopiujemy nasze ssh do naszego serwera.

	local$ ssh-copy-id virrages@104.131.76.86


## Security

Musimy dezaktywować roota ze względów bezpieczeństwa
Otwieramy

	nano /etc/ssh/sshd_config

i zmieniamy linijkę

	PermitRootLogin yes

na

	PermitRootLogin no

## Testujemy połączenie

Teraz restartujemy nasze SSH

	service ssh restart

Otwieramy nową kartę w terminalu i wpisujemy

	ssh virrages@104.131.76.86

Powinniśmy od razu zostać przekierowani i przy komendzie `sudo` powinno nas zapytać o hasło.
Koniec tej części.

## All in one

	sudo apt-get update; sudo apt-get build-dep python3-psycopg2; sudo apt-get install python3-pip python3-dev nginx git; sudo pip3 install virtualenv; git clone https://github.com/VirrageS/przygoda; cd przygoda; virtualenv env; source env/bin/activate; pip3 install psycopg2; pip3 install -r requirements.txt; deactivate; sudo nano /etc/init/przygoda.conf;

```
description "Gunicorn application server running przygoda"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid ubuntu
setgid www-data

env PATH=/home/ubuntu/przygoda/env/bin
chdir /home/ubuntu/przygoda
exec gunicorn --workers 4 --bind unix:przygoda.sock -m 007 run:app
```

	sudo start przygoda; sudo rm -rf /etc/nginx/sites-enabled/default; sudo rm -rf /etc/nginx/sites-available/default; sudo nano /etc/nginx/sites-available/przygoda

```
server {
    listen 80;
    server_name ;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/przygoda/przygoda.sock;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

	sudo ln -s /etc/nginx/sites-available/przygoda /etc/nginx/sites-enabled; sudo nginx -t; sudo service nginx restart


## Aplikacja

Na początku ściągamy wszystkie potrzebne nam biblioteki i narzędzia

	sudo apt-get update
	sudo apt-get build-dep python3-psycopg2
	sudo apt-get install python3-pip python3-dev nginx git

Następnie instalujemy virtualne środowisko

	sudo pip3 install virtualenv

Teraz musimy ściągnąć nasz projekt

	git clone https://github.com/VirrageS/przygoda
	cd ~/przygoda

Instalujemy w nim virtualne środowisko i aktywujemy je

	virtualenv env
	source env/bin/activate

Instalujemy wszystko czego potrzebujemy

	pip3 install psycopg2
	pip3 install -r requirements.txt

Dezaktywujemy virtualne środowisko i przechodzimy do dalszej części

	deactivate

## Gunicorn

Tworzymy skrypt, który będzie ciągle próbował utrzymać stabliność

	sudo nano /etc/init/przygoda.conf

i umieszczamy w nim

```
description "Gunicorn application server running przygoda"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid virrages
setgid www-data

env PATH=/home/virrages/przygoda/env/bin
chdir /home/virrages/przygoda
exec gunicorn --workers 4 --bind unix:przygoda.sock -m 007 run:app
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

```
server {
    listen 80;
    server_name ;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/przygoda/przygoda.sock;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

Przenosimy konfigurację z dostępnych do aktywnych stron

	sudo ln -s /etc/nginx/sites-available/przygoda /etc/nginx/sites-enabled

Sprawdzamy czy nasza konfiguracja nginx'a jest poprawna

	sudo nginx -t

Teraz restartujemy nginx'a i powinno już wszystko działać

	sudo service nginx restart

# Server testing

## Stress tests

	ab -k -n 50000 -c 500 -e test.cvs http://..../
