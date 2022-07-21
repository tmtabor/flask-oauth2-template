from authlib.integrations.base_client import OAuthError
from flask import Flask, url_for, session, render_template, redirect, abort, request
from authlib.integrations.flask_client import OAuth
from requests import PreparedRequest

app = Flask(__name__)
app.secret_key = '!secret'
app.config.from_object('config')

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

oauth.register(
    name='globus',
    api_base_url='https://auth.globus.org/v2/oauth2/',
    access_token_url='https://auth.globus.org/v2/oauth2/token',
    authorize_url='https://auth.globus.org/v2/oauth2/authorize',
    userinfo_endpoint='userinfo',
    jwks_uri='https://auth.globus.org/jwk.json',
    client_kwargs={
        'scope': 'openid email profile urn:globus:auth:scope:transfer.api.globus.org:all'
    }
)

oauth.register(
    name='genepattern',
    authorize_url='https://cloud.genepattern.org/gp/rest/v1/oauth2/authorize',
    access_token_url='https://cloud.genepattern.org/gp/rest/v1/oauth2/token',
)


@app.route('/')
def homepage():
    user = session.get('user')
    return render_template('home.html', user=user)


@app.route('/login/<name>', methods=('GET', 'POST'))
def login(name):
    client = oauth.create_client(name)
    if not client: abort(404)

    if request.method == 'GET':
        if name == 'genepattern': return render_template('login.html')

        redirect_uri = url_for('auth', name=name, _external=True)
        if '127.0.0.1' in redirect_uri: redirect_uri.replace('127.0.0.1', 'localhost')  # Fix for Globus dev servers
        return client.authorize_redirect(redirect_uri)
    else:
        try: return handle_genepattern_auth()
        except OAuthError as e:
            if e.description: return render_template('login.html')
            raise

def handle_genepattern_auth():
    params = dict(
        grant_type="password",
        username=request.form.get('username'),
        password=request.form.get('password'),
        client_id="Flask")
    req = PreparedRequest()
    req.prepare_url(oauth.genepattern.access_token_url, params)
    oauth.genepattern.access_token_url = req.url
    token = oauth.genepattern.fetch_access_token()
    return render_template('home.html')


@app.route('/auth/<name>')
def auth(name):
    client = oauth.create_client(name)
    if not client:
        abort(404)

    token = client.authorize_access_token()
    user = token.get('userinfo')
    if not user:
        user = client.userinfo()

    session['user'] = user
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
