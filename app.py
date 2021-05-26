from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://mtafzsrnlfybdd:2693694e171752c6330b1133b6b1fc0e6fd144d6dfe9c0dc8014a2e9b3b15f6e@ec2-23-21-229-200.compute-1.amazonaws.com:5432/d9clhorui9ktrb"

db = SQLAlchemy(app)
ma = Marshmallow(app)
heroku = Heroku(app)
CORS(app)


class Month(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    days_in_month = db.Column(db.Integer, nullable=False)
    days_in_previous_month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def __init__(self, name, start_day, days_in_month, days_in_previous_month, year):
        self.name = name
        self.start_day = start_day
        self.days_in_month = days_in_month
        self.days_in_previous_month = days_in_previous_month
        self.year = year
    
class MonthSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "start_day", "days_in_month", "days_in_previous_month", "year")

month_schema = MonthSchema()
multiple_month_schema = MonthSchema(many=True)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    month_id = db.Column(db.Integer, nullable=False)

    def __init__(self, text, date, month_id):
        self.text = text
        self.date = date
        self.month_id = month_id

class ReminderSchema(ma.Schema):
    class Meta:
        fields = ("id", "text", "date", "month_id")

reminder_schema = ReminderSchema()
multiple_reminder_schema = ReminderSchema(many=True)


@app.route("/month/add", methods=["POST"])
def add_month():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON.")

    post_data = request.get_json()
    name = post_data.get("name")
    start_day = post_data.get("start_day")
    days_in_month = post_data.get("days_in_month")
    days_in_previous_month = post_data.get("days_in_previous_month")
    year = post_data.get("year")

    record = Month(name, start_day, days_in_month, days_in_previous_month, year)
    db.session.add(record)
    db.session.commit()

    return jsonify("Month added")

@app.route("/month/add/multiple", methods=["POST"])
def add_multiple_months():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON.")

    post_data = request.get_json()
    data = post_data.get("data")
    for month in data:
        record = Month(month["name"], month["start_day"], month["days_in_month"], month["days_in_previous_month"], month["year"])
        db.session.add(record)

    db.session.commit()

    return jsonify("All months added")        

@app.route("/month/get", methods=["GET"])
def get_all_months():
    all_months = db.session.query(Month).all()
    return jsonify(multiple_month_schema.dump(all_months))

@app.route("/month/get/<month_name>/<month_year>", methods=["GET"])
def get_one_month(month_name, month_year):
    month = db.session.query(Month).filter(Month.name == month_name).filter(Month.year == month_year).first()
    return jsonify(month_schema.dump(month))


@app.route("/reminder/add", methods=["POST"])
def add_reminder():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON.")

    post_data = request.get_json()
    text = post_data.get("text")
    date = post_data.get("date")
    month_id = post_data.get("month_id")

    record = Reminder(text, date, month_id)
    db.session.add(record)
    db.session.commit()

    return jsonify("Reminder added")

@app.route("/reminder/get", methods=["GET"])
def get_all_reminders():
    all_reminders = db.session.query(Reminder).all()
    return jsonify(multiple_reminder_schema.dump(all_reminders))

@app.route("/reminder/get/<month_id>/<date>", methods=["GET"])
def get_one_reminder(month_id, date):
    reminder = db.session.query(Reminder).filter(Reminder.month_id == month_id).filter(Reminder.date == date).first()
    return jsonify(reminder_schema.dump(reminder))

@app.route("/reminder/update/<id>", methods=["PUT"])
def update_reminder(id):
    reminderr = db.session.query(Reminder).filter(Reminder.id == id).first()
    if reminder is None:
        return jsonify(f"Error: No reminder with id {id}.")

    put_data = request.get_json()
    new_text = put_data.get("text")

    if new_text == "":
        return jsonify("Error: Text can not be blank.")

    reminder.text = new_text
    db.session.commit()

    return jsonify("Reminder updated")

@app.route("/reminder/delete/<id>", methods=["DELETE"])
def delete_reminder(id):
    reminder = db.session.query(Reminder).filter(Reminder.id == id).first()
    db.session.delete(reminder)
    db.session.commit()
    return jsonify("Reminder deleted")


if __name__ == "__main__":
    app.run(debug=True)