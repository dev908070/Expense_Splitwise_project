from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from datetime import timedelta,datetime
import json
from flask_apscheduler import APScheduler

import user
import expense as exp



app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'hagnosofttesting@gmail.com'
app.config['MAIL_PASSWORD'] = "mapqszvafxvvbahw"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
reciver='hagnosofttesting@gmail.com'
mail = Mail(app)


app.config["JWT_SECRET_KEY"] = "z7mv6ps81hjdyw8jfv8f2m0h14w679he14345"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=7)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=8)
jwt = JWTManager(app)

apikey_global="global_api_key"

sched = BackgroundScheduler()



#################################################API's####################################################
def send_mail(sender,reciver_list,data):
    with app.app_context():
        recipients = reciver_list
        msg = Message('Hello',sender=sender,recipients=recipients)
        table_html = '<table border="1">'
        table_html += '<tr><th>' + '</th><th>'.join(data[0].keys()) + '</th></tr>'
        for row in data:
            table_html += '<tr><td>' + '</td><td>'.join(map(str, row.values())) + '</td></tr>'
        table_html += '</table>'
        html_body = f'<p>You are added in a splitexpense and your expense table is as follows:</p>{table_html}'
        msg.html = html_body
        mail.send(msg)
    return 'Sent'

def sendemailweekly():
    for i in exp.get_distinct_expGroupIds():
        gamil_list=exp.getusersmail(i)
        data = exp.getExpenseListbyexpGroupId(i)
        result = send_mail(reciver,gamil_list,data)
    return ""
# sched.add_job(sendemailweekly,'interval',minutes=1)
sched.add_job(sendemailweekly,'interval',weeks=1)
sched.start()

@app.route("/")
def index():
    return "Splitwise project is running succesfully"

@app.route("/jwtrefresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    api_key = request.headers["api-key"]
    content_type = request.headers["Content-Type"]
    if api_key!=apikey_global:
        return  jsonify({"message": "Unauthorized Access" }),401
    else:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return jsonify(access_token=access_token,refresh_token=refresh_token),200


@app.route('/registeruser',methods=["POST"])
def registerUser():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            param_json= request.get_json()
            name = param_json['name']
            email = param_json['email']
            mobileNumber = param_json['mobileNumber']
            password=param_json['password']
            registerUser=user.registerUser(name,email,mobileNumber,password)
            if registerUser!="User registered successfully":
                return jsonify({"message": registerUser }),452
            else:
                return jsonify({"message": registerUser }),200
    except Exception as ex:
        return jsonify({"error":str(ex)}),500      

@app.route("/login", methods=["POST"])
def login():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            param_json= request.get_json()
            email = str(param_json['email'])
            password =  str(param_json['password'])
            check_login=user.loginUser(email,password)
            if check_login=="Wrong password entered" or check_login=="email is not exists please register first" :
                return jsonify({"message": check_login }),452
            access_token = create_access_token(identity=email)
            refresh_token=create_refresh_token(identity=email)
            check_login= json.loads(check_login)
            return jsonify(access_token=access_token, refresh_token=refresh_token,data=check_login,message="Logged in successfully"),200
    except Exception as ex:
        return jsonify({"error":str(ex)}),500
    
@app.route("/createExpenseGroup", methods=["POST"])
# @jwt_required()
def createExpenseGroup():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            param_json= request.get_json()
            userId=param_json['userId']
            expenseGroupName = param_json["expenseGroupName"]
            result = exp.createExpenseGroup(expenseGroupName,userId)
            if result =="Success":
                return  jsonify({"message": "Expense Group created successfully" }),200
            else:
                return  jsonify({"message":result}),452
    except Exception as ex:
        return jsonify({"error":str(ex)}),500
    

@app.route("/createExpenseUserMapping", methods=["POST"])
# @jwt_required()
def createExpenseUserMapping():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            param_json= request.get_json()
            expGroupId=param_json['expGroupId']
            userId=param_json['userId']
            json_data = param_json["json_data"]
            result = exp.createExpenseUserMapping(userId,json_data,expGroupId)
            if result =="Success":
                return  jsonify({"message": "Expense Group user mapping created successfully" }),200
            else:
                return  jsonify({"message":result}),452
    except Exception as ex:
        return jsonify({"error":str(ex)}),500

@app.route("/expenseSplit", methods=["POST"])
# @jwt_required()
def expenseSplit():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            param_json= request.get_json()
            expGroupId=param_json['expGroupId']
            mapping_id=param_json['expense__by_user_id']
            total_expense_amount=param_json['total_expense_amount']
            expense_type=param_json['expense_type']
            user_id_amount_json = param_json["user_id_exact_amount_json"]
            user_id_percenta_amount_json = param_json["user_id_percenta_amount_json"]
            
            if expense_type=="EQUAL":
                result = exp.expenseSplit(expGroupId,mapping_id,total_expense_amount)
            if expense_type=="EXACT":
                result = exp.expenseExact(expGroupId,mapping_id,total_expense_amount,user_id_amount_json)
            if expense_type=="PERCENT":
                result = exp.expensePercent(expGroupId,mapping_id,total_expense_amount,user_id_percenta_amount_json)
            if result =="Success":
                gamil_list=exp.getusersmail(expGroupId)
                data = exp.getExpenseListbyexpGroupId(expGroupId)
                send_mail(reciver,gamil_list,data)
                return  jsonify({"message": "Expense split successfully" }),200
            else:
                return  jsonify({"message":result}),452
    except Exception as ex:
        return jsonify({"error":str(ex)}),500
    
@app.route("/getExpenseGrouplist", methods=["GET"])
# @jwt_required()
def getExpenseGrouplist():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            userId=request.args.get('userId')
            result=exp.getExpenseGrouplist(userId)
            return  jsonify(result),200
    except Exception as ex:
        return jsonify({"error":str(ex)}),500
    
@app.route("/getUserMappinglist", methods=["GET"])
# @jwt_required()
def getUserMappinglist():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            expGroupId=request.args.get('expGroupId')
            result=exp.getUserMappinglist(expGroupId)
            return  jsonify(result),200
    except Exception as ex:
        return jsonify({"error":str(ex)}),500
    
@app.route("/getExpenseListbyexpGroupId", methods=["GET"])
# @jwt_required()
def getExpenseListbyexpGroupId():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            expGroupId=request.args.get('expGroupId')
            result=exp.getExpenseListbyexpGroupId(expGroupId)
            return  jsonify(result),200
    except Exception as ex:
        return jsonify({"error":str(ex)}),500
    
@app.route("/getSingleUserExpenseList", methods=["GET"])
# @jwt_required()
def getSingleUserExpenseList():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            userId=request.args.get('userId')
            expGroupId=request.args.get('expGroupId')
            result=exp.getSingleUserExpenseList(expGroupId, userId)
            return  jsonify(result),200
    except Exception as ex:
        return jsonify({"error":str(ex)}),500
    
@app.route("/showNonZeroBalances", methods=["GET"])
# @jwt_required()
def showNonZeroBalances():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            expGroupId=request.args.get('expGroupId')
            result=exp.show_non_zero_balances(expGroupId)
            return  jsonify(result),200
    except Exception as ex:
        return jsonify({"error":str(ex)}),500
    
@app.route("/getowingdata", methods=["GET"])
# @jwt_required()
def getowingdata():
    try:
        api_key = request.headers["api-key"]
        if api_key!=apikey_global:
            return  jsonify({"message": "Unauthorized Access" }),401
        else:
            expGroupId=request.args.get('expGroupId')
            result=exp.calculate_owings(expGroupId)
            return  jsonify(result),200
    except Exception as ex:
        return jsonify({"error":str(ex)}),500

if __name__=="__main__":
    app.run()   