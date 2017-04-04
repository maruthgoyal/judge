from flask import Flask, url_for, redirect, render_template, request, make_response, flash
from engine import Engine
import time

app = Flask(__name__)
eng= Engine()
app.secret_key = "eeeriudjvb2e0r24r9"

PROG_URL = "/prog"

@app.errorhandler(401)  # A robot is being used
def fourzeroone(e):

    return render_template("robot.html"), 401

@app.errorhandler(404) # Page not found
def fourzerofour(e):

    return render_template("notFound.html"), 404

@app.errorhandler(403) # If user trying to access restricted resource.
def fourzerothree(e):

    ''' Access Denied '''

    return render_template("backoff.html"), 403

@app.errorhandler(429) # Rate limited
def fourtwonine(e):

    ''' Too many requests to the site '''

    return render_template("rate_limited.html"), 429

# @app.before_request  # Check if user is not a robot or blacklisted before every request
# def before_request():
#
#     ''' Checking is a robot '''
#
#     if request.method != "PUT":
#
#         user_agent = request.user_agent
#
#         if any(x==None for x in (user_agent.platform, user_agent.browser, user_agent.version)):
#
#             abort(401)
#
#         if eng.isBlacklisted(request.headers['X-Forwarded-For']):
#
#             abort(403)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/results')
def results():
    return render_template("results.html")


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('user', '', expires=0)
    return resp

@app.route(PROG_URL + '/', methods=["GET", "POST"])
def login():

    startTime, endTime = eng.getTimes()
    t = time.time()

    if t >= startTime and t < endTime:

        if request.method == 'GET':

            if 'user' in request.cookies:
                return redirect(url_for('play'))

            return render_template("login.html")

        else:

            uname = request.form['username']
            password = request.form['password']

            id_of_user = eng.authenticate(uname, password)

            if id_of_user:

                resp = make_response(redirect(url_for('play')))
                resp.set_cookie("user", id_of_user)

                return resp

            return render_template('login.html', error=True)

    elif t < startTime:
        return render_template("notStarted.html")

    else:
        return render_template("ended.html")

@app.route(PROG_URL + '/play/<int:num>', methods=["GET", "POST"])
@app.route(PROG_URL + '/play', methods=["GET", "POST"])
def play(num=None):

    startTime, endTime = eng.getTimes()
    t = time.time()

    if t >= startTime and t < endTime:

        if request.method == 'GET':

            if not num:
                return render_template("problems.html")
            else:
                return render_template("problem%d.html" % num, message=None)

        elif request.method == 'POST':

            print request.files

            if not num:
                return redirect(url_for('play'))

            if 'program' in request.files:

                eng.savefile(request.files['program'].read(), request.cookies['user'], num)
                return render_template("problem%d.html" % num, message="Submitted.")

            if 'small' in request.files:

                f = request.files['small']

                correct = eng.eval(request.cookies['user'], f, num)

                if correct:

                    return render_template("problem%d.html" % num, message="Correct small answer!")

                else:

                    return render_template("problem%d.html" % num, message="INCORRECT small ANSWER")

            if 'large' in request.files:

                f = request.files['large']

                correct = eng.eval(request.cookies['user'], f, num, large=True)

                if correct:

                    return render_template("problem%d.html" % num, message="Correct large answer!")

                else:

                    return render_template("problem%d.html" % num, message="INCORRECT large ANSWER")


            return render_template("problems.html")

    elif t < startTime:
        return render_template("notStarted.html")

    else:
        return render_template("ended.html")

@app.route('/rules')
def rules():
    return render_template("rules.html")

@app.route('/leaderboard')
def leaderboard():

    board = eng.getleaderboard()
    return render_template("leaderboard.html", lb=board)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
