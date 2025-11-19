from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Stack2764@localhost/Tracker'
app.secret_key = "secret123"
db = SQLAlchemy(app)

class inventory(db.Model):
    __tablename__ = 'inventory'
    date_time = db.Column(db.DateTime, primary_key=True)
    job_num = db.Column(db.String(50))
    supp_code = db.Column(db.String(100))
    broker_code = db.Column(db.String(100))
    supplier_name = db.Column(db.String(100))
    width = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    order_num = db.Column(db.String(100))
    utilize = db.Column(db.Integer)
    tpipe = db.Column(db.String(100))
    dc_num = db.Column(db.String(100))
    wastage = db.Column(db.Integer)
    coil_type = db.Column(db.String(100))
    comments = db.Column(db.String(200))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['email'] == "a@m.com" and request.form['password'] == "1":
            return redirect("/main")

    return render_template('login.html')

@app.route("/main")
def main_page():
    records = inventory.query.order_by(inventory.date_time.desc()).all()
    return render_template("main.html", records=records)

@app.route("/submit", methods=["POST"])
def submit_data():
    try:
        record = inventory(
            date_time=datetime.now(),
            job_num=request.form.get("JobNumber"),
            supp_code=request.form.get("SupplierCode"),
            broker_code=request.form.get("BrokerCode"),
            supplier_name=request.form.get("supplier"),
            width=request.form.get("Width"),
            weight=request.form.get("Weight"),
            order_num=request.form.get("Order"),
            utilize=request.form.get("Utilize"),
            tpipe=request.form.get("Tpipe"),
            dc_num=request.form.get("DC"),
            wastage=request.form.get("Wastage"),
            coil_type=request.form.get("coil"),
            comments=request.form.get("Comments")
        )

        db.session.add(record)
        db.session.commit()

        return redirect("/main")

    except Exception as e:
        return f"Error: {e}"

@app.route("/search", methods=["GET", "POST"])
def search_jobs():
    msg = ""

    if request.method == "POST":
        sdate = request.form.get("sdate")

        # Example: search in DB
        results = inventory.query.filter(
            db.func.date(inventory.date_time) == sdate
        ).all()

        if not results:
            msg = "No records found for this date"

        return render_template("search.html", msg=msg, results=results)

    return render_template("search.html", msg=msg)

@app.route("/delete/<date_time>")
def delete_record(date_time):
    try:
        record = inventory.query.filter_by(date_time=date_time).first()

        if record:
            db.session.delete(record)
            db.session.commit()
            return redirect("/main")
        else:
            return "Record not found."

    except Exception as e:
        return f"Error deleting record: {e}"


@app.route("/edit/<date_time>", methods=["GET"])
def edit_record(date_time):
    record = inventory.query.filter_by(date_time=date_time).first()
    if not record:
        return "Record not found."

    return render_template("edit.html", record=record)

@app.route("/update/<date_time>", methods=["POST"])
def update_record(date_time):
    try:
        record = inventory.query.filter_by(date_time=date_time).first()

        if not record:
            return "Record not found."

        # Update values
        record.job_num = request.form.get("JobNumber")
        record.supp_code = request.form.get("SupplierCode")
        record.broker_code = request.form.get("BrokerCode")
        record.supplier_name = request.form.get("supplier")
        record.width = request.form.get("Width")
        record.weight = request.form.get("Weight")
        record.order_num = request.form.get("Order")
        record.utilize = request.form.get("Utilize")
        record.tpipe = request.form.get("Tpipe")
        record.dc_num = request.form.get("DC")
        record.wastage = request.form.get("Wastage")
        record.coil_type = request.form.get("coil")
        record.comments = request.form.get("Comments")

        db.session.commit()

        return redirect("/main")

    except Exception as e:
        return f"Error updating record: {e}"

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
