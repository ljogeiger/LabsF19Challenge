from flask import Flask, render_template, redirect, request, flash, url_for, session, jsonify
import json
import requests
import sys

"""
Basic outline:
I give the user two options. He/she can either follow the UI instructions or he/she can go to 'information/<building_name>'.
But he/she must get and insert the token before he/she can make an API call.
The workflow for following on screen instructions is as follows:
    1 - Go to index.html
    2 - Get Access Token (by redirecting user to ADI website)
    3 - Store and insert token
    4 - Have user select building
    5 - Make API call
    6 - Parse and dislpay API JSON file
"""

app = Flask(__name__)

app.secret_key = '772f2253fd3a4c2524a93c70aefeac2e'

base_url = "http://density.adicu.com/"
building_to_id = {"Avery": "124", "Butler": "115", "East Asian Library": "97", "John Jay": "153",
                  "Lehman Library": "109", "Lerner": "101", "Northwest Corner Building": "99", "Uris": "2",
                  "Lehman_Library": "109", "East_Asian_Library": "97", "John_Jay": "153", "Northwest_Corner_Building": "99"}

# Home


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')

# Redirects user to get Access Token which he/she then copies and pastes into the website


@app.route('/getAccessToken', methods=['GET'])
def getAccessToken():
    return redirect('https://density.adicu.com/auth')

# Allows the user to insert the token


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

# Makes the call to Density API


@app.route('/getData', methods=['GET', 'POST'])
def getData():
    token = session.get('token', 'not set')
    if request.method == 'POST':
        building = request.form['text'].strip().title()  # Error prevention
        number = request.form['number'].strip()
        if number is "":
            response_list = getBuildingsFromName(building, token)
        else:
            response_list = getLeastFullBuildings(number, token)
        return render_template('response.html', response=response_list)
    elif request.method == 'GET':
        return render_template('data.html')

# If user enters a building name return a list of the buildings within that building's parent id


def getBuildingsFromName(building, token):
    try:
        data = requests.get(base_url + "latest/building/" +
                            building_to_id[building] + "?auth_token=" + token)
        data_json = data.json()
        end_list = []
        for item in data_json["data"]:
            building = "{} is {}% full".format(
                item["group_name"], item["percent_full"])
            end_list.append(building)
    except KeyError:
        end_list = ["No buildings found"]
    if not end_list:
        end_list = ["No buildings found"]
    return end_list

# If user enters a number then make api call to get all buildings, then sort in ascending order, and get the first <number> buildings


def getLeastFullBuildings(number, token):
    try:
        data = requests.get(base_url + "latest?auth_token=" + token)
        data_json = data.json()
        presorted_end_list = []
        end_list = []
        for item in data_json["data"]:
            presorted_end_list.append(
                [item["group_name"], int(item["percent_full"])])
        presorted_end_list.sort(key=lambda x: x[1])
        for i in range(0, int(number)):
            building = "{} is {}% full".format(
                presorted_end_list[i][0], presorted_end_list[i][1])
            end_list.append(building)
    except KeyError:
        end_list = ["No buildings found"]
    if not end_list:
        end_list = ["No buildings found"]
    return end_list

# Facilitates specified url path of README if user does not want to go through UI workflow


@app.route('/information/<item>', methods=['GET', 'POST'])
def information(item):
    token = session.get('token', 'not set')
    if token is "not set":
        flash("You must enter a token", 'danger')
        return redirect(url_for('enterToken'))
    if item in building_to_id:
        response_list = getBuildingsFromName(item, token)
    else:
        response_list = getLeastFullBuildings(item, token)
    return render_template('response.html', response=response_list)


if __name__ == '__main__':
    app.run(host='localhost', debug="true")
