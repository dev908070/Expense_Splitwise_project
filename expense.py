from user import session
from db_layer import Expense_group,Expense_group_user_mapping,Expense_data,User
import json
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import and_,func
from sqlalchemy.orm import aliased

def createExpenseGroup(expenseGroupName,userId):
    new_Expense_group = Expense_group(expGroupName=expenseGroupName, userId=userId)
    session.add(new_Expense_group)
    session.commit()
    session.close()
    return "Success"

def check_record_exists(table_name,email, mobile_number, expGroupId):
    existing_record = session.query(table_name).\
        filter_by(email=email, mobileNumber=mobile_number, expGroupId=expGroupId).first()
    return existing_record is not None

    
def createExpenseUserMapping(userId,json_data,expGroupId):
    dictdata=json.loads(json_data)
    user_data = session.query(User).filter_by(userId=userId).all()
    columns=['name','email','mobileNumber']
    user_data = [{column: getattr(user, column) for column in columns} for user in user_data][0]
    check_resp = check_record_exists(Expense_group_user_mapping,user_data['email'],user_data['mobileNumber'],expGroupId)
    if check_resp==False:
        dictdata.append(user_data)
    for i in range(len(dictdata)):
        name=dictdata[i]['name']
        email=dictdata[i]['email']
        mobileNumber=dictdata[i]['mobileNumber']
        if check_record_exists(Expense_group_user_mapping,email, mobileNumber, expGroupId):
            return str(email)+" and "+str(mobileNumber)+" data may be duplicate or already avaliable in this group"
        new_Expense_group_user_mapping = Expense_group_user_mapping(name=name, email=email, mobileNumber=mobileNumber,expGroupId=expGroupId)
        session.add(new_Expense_group_user_mapping)
        session.commit()
    session.close()
    return "Success"

def update_or_insert_amount(expGroupId,mapping_id, new_amount):
    try:
        existing_record = session.query(Expense_data).\
            filter_by(user_mapping_id=mapping_id).one()
        existing_record.splited_exp_amount = existing_record.splited_exp_amount+int(new_amount)
        session.commit()
        session.close()
        return True
    except NoResultFound:
        new_mapping = Expense_data(expGroupId=expGroupId,user_mapping_id=mapping_id, splited_exp_amount=new_amount, total_expense_amount=0)
        session.add(new_mapping)
        session.commit()
        session.close()
        return True
    except Exception as e:
        session.rollback()
        return False

def update_insert_total_exp_amount(expGroupId,mapping_id,total_expense_amount):
    try:
        existing_record = session.query(Expense_data).filter_by(user_mapping_id=mapping_id).one()
        existing_record.total_expense_amount = existing_record.total_expense_amount+int(total_expense_amount)
        session.commit()
        session.close()
    except NoResultFound:
        new_mapping = Expense_data(expGroupId=expGroupId,user_mapping_id=mapping_id, splited_exp_amount=0, total_expense_amount=total_expense_amount)
        session.add(new_mapping)
        session.commit()
        session.close()

def expenseSplit(expGroupId,mapping_id,total_expense_amount):
    mapping_ids = session.query(Expense_group_user_mapping.expense_group_user_mapping_id).filter_by(expGroupId=expGroupId).all()
    mapping_ids = [value for value, in mapping_ids]
    count = session.query(Expense_group_user_mapping.expense_group_user_mapping_id).filter_by(expGroupId=expGroupId).count()
    if count==0:
        return "Please create expense group and user first"
    if count>=1000:
        return "expense group can't be more than 1000 participants"
    if int(total_expense_amount)>=10000000:
        return "maximum amount for an expense can go up to INR 1,00,00,000"
    new_amount = int(total_expense_amount)/count
    new_amount = round(new_amount, 2)
    update_insert_total_exp_amount(expGroupId,mapping_id,total_expense_amount)
    for i in range(count):
        update_or_insert_amount(expGroupId,mapping_ids[i], new_amount)
    return "Success"

def expenseExact(expGroupId,mapping_id,total_expense_amount,user_id_amount_json):
        user_id_amount_json=json.loads(user_id_amount_json)
        exp_list = [int(d.get('individual_expense_amount', 0)) for d in user_id_amount_json]
        total_exp=sum(exp_list)
        if total_exp!=int(total_expense_amount):
            return "Total split expense is not equal to total_expense_amount"
        if len(user_id_amount_json)>=1000:
            return "expense group can't be more than 1000 participants"
        if int(total_expense_amount)>=10000000:
            return "maximum amount for an expense can go up to INR 1,00,00,000"
        update_insert_total_exp_amount(expGroupId,mapping_id,total_expense_amount)
        for i in range(len(user_id_amount_json)):
            update_or_insert_amount(expGroupId,user_id_amount_json[i]['expense_by_user_id'], user_id_amount_json[i]['individual_expense_amount'])
        return "Success"

def expensePercent(expGroupId,mapping_id,total_expense_amount,user_id_percenta_amount_json):
    user_id_percenta_amount_json=json.loads(user_id_percenta_amount_json)
    percentage_list=[int(d.get('expense_percent')) for d in user_id_percenta_amount_json]
    total_percentage=sum(percentage_list)
    if total_percentage!=100:
        return "Total split percentage is not equal to 100%"
    if len(user_id_percenta_amount_json)>=1000:
        return "expense group can't be more than 1000 participants"
    if int(total_expense_amount)>=10000000:
        return "maximum amount for an expense can go up to INR 1,00,00,000"
    update_insert_total_exp_amount(expGroupId,mapping_id,total_expense_amount)
    for i in range(len(user_id_percenta_amount_json)):
        expense_percentage=(percentage_list[i]/100)*int(total_expense_amount)
        update_or_insert_amount(expGroupId,user_id_percenta_amount_json[i]['expense_user_id'], expense_percentage)
    return "Success"

def getExpenseGrouplist(userId):
    user_data = session.query(Expense_group).filter_by(userId=userId).all()
    columns=['expGroupId','expGroupName','created_at']
    user_data = [{column: getattr(user, column) for column in columns} for user in user_data]
    session.close()
    return user_data

def getUserMappinglist(expGroupId):
    user_data = session.query(Expense_group_user_mapping).filter_by(expGroupId=expGroupId).all()
    columns=['expense_group_user_mapping_id','name','email','mobileNumber','expGroupId','created_at']
    user_data = [{column: getattr(user, column) for column in columns} for user in user_data]
    session.close()
    return user_data

def getusersmail(expGroupId):
    emails = session.query(Expense_group_user_mapping.email).filter_by(expGroupId=expGroupId).all()
    email_list = [result[0] for result in emails]
    return email_list

def getExpenseListbyexpGroupId(expGroupId):
    user_mapping_alias = aliased(Expense_group_user_mapping, name="user_mapping")
    query_result = session.query(
        user_mapping_alias.name,
        Expense_data.total_expense_amount,
        func.round(Expense_data.splited_exp_amount, 2).label('splited_exp_amount')
    ).join(
        Expense_data,
        and_(
            user_mapping_alias.expense_group_user_mapping_id == Expense_data.user_mapping_id,
            user_mapping_alias.expGroupId == Expense_data.expGroupId
        )).filter(
    user_mapping_alias.expGroupId == expGroupId
    ).all()

    columns=['name','total_expense_amount','splited_exp_amount']
    user_data = [{column: getattr(user, column) for column in columns} for user in query_result]
    session.close()
    print(user_data)
    return user_data

def getSingleUserExpenseList(expGroupId, userId):
    user_mapping_alias = aliased(Expense_group_user_mapping, name="user_mapping")
    query_result = session.query(
        user_mapping_alias.name,
        Expense_data.total_expense_amount,
        func.round(Expense_data.splited_exp_amount, 2).label('splited_exp_amount')
    ).join(
        Expense_data,
        and_(
            user_mapping_alias.expense_group_user_mapping_id == Expense_data.user_mapping_id,
            user_mapping_alias.expGroupId == Expense_data.expGroupId
        )
    ).filter(
        user_mapping_alias.expGroupId == expGroupId,
        user_mapping_alias.expense_group_user_mapping_id == userId
    ).all()

    columns = ['name', 'total_expense_amount', 'splited_exp_amount']
    user_data = [{column: getattr(user, column) for column in columns} for user in query_result]
    session.close()
    print(user_data)
    return user_data


def show_non_zero_balances(expGroupId):
    user_mapping_alias = aliased(Expense_group_user_mapping, name="user_mapping")
    query_result = session.query(
        user_mapping_alias.name,
        Expense_data.total_expense_amount,
        func.round(Expense_data.splited_exp_amount, 2).label('splited_exp_amount')
    ).join(
        Expense_data,
        and_(
            user_mapping_alias.expense_group_user_mapping_id == Expense_data.user_mapping_id,
            user_mapping_alias.expGroupId == Expense_data.expGroupId,
            Expense_data.total_expense_amount != 0,
            Expense_data.splited_exp_amount != 0
        )).filter(
    user_mapping_alias.expGroupId == expGroupId
    ).all()

    columns=['name','total_expense_amount','splited_exp_amount']
    user_data = [{column: getattr(user, column) for column in columns} for user in query_result]
    session.close()
    print(user_data)
    return user_data

def get_distinct_expGroupIds():
    expGroupIds = session.query(Expense_group_user_mapping.expGroupId).distinct().all()
    expGroupId_list = [result[0] for result in expGroupIds]
    return expGroupId_list

def calculate_owings(expGroupId):
    data=getExpenseListbyexpGroupId(expGroupId)
    owings_list = []
    for person in data:
        if person['total_expense_amount'] > person['splited_exp_amount']:
            for other_person in data:
                if other_person['total_expense_amount'] < other_person['splited_exp_amount']:
                    amount_owed = min(person['total_expense_amount'] - person['splited_exp_amount'],
                                      other_person['splited_exp_amount'] - other_person['total_expense_amount'])
                    owings_list.append({f"{person['name']} owes {other_person['name']}": amount_owed})
                    person['total_expense_amount'] -= amount_owed
                    other_person['total_expense_amount'] += amount_owed
    return owings_list




