import re
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import defaultdict
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Abdare123@localhost/Tracker'
app.secret_key = "secret123"
db = SQLAlchemy(app)


# ----------------------------
# DATABASE MODELS
# ----------------------------

class CoilType(db.Model):
    __tablename__ = 'coil_types'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True, nullable=False)

class ItemDescription(db.Model):
    __tablename__ = 'item_descriptions'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True, nullable=False)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True, nullable=False)

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True, nullable=False)


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

@app.route("/")
def homepage():
    return redirect("/home")


@app.route("/home")
def home():
    return render_template("home.html")



# ----------------------------
# LOGIN PAGE
# ----------------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['email'] == "a@m.com" and request.form['password'] == "1":
            return redirect("/main")
    return render_template('login.html')


# ----------------------------
# MAIN / GRN PAGE
# ----------------------------

@app.route("/main")
def main_page():
    records = inventory.query.order_by(inventory.date_time.desc()).all()

    # Serial number handling
    pattern = re.compile(r"^([A-Z])-010-(\d{5})-(\d{2})$")
    counters = defaultdict(int)

    for r in records:
        if r.serial_num:
            m = pattern.match(r.serial_num)
            if m:
                prefix = m.group(1)
                num = int(m.group(2))
                counters[prefix] = max(counters[prefix], num)

    # MAIN PAGE NOW DOES NOT SHOW SUBMITTED RECORDS
    return render_template(
        "main.html",
        counters=dict(counters),
        coil_types=CoilType.query.all(),
        suppliers=Supplier.query.all(),
        grades=Grade.query.all(),
        item_descs=ItemDescription.query.all()
    )


@app.route("/grn")
def grn():
    return redirect("/main")  # GRN simply loads main page


# ----------------------------
# SUBMIT DATA
# ----------------------------

@app.route("/submit", methods=["POST"])
def submit_data():
    try:
        record = inventory(
            date_time=datetime.now(),
            serial_num=request.form.get("serial_num"),
            job_num=request.form.get("JobNumber"),
            supp_code=request.form.get("SupplierCode"),
            broker_code=request.form.get("BrokerCode"),
            supplier_name=request.form.get("supplier_name"),

            weight=request.form.get("Weight"),
            manufcode=request.form.get("manufcode"),
            dc_num=request.form.get("dc_num"),
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


# ----------------------------
# SEARCH PAGE
# ----------------------------

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


# ----------------------------
# RECORDS PAGE (TABLE ONLY)
# ----------------------------

@app.route("/records")
def records_page():
    data = inventory.query.order_by(inventory.date_time.desc()).all()
    return render_template("records.html", data=data)


# ----------------------------
# DELETE A RECORD
# ----------------------------

@app.route("/delete/<date_time>")
def delete_record(date_time):
    try:
        record = inventory.query.filter_by(date_time=date_time).first()

        if record:
            db.session.delete(record)
            db.session.commit()
            return redirect("/records")
        else:
            return "Record not found."

    except Exception as e:
        return f"Error deleting record: {e}"


# ----------------------------
# EDIT PAGE
# ----------------------------

@app.route("/edit/<date_time>")
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
        record.supplier_name = request.form.get("supplier_name")

        record.weight = request.form.get("Weight")
        record.manufcode = request.form.get("manufcode")
        record.dc_num = request.form.get("dc_num")
        record.coil_type = request.form.get("coil")
        record.comments = request.form.get("Comments")

        record.hardness = request.form.get("Hardness")
        record.grade = request.form.get("Grade")
        record.batchNo = request.form.get("BatchNo")
        record.itemcode = request.form.get("itemcode")
        record.uom = request.form.get("UOM")
        record.item_desc = request.form.get("ItemDesc")

        db.session.commit()
        return redirect("/records")

    except Exception as e:
        return f"Error updating record: {e}"


# ----------------------------
# JOB SHEET PAGE
# ----------------------------

@app.route("/job_sheet/<date_time>")
def job_sheet(date_time):
    row = inventory.query.filter_by(date_time=date_time).first()
    if not row:
        return "Record not found", 404

    return render_template("job_sheet.html", r=row)


# ----------------------------
# MANAGE OPTIONS (COIL, SUPPLIER, DESC, GRADE)
# ----------------------------

@app.route("/add_option", methods=["POST"])
def add_option():
    data = request.get_json()
    option_type = data.get("type")
    value = data.get("value").strip()

    if option_type == "coil":
        new_entry = CoilType(value=value)
    elif option_type == "supplier":
        new_entry = Supplier(value=value)
    elif option_type == "itemdesc":
        new_entry = ItemDescription(value=value)
    elif option_type == "grade":
        new_entry = Grade(value=value)
    else:
        return {"status": "error", "message": "Invalid option type"}

    try:
        db.session.add(new_entry)
        db.session.commit()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route("/get_options/<type_name>")
def get_options(type_name):
    if type_name == "coil":
        values = [c.value for c in CoilType.query.all()]
    elif type_name == "supplier":
        values = [s.value for s in Supplier.query.all()]
    elif type_name == "grade":
        values = [g.value for g in Grade.query.all()]
    elif type_name == "itemdesc":
        values = [d.value for d in ItemDescription.query.all()]
    else:
        values = []

    return jsonify(values)


@app.route("/edit_option", methods=["POST"])
def edit_option():
    data = request.get_json()
    t = data.get("type")
    old_value = data.get("old")
    new_value = data.get("new")

    if t == "coil":
        entry = CoilType.query.filter_by(value=old_value).first()
    elif t == "supplier":
        entry = Supplier.query.filter_by(value=old_value).first()
    elif t == "grade":
        entry = Grade.query.filter_by(value=old_value).first()
    elif t == "itemdesc":
        entry = ItemDescription.query.filter_by(value=old_value).first()
    else:
        return jsonify({"status": "error", "message": "Invalid type"})

    if entry:
        entry.value = new_value.strip()
        db.session.commit()

    return jsonify({"status": "success"})


@app.route("/delete_option", methods=["POST"])
def delete_option():
    data = request.get_json()
    t = data.get("type")
    value = data.get("value")

    if t == "coil":
        entry = CoilType.query.filter_by(value=value).first()
    elif t == "supplier":
        entry = Supplier.query.filter_by(value=value).first()
    elif t == "grade":
        entry = Grade.query.filter_by(value=value).first()
    elif t == "itemdesc":
        entry = ItemDescription.query.filter_by(value=value).first()
    else:
        return jsonify({"status": "error", "message": "Invalid type"})

    if entry:
        db.session.delete(entry)
        db.session.commit()

    return jsonify({"status": "success"})


# ----------------------------
# LOGOUT
# ----------------------------

@app.route("/logout")
def logout():
    return redirect("/")


# ----------------------------
# RUN APP
# ----------------------------

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
