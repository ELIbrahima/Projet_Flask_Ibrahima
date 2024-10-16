from .app import app
from flask import render_template, flash
from .models import get_sample, get_book, get_author, get_all_authors
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired
from flask import url_for, redirect
from .app import db
from wtforms import PasswordField
from .models import User
from hashlib import sha256
from flask_login import login_user, current_user
from flask import request
from flask_login import logout_user
from flask_login import login_required

from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import DataRequired, URL
from .models import Book, Author


class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])


class BookForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    price = DecimalField('Prix', validators=[DataRequired()])
    author_id = SelectField('Auteur', coerce=int, validators=[DataRequired()])
    amazon_link = StringField('Lien Amazon', validators=[DataRequired(), URL()])
    image_url = StringField('Image URL', validators=[DataRequired()])  # Ajouter un champ pour l'URL de l'image


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/books/")
def books():
    all_books = Book.query.all()  # Récupérer tous les livres
    return render_template(
        "books.html",
        title="Tiny - Amazon",
        books=all_books)  # Passer tous les livres au template


@app.route('/books/new', methods=['GET', 'POST'])
@login_required
def create_book():
    form = BookForm()

    # Charger les auteurs existants pour la liste déroulante
    form.author_id.choices = [(author.id, author.name) for author in get_all_authors()]

    if form.validate_on_submit():
        # Créer un nouveau livre à partir des données du formulaire
        new_book = Book(
            title=form.title.data,
            price=form.price.data,
            author_id=form.author_id.data,
            image_url=form.image_url.data,
            purchase_url=form.amazon_link.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash("Livre ajouté avec succès!", "success")
        return redirect(url_for('books'))

    return render_template('create_book.html', form=form)


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = get_book(book_id)  # Récupère le livre par son ID
    if book is None:
        abort(404)  # Renvoie une erreur 404 si le livre n'est pas trouvé
    return render_template('book_detail.html', book=book)


@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = get_book(book_id)  # Récupérer le livre par son ID
    if not book:
        flash("Livre introuvable.", "error")
        return redirect(url_for('books'))

    form = BookForm(obj=book)
    form.author_id.choices = [(author.id, author.name) for author in get_all_authors()]

    if form.validate_on_submit():
        # Mettre à jour le livre avec les nouvelles données
        book.title = form.title.data
        book.price = form.price.data
        book.author_id = form.author_id.data
        book.purchase_url = form.amazon_link.data
        book.image_url = form.image_url.data

        db.session.commit()
        flash("Livre modifié avec succès!", "success")
        return redirect(url_for('books'))

    return render_template('edit_book.html', form=form, book=book)


@app.route("/edit/author/<int:author_id>")
@login_required
def edit_author(author_id):
    a = get_author(author_id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template("edit-author.html", author=a, form=f)


@app.route("/save/author/", methods=("POST",))
def save_author():
    a = None
    f = AuthorForm()
    if f.validate_on_submit():
        id = int(f.id.data)
        a = get_author(id)
        a.name = f.name.data
        db.session.commit()
        return redirect(url_for('books', title="Tiny - Amazon", books=Book.query.all(), next=request.url))
    a = get_author(int(f.id.data))
    return render_template("edit-author.html", author=a, form=f)


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    next = HiddenField()

    def get_authenticated_user(self):
        user = User.query.get(self.username.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None


@app.route("/login/", methods=("GET", "POST",))
def login():
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            flash('Connexion réussie!', 'success')
            login_user(user)
            next = f.next.data or url_for("home")
            return redirect(next)
    return render_template("login.html", form=f)


@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))
