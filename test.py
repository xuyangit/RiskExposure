from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import Response
from flask import json
from flask import redirect, url_for
from flask import make_response
from datetime import date, datetime
import jwt
import pymysql.cursors

app = Flask(__name__)
sqlCli = pymysql.connect(host='localhost',
                         user='root',
                         password='xuyang2008',
                         db='commodity',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)

@app.route("/")
@app.route("/home")
def home():
    return render_template("Home.html")

@app.route("/swapTran", methods = ["POST"])
def swapTran():
    userid = request.cookies.get('userid')
    if(userid != None and userid != ''):
        buyOrSell = request.form['buyOrSell']
        quantity = request.form['lotOfSwap']
        price = request.form['priceOfSwap']
        startDate = request.form['startDate']
        endDate = request.form['endDate']
        if(quantity == None or quantity == ""):
            return jsonify(err = "Please enter the lots", risk = "")
        elif(price == None or price == ""):
            return jsonify(err = "Please enter the price", risk = "")
        price = float(price)
        quantity = int(quantity)
        if(price <= 0):
            return jsonify(err = "The price should be a positive number", risk = "")
        tradeId = jwt.encode({'userid' : userid, 'time' : str(datetime.now())}, 'secret', algorithm = 'HS256')
        try:
            with sqlCli.cursor() as cursor:
                sql = "select settleDate, productCode from `futureInfo`";
            with sqlCli.cursor() as cursor:
                sql = "insert into `future` values ({}, {}, '{}', '{}', '{}', '{}')".format(
                    quantity, price, futureCode, userid,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tradeId)
                cursor.execute(sql)
            sqlCli.commit()
        except:
            return jsonify(err = "Trade fails because of database error, please retry", risk = "")
        finally:
            return jsonify(err = "", risk = "{}".format(quantity))
        
@app.route("/futureTran", methods = ["POST"])
def futureTran():
    userid = request.cookies.get('userid')
    if(userid != None and userid != ''):
        quantity = request.form['lotOfFuture']
        price = request.form['priceOfFuture']
        futureCode = request.form['futureCode']
        if(quantity == None or quantity == ""):
            return jsonify(err = "Please enter the lots", risk = "")
        elif(price == None or price == ""):
            return jsonify(err = "Please enter the price", risk = "")
        price = float(price)
        quantity = int(quantity)
        if(price <= 0):
            return jsonify(err = "The price should be a positive number", risk = "")
        tradeId = jwt.encode({'userid' : userid, 'time' : str(datetime.now())}, 'secret', algorithm = 'HS256')
        try:
            with sqlCli.cursor() as cursor:
                sql = "insert into `future` values ({}, {}, '{}', '{}', '{}', '{}')".format(
                    quantity, price, futureCode, userid,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tradeId)
                cursor.execute(sql)
            sqlCli.commit()
        except:
            return jsonify(err = "Trade fails because of database error, please retry", risk = "")
        finally:
            return jsonify(err = "", risk = "{}".format(quantity))
        
@app.route("/getUserInfo")
def getUserInfo():
    userid = request.cookies.get('userid')
    result = None
    if(userid != None and userid != ''):
        try:
            with sqlCli.cursor() as cursor:
                sql = "select * from `user` where id = '{}'".format(userid)
                cursor.execute(sql)
                result = cursor.fetchone()
        finally:
            if(result != None):
                return jsonify(name = result['firstname'] + ' ' + result['lastname'],
                               email = result['eaddress'],
                               userName = result['id'])
    else:
        return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("Login.html")

@app.route("/tradehistory")
def tradeHistory():
    userid = request.cookies.get('userid')
    futureResult = []
    swapResult = []
    res = {"future" : futureResult, "swap" : swapResult}
    if(userid != None and userid != ''):
        try:
            with sqlCli.cursor() as cursor:
                sql = "select * from `future` where userId = '{}'".format(userid)
                rows = cursor.execute(sql)
                for i in range(rows):
                    futureResult.append(cursor.fetchone())
                sql = "select * from `swap` where userId = '{}'".format(userid)
                rows = cursor.execute(sql)
                for i in range(rows):
                    swapResult.append(cursor.fetchone())
        finally:
            jsonRes = json.dumps(res)
            return Response(jsonRes, mimetype='application/json')
        
@app.route("/getfutureinfo")
def getFutureInfo():
    currentTime = datetime.now()
    result = []
    try:
        with sqlCli.cursor() as cursor:
            sql = "select settleDate, productCode from `futureInfo`"
            rows = cursor.execute(sql)
            for i in range(rows):
                record = cursor.fetchone()
                settleDate = record['settleDate']
                delta = settleDate - currentTime
                if(delta.days > 0):
                    result.append(record['productCode'])
    finally:
        return jsonify(info = result)
                    
@app.route("/userpage")
def userPage():
    userid = request.cookies.get('userid')
    if(userid != None and userid != ''):
        return render_template("UserPage.html")
    else:
        return redirect(url_for('login'))
    
@app.route("/loginO", methods=["POST"])
def userLogin():
    userid = request.form['userid']
    password = request.form['password']
    result = None
    try:
        with sqlCli.cursor() as cursor: 
            sql = "select * from `user` where id = '{}' and password = '{}' and type = 0".format(userid, password)
            cursor.execute(sql)
            result = cursor.fetchone()
    finally:
        if(result == None):
            return jsonify(err = 'invalid', redirect = '')
        else:
            response = make_response(jsonify(err = '', redirect = 'userpage'))
            response.set_cookie('userid', userid)
            return response
    return jsonify(err = 'invalid', redirect = '')
@app.route("/loginA", methods=["POST"])
def adminLogin():
    userid = request.form['userid']
    password = request.form['password']
    result = None
    try:
        with sqlCli.cursor() as cursor:
            sql = "select * from `user` where id = '{}' and password = '{}' and type = 1".format(userid, password)
            cursor.execute(sql)
            result = cursor.fetchone()
    finally:
        if(result == None):
            return jsonify(err = 'invalid', redirect = '')
        else:
            return jsonify(err = '', redirect = 'userpage')
    return jsonify(err = 'invalid', redirect = '')
            
@app.route("/register/validation", methods=["POST"])
def registerValid():
    data = request.get_json()
    result = None
    field = data['field']
    if(field == "email"):
        try:
            with sqlCli.cursor() as cursor:
                sql = "select * from `user` where eaddress = '{}'".format(data['data'])
                cursor.execute(sql)
                result = cursor.fetchone()
        finally:
            if(result != None):
                 return 'EMAIL_ALREADY_EXIST'
            else:
                return ''
    elif(field == "userid"):
        try:
            with sqlCli.cursor() as cursor:
                sql = "select * from `user` where id = '{}'".format(data['data'])
                cursor.execute(sql)
                result = cursor.fetchone()
        finally:
            if(result != None):
                return "USERNAME_ALREADY_EXIST"
            else:
                return ''
    else:
        return ''
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        userid = request.form['userid']
        eaddress = request.form['eaddress']
        password = request.form['password']
        try:
            with sqlCli.cursor() as cursor:
                sql = "insert into `user` (`id`, `firstname`, `lastname`, `eaddress`, `type`, `password`)\
                       values ('{}', '{}', '{}', '{}', {}, '{}')".format(userid, firstname, lastname, eaddress, 0, password)
                cursor.execute(sql)
            sqlCli.commit()
        finally:
            return jsonify(err = '', redirect = 'login')
    else:
        return render_template("Register.html")

@app.route("/riskEvaluation")
def riskEvaluation():
    return render_template("RiskEvaluation.html")



if __name__ == "__main__":
    app.run(debug=True)
