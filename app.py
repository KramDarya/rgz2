from flask import Flask, redirect, session, url_for, render_template
from rgz import rgz

app = Flask(__name__)
app.secret_key = "123"
app.register_blueprint(rgz)
