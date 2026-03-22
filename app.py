from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = "openhouse.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_date TEXT,
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

            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        visit_date = request.form.get("visit_date", "").strip()
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

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO visitors (
                visit_date, full_name, address, phone, email,
                visitor_role, working_with_agent, preapproved, price_range,
                presently, need_to_sell, purchase_type, household_size,
                purchase_timeline, bedrooms_needed,
                heard_about_us, heard_about_us_other, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            visit_date, full_name, address, phone, email,
            visitor_role, working_with_agent, preapproved, price_range,
            presently, need_to_sell, purchase_type, household_size,
            purchase_timeline, bedrooms_needed,
            heard_about_us, heard_about_us_other, created_at
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("thank_you"))

    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("form.html", today=today)


@app.route("/thankyou")
def thank_you():
    return render_template("thankyou.html")


@app.route("/admin")
def admin():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM visitors ORDER BY id DESC")
    visitors = c.fetchall()
    conn.close()
    return render_template("admin.html", visitors=visitors)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)