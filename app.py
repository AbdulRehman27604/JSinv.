import re
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Stack2764@localhost/Tracker'
app.secret_key = "secret123"
db = SQLAlchemy(app)


class inventory(db.Model):
    __tablename__ = 'inventory'

    date_time = db.Column(db.DateTime, primary_key=True)

    serial_num = db.Column(db.String(100))
    job_num = db.Column(db.String(50))
    supp_code = db.Column(db.String(100))
    broker_code = db.Column(db.String(100))
    supplier_name = db.Column(db.String(100))

    weight = db.Column(db.Integer)
    manufcode = db.Column(db.String(100))
    dc_num = db.Column(db.String(100))
    coil_type = db.Column(db.String(100))
    comments = db.Column(db.String(200))

    hardness = db.Column(db.String(50))
    grade = db.Column(db.String(50))
    batchNo = db.Column(db.String(50))
    itemcode = db.Column(db.String(100))
    uom = db.Column(db.String(50))
    item_desc = db.Column(db.String(200))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['email'] == "a@m.com" and request.form['password'] == "1":
            return redirect("/main")
    return render_template('login.html')


@app.route("/main")
def main_page():
    records = inventory.query.order_by(inventory.date_time.desc()).all()

    # Serial counter prefix extraction
    pattern = re.compile(r"^([A-Z])-010-(\d{5})-(\d{2})$")
    counters = defaultdict(int)

    for r in records:
        if r.serial_num:
            m = pattern.match(r.serial_num)
            if m:
                prefix = m.group(1)
                num = int(m.group(2))
                counters[prefix] = max(counters[prefix], num)

    return render_template("main.html", records=records, counters=dict(counters))


@app.route("/submit", methods=["POST"])
def submit_data():
    try:
        record = inventory(
            date_time=datetime.now(),
            serial_num=request.form.get("serial_num"),
            job_num=request.form.get("JobNumber"),
            supp_code=request.form.get("SupplierCode"),
            broker_code=request.form.get("BrokerCode"),
            supplier_name=request.form.get("supplier"),

            weight=request.form.get("Weight"),
            manufcode=request.form.get("Maufcode"),
            dc_num=request.form.get("DC"),
            coil_type=request.form.get("coil"),
            comments=request.form.get("Comments"),

            hardness=request.form.get("Hardness"),
            grade=request.form.get("Grade"),
            batchNo=request.form.get("BatchNo"),
            itemcode=request.form.get("itemcode"),
            uom=request.form.get("UOM"),
            item_desc=request.form.get("ItemDesc")
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

        record.job_num = request.form.get("JobNumber")
        record.supp_code = request.form.get("SupplierCode")
        record.broker_code = request.form.get("BrokerCode")
        record.supplier_name = request.form.get("supplier")

        record.weight = request.form.get("Weight")
        record.manufcode = request.form.get("Maufcode")
        record.dc_num = request.form.get("DC")
        record.coil_type = request.form.get("coil")
        record.comments = request.form.get("Comments")

        record.hardness = request.form.get("Hardness")
        record.grade = request.form.get("Grade")
        record.batchNo = request.form.get("BatchNo")
        record.itemcode = request.form.get("itemcode")
        record.uom = request.form.get("UOM")
        record.item_desc = request.form.get("ItemDesc")

        db.session.commit()

        return redirect("/main")

    except Exception as e:
        return f"Error updating record: {e}"

@app.route("/job_sheet/<date_time>")
def job_sheet(date_time):

    # Retrieve the full row based on date_time
    row = db.session.query(inventory).filter_by(date_time=date_time).first()

    if not row:
        return "Record not found", 404

    return render_template("job_sheet.html", r=row)



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
