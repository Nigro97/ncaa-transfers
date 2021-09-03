import traceback
import logging.config

from flask import Flask
from flask import render_template, request, redirect, url_for
from sqlalchemy import desc

# Initialize the Flask application
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Set logging configuration
logging.config.fileConfig(app.config['LOGGING_CONFIG'])
logger = logging.getLogger(app.config['APP_NAME'])
logger.debug('Web app log')

from src.results_db import Results, ResultsManager

# Initialize the database session
results_manager = ResultsManager(app)


# Create first view of app
@app.route('/', methods=['GET','POST'])
def get_input():
    """View that processes a POST with user input to select a player type and sort column from displayed dropdown menus
    Args:
        None
    Returns:
        Redirect to index page (or error view if error occurs)
    """
    # If the request method is GET then show the homepage
    if request.method == 'GET':
        try:
            logger.info('Home selection page displayed.')
            return render_template('get_input.html')
        except:
            # If an error occurs, show the error page instead
            logger.warning('Not able to display selection page, error page returned')
            return render_template('error.html')

    # If the request method is POST then get the user inputs and redirect to the index page
    if request.method == 'POST':
        player_filter = request.form['player_type']
        sort_col = request.form['sort_col']
        url_for_post = url_for('index', player_filter=player_filter, sort_col=sort_col)
        logger.info('User inputs received and submit button pushed. Redirecting to display page.')
        return redirect(url_for_post)


# Create second view (index) of app
@app.route('/index/<player_filter>/<sort_col>', methods=['GET','POST'])
def index(player_filter, sort_col):
    """Main view that displays players filtered by player type and sorted by a statistics column.
    Create view into index page that uses data queried from Results database and
    inserts it into the app/templates/index.html template.
    Args:
        player_filter: (string), Required: The player type chosen by the user
        sort_col: (String), Required: The column to sort by as chosen by the user
    Returns:
        Rendered index html template (or error view if error occurs)
    """

    try:
        if player_filter == 'player_type':
            # Redirect to the first page if the URL at the top of the page is clicked
            logger.info('Button pressed to return to selection page.')
            return redirect(url_for('get_input'))
        else:
            # Query the database using the player type input as a filter, ordering by the sort column input, and limiting to 100 records
            stats = results_manager.session.query(Results).filter(Results.player_type == player_filter).order_by(desc(sort_col)).limit(app.config["MAX_ROWS_SHOW"]).all()
            logger.info('Players statistics display filtered by %s and sorted by %s', player_filter, sort_col)
            return render_template('index.html', stats=stats, player_filter=player_filter, sort_col=sort_col)
    except:
        # If an error occurs, display the traceback of the error and the error view
        traceback.print_exc()
        logger.warning('Not able to display players, error page returned')
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host=app.config['HOST'])
