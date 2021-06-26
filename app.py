from flask import Flask, render_template, jsonify, request, redirect, session
import json
import os
import requests
from flask_cors import CORS
import mwoauth
from requests_oauthlib import OAuth1

from utils import _str

app = Flask( __name__ )
cors = CORS(
    app,
    supports_credentials=True,
    origins=["https://bodh.toolforge.org", "http://127.0.0.1:3000", "http://127.0.0.1"],
    resources={
        r"/api/*": {
            "origins": [
                "https://bodh.toolforge.org",
                "http://127.0.0.1:3000"
            ]
        }
    }
)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config.from_object( os.environ['APP_SETTINGS'] )
app.secret_key = os.urandom(50)
consumer_token = mwoauth.ConsumerToken(
    app.config["CONSUMER_KEY"],
    app.config["CONSUMER_SECRET"]
)
handshaker = mwoauth.Handshaker(app.config["OAUTH_MWURI"], consumer_token)
API_URL = app.config["OAUTH_MWURI"] + "api.php"


@app.route('/')
def index():
    user = get_current_user()
    return render_template('index.html', user=user)

#############################
# ------ API Part -----------
#############################


@app.route('/api/createform', methods=['POST'])
def createform():
    lexemeId = request.get_json().get('lexemeId')
    lang = request.get_json().get('lang')
    value = request.get_json().get('value')
    if(request.method == "POST"):
        if None in (lexemeId, lang, value):
            return jsonify({
                "status": "error",
                "msg": "Can't find must value in request"
            })

        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            response = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = response.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]
            param = {
                "action": "wbladdform",
                "format": "json",
                "lexemeId": lexemeId,
                "data": json.dumps({
                    "representations": {
                        lang: {
                            "language": lang,
                            "value": value
                        }
                    },
                    "grammaticalFeatures": [],
                    "claims": []
                }),
                "token": csrf_token
            }
            r = requests.post(url=API_URL, data=param, auth=ses)
            return json.loads( r.text )
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            })


@app.route('/api/createsense', methods=['POST'])
def createsense():
    lexemeId = request.get_json().get('lexemeId')
    lang = request.get_json().get('lang')
    value = request.get_json().get('value')
    if(request.method == "POST"):
        if None in (lexemeId, lang, value):
            return jsonify({
                "status": "error",
                "msg": "Can't find must value in request"
            })

        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            response = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = response.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]
            param = {
                "action": "wbladdsense",
                "format": "json",
                "lexemeId": lexemeId,
                "data": json.dumps({
                    "glosses": {
                        lang: {
                            "language": lang,
                            "value": value
                        }
                    }
                }),
                "token": csrf_token
            }
            r = requests.post(url=API_URL, data=param, auth=ses)
            return json.loads( r.text )
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            })


@app.route('/api/createclaim', methods=['POST'])
def createclaim():
    if(request.method == "POST"):
        entity = request.get_json().get('entity')
        property = request.get_json().get('property')
        value = request.get_json().get('value')
        type = request.get_json().get('type')
        if None in ( entity, property, value, type ):
            return jsonify({
                "status": "error",
                "msg": "Can't find required data in request"
            }), 400

        if type == "string":
            newValue = f"\"{value}\""
        elif type == "wikibase-lexeme" or type == "wikibase-item":
            newValue = json.dumps({
                "entity-type": "item",
                "id": value
            })
        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            response = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = response.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]
            param = {
                "action": "wbcreateclaim",
                "format": "json",
                "entity": entity,
                "snaktype": "value",
                "property": property,
                "value": newValue,
                "token": csrf_token
            }
            r = requests.post(url=API_URL, data=param, auth=ses)
            return json.loads( r.text )
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            }), 400


@app.route('/api/editclaim', methods=['POST'])
def editclaim():
    if(request.method == "POST"):
        claimId = request.get_json().get('claimId')
        claimType = request.get_json().get('claimType')
        value = request.get_json().get('value')

        if None in (claimId, value, claimType):
            return jsonify({
                "status": "error",
                "msg": "Can't find required value in request"
            }), 400

        if claimType == "string":
            newValue = f"\"{value}\""
        elif claimType == "wikibase-lexeme" or claimType == "wikibase-item":
            newValue = json.dumps({
                "entity-type": "item",
                "id": value
            })
        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            response = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = response.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]
            param = {
                "action": "wbsetclaimvalue",
                "format": "json",
                "claim": claimId,
                "value": newValue,
                "snaktype": "value",
                "token": csrf_token
            }
            r = requests.post(url=API_URL, data=param, auth=ses)
            return json.loads( r.text )
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            }), 400


@app.route('/api/deleteitem', methods=['POST'])
def deleteitem():
    if(request.method == "POST"):
        itemId = request.get_json().get('itemId')
        if itemId == None:
            return jsonify({
                "status": "error",
                "msg": "Can't find itemId in request"
            })
        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            response = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = response.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]
            print( csrf_token )
            param = {
                "action": "wbremoveclaims",
                "format": "json",
                "claim": itemId,
                "token": csrf_token
            }
            r = requests.post(url=API_URL, data=param, auth=ses)
            return json.loads( r.text )
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            })


# Remove form
@app.route('/api/deleteform', methods=['POST'])
def deleteform():
    if(request.method == "POST"):
        itemId = request.get_json().get('itemId')
        if itemId == None:
            return jsonify({
                "status": "error",
                "msg": "Can't find itemId in request"
            })
        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            response = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = response.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]
            print( csrf_token )
            param = {
                "action": "wblremoveform",
                "format": "json",
                "id": itemId,
                "token": csrf_token
            }
            r = requests.post(url=API_URL, data=param, auth=ses)
            return json.loads( r.text )
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            })


# Remove sense
@app.route('/api/deletesense', methods=['POST'])
def deletesense():
    if(request.method == "POST"):
        itemId = request.get_json().get('itemId')
        if itemId == None:
            return jsonify({
                "status": "error",
                "msg": "Can't find itemId in request"
            })
        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            response = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = response.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]
            print( csrf_token )
            param = {
                "action": "wblremovesense",
                "format": "json",
                "id": itemId,
                "token": csrf_token
            }
            r = requests.post(url=API_URL, data=param, auth=ses)
            return json.loads( r.text )
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            })


@app.route('/api/editform', methods=['POST'])
def editform():
    if(request.method == "POST"):
        formId = request.get_json().get('formId')
        lang = request.get_json().get('lang')
        newValue = request.get_json().get('value')
        if None in ( formId, lang, newValue ):
            return jsonify({
                "status": "error",
                "msg": "Can't find must value in request"
            })

        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            # Getting all current data
            entity_param = {
                "action": "wbgetentities",
                "format": "json",
                "ids": formId
            }
            r1 = requests.get(url=API_URL, params=entity_param)
            try:
                representations = r1.json()["entities"][formId]["representations"]
                grammaticalFeatures = r1.json()["entities"][formId]["grammaticalFeatures"]
            except Exception:
                return jsonify({
                    "status": "error",
                    "msg": f"{formId} is not exist"
                }), 400
            try:
                representations[lang]["value"] = newValue
            except Exception:
                return jsonify({
                    "status": "error",
                    "msg": "Can't edit as language is not exist"
                }), 400
            # Getting CSRF token
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            r2 = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = r2.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]
            param = {
                "action": "wbleditformelements",
                "format": "json",
                "formId": formId,
                "data": json.dumps({
                    "representations": representations,
                    "grammaticalFeatures": grammaticalFeatures
                }),
                "token": csrf_token
            }
            r3 = requests.post(url=API_URL, data=param, auth=ses)
            return jsonify(r3.text)
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            })


@app.route('/api/editsense', methods=['POST'])
def editsense():
    if(request.method == "POST"):
        senseId = request.get_json().get('senseId')
        lang = request.get_json().get('lang')
        newValue = request.get_json().get('value')
        if None in (senseId, lang, newValue):
            return jsonify({
                "status": "error",
                "msg": "Can't find must value in request"
            }), 400

        # Creating auth session
        ses = authenticated_session()
        if ses != None:
            # Getting all current data
            entity_param = {
                "action": "wbgetentities",
                "format": "json",
                "ids": senseId
            }
            r1 = requests.get(url=API_URL, params=entity_param)
            try:
                glosses = r1.json()["entities"][senseId]["glosses"]
            except Exception:
                return jsonify({
                    "status": "error",
                    "msg": f"{senseId} is not exist"
                }), 400
            try:
                glosses[lang]["value"] = newValue
            except Exception:
                return jsonify({
                    "status": "error",
                    "msg": "Can't edit as language is not exist"
                }), 400
            # Getting CSRF token
            csrf_param = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }
            response = requests.get(url=API_URL, params=csrf_param, auth=ses)
            data = response.json()
            csrf_token = data["query"]["tokens"]["csrftoken"]

            # Making edit request to Wikidata
            param = {
                "action": "wbleditsenseelements",
                "format": "json",
                "senseId": senseId,
                "data": json.dumps({
                    "glosses": glosses
                }),
                "token": csrf_token
            }
            r = requests.post(url=API_URL, data=param, auth=ses)
            return jsonify(r.text)
        else:
            return jsonify({
                "status": "error",
                "msg": "Authentication error"
            })


@app.route('/api/profile')
def api_profile():
    return jsonify( {
        "logged": get_current_user() is not None,
        "username": get_current_user()
    })

#############################
# ------------ Login --------
#############################


@app.route('/login')
def login():
    redirect_to, request_token = handshaker.initiate()
    keyed_token_name = _str(request_token.key) + '_request_token'
    keyed_next_name = _str(request_token.key) + '_next'
    session[keyed_token_name] = \
        dict(zip(request_token._fields, request_token))
    if 'next' in request.args:
        session[keyed_next_name] = request.args.get('next')
    else:
        session[keyed_next_name] = 'index'
    return redirect(redirect_to)


@app.route('/logout')
def logout():
    session['mwoauth_access_token'] = None
    session['mwoauth_username'] = None
    if 'next' in request.args:
        return redirect(request.args['next'])
    return redirect( app.config["APP_REDIRECT_URI"] )


@app.route('/oauth-callback')
def oauth_callback():
    request_token_key = request.args.get('oauth_token', 'None')
    keyed_token_name = _str(request_token_key) + '_request_token'
    keyed_next_name = _str(request_token_key) + '_next'
    if keyed_token_name not in session:
        err_msg = "OAuth callback failed. Can't find keyed token. Are cookies disabled?"
        err_msg = err_msg + '\n Go <a href="https://bodh.toolforge.org">Bodh</a>'
        return err_msg
    access_token = handshaker.complete(
        mwoauth.RequestToken(**session[keyed_token_name]),
        request.query_string)
    session['mwoauth_access_token'] = \
        dict(zip(access_token._fields, access_token))
    del session[keyed_next_name]
    del session[keyed_token_name]
    get_current_user(False)
    return redirect( app.config["APP_REDIRECT_URI"] )


@app.before_request
def force_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        return redirect(
            'https://' + request.headers['Host'] + request.headers['X-Original-URI'],
            code=301
        )


def get_current_user(cached=True):
    if cached:
        return session.get('mwoauth_username')
    # Get user info
    identity = handshaker.identify(
        mwoauth.AccessToken(**session['mwoauth_access_token']))
    # Store user info in session
    session['mwoauth_username'] = identity['username']
    return session['mwoauth_username']


def authenticated_session():
    if 'mwoauth_access_token' in session:
        auth = OAuth1(
            client_key=app.config["CONSUMER_KEY"],
            client_secret=app.config["CONSUMER_SECRET"],
            resource_owner_key=session['mwoauth_access_token']['key'],
            resource_owner_secret=session['mwoauth_access_token']['secret']
        )
        return auth
    return None


if __name__ == "__main__":
    app.run()
