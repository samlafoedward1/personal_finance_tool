from flask import render_template, url_for, flash, redirect, request, Blueprint, Response, current_app, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, IncomeForm, ExpenseForm
from app.models import User, Income, Expense
from collections import defaultdict

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
@main_bp.route("/home")
def home():
    return render_template('index.html')

@main_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('User is already authenticated', 'info')
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    transactions = []
    incomes = Income.query.filter_by(author=current_user).all()
    expenses = Expense.query.filter_by(author=current_user).all()

    for income in incomes:
        transactions.append({
            'date': income.date,
            'description': income.description,
            'amount': income.amount,
            'category': income.category
        })

    for expense in expenses:
        transactions.append({
            'date': expense.date,
            'description': expense.description,
            'amount': expense.amount,
            'category': expense.category
        })

    for transaction in transactions:
        if 'date' not in transaction:
            current_app.logger.error(f"Missing 'date' in transaction: {transaction}")

    transactions.sort(key=lambda x: x['date'], reverse=True)

    return render_template('dashboard.html', title='Dashboard', transactions=transactions)

@main_bp.route("/add_transaction", methods=['GET', 'POST'])
@login_required
def add_transaction():
    income_form = IncomeForm()
    expense_form = ExpenseForm()
    if income_form.validate_on_submit() and income_form.submit.data:
        income = Income(amount=income_form.amount.data, category=income_form.category.data, description=income_form.description.data, author=current_user)
        db.session.add(income)
        db.session.commit()
        flash('Your income has been recorded!', 'success')
        return redirect(url_for('main.dashboard'))
    if expense_form.validate_on_submit() and expense_form.submit.data:
        expense = Expense(amount=expense_form.amount.data, category=expense_form.category.data, description=expense_form.description.data, author=current_user)
        db.session.add(expense)
        db.session.commit()
        flash('Your expense has been recorded!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_transaction.html', title='Add Transaction', income_form=income_form, expense_form=expense_form)



@main_bp.route("/transaction_data")
@login_required
def transaction_data():
    incomes = Income.query.filter_by(author=current_user).all()
    expenses = Expense.query.filter_by(author=current_user).all()

    income_data = defaultdict(float)
    expense_data = defaultdict(float)

    for income in incomes:
        income_data[income.category] += income.amount

    for expense in expenses:
        expense_data[expense.category] += expense.amount

    data = {
        "income_labels": list(income_data.keys()),
        "income_sizes": list(income_data.values()),
        "expense_labels": list(expense_data.keys()),
        "expense_sizes": list(expense_data.values())
    }

    return jsonify(data)


@main_bp.route("/switchable_graphs")
@login_required
def switchable_graphs_view():
    return render_template('switchable_graphs.html', title='Switchable Graphs')
