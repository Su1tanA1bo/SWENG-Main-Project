from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY']='thecodex'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user1')
def user1():
    return render_template('user1.html')

@app.route('/user2')
def user2():
    return render_template('user2.html')

if __name__ == '__main__':
    app.run(debug=True)