from flask import Flask, render_template, redirect, request, flash, url_for, session, jsonify
import json
import requests
import sys

app = Flask(__name__)

app.secret_key = '772f2253fd3a4c2524a93c70aefeac2e'

base_url = "http://density.adicu.com/"
building_to_id = {"Avery": "124", "Butler": "115", "East Asian Library": "97", "John Jay": "153",
                  "Lehman Library": "109", "Lerner": "101", "Northwest Corner Building": "99", "Uris": "2"}


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')


@app.route('/getAccessToken', methods=['GET'])
def getAccessToken():
    return redirect('https://density.adicu.com/auth')


@app.route('/enterToken', methods=['GET', 'POST'])
def enterToken():
    if request.method == 'POST':
        token = request.form['text']
        if token == "":
            flash("You must enter a token.", 'danger')
            return render_template('token.html')
        else:
            session['token'] = token
            flash('Entered access token: ' +
                  str(session.get('token', 'not set')), 'success')
            return redirect(url_for('getData'))
    elif request.method == 'GET':
        return render_template('token.html')


@app.route('/getData', methods=['GET', 'POST'])
def getData():
    token = session.get('token', 'not set')
    if request.method == 'POST':
        building = request.form['text'].strip().title()
        number = request.form['number'].strip()
        # flash("" + building + str(type(number)), 'success')
        if number is "":
            try:
                data = requests.get(base_url + "latest/building/" +
                                    building_to_id[building] + "?auth_token=" + token)
                # flash(base_url + "latest/building/" +
                #       building_to_id[building] + "?auth_token=" + token, 'success')
                data_json = data.json()
                end_list = []
                for item in data_json["data"]:
                    building = "{} is {}% full".format(
                        item["building_name"], item["percent_full"])
                    end_list.append(building)
            except KeyError:
                end_list = ["No buildings found"]
        else:
            data = requests.get(base_url + "latest/building/" +
                                number + "?auth_token=" + token)
        return render_template('response.html', response=end_list)
    elif request.method == 'GET':
        return render_template('data.html')


if __name__ == '__main__':
    app.run(host='localhost', debug="true")


"""
Basic outline:
    1 - Go to index.html
    2 - Get Access Token (by redirecting user to ADI website)
    3 - Get access token from user?
    4 - Store and insert token
    5 - Have user select building
    6 - Make API call
    7 - Parse and dislpay API JSON file
"""
