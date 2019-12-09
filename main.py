from app import app, db
from app.models import User, Gym, Climb
import os

@app.shell_context_processor
def make_shell_context():
	return { 'db': db, 'User': User, 'Gym': Gym, 'Climb': Climb }

if __name__ == '__main__':
	app.debug = True
	port = int(os.environ.get('PORT', 3001))
	app.run(host='localhost', port=port)

    