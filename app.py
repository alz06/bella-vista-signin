import os
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import psycopg
from psycopg.rows import dict_row

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-this")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

if not ADMIN_PASSWORD_HASH:
    raise RuntimeError("ADMIN_PASSWORD_HASH is not set in .env")


def get_conn():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS visitors (
                    id SERIAL PRIMARY KEY,
                    visit_date DATE,
                    full_name TEXT NOT NULL,
                    address TEXT,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,

                    visitor_role TEXT,
                    working_with_agent TEXT,
                    preapproved TEXT,
                    price_range TEXT,

                    presently TEXT,
                    need_to_sell TEXT,
                    purchase_type TEXT,
                    household_size TEXT,
                    purchase_timeline TEXT,
                    bedrooms_needed TEXT,

                    heard_about_us TEXT,
                    heard_about_us_other TEXT,

                    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped_view


@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        visit_date = request.form.get("visit_date") or None
        full_name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        visitor_role = request.form.get("visitor_role", "").strip()
        working_with_agent = request.form.get("working_with_agent", "").strip()
        preapproved = request.form.get("preapproved", "").strip()
        price_range = request.form.get("price_range", "").strip()

        presently = request.form.get("presently", "").strip()
        need_to_sell = request.form.get("need_to_sell", "").strip()
        purchase_type = request.form.get("purchase_type", "").strip()
        household_size = request.form.get("household_size", "").strip()
        purchase_timeline = request.form.get("purchase_timeline", "").strip()
        bedrooms_needed = request.form.get("bedrooms_needed", "").strip()

        heard_about_us = request.form.get("heard_about_us", "").strip()
        heard_about_us_other = request.form.get("heard_about_us_other", "").strip()

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO visitors (
                        visit_date, full_name, address, phone, email,
                        visitor_role, working_with_agent, preapproved, price_range,
                        presently, need_to_sell, purchase_type, household_size,
                        purchase_timeline, bedrooms_needed,
                        heard_about_us, heard_about_us_other
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    visit_date, full_name, address, phone, email,
                    visitor_role, working_with_agent, preapproved, price_range,
                    presently, need_to_sell, purchase_type, household_size,
                    purchase_timeline, bedrooms_needed,
                    heard_about_us, heard_about_us_other
                ))
            conn.commit()

        return redirect(url_for("thank_you"))

    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("form.html", today=today)


@app.route("/thankyou")
def thank_you():
    return render_template("thankyou.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session.clear()
            session["admin_logged_in"] = True
            session["admin_username"] = username
            return redirect(url_for("admin"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin")
@login_required
def admin():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM visitors
                ORDER BY submitted_at DESC, id DESC
            """)
            visitors = cur.fetchall()

    return render_template("admin.html", visitors=visitors)
    

if __name__ == "__main__":
    init_db()
    app.run(debug=True)