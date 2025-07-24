import customtkinter as ctk
from tkcalendar import Calendar
import threading
import time
import csv
import os

CSV_FILE = "debt_data.csv"
USERS_FILE = "users.csv"
records = []
current_user = None  # Store the logged-in username

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# ========== Load & Save ==========
def load_data():
    global records
    records.clear()
    if not os.path.exists(CSV_FILE) or not current_user:
        return
    temp = []
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get('username') != current_user:
                continue  # Only load records for the logged-in user
            entry_type = row.get('type', 'creditor')
            name = row['name']
            purpose = row['purpose']
            total_debt = float(row['total_debt'])
            status = row.get('status', 'active')
            date = row['date']
            amount = row['amount']
            action = row.get('action', 'payment')
            debt_purpose = row.get('debt_purpose', '')

            existing = next((r for r in temp if r['name'] == name and r['type'] == entry_type), None)
            if not existing:
                existing = {
                    "name": name,
                    "purpose": purpose,
                    "total_debt": total_debt,
                    "payments": [],
                    "debts": [],
                    "status": status,
                    "type": entry_type
                }
                temp.append(existing)

            if date and amount:
                if action == 'debt':
                    existing["debts"].append({
                        "date": date,
                        "amount": float(amount),
                        "purpose": debt_purpose
                    })
                else:
                    existing["payments"].append({
                        "date": date,
                        "amount": float(amount)
                    })
    records.extend(temp)

def save_all_data():
    # Load all existing records
    all_records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                all_records.append(row)

    # Remove all records for the current user
    all_records = [r for r in all_records if r.get('username') != current_user]

    # Add current user's records
    for entry in records:
        if entry['payments']:
            for p in entry['payments']:
                all_records.append({
                    'username': current_user,
                    'type': entry['type'],
                    'name': entry['name'],
                    'purpose': entry['purpose'],
                    'total_debt': entry['total_debt'],
                    'status': entry['status'],
                    'date': p['date'],
                    'amount': p['amount'],
                    'action': 'payment',
                    'debt_purpose': ''
                })
        if entry['debts']:
            for d in entry['debts']:
                all_records.append({
                    'username': current_user,
                    'type': entry['type'],
                    'name': entry['name'],
                    'purpose': entry['purpose'],
                    'total_debt': entry['total_debt'],
                    'status': entry['status'],
                    'date': d['date'],
                    'amount': d['amount'],
                    'action': 'debt',
                    'debt_purpose': d['purpose']
                })
        if not entry['payments'] and not entry['debts']:
            all_records.append({
                'username': current_user,
                'type': entry['type'],
                'name': entry['name'],
                'purpose': entry['purpose'],
                'total_debt': entry['total_debt'],
                'status': entry['status'],
                'date': '',
                'amount': '',
                'action': '',
                'debt_purpose': ''
            })

    # Write all records back to the CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'type', 'name', 'purpose', 'total_debt', 'status', 'date', 'amount', 'action', 'debt_purpose']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_records:
            writer.writerow(row)

def load_users():
    users = []
    if not os.path.exists(USERS_FILE):
        return users
    with open(USERS_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users

def save_user(username, password):
    file_exists = os.path.exists(USERS_FILE)
    with open(USERS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['username', 'password'])
        writer.writerow([username, password])

# ========== App ==========
app = ctk.CTk()
app.title("Utang Tracker")
app.geometry("1000x800")
app.minsize(800, 600)
app.rowconfigure(0, weight=1)
app.columnconfigure(0, weight=1)

current_frame = None

# ========== Pages ==========
def show_login_page():
    global current_frame, current_user
    current_user = None
    if current_frame:
        current_frame.destroy()

    frame = ctk.CTkFrame(app)
    frame.grid(row=0, column=0, sticky="nsew")
    current_frame = frame

    app_title = ctk.CTkLabel(
        frame,
        text="💼 Utang Tracker",
        font=ctk.CTkFont(size=28, weight="bold")
    )
    app_title.pack(pady=(40, 5))

    byline = ctk.CTkLabel(
        frame,
        text="by John Allen Esteleydes",
        font=ctk.CTkFont(size=14, slant="italic"),
        text_color="#636e72"
    )
    byline.pack(pady=(0, 30))

    title = ctk.CTkLabel(frame, text="🔐 Login", font=ctk.CTkFont(size=24, weight="bold"))
    title.pack(pady=10)

    user_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=300)
    user_entry.pack(pady=10)

    pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
    pass_entry.pack(pady=10)

    status = ctk.CTkLabel(frame, text="")
    status.pack(pady=10)

    def attempt_login():
        username = user_entry.get().strip()
        password = pass_entry.get().strip()
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                status.configure(text="✅ Login successful!", text_color="green")
                global current_user
                current_user = username
                show_loading_page()
                return
        status.configure(text="❌ Invalid username or password!", text_color="red")

    login_btn = ctk.CTkButton(frame, text="Sign In", width=200, height=40, corner_radius=20, command=attempt_login)
    login_btn.pack(pady=20)

    def show_register_page():
        show_registration_page()

    register_btn = ctk.CTkButton(frame, text="Create Account", width=200, height=30, corner_radius=20, fg_color="#00b894", command=show_register_page)
    register_btn.pack(pady=5)

    close_btn = ctk.CTkButton(frame, text="❌ Close App", width=200, height=30, corner_radius=20,
                               fg_color="#d63031", command=app.destroy)
    close_btn.pack(pady=10)

def show_loading_page():
    global current_frame
    if current_frame:
        current_frame.destroy()

    frame = ctk.CTkFrame(app)
    frame.grid(row=0, column=0, sticky="nsew")
    current_frame = frame

    loading_label = ctk.CTkLabel(frame, text="Loading your tracker...", font=ctk.CTkFont(size=22))
    loading_label.pack(expand=True)

    def after_loading():
        load_data()
        time.sleep(1.2)
        show_main_page()

    threading.Thread(target=after_loading).start()

def show_main_page():
    global current_frame
    if current_frame:
        current_frame.destroy()

    scroll = ctk.CTkScrollableFrame(app)
    scroll.grid(row=0, column=0, sticky="nsew")
    current_frame = scroll

    container = ctk.CTkFrame(scroll, fg_color="gray90")
    container.pack(fill="both", expand=True, padx=10, pady=10)
    container.columnconfigure(0, weight=1)
    container.columnconfigure(1, weight=1)

    creditors_frame = ctk.CTkFrame(container)
    creditors_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    title1 = ctk.CTkLabel(creditors_frame, text="💸 Who I Owe", font=ctk.CTkFont(size=20, weight="bold"))
    title1.pack(pady=10)

    creditors = [r for r in records if r['type'] == 'creditor' and r['status'] == 'active']
    for entry in creditors:
        total_paid = sum(p['amount'] for p in entry['payments'])
        remaining = entry['total_debt'] - total_paid
        btn = ctk.CTkButton(
            creditors_frame,
            text=f"{entry['name']} | ₱{remaining:.2f}",
            command=lambda e=entry: show_detail_page(e)
        )
        btn.pack(pady=5, fill="x")

    creditors_paid = [r for r in records if r['type'] == 'creditor' and r['status'] == 'paid']
    if creditors_paid:
        paid_label = ctk.CTkLabel(creditors_frame, text="✅ Fully Paid", font=ctk.CTkFont(size=16, weight="bold"))
        paid_label.pack(pady=(10, 5))
        for entry in creditors_paid:
            btn = ctk.CTkButton(creditors_frame, text=f"{entry['name']} | ₱0.00",
                                command=lambda e=entry: show_detail_page(e))
            btn.pack(pady=2, fill="x")

    add_c_btn = ctk.CTkButton(creditors_frame, text="➕ Add Creditor", fg_color="#0984e3",
                               command=lambda: show_add_entry_page('creditor'))
    add_c_btn.pack(pady=20)

    debtors_frame = ctk.CTkFrame(container)
    debtors_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    title2 = ctk.CTkLabel(debtors_frame, text="📥 Who Owes Me", font=ctk.CTkFont(size=20, weight="bold"))
    title2.pack(pady=10)

    debtors = [r for r in records if r['type'] == 'debtor' and r['status'] == 'active']
    for entry in debtors:
        total_paid = sum(p['amount'] for p in entry['payments'])
        remaining = entry['total_debt'] - total_paid
        btn = ctk.CTkButton(
            debtors_frame,
            text=f"{entry['name']} | ₱{remaining:.2f}",
            command=lambda e=entry: show_detail_page(e)
        )
        btn.pack(pady=5, fill="x")

    debtors_paid = [r for r in records if r['type'] == 'debtor' and r['status'] == 'paid']
    if debtors_paid:
        paid_label = ctk.CTkLabel(debtors_frame, text="✅ Fully Paid", font=ctk.CTkFont(size=16, weight="bold"))
        paid_label.pack(pady=(10, 5))
        for entry in debtors_paid:
            btn = ctk.CTkButton(debtors_frame, text=f"{entry['name']} | ₱0.00",
                                command=lambda e=entry: show_detail_page(e))
            btn.pack(pady=2, fill="x")

    add_d_btn = ctk.CTkButton(debtors_frame, text="➕ Add Debtor", fg_color="#00b894",
                               command=lambda: show_add_entry_page('debtor'))
    add_d_btn.pack(pady=20)

    logout_btn = ctk.CTkButton(scroll, text="Logout", fg_color="#d63031", command=show_login_page)
    logout_btn.pack(pady=10)

# For detail page and add entry, same pattern.
# If you want the **rest**, say **“continue”** and I’ll send it all ready-to-run!
def show_add_entry_page(entry_type):
    global current_frame
    if current_frame:
        current_frame.destroy()

    frame = ctk.CTkFrame(app)
    frame.grid(row=0, column=0, sticky="nsew")
    current_frame = frame

    title = ctk.CTkLabel(frame, text=f"➕ Add {'Creditor' if entry_type == 'creditor' else 'Debtor'}",
                         font=ctk.CTkFont(size=24, weight="bold"))
    title.pack(pady=20)

    name_entry = ctk.CTkEntry(frame, placeholder_text="Name", width=400)
    name_entry.pack(pady=10)

    purpose_entry = ctk.CTkEntry(frame, placeholder_text="Purpose", width=400)
    purpose_entry.pack(pady=10)

    total_entry = ctk.CTkEntry(frame, placeholder_text="Total Amount", width=400)
    total_entry.pack(pady=10)

    def add_entry():
        name = name_entry.get().strip()
        purpose = purpose_entry.get().strip()
        try:
            total = float(total_entry.get().strip())
        except:
            return
        records.append({
            "name": name,
            "purpose": purpose,
            "total_debt": total,
            "payments": [],
            "debts": [],
            "status": "active",
            "type": entry_type,
            "username": current_user  # Add this line
        })
        save_all_data()
        show_main_page()

    save_btn = ctk.CTkButton(frame, text="Save", fg_color="#00b894", command=add_entry)
    save_btn.pack(pady=10)

    cancel_btn = ctk.CTkButton(frame, text="Cancel", fg_color="#636e72", command=show_main_page)
    cancel_btn.pack(pady=5)


def show_detail_page(entry):
    global current_frame
    if current_frame:
        current_frame.destroy()

    scroll = ctk.CTkScrollableFrame(app)
    scroll.grid(row=0, column=0, sticky="nsew")
    current_frame = scroll

    container = ctk.CTkFrame(scroll, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=20, pady=20)

    title = ctk.CTkLabel(
        container,
        text=f"{entry['name']}",
        font=ctk.CTkFont(size=26, weight="bold"),
        fg_color="#00b894",
        corner_radius=10,
        height=50,
        anchor="center"
    )
    title.pack(pady=(10, 5), fill="x")

    purpose = ctk.CTkLabel(container, text=f"Purpose: {entry['purpose']}",
                           font=ctk.CTkFont(size=16))
    purpose.pack(pady=(0, 15))

    total_paid = sum(p['amount'] for p in entry['payments'])
    total_debts = sum(d['amount'] for d in entry['debts'])
    remaining = entry['total_debt'] - total_paid

    info = ctk.CTkLabel(
        container,
        text=f"💵 Total Debt: ₱{entry['total_debt']:.2f}\n"
             f"➕ Added Debts: ₱{total_debts:.2f}\n"
             f"✅ Total Paid: ₱{total_paid:.2f}\n"
             f"🧾 Remaining: ₱{remaining:.2f}",
        font=ctk.CTkFont(size=18)
    )
    info.pack(pady=10)

    history_frame = ctk.CTkFrame(container, fg_color="transparent")
    history_frame.pack(pady=(20, 5))

    history = ctk.CTkLabel(history_frame, text="📜 Payment History",
                           font=ctk.CTkFont(size=18, weight="bold"))
    history.pack()

    if entry['payments']:
        for p in entry['payments']:
            line = ctk.CTkLabel(history_frame, text=f"• {p['date']} — ₱{p['amount']:.2f}")
            line.pack()
    else:
        ctk.CTkLabel(history_frame, text="No payments yet.").pack()

    if entry['debts']:
        debt_title = ctk.CTkLabel(history_frame, text="💳 Debt History",
                                    font=ctk.CTkFont(size=18, weight="bold"))
        debt_title.pack(pady=(20, 5))
        for d in entry['debts']:
            line = ctk.CTkLabel(history_frame, text=f"• {d['date']} — ₱{d['amount']:.2f} ({d['purpose']})")
            line.pack()

    form_frame = ctk.CTkFrame(container, fg_color="transparent")
    form_frame.pack_forget()

    calendar_frame = ctk.CTkFrame(container)
    calendar = Calendar(calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
    calendar.pack(pady=5)

    def pick_date(target_entry):
        calendar_frame.pack(pady=10)
        def select():
            target_entry.delete(0, 'end')
            target_entry.insert(0, calendar.get_date())
            calendar_frame.pack_forget()
        ctk.CTkButton(calendar_frame, text="📅 Select Date", command=select).pack(pady=5)

    def clear_form():
        for widget in form_frame.winfo_children():
            widget.destroy()
        form_frame.pack_forget()
        calendar_frame.pack_forget()

    def show_payment_form():
        clear_form()
        form_frame.pack(pady=10)
        pay_amt = ctk.CTkEntry(form_frame, placeholder_text="Payment Amount (₱)", width=300)
        pay_amt.pack(pady=5)
        pay_date = ctk.CTkEntry(form_frame, placeholder_text="Payment Date", width=300)
        pay_date.pack(pady=5)
        ctk.CTkButton(form_frame, text="📅 Pick Date", command=lambda: pick_date(pay_date)).pack(pady=5)
        ctk.CTkButton(form_frame, text="💾 Save Payment", fg_color="#00b894",
                      command=lambda: save_payment(pay_amt, pay_date)).pack(pady=5)
        ctk.CTkButton(form_frame, text="Cancel", fg_color="#636e72",
                      command=clear_form).pack(pady=5)

    def save_payment(pay_amt, pay_date):
        try:
            amount = float(pay_amt.get())
            date = pay_date.get().strip()
            if not date:
                return
            total_paid = sum(p['amount'] for p in entry['payments'])
            remaining = entry['total_debt'] - total_paid
            if amount > remaining:
                pay_amt.configure(placeholder_text="Cannot exceed remaining!")
                msg = getattr(form_frame, "msg_label", None)
                if not msg:
                    form_frame.msg_label = ctk.CTkLabel(form_frame, text="❌ Payment cannot exceed remaining balance.", text_color="red")
                    form_frame.msg_label.pack()
                else:
                    msg.configure(text="❌ Payment cannot exceed remaining balance.")
                return
            msg = getattr(form_frame, "msg_label", None)
            if msg:
                msg.destroy()
                del form_frame.msg_label
            entry['payments'].append({"date": date, "amount": amount})
            save_all_data()
            show_detail_page(entry)
        except:
            pass

    def show_debt_form():
        clear_form()
        form_frame.pack(pady=10)
        debt_amt = ctk.CTkEntry(form_frame, placeholder_text="Debt Amount (₱)", width=300)
        debt_amt.pack(pady=5)
        debt_purpose = ctk.CTkEntry(form_frame, placeholder_text="Debt Purpose", width=300)
        debt_purpose.pack(pady=5)
        debt_date = ctk.CTkEntry(form_frame, placeholder_text="Debt Date", width=300)
        debt_date.pack(pady=5)
        ctk.CTkButton(form_frame, text="📅 Pick Date", command=lambda: pick_date(debt_date)).pack(pady=5)
        ctk.CTkButton(form_frame, text="💾 Save Debt", fg_color="#0984e3",
                      command=lambda: save_debt(debt_amt, debt_purpose, debt_date)).pack(pady=5)
        ctk.CTkButton(form_frame, text="Cancel", fg_color="#636e72",
                      command=clear_form).pack(pady=5)

    def save_debt(debt_amt, debt_purpose, debt_date):
        try:
            amount = float(debt_amt.get())
            purpose = debt_purpose.get().strip()
            date = debt_date.get().strip()
            if not date or not purpose:
                return
            entry['debts'].append({"date": date, "amount": amount, "purpose": purpose})
            entry['total_debt'] += amount
            save_all_data()
            show_detail_page(entry)
        except:
            pass

    def show_edit_form(entry):
        clear_form()
        form_frame.pack(pady=10)

        name_label = ctk.CTkLabel(form_frame, text="Name:", anchor="w")
        name_label.pack(pady=(0, 2), fill="x")
        name_entry = ctk.CTkEntry(form_frame, width=300)
        name_entry.insert(0, entry['name'])
        name_entry.pack(pady=5)

        purpose_label = ctk.CTkLabel(form_frame, text="Purpose:", anchor="w")
        purpose_label.pack(pady=(10, 2), fill="x")
        purpose_entry = ctk.CTkEntry(form_frame, width=300)
        purpose_entry.insert(0, entry['purpose'])
        purpose_entry.pack(pady=5)

        status_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        status_label.pack(pady=5)

        def save_edit():
            new_name = name_entry.get().strip()
            new_purpose = purpose_entry.get().strip()
            if not new_name or not new_purpose:
                status_label.configure(text="❌ Both fields are required.")
                return
            entry['name'] = new_name
            entry['purpose'] = new_purpose
            save_all_data()
            show_detail_page(entry)

        ctk.CTkButton(form_frame, text="💾 Save Changes", fg_color="#00b894", command=save_edit).pack(pady=10)
        ctk.CTkButton(form_frame, text="Cancel", fg_color="#636e72", command=clear_form).pack(pady=5)

    action_buttons = ctk.CTkFrame(container, fg_color="transparent")
    action_buttons.pack(pady=15)

    ctk.CTkButton(action_buttons, text="✏️ Edit", fg_color="#fdcb6e",
                  command=lambda: show_edit_form(entry)).pack(side="left", padx=10)

    if entry['status'] != 'paid' and remaining > 0:
        ctk.CTkButton(action_buttons, text="➕ Add Payment", width=200, command=show_payment_form).pack(side="left", padx=10)
        ctk.CTkButton(action_buttons, text="➕ Add More Debt", width=200, command=show_debt_form).pack(side="left", padx=10)

    if remaining <= 0 and entry['status'] != 'paid':
        ctk.CTkButton(container, text="✅ Mark as Fully Paid", fg_color="#6c5ce7",
                      command=lambda: mark_fully_paid(entry)).pack(pady=10)

    bottom_actions = ctk.CTkFrame(container, fg_color="transparent")
    bottom_actions.pack(pady=20)

    def show_delete_confirmation():
        for widget in bottom_actions.winfo_children():
            widget.destroy()
        ctk.CTkLabel(bottom_actions, text="Are you sure you want to delete?", text_color="#d63031").pack(side="left", padx=10)
        ctk.CTkButton(bottom_actions, text="Yes, Delete", fg_color="#d63031",
                      command=lambda: delete_entry(entry)).pack(side="left", padx=10)
        ctk.CTkButton(bottom_actions, text="Cancel", fg_color="#636e72",
                      command=reset_bottom_actions).pack(side="left", padx=10)

    def reset_bottom_actions():
        for widget in bottom_actions.winfo_children():
            widget.destroy()
        ctk.CTkButton(bottom_actions, text="🗑️ Delete", fg_color="#d63031",
                      command=show_delete_confirmation).pack(side="left", padx=10)
        ctk.CTkButton(bottom_actions, text="⬅️ Back", fg_color="#636e72",
                      command=show_main_page).pack(side="left", padx=10)

    reset_bottom_actions()


def mark_fully_paid(entry):
    entry['status'] = 'paid'
    save_all_data()
    show_main_page()


def delete_entry(entry):
    records.remove(entry)
    save_all_data()
    show_main_page()


def show_registration_page():
    global current_frame
    if current_frame:
        current_frame.destroy()
    frame = ctk.CTkFrame(app)
    frame.grid(row=0, column=0, sticky="nsew")
    current_frame = frame

    ctk.CTkLabel(frame, text="Create Account", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
    user_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=300)
    user_entry.pack(pady=10)
    pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300)
    pass_entry.pack(pady=10)
    status = ctk.CTkLabel(frame, text="")
    status.pack(pady=10)

    def register():
        username = user_entry.get().strip()
        password = pass_entry.get().strip()
        if not username or not password:
            status.configure(text="❌ Please fill all fields.", text_color="red")
            return
        users = load_users()
        if any(u['username'] == username for u in users):
            status.configure(text="❌ Username already exists.", text_color="red")
            return
        save_user(username, password)
        status.configure(text="✅ Account created! Please login.", text_color="green")
        frame.after(1200, show_login_page)

    ctk.CTkButton(frame, text="Register", fg_color="#00b894", command=register).pack(pady=10)
    ctk.CTkButton(frame, text="Back to Login", fg_color="#636e72", command=show_login_page).pack(pady=5)


show_login_page()
app.mainloop()
