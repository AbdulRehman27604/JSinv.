from flask import Flask, render_template, request, session, redirect


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == "a@m.com" and password == "1":
            return render_template('main.html')


    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
