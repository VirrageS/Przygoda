# Przygoda
Aplikacja Przygoda jest najlepszym sposobem na znajdowanie miłośników rowerów

# Clone the project
git clone git@github.com:USERNAME/helloflask.git

# Initialize virtualenv and install dependencies
sudo pip install virtualenv
cd PATH_TO_FOLDER
virtualenv flaskenv
cd flaskenv
pip install -r requirements.txt
cd ..

# Start env
source flaskenv/bin/activate

# Create database
	user@Machine:~/Projects/dev$ . env/bin/activate
	(env)user@Machine:~/Projects/dev$ python shell.py
	>>> from app import db
	>>> db.create_all()
	>>> exit()

# Run
python run.py
