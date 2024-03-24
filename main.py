from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float


app = Flask(__name__)

Bootstrap(app)
app.secret_key = os.config['SECRET KEY']
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"


class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    rating = StringField('Rating', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RatingForm(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Book(db.Model):   # Creating Database and schema
    title: Mapped[str] = mapped_column(String(250), primary_key=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    with app.app_context():
        result = db.session.execute(db.select(Book).order_by(Book.title))
        all_books = result.scalars().all()
    return render_template('index.html', books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = BookForm()
    if form.validate_on_submit():
        with app.app_context():
            new_book = Book(title=form.title.data, author=form.author.data, rating=form.rating.data)
            db.session.add(new_book)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)


@app.route("/edit/<string:title_id>", methods=['GET', 'POST'])
def change_rating(title_id):
    form = RatingForm()
    if form.validate_on_submit():
        with app.app_context():
            book_to_update = db.session.execute(db.select(Book).where(Book.title == title_id)).scalar()
            book_to_update.rating = form.rating.data
            db.session.commit()
        return redirect(url_for('home'))
    with app.app_context():
        book = db.session.execute(db.select(Book).where(Book.title == title_id)).scalar()
    return render_template('rating.html', book=book, form=form)


@app.route("/delete/<string:title_id>", methods=['GET', 'POST'])
def delete(title_id):
    with app.app_context():
        book = db.session.execute(db.select(Book).where(Book.title == title_id)).scalar()
        db.session.delete(book)
        db.session.commit()
        result = db.session.execute(db.select(Book).order_by(Book.title))
        all_books = result.scalars().all()
    return render_template('index.html', books=all_books)


if __name__ == "__main__":
    app.run(debug=True, port=3000)
