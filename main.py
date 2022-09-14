from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TimeField, SelectField, URLField
from wtforms.validators import DataRequired, URL


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    # open_time = db.Column(db.String(250), nullable=False)
    # close_time = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    # power = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    # rating = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Alternatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

db.create_all()

class CafeForm(FlaskForm):
    name = StringField(u'Cafe name', validators=[DataRequired()])
    map_url = URLField(u'Cafe Location on Google Maps(URL)',
                            validators=[URL(True, "Invalid URL")])
    img_url = URLField('Cafe Image (URL)',
                     validators=[URL(), DataRequired()])
    location = StringField(u'Location',
                           validators=[DataRequired()])
    has_sockets = SelectField('Sockets Availability:',
                              choices=[("0", "Nope"), ("1", "Yes")])
    has_wifi = SelectField('Wifi Availability:',
                              choices=[("0", "Nope"), ("1", "Yes")])
    wc = SelectField('Toilet Availability: ',
                     choices=[("0", "Nope"), ("1", "Yes")])
    calls = SelectField('Can take calls:',
                        choices=[("0", "Nope"), ("1", "Yes")])
    coffee_price = StringField(u'Coffee Price',
                           validators=[DataRequired()])
    seats = StringField('Number of seats:',
                        validators=[DataRequired()])
    submit = SubmitField('Submit')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/cafes")
def cafes():
    all_cafes = db.session.query(Cafe).all()
    cafe_name = [cafe.to_dict() for cafe in all_cafes]
    return render_template("cafes.html", cafe_list=cafe_name)


def boolean_convert(to_convert):
    if to_convert == "1":
        return bool(to_convert)
    else:
        return 0


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    if os.path.isfile("cafes.db"):
        print("Database is already created.")

        form = CafeForm()
        if form.validate_on_submit():
            new_cafe = Cafe(
                name=request.form['name'],
                map_url=request.form["map_url"],
                img_url=request.form["img_url"],
                location=request.form["location"],
                seats=request.form["seats"],
                has_toilet=boolean_convert(request.form["wc"]),
                has_wifi=boolean_convert(request.form["has_wifi"]),
                has_sockets=boolean_convert(request.form["has_sockets"]),
                can_take_calls=boolean_convert(request.form["calls"]),
                coffee_price=f"${request.form['coffee_price']}",
            )
            db.session.add(new_cafe)
            # db.session.rollback()
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template("add.html", form=form)
    else:
        db.create_all()
        print("Database created.")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        #UPDATE RECORD
        cafe_id = request.form["id"]
        cafe_to_update = Cafe.query.get(cafe_id)
        cafe_to_update.name = request.form["name"]
        cafe_to_update.img_url = request.form["img_url"]
        cafe_to_update.location = request.form["location"]
        cafe_to_update.map_url = request.form["map_url"]
        cafe_to_update.seats = request.form["seats"]
        cafe_to_update.has_toilet = boolean_convert(request.form["has_toilet"])
        cafe_to_update.has_wifi = boolean_convert(request.form["has_wifi"])
        cafe_to_update.has_sockets = boolean_convert(request.form["has_sockets"])
        cafe_to_update.can_take_calls = boolean_convert(request.form["can_take_calls"])
        cafe_to_update.coffee_price = request.form["price"]
        db.session.commit()
        return redirect(url_for('cafes'))
    cafe_id = request.args.get('id')
    cafe_selected = Cafe.query.get(cafe_id)
    return render_template("edit.html", cafe=cafe_selected)

@app.route("/delete")
def delete():
    cafe_id = request.args.get('id')

    # DELETE A RECORD BY ID
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('cafes'))



if __name__ == '__main__':
    app.run(debug=True)
