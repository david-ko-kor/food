

from flask import Flask, render_template,g,request
from datetime import datetime
from database import get_db,connet_db

app = Flask(__name__)
@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

@app.route('/',methods=['GET','POST'])
def index():
    db = get_db()
    if request.method =='POST':
        date = request.form['date']
        print(date)
        dataBaseTime = datetime.strptime(date,'%Y-%m-%d')
        print(dataBaseTime)
        dateTime =datetime.strftime(dataBaseTime,'%Y%m%d')
        print(dateTime)
        db.execute('insert  into log_date(entry_date) values(?)',[dateTime])
        db.commit()
    cur=db.execute("""select log_date.entry_date,sum(food.protein) as protein,sum(food.carbohydrates) as carbohydrates ,sum(food.fat) as fat,sum(food.calories) as calories from log_date
                      join food_date on food_date.log_date_id = log_date.id 
                      join food on food.id = food_date.food_id 
                      group by log_date.id 
                      order by log_date.entry_date""")
    result =cur.fetchall()
    print('1',result)
    for i in result:
        print(type(i['entry_date']))
        dateConvert =datetime.strptime(str(i['entry_date']),'%Y%m%d')
        print(dateConvert)
        entry_list = [
            {str(i['entry_date']): datetime.strptime(str(i['entry_date']), '%Y%m%d').strftime('%B %d, %Y'),'origin':i['entry_date'],'protein':i['protein'],'carbohydrates':i['carbohydrates'],'fat':i['fat'],'calories':i['calories']}
            for i in result
        ]
        # list =[{i['entry_date']:datetime.strftime(dateConvert,'%B%d %Y')}for i in result]
        # print(list)
        print(entry_list)
    return render_template('home.html',list=entry_list)

@app.route('/view/<date>',methods=['GET','POST'])
def view(date):
    db = get_db()
    cur = db.execute('select id, entry_date from log_date where entry_date=?', [date])
    result = cur.fetchone()
    print(result)
    if request.method =='POST':
        db.execute('''insert into food_date (food_id,log_date_id) 
                      values(?,?)''',[request.form['foodname'],result['id']])
        db.commit()

    dateFormate=datetime.strptime(str(result['entry_date']),'%Y%m%d')
    print(dateFormate)
    resultDate = datetime.strftime(dateFormate,'%B %d %Y')
    print(resultDate)
    food_cur =db.execute('select id,name from food')
    foodlist=food_cur.fetchall()
    print(foodlist)
    log_cur=db.execute('''select food.id,food.name,food.protein,food.carbohydrates,food.fat,food.calories from log_date 
                          join food_date on food_date.log_date_id = log_date.id
                          join food on food.id = food_date.food_id 
                          where log_date.entry_date = ?''',[date])
    log_result =log_cur.fetchall()
    total={}
    total['protein']=0
    total['carbohydrates']=0
    total['fat']=0
    total['calories']=0

    for i in log_result:
        total['protein']+=i['protein']
        total['carbohydrates']+=i['carbohydrates']
        total['fat']+=i['fat']
        total['calories']+=i['calories']
    print(total)

    return render_template('day.html',entry_date=result['entry_date'] ,\
                           result=resultDate,foodlist=foodlist,log_result=log_result,total=total)

@app.route('/food',methods=['GET','POST'])
def food():
    db = get_db()
    if request.method =='POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        print(name,protein,carbohydrates,fat)
        calories = protein * 4 + carbohydrates * 4 + fat * 4
        print(calories)
        db.execute('insert into food(name,protein,carbohydrates,fat,calories) values(?,?,?,?,?)',[name,protein,carbohydrates,fat,calories])
        db.commit()
    cur =db.execute('select * from food')
    results =cur.fetchall()
        # return '<h1>name:{},protein:{},carbs:{},fat:{}</h1>'.format(request.form['food-name'],request.form['protein'],request.form['carbohydrates'],request.form['fat'])
    return render_template('add_food.html',results=results)

if __name__ == '__main__':
    app.run(debug=True)