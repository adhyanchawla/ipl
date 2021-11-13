from flask import Flask, request, jsonify
from flask import send_from_directory
import json
import uuid
import pandas as pd
data = pd.read_csv('IPL Ball-by-Ball 2008-2020.csv')

def topBatters(team1,team2):
    batrat1=dict()
    for player1 in team1:
        if(('atter' in player1['role'] or 'rounder' in player1['role'])):  
            truns=0
            tdismisals=0
            ttotalBalls=0
            for opp in team2:
                if('owler' in opp['role'] or 'rounder' in opp['role']):
                    player1data=data[(data['batsman']==player1['fullName'])]
                    oppplay=player1data[(player1data['bowler']==opp['fullName'])]

                    runs=sum(oppplay['batsman_runs'])
                    
                    dismisals=sum(oppplay['is_wicket'])
                    runouts=len(oppplay[(oppplay['is_wicket']) & (oppplay['dismissal_kind']=="run out")])
                    dismisals-=runouts
                    
                    balls=len(oppplay)
                    extraBalls=len(oppplay[(oppplay['extras_type']=="wides") | (oppplay['extras_type']=="noballs")])
                    totalBalls=balls-extraBalls
                    
                    truns+=runs
                    tdismisals+=dismisals
                    ttotalBalls+=totalBalls

            if(tdismisals==0):
                avg=None
            else:
                avg=truns/tdismisals     
            if(ttotalBalls==0):
                strike_rate=None
            else:
                strike_rate=(truns/ttotalBalls)*100

            if(avg):
                rating=(truns)**(1/2) * avg * strike_rate
                batrat1[player1["fullName"]]=rating
            elif(strike_rate):
                rating=7*truns*strike_rate
                batrat1[player1["fullName"]]=rating

    sort_batrat1 = sorted(batrat1.items(), key=lambda x: x[1],reverse=True)
    bat1top=list(sort_batrat1)[:3]
    return bat1top

def topBowlers(team1,team2):
    bowlrat1=dict()
    for player1 in team1:
        if(('owler' in player1['role'] or 'rounder' in player1['role'])):  
            truns=0
            tdismisals=0
            ttotalBalls=0
            for opp in team2:
                if('atter' in opp['role'] or 'rounder' in opp['role']):
                    player1data=data[(data['bowler']==player1['fullName'])]
                    oppplay=player1data[(player1data['batsman']==opp['fullName'])]
                    extras=oppplay[(oppplay['extras_type']=="wides") | (oppplay['extras_type']=="noballs")]
                    extra_runs=sum(extras['extra_runs'])
                    runs=sum(oppplay['batsman_runs'])
                    runs+=extra_runs
                    
                    dismisals=sum(oppplay['is_wicket'])
                    runouts=len(oppplay[(oppplay['is_wicket']) & (oppplay['dismissal_kind']=="run out")])
                    dismisals-=runouts
                    
                    balls=len(oppplay)
                    extraBalls=len(extras)
                    totalBalls=balls-extraBalls
                    
                    truns+=runs
                    tdismisals+=dismisals
                    ttotalBalls+=totalBalls

            if (ttotalBalls>0):
                economy=(truns/ttotalBalls)*6
                rating=48*(tdismisals/ttotalBalls) - economy +(ttotalBalls)**(1/3)+ 1000
                bowlrat1[player1["fullName"]]=rating

    sort_bowlrat1 = sorted(bowlrat1.items(), key=lambda x: x[1],reverse=True)
    bowl1top=list(sort_bowlrat1)[:3]
    return bowl1top

app = Flask(__name__)

@app.route('/', methods=['GET'])
def send_index():
    return send_from_directory('./www', "index.html")

@app.route('/<path:path>', methods=['GET'])
def send_root(path):
    return send_from_directory('./www', path)

@app.route('/api/mpg', methods=['POST'])
def calc_mpg():
    content = request.get_json(force=True)
    errors = []

    f=open('teams/'+ content['team1']+'.json','r')
    team1=json.load(f)
    f.close()
    f=open('teams/'+ content['team2']+'.json','r')
    team2=json.load(f)
    f.close()
    
    bat1top=topBatters(team1,team2)
    bat2top=topBatters(team2,team1)
    bowl1top=topBowlers(team1,team2)
    bowl2top=topBowlers(team2,team1)

    response = {"id":str(uuid.uuid4()),"bat1top":bat1top,"bat2top":bat2top,'bowl1top':bowl1top,'bowl2top':bowl2top}
    return jsonify(response)


if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
    
