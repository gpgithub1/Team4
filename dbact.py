import pymysql
import pymysql.cursors
from datetime import datetime

db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='root1234',db='travel')

greetings = ["hi", "hello", "hello there", "hello, there"]
bookText = ["book a flight", "i want to book a flight", "book flight"]
destination = ["new york","boston", "texas", "san fransisco", "florida", "chicago"]
source = ["new york","boston", "texas", "san fransisco", "florida", "chicago" ]

def store_data(data):
    destination = data['destination']
    source = data['source']
    date = data['date']
    sql = ("select * from flights where destination = '%s' and source = '%s' and sourcetime >= '%s'" %(destination, source, date))
    cur = db.cursor()
    cur.execute(sql)
    all_data = cur.fetchall()
    return all_data


def validate(dateTime):
    try:
        if(dateTime != datetime.strptime(dateTime, "%Y-%m-%d").strftime('%Y-%m-%d')):
            raise ValueError
        return True
    except ValueError:
        return False
