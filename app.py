import re
import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import defaultdict
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Stack2764@localhost/Tracker'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///local.db"
)
app.secret_key = "secret123"
db = SQLAlchemy(app)


# ----------------------------
# DATABASE MODELS
# ----------------------------
#
# -------------SETUP--------------------
class PipeSize(db.Model):
    __tablename__ = 'pipe_sizes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)

class ThicknessSize(db.Model):
    __tablename__ = 'thickness_sizes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)

class StripSize(db.Model):
    __tablename__ = 'strip_sizes'

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    size = db.Column(db.String(50))

    thickness_code = db.Column(db.String(20))
    thickness_name = db.Column(db.String(200))

    pipe_code = db.Column(db.String(20))
    pipe_name = db.Column(db.String(200))

    pipe_weight = db.Column(db.String(50))

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


class CuttingJob(db.Model):
    __tablename__ = "cutting_jobs"

    id = db.Column(db.Integer, primary_key=True)

    job_no = db.Column(db.String(100))
    job_date = db.Column(db.String(50))

    supplier_code = db.Column(db.String(100))
    supplier_name = db.Column(db.String(200))
    broker_code = db.Column(db.String(100))
    broker_name = db.Column(db.String(200))
    comments = db.Column(db.String(300))
    lot_no = db.Column(db.String(100))
    tm_no = db.Column(db.String(100))
    item_name = db.Column(db.String(200))

    manuf_code = db.Column(db.String(100))
    uom = db.Column(db.String(50))
    batch_no = db.Column(db.String(100))
    coil_weight = db.Column(db.String(100))
    hardness = db.Column(db.String(100))
    grade = db.Column(db.String(100))
    coil_type = db.Column(db.String(100))
    item_code = db.Column(db.String(100))

    coil_width = db.Column(db.String(100))
    utilize = db.Column(db.String(100))
    wastage = db.Column(db.String(100))
    weight_mm = db.Column(db.String(100))
    total_pipe = db.Column(db.String(100))

    pipe_code = db.Column(db.String(100))
    pipe_name = db.Column(db.String(200))

    thickness_code = db.Column(db.String(100))
    thickness_name = db.Column(db.String(200))

    strip_code = db.Column(db.String(100))
    strip_name = db.Column(db.String(200))
    strip_size = db.Column(db.String(100))

    quantity = db.Column(db.String(100))
    total_width = db.Column(db.String(100))
    line_weight = db.Column(db.String(100))
    issue = db.Column(db.String(10))

    created_at = db.Column(db.DateTime, default=datetime.now)
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
            return redirect("/home")
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

@app.route("/setup")
def setup():
    return render_template("setup.html")

@app.route("/pipe-size-setup", methods=["GET", "POST"])
def pipe_size_setup():
    if request.method == "POST":
        code = request.form.get("pipe_code")
        name = request.form.get("pipe_name")

        if code and name:
            new_pipe = PipeSize(code=code.strip(), name=name.strip())
            db.session.add(new_pipe)
            db.session.commit()

        return redirect("/pipe-size-setup")

    pipe_sizes = PipeSize.query.order_by(PipeSize.code.asc()).all()

    return render_template(
        "pipe_size_setup.html",
        pipe_sizes=pipe_sizes,
        edit_pipe=None
    )


@app.route("/pipe-size-edit/<int:id>")
def pipe_size_edit(id):
    edit_pipe = PipeSize.query.get_or_404(id)
    pipe_sizes = PipeSize.query.order_by(PipeSize.code.asc()).all()

    return render_template(
        "pipe_size_setup.html",
        pipe_sizes=pipe_sizes,
        edit_pipe=edit_pipe
    )


@app.route("/pipe-size-update/<int:id>", methods=["POST"])
def pipe_size_update(id):
    pipe = PipeSize.query.get_or_404(id)

    pipe.code = request.form.get("pipe_code").strip()
    pipe.name = request.form.get("pipe_name").strip()

    db.session.commit()

    return redirect("/pipe-size-setup")


@app.route("/pipe-size-delete/<int:id>")
def pipe_size_delete(id):
    pipe = PipeSize.query.get_or_404(id)

    db.session.delete(pipe)
    db.session.commit()

    return redirect("/pipe-size-setup")


@app.route("/thickness-size-setup", methods=["GET", "POST"])
def thickness_size_setup():
    if request.method == "POST":
        code = request.form.get("thickness_code")
        name = request.form.get("thickness_name")

        if code and name:
            new_thickness = ThicknessSize(
                code=code.strip(),
                name=name.strip()
            )
            db.session.add(new_thickness)
            db.session.commit()

        return redirect("/thickness-size-setup")

    thickness_sizes = ThicknessSize.query.order_by(ThicknessSize.code.asc()).all()

    return render_template(
        "thickness_size_setup.html",
        thickness_sizes=thickness_sizes,
        edit_thickness=None
    )


@app.route("/thickness-size-edit/<int:id>")
def thickness_size_edit(id):
    edit_thickness = ThicknessSize.query.get_or_404(id)
    thickness_sizes = ThicknessSize.query.order_by(ThicknessSize.code.asc()).all()

    return render_template(
        "thickness_size_setup.html",
        thickness_sizes=thickness_sizes,
        edit_thickness=edit_thickness
    )


@app.route("/thickness-size-update/<int:id>", methods=["POST"])
def thickness_size_update(id):
    thickness = ThicknessSize.query.get_or_404(id)

    thickness.code = request.form.get("thickness_code").strip()
    thickness.name = request.form.get("thickness_name").strip()

    db.session.commit()

    return redirect("/thickness-size-setup")


@app.route("/thickness-size-delete/<int:id>")
def thickness_size_delete(id):
    thickness = ThicknessSize.query.get_or_404(id)

    db.session.delete(thickness)
    db.session.commit()

    return redirect("/thickness-size-setup")

@app.route("/strip-size-setup", methods=["GET", "POST"])
def strip_size_setup():
    if request.method == "POST":
        strip_code = request.form.get("strip_code")
        strip_name = request.form.get("strip_name")
        size = request.form.get("size")
        thickness_id = request.form.get("thickness_id")
        pipe_id = request.form.get("pipe_id")
        pipe_weight = request.form.get("pipe_weight")

        thickness = ThicknessSize.query.get(thickness_id)
        pipe = PipeSize.query.get(pipe_id)

        if strip_code and strip_name and thickness and pipe:
            new_strip = StripSize(
                code=strip_code.strip(),
                name=strip_name.strip(),
                size=size.strip() if size else "",
                thickness_code=thickness.code,
                thickness_name=thickness.name,
                pipe_code=pipe.code,
                pipe_name=pipe.name,
                pipe_weight=pipe_weight.strip() if pipe_weight else ""
            )

            db.session.add(new_strip)
            db.session.commit()

        return redirect("/strip-size-setup")

    strip_sizes = StripSize.query.order_by(StripSize.code.asc()).all()
    thickness_sizes = ThicknessSize.query.order_by(ThicknessSize.code.asc()).all()
    pipe_sizes = PipeSize.query.order_by(PipeSize.code.asc()).all()

    return render_template(
        "strip_size_setup.html",
        strip_sizes=strip_sizes,
        thickness_sizes=thickness_sizes,
        pipe_sizes=pipe_sizes,
        edit_strip=None
    )


@app.route("/strip-size-edit/<int:id>")
def strip_size_edit(id):
    edit_strip = StripSize.query.get_or_404(id)

    strip_sizes = StripSize.query.order_by(StripSize.code.asc()).all()
    thickness_sizes = ThicknessSize.query.order_by(ThicknessSize.code.asc()).all()
    pipe_sizes = PipeSize.query.order_by(PipeSize.code.asc()).all()

    return render_template(
        "strip_size_setup.html",
        strip_sizes=strip_sizes,
        thickness_sizes=thickness_sizes,
        pipe_sizes=pipe_sizes,
        edit_strip=edit_strip
    )


@app.route("/strip-size-update/<int:id>", methods=["POST"])
def strip_size_update(id):
    strip = StripSize.query.get_or_404(id)

    strip_code = request.form.get("strip_code")
    strip_name = request.form.get("strip_name")
    size = request.form.get("size")
    thickness_id = request.form.get("thickness_id")
    pipe_id = request.form.get("pipe_id")
    pipe_weight = request.form.get("pipe_weight")

    thickness = ThicknessSize.query.get(thickness_id)
    pipe = PipeSize.query.get(pipe_id)

    if thickness and pipe:
        strip.code = strip_code.strip()
        strip.name = strip_name.strip()
        strip.size = size.strip() if size else ""

        strip.thickness_code = thickness.code
        strip.thickness_name = thickness.name

        strip.pipe_code = pipe.code
        strip.pipe_name = pipe.name

        strip.pipe_weight = pipe_weight.strip() if pipe_weight else ""

        db.session.commit()

    return redirect("/strip-size-setup")


@app.route("/strip-size-delete/<int:id>")
def strip_size_delete(id):
    strip = StripSize.query.get_or_404(id)

    db.session.delete(strip)
    db.session.commit()

    return redirect("/strip-size-setup")

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


@app.route("/cut", methods=["GET", "POST"])
def cutting_job():
    if request.method == "POST":
        pipe = PipeSize.query.get(request.form.get("pipe_id"))
        thickness = ThicknessSize.query.get(request.form.get("thickness_id"))
        strip = StripSize.query.get(request.form.get("strip_id"))

        new_cutting = CuttingJob(
            job_no=request.form.get("job_no"),
            job_date=request.form.get("job_date"),

            supplier_code=request.form.get("supplier_code"),
            supplier_name=request.form.get("supplier_name"),
            broker_code=request.form.get("broker_code"),
            broker_name=request.form.get("broker_name"),
            comments=request.form.get("comments"),
            lot_no=request.form.get("lot_no"),
            tm_no=request.form.get("tm_no"),
            item_name=request.form.get("item_name"),

            manuf_code=request.form.get("manuf_code"),
            uom=request.form.get("uom"),
            batch_no=request.form.get("batch_no"),
            coil_weight=request.form.get("coil_weight"),
            hardness=request.form.get("hardness"),
            grade=request.form.get("grade"),
            coil_type=request.form.get("coil_type"),
            item_code=request.form.get("item_code"),

            coil_width=request.form.get("coil_width"),
            utilize=request.form.get("utilize"),
            wastage=request.form.get("wastage"),
            weight_mm=request.form.get("weight_mm"),
            total_pipe=request.form.get("total_pipe"),

            pipe_code=pipe.code if pipe else "",
            pipe_name=pipe.name if pipe else "",

            thickness_code=thickness.code if thickness else "",
            thickness_name=thickness.name if thickness else "",

            strip_code=strip.code if strip else "",
            strip_name=strip.name if strip else "",
            strip_size=strip.size if strip else "",

            quantity=request.form.get("quantity"),
            total_width=request.form.get("total_width"),
            line_weight=request.form.get("line_weight"),
            issue=request.form.get("issue")
        )

        db.session.add(new_cutting)
        db.session.commit()

        return redirect("/cut")

    grn_records = inventory.query.order_by(inventory.date_time.desc()).all()
    cutting_records = CuttingJob.query.order_by(CuttingJob.id.desc()).all()

    return render_template(
        "cutting_job.html",
        grn_records=grn_records,
        pipe_sizes=PipeSize.query.all(),
        thickness_sizes=ThicknessSize.query.all(),
        strip_sizes=StripSize.query.all(),
        cutting_records=cutting_records,
        edit_cutting=None,
        job_no=None
    )


@app.route("/cut-edit/<int:id>")
def cut_edit(id):
    edit_cutting = CuttingJob.query.get_or_404(id)

    grn_records = inventory.query.order_by(inventory.date_time.desc()).all()
    cutting_records = CuttingJob.query.order_by(CuttingJob.id.desc()).all()

    return render_template(
        "cutting_job.html",
        grn_records=grn_records,
        pipe_sizes=PipeSize.query.all(),
        thickness_sizes=ThicknessSize.query.all(),
        strip_sizes=StripSize.query.all(),
        cutting_records=cutting_records,
        edit_cutting=edit_cutting,
        job_no=edit_cutting.job_no
    )


@app.route("/cut-update/<int:id>", methods=["POST"])
def cut_update(id):
    record = CuttingJob.query.get_or_404(id)

    pipe = PipeSize.query.get(request.form.get("pipe_id"))
    thickness = ThicknessSize.query.get(request.form.get("thickness_id"))
    strip = StripSize.query.get(request.form.get("strip_id"))

    record.job_no = request.form.get("job_no")
    record.job_date = request.form.get("job_date")

    record.supplier_code = request.form.get("supplier_code")
    record.supplier_name = request.form.get("supplier_name")
    record.broker_code = request.form.get("broker_code")
    record.broker_name = request.form.get("broker_name")
    record.comments = request.form.get("comments")
    record.lot_no = request.form.get("lot_no")
    record.tm_no = request.form.get("tm_no")
    record.item_name = request.form.get("item_name")

    record.manuf_code = request.form.get("manuf_code")
    record.uom = request.form.get("uom")
    record.batch_no = request.form.get("batch_no")
    record.coil_weight = request.form.get("coil_weight")
    record.hardness = request.form.get("hardness")
    record.grade = request.form.get("grade")
    record.coil_type = request.form.get("coil_type")
    record.item_code = request.form.get("item_code")

    record.coil_width = request.form.get("coil_width")
    record.utilize = request.form.get("utilize")
    record.wastage = request.form.get("wastage")
    record.weight_mm = request.form.get("weight_mm")
    record.total_pipe = request.form.get("total_pipe")

    record.pipe_code = pipe.code if pipe else ""
    record.pipe_name = pipe.name if pipe else ""

    record.thickness_code = thickness.code if thickness else ""
    record.thickness_name = thickness.name if thickness else ""

    record.strip_code = strip.code if strip else ""
    record.strip_name = strip.name if strip else ""
    record.strip_size = strip.size if strip else ""

    record.quantity = request.form.get("quantity")
    record.total_width = request.form.get("total_width")
    record.line_weight = request.form.get("line_weight")
    record.issue = request.form.get("issue")

    db.session.commit()

    return redirect("/cut")


@app.route("/cut-delete/<int:id>")
def cut_delete(id):
    record = CuttingJob.query.get_or_404(id)

    db.session.delete(record)
    db.session.commit()

    return redirect("/cut")

@app.route("/cut-records")
def cut_records_page():
    data = CuttingJob.query.order_by(CuttingJob.created_at.desc()).all()
    return render_template("cut_records.html", data=data)

@app.route("/cut-sheet/<int:id>")
def cut_sheet(id):
    selected_cut = CuttingJob.query.get_or_404(id)

    cuts = CuttingJob.query.filter_by(
        lot_no=selected_cut.lot_no,
        job_date=selected_cut.job_date
    ).order_by(CuttingJob.id.asc()).all()

    if not cuts:
        return "No cutting records found for this coil and date.", 404

    first = cuts[0]

    total_width = 0
    total_weight = 0
    total_pipe = 0

    for c in cuts:
        total_width += float(c.total_width or 0)
        total_weight += float(c.line_weight or 0)
        total_pipe += float(c.quantity or 0)

    coil_width = float(first.coil_width or 0)
    wastage = coil_width - total_width

    return render_template(
        "cut_sheet.html",
        first=first,
        cuts=cuts,
        total_width=total_width,
        total_weight=total_weight,
        total_pipe=total_pipe,
        coil_width=coil_width,
        wastage=wastage
    )

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
