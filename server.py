"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, jsonify, url_for
from datetime import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#
# The following is a dummy URI that does not connect to a valid database.
# You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "yz4429"
DATABASE_PASSWRD = "3372"
DATABASE_HOST = "34.148.107.47"  # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI, future=True)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
    create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	"""
    res = conn.execute(text(create_table_command))
    insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
    res = conn.execute(text(insert_table_command))
    # you need to commit for create, insert, update queries to reflect
    conn.commit()


@app.before_request
def before_request():
    """
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback;
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)

    #
    # example of a database query
    #
    select_query = "SELECT name from test"
    cursor = g.conn.execute(text(select_query))
    names = []
    for result in cursor:
        names.append(result[0])
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)


# Example of adding new data to the database
@app.route('/add_artwork', methods=['POST'])
def add_Artwork():
    select_query = "SELECT artist_id, name FROM artist"
    cursor = g.conn.execute(text(select_query))
    results = []
    for result in cursor:
        results.append(result)
    return render_template('add_artwork.html', artists=results)


@app.route('/add_artist', methods=['POST'])
def add_Artist():
    return render_template('add_artist.html')


@app.route('/login')
def login():
    abort(401)


# this_is_never_executed()


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    select_query = "SELECT title, year, name " \
                   "FROM artwork " \
                   "LEFT OUTER JOIN artist a ON artwork.artist_id = a.artist_id"

    dictionary = {'title': 'title', 'artist': 'name'}
    filters = list(filter(lambda x: request.form.get(x) is not None, ['title', 'artist']))

    for i in range(len(filters)):
        current_filter = filters[i]
        if i == 0:
            select_query += ' WHERE '
        select_query += dictionary[current_filter] + ' LIKE \'%' + query.replace('\'', '\'\'') + '%\''
        if i < len(filters) - 1:
            select_query += ' OR '

    cursor = g.conn.execute(text(select_query))
    results = []
    for result in cursor:
        temp = []
        for data in result:
            temp.append(data)
        results.append(temp)
    cursor.close()
    # return jsonify({'result': titles})
    return render_template('results.html', results=results, heads=['Title', 'Year', 'Artist'], query=query)


@app.route('/artwork', methods=['GET'])
def getArtwork():
    title = request.args.get('title')
    select_query = "SELECT title, a.name, m.name, m.location, year, medium, description FROM artwork LEFT OUTER JOIN " \
                   "artist a on artwork.artist_id = a.artist_id LEFT OUTER JOIN museum m on " \
                   "artwork.on_loan_to_museum_id = m.museum_id or artwork.on_loan_from_museum_id = m.museum_id WHERE " \
                   "artwork.title = "

    select_query += "'" + title.replace('\'', '\'\'') + "'"
    cursor = g.conn.execute(text(select_query))
    results = []
    for result in cursor:
        results.append(result)
    return render_template('artwork.html', result=results[0])


@app.route('/artist', methods=['GET'])
def getArtist():
    name = request.args.get('name')
    select_query = "SELECT name, birthplace, date_of_birth, date_of_death FROM artist WHERE name = "
    select_query += "'" + name.replace('\'', '\'\'') + "'"
    cursor = g.conn.execute(text(select_query))
    results = []
    for result in cursor:
        results.append(result)
    select_query = "SELECT title, year, medium FROM artwork JOIN artist a on a.artist_id = artwork.artist_id WHERE " \
                   "name ="
    select_query += "'" + name.replace('\'', '\'\'') + "'"
    cursor = g.conn.execute(text(select_query))
    artworks = []
    for result in cursor:
        artworks.append(result)
    return render_template('artist.html', result=results[0], artworks=artworks)


@app.route('/museum', methods=["GET"])
def getMuseum():
    name = request.args.get('name')
    select_query = "SELECT * FROM museum WHERE name = "
    select_query += "'" + name.replace('\'', '\'\'') + "'"
    cursor = g.conn.execute(text(select_query))
    museums = []
    for result in cursor:
        museums.append(result)
    museum = museums[0]
    select_query = "SELECT title, year, a.name FROM artwork JOIN artist a on a.artist_id = artwork.artist_id " \
                   "WHERE on_loan_from_museum_id = '%s' OR on_loan_to_museum_id = '%s'" % (
                       museum[0].replace('\'', '\'\''), museum[0].replace('\'', '\'\''))
    cursor = g.conn.execute(text(select_query))
    artworks = []
    for result in cursor:
        artworks.append(result)
    return render_template('museum.html', museum=museum, artworks=artworks)

@app.route('/submit_artwork', methods=["POST"])
def addArtwork():
    title = request.form.get('title')
    artist_id = int(request.form.get('artist'))
    year = int(request.form.get('year'))
    description = request.form.get('description')
    medium = request.form.get('medium')

    query = "INSERT INTO artwork (title, year, description, medium, artist_id) VALUES ('%s', '%d', '%s', '%s', '%d');" % (
        title.replace('\'', '\'\''), year, description.replace('\'', '\'\''), medium.replace('\'', '\'\''), artist_id)

    g.conn.execute(text(query))
    g.conn.commit()
    return redirect(url_for('index'))


@app.route('/submit_artist', methods=["POST"])
def addArtist():
    print(request.form)
    name = request.form.get('name')
    birthplace = request.form.get('birth_place')
    dob = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()

    query = "INSERT INTO artist (name, birthplace, date_of_birth) VALUES ('%s', '%s', '%s');" % (
        name.replace('\'', '\'\''), birthplace.replace('\'', '\'\''), dob)

    if request.form.get('date_of_death') != '':
        dod = datetime.strptime(request.form.get('date_of_death'), '%Y-%m-%d').date()
        query = "INSERT INTO artist (name, birthplace, date_of_birth, date_of_death) VALUES ('%s', '%s', '%s', '%s');" % (
            name.replace('\'', '\'\''), birthplace.replace('\'', '\'\''), dob, dod)
    g.conn.execute(text(query))
    g.conn.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
		This function handles command line parameters.
		Run the server using:
			python server.py
		Show the help text using:
			python server.py --help
		"""

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
