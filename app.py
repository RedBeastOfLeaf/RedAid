from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import datetime
import logging

app = Flask(__name__)
app.secret_key = "redaid"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:toor@localhost/applicant_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {
    'blood_bank': 'mysql://root:toor@localhost/blood_bank_database',
    'hospital': 'mysql://root:toor@localhost/hospital_database'
}

db = SQLAlchemy(app)


class applicant(db.Model):
    __tablename__ = 'applicant'
    applicant_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    applicant_gender = db.Column(db.String(10), default=None)
    birthdate = db.Column(db.Date, default=None)
    age = db.Column(db.Integer, default=None)


class login_table(db.Model):
    __tablename__ = 'login'
    user_id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.applicant_id'), nullable=False)
    login_name = db.Column(db.String(15), nullable=False)
    PWD = db.Column(db.String(15), nullable=False)


class medical_record(db.Model):
    __tablename__ = 'medical_record'
    record_id = db.Column(db.Integer, primary_key=True, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.applicant_id'), nullable=False)
    past_diseases = db.Column(db.String(255), nullable=False)
    blood_donated = db.Column(db.Integer, nullable=False)


class weight_category(db.Model):
    __tablename__ = 'weight_category'
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.applicant_id'), nullable=False, primary_key=True)
    weight = db.Column(db.Float, primary_key=True, nullable=False)
    height = db.Column(db.Float, primary_key=True, nullable=False)
    BMI = db.Column(db.Float)


class applicant_phone(db.Model):
    __tablename__ = 'applicant_phno'
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.applicant_id'), primary_key=True, nullable=False)
    applicant_phno = db.Column(db.String(12), default=None)


class appointments(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey(
        'applicant.applicant_id'), nullable=False)
    appointment_date = db.Column(db.Date, default=None)


class department(db.Model):
    __bind_key__ = 'hospital'
    __tablename__ = 'department'
    dept_id = db.Column(db.Integer, primary_key=True, nullable=False)
    dept_name = db.Column(db.String(40), nullable=False)


class doctor(db.Model):
    __bind_key__ = 'hospital'
    __tablename__ = 'doctor'
    doctor_id = db.Column(db.Integer, primary_key=True, nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey(
        'department.dept_id'), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    doctor_gender = db.Column(db.String(10))
    doctor_salary = db.Column(db.Float, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, default=None)


class doctor_phone(db.Model):
    __bind_key__ = 'hospital'
    __tablename__ = 'doctor_phno'
    doctor_id = db.Column(db.Integer, db.ForeignKey(
        'doctor.doctor_id'), primary_key=True, nullable=False)
    doctor_phno = db.Column(db.String(12), default=None)


class doctor_login_table(db.Model):
    __bind_key__ = 'hospital'
    __tablename__ = 'doctor_login'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey(
        'doctor.doctor_id'), nullable=False)
    login_name = db.Column(db.String(15), nullable=False)
    PWD = db.Column(db.String(15), nullable=False)


class orders(db.Model):
    __bind_key__ = 'hospital'
    __tablename__ = 'blood_demand'
    order_id = db.Column(db.Integer, primary_key=True, nullable=False)
    blood_type = db.Column(db.String(5), nullable=False)
    blood_quantity = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.String(15), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey(
        'doctor.doctor_id'), nullable=False)


class staff(db.Model):
    __bind_key__ = 'blood_bank'
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    staff_gender = db.Column(db.String(10))
    birthdate = db.Column(db.Date, default=None)
    age = db.Column(db.Integer, default=None)


class staff_phone(db.Model):
    __bind_key__ = 'blood_bank'
    __tablename__ = 'staff_phno'
    staff_id = db.Column(db.Integer, db.ForeignKey(
        'staff.staff_id'), primary_key=True, nullable=False)
    staff_phno = db.Column(db.String(12), default=None)


class staff_login_table(db.Model):
    __bind_key__ = 'blood_bank'
    __tablename__ = 'staff_login'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey(
        'staff.staff_id'), nullable=False)
    login_name = db.Column(db.String(15), nullable=False)
    PWD = db.Column(db.String(15), nullable=False)


@app.route('/')
def home():
    if "user" in session:
        user = session["user"]
        if user == "admin":
            fuser = "Admin"
        elif session["path"] == "applicant":
            a = login_table.query.filter_by(
                applicant_id=session["user"]).first()
            fuser = a.login_name
        elif session["path"] == "doctor":
            d = doctor_login_table.query.filter_by(
                doctor_id=session["user"]).first()
            fuser = d.login_name
        elif session["path"] == "staff":
            s = staff_login_table.query.filter_by(
                staff_id=session["user"]).first()
            fuser = s.login_name

        return render_template("index.html", fuser=fuser)
    return render_template("index.html")


@app.route('/applicants')
def applicants():
    all_applicants = applicant.query.all()
    return render_template("applicant.html", appl=all_applicants)


@app.route('/login')
def login():
    if "user" in session:
        if session["user"] == "admin":
            return redirect("/admin")
        url = "/" + session["path"] + "/" + str(session["user"])
        return redirect(url)
    return render_template("login.html")


@app.route('/signup')
def signup():
    if "user" in session:
        if session["user"] == "admin":
            return redirect("/admin")
        url = "/" + session["path"] + "/" + str(session["user"])
        return redirect(url)
    return render_template("signup.html")


@app.route('/login/<path>', methods=['GET', 'POST'])
def login_path(path):
    error = None
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        if uname == 'admin' and pwd == '123':
            session["user"] = "admin"
            return redirect('/admin')

        session["path"] = path

        if path == 'applicant':
            a = login_table.query.filter_by(login_name=uname).first()
            if a == None:
                error = 'User not found'
                return render_template("flogin.html", path=path, error=error)
            if a.PWD == pwd:
                error = None
                session["user"] = a.applicant_id
                return redirect('/applicant/' + str(a.applicant_id))
            error = 'Wrong Password'
            return render_template("flogin.html", path=path, error=error)

        elif path == 'doctor':
            d = doctor_login_table.query.filter_by(login_name=uname).first()
            if d == None:
                error = 'User not found'
                return render_template("flogin.html", path=path, error=error)
            if d.PWD == pwd:
                error = None
                session["user"] = d.doctor_id
                return redirect('/doctor/' + str(d.doctor_id))
            error = 'Wrong Password'
            return render_template("flogin.html", path=path, error=error)

        elif path == 'staff':
            s = staff_login_table.query.filter_by(login_name=uname).first()
            if s == None:
                error = 'User not found'
                return render_template("flogin.html", path=path, error=error)
            if s.PWD == pwd:
                error = None
                session["user"] = s.staff_id
                return redirect('/staff/' + str(s.staff_id))
            error = 'Wrong Password'
            return render_template("flogin.html", path=path, error=error)

    if "user" in session:
        if session["user"] == "admin":
            return redirect("/admin")
        url = "/" + session["path"] + "/" + str(session["user"])
        return redirect(url)
    return render_template("flogin.html", path=path, error=error)


@app.route('/signup/<path>', methods=['GET', 'POST'])
def signup_path(path):
    dt = datetime.date.today()
    maxdate = dt - datetime.timedelta(days=18*365)
    error = None
    inputs = {'fname': '', 'lname': '', 'gender': '', 'dob': '', 'phone': '', 'uname': '', 'pwd': '',
              'cpwd': '', 'weight': '', 'height': '', 'pastdiseases': '', 'blood': '', 'salary': '', 'department': ''}
    if request.method == 'POST':
        inputs['fname'] = request.form['firstname']
        inputs['lname'] = request.form['lastname']
        inputs['gender'] = request.form['gender']
        inputs['dob'] = request.form['DOB']
        inputs['phone'] = request.form['phone']
        if path == 'applicant':
            inputs['weight'] = request.form['weight']
            inputs['height'] = request.form['height']
            inputs['pastdiseases'] = request.form['pastdiseases']
            inputs['blood'] = request.form['blood']
        elif path == 'doctor':
            inputs['salary'] = request.form['salary']
            inputs['department'] = request.form['department']
        inputs['uname'] = request.form['username']
        inputs['pwd'] = request.form['password']
        inputs['cpwd'] = request.form['confirm-password']

        today = datetime.date.today()
        dob = inputs['dob'].split('-')
        b_day, b_month, b_year = int(dob[2]), int(dob[1]), int(dob[0])
        dob = datetime.date(b_year, b_month, b_day)

        age = today.year - dob.year - \
            ((today.month, today.day) < (dob.month, dob.day))

        al = login_table.query.all()
        dl = doctor_login_table.query.all()

        if inputs['pwd'] != inputs['cpwd']:
            error = 'Password does not match'
            return render_template("fsignup.html", path=path, maxdate=maxdate, error=error, inputs=inputs)

        if path == 'applicant':
            for l in al:
                if l.login_name == inputs['uname']:
                    error = 'Username already exists'
                    return render_template("fsignup.html", path=path, maxdate=maxdate, error=error, inputs=inputs)

            bmi = 0
            w = float(inputs['weight'])
            h = float(inputs['height'])
            bmi = round((w)/((h/100)**2), ndigits=2)

            appl = applicant(first_name=inputs['fname'], last_name=inputs['lname'],
                             applicant_gender=inputs['gender'], birthdate=inputs['dob'], age=age)
            db.session.add(appl)
            db.session.commit()

            a = applicant.query.order_by(applicant.applicant_id.desc()).first()

            a_log = login_table(applicant_id=a.applicant_id,
                                login_name=inputs['uname'], PWD=inputs['pwd'])
            db.session.add(a_log)
            db.session.commit()

            a_med = medical_record(
                applicant_id=a.applicant_id, past_diseases=inputs['pastdiseases'], blood_donated=inputs['blood'])
            db.session.add(a_med)
            db.session.commit()

            a_wc = weight_category(
                applicant_id=a.applicant_id, weight=inputs['weight'], height=inputs['height'], BMI=bmi)
            db.session.add(a_wc)
            db.session.commit()

            a_phno = applicant_phone(
                applicant_id=a.applicant_id, applicant_phno=inputs['phone'])
            db.session.add(a_phno)
            db.session.commit()

            session["user"] = a.applicant_id
            session["path"] = path
            return redirect('/applicant/' + str(a.applicant_id))

        elif path == 'doctor':
            for l in dl:
                if l.login_name == inputs['uname']:
                    error = 'Username already exists'
                    return render_template("fsignup.html", path=path, maxdate=maxdate, error=error, inputs=inputs)
            dept = department.query.filter_by(
                dept_name=inputs['department']).first()
            doc = doctor(first_name=inputs['fname'], last_name=inputs['lname'], dept_id=dept.dept_id,
                         doctor_gender=inputs['gender'], doctor_salary=inputs['salary'], birth_date=inputs['dob'], age=age)
            db.session.add(doc)
            db.session.commit()

            d = doctor.query.order_by(doctor.doctor_id.desc()).first()

            d_log = doctor_login_table(doctor_id=d.doctor_id,
                                       login_name=inputs['uname'], PWD=inputs['pwd'])
            db.session.add(d_log)
            db.session.commit()

            d_phno = doctor_phone(
                doctor_id=d.doctor_id, doctor_phno=inputs['phone'])
            db.session.add(d_phno)
            db.session.commit()

            session["user"] = d.doctor_id
            session["path"] = path
            return redirect('/doctor/' + str(d.doctor_id))

    if "user" in session:
        if session["user"] == "admin":
            return redirect("/admin")
        url = "/" + session["path"] + "/" + str(session["user"])
        return redirect(url)
    return render_template("fsignup.html", path=path, maxdate=maxdate, error=error, inputs=inputs)


@app.route('/admin')
def admin_path():
    if "user" in session and session["user"] == "admin":
        all = applicant.query.all()
        count = 0
        for a in all:
            count += 1
        return render_template("admin_home.html", count=count)
    else:
        return redirect("/login")


@app.route('/applicant/<int:applicant_id>')
def applicant_page(applicant_id):
    if "user" in session and session['path'] == 'applicant' and session['user'] == applicant_id:
        a = appointments.query.filter_by(applicant_id=applicant_id).first()
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        delta = 0
        if a == None:
            appointment = delta
        elif a.appointment_id == None:
            appointment = delta
        else:
            x = datetime.datetime.strptime(today, '%Y-%m-%d')
            y = datetime.datetime.strptime(str(a.appointment_date), '%Y-%m-%d')
            delta = y - x
            appointment = delta.days

        return render_template("applicant_home.html", applicant_id=applicant_id, appointment=appointment)
    else:
        return redirect("/login")


@app.route('/appointment/<int:applicant_id>/<purpose>', methods=['GET', 'POST'])
def appointment(applicant_id, purpose):
    if 'user' in session and session['path'] == 'applicant':
        a = appointments.query.filter_by(applicant_id=applicant_id).first()
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        if request.method == 'POST':
            appointment_date = request.form['Appointment']
            if a == None or a.appointment_date == None:
                ad = appointments(applicant_id=applicant_id,
                                  appointment_date=appointment_date)
                db.session.add(ad)
                db.session.commit()
            else:
                a.appointment_date = appointment_date
                db.session.commit()
            return redirect('/login')
        if purpose == 'update':
            d_value = a.appointment_date
            return render_template("appointments.html", applicant_id=applicant_id, mindate=today, purpose=purpose, d_value=d_value)
        return render_template("appointments.html", applicant_id=applicant_id, mindate=today, purpose=purpose)
    else:
        return redirect("/login")


@app.route('/doctor/<int:doctor_id>')
def doctor_page(doctor_id):
    if "user" in session and session['path'] == 'doctor' and session['user'] == doctor_id:
        d = doctor.query.filter_by(doctor_id=doctor_id).first()
        return render_template("doctor_home.html", doctor_id=doctor_id, d=d)
    else:
        return redirect("/login")


@app.route('/request/<int:doctor_id>', methods=['GET', 'POST'])
def doc_req(doctor_id):
    if "user" in session and session['path'] == 'doctor' and session['user'] == doctor_id:
        if request.method == 'POST':
            status = 'Processing'
            bld_quantity = request.form['blood_quantity']
            bld_type = request.form['blood_group']
            o = orders(blood_type=bld_type, blood_quantity=bld_quantity,
                       order_status=status, doctor_id=doctor_id)
            db.session.add(o)
            db.session.commit()
            return redirect('/login')
        return render_template("doc_req.html", doctor_id=doctor_id)
    else:
        return redirect("/login")


@app.route('/staff/<int:staff_id>')
def staff_page(staff_id):
    if "user" in session and session['path'] == 'staff' and session['user'] == staff_id:
        s = staff.query.filter_by(staff_id=staff_id).first()
        return render_template("staff_home.html", s=s, staff_id=staff_id)
    else:
        return redirect("/login")


@app.route('/staff/<int:staff_id>/<table>')
def appoints(staff_id, table):
    if "user" in session and session['path'] == 'staff' and session['user'] == staff_id:
        applicants = list()
        doctors = list()
        d = list()
        dph = list()
        a = list()
        aph = list()
        s = staff.query.filter_by(staff_id=staff_id).first()
        if table == 'appointments':
            ap = appointments.query.order_by(
                appointments.appointment_date.asc()).all()
            for x in ap:
                applicants.append(x.applicant_id)
            for y in applicants:
                a.append(applicant.query.filter_by(applicant_id=y).first())
            for z in applicants:
                aph.append(applicant_phone.query.filter_by(
                    applicant_id=z).first())
            appoint = zip(a, ap, aph)
            print(a, aph)
            return render_template("appointments_table.html", appoint=appoint, staff_id=staff_id, s=s)
        elif table == 'orders':
            l = True
            o = orders.query.filter_by(order_status='Processing').all()
            if o == []:
                l = False
                return render_template('orders_table.html', l=l)
            else:
                for x in o:
                    doctors.append(x.doctor_id)
                for y in doctors:
                    d.append(doctor.query.filter_by(doctor_id=y).first())
                for z in doctors:
                    dph.append(doctor_phone.query.filter_by(
                        doctor_id=z).first())
                ord = zip(o, d, dph)
                return render_template("orders_table.html", ord=ord, staff_id=staff_id, s=s, l=l)
        else:
            return redirect('/login')
    else:
        return redirect('/login')


@ app.route('/complete/<int:staff_id>/<int:order_id>')
def complete_order(staff_id, order_id):
    if 'user' in session and session['path'] == 'staff' and session['user'] == staff_id:
        order = orders.query.filter_by(order_id=order_id).first()
        order.order_status = 'Completed'
        db.session.commit()
        return redirect('/staff/' + str(staff_id) + '/' + 'orders')
    return redirect('/login')


@ app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("path", None)
    return redirect("/")


@ app.route('/database')
def database():
    if "user" in session and session["user"] == "admin":
        return render_template("databases.html")
    return redirect("/login")


@ app.route('/database/<path>')
def database_path(path):
    if "user" in session and session["user"] == "admin":
        if path == "applicant":
            a = applicant.query.all()
            am = medical_record.query.all()
            aw = weight_category.query.all()
            all_applicants = zip(a, am, aw)
            return render_template("applicant_database.html", all=all_applicants)
        elif path == "doctor":
            d = doctor.query.all()
            dd = department.query.all()
            fdd = list()
            for dx in d:
                dep = department.query.filter_by(dept_id=dx.dept_id).first()
                fdd.append(dep.dept_name)
            all_doctors = zip(d, fdd)
            return render_template("doctor_database.html", all=all_doctors)
        elif path == "staff":
            s = staff.query.all()
            return render_template("staff_database.html", s=s)

    return redirect("/login")


@ app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@ app.route('/privacy')
def privacy():
    return render_template("privacypolicy.html")


@ app.route('/order')
def order():
    o = orders.query.filter_by(order_status='Processing').all()
    for i in o:
        print(i.doctor_id)
    return 'Done'


if __name__ == '__main__':
    app.run()
