import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
import csv
import os
from datetime import datetime, timedelta
import hashlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import random
import webbrowser




# Set appearance mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class UtangTracker:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Utang Tracker")
        self.root.geometry("1200x800")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.init_csv_files()
        
        # Current user
        self.current_user = None
        
        # Current view state
        self.current_view = "login"
        self.selected_person_data = None
        self.selected_debt = None
        
        # Matplotlib figure and canvas
        self.fig = None
        self.canvas = None
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Start with login screen
        self.show_login_screen()
        
    def init_csv_files(self):
        """Initialize CSV files if they don't exist"""
        if not os.path.exists("users.csv"):
            with open("users.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["username", "password_hash", "registration_date"])
        
        if not os.path.exists("debt_data.csv"):
            with open("debt_data.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["user", "full_name", "amount", "relationship", "interest_rate", 
                               "date_added", "due_date", "notes", "status", "debt_id"])
        
        if not os.path.exists("payments.csv"):
            with open("payments.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["debt_id", "payment_amount", "payment_date"])
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def clear_main_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login screen with option to switch to register"""
        self.current_view = "login"
        self.clear_main_frame()
        
        title_label = ctk.CTkLabel(self.main_frame, text="Utang Tracker", 
                                 font=ctk.CTkFont(size=32, weight="bold"))
        title_label.pack(pady=30)
        
        author_label = ctk.CTkLabel(self.main_frame, text="By John Allen Esteleydes", 
                                  font=ctk.CTkFont(size=16, slant="italic"), 
                                  text_color="#D3D3D3")
        author_label.pack(pady=2)
        
        self.login_frame = ctk.CTkFrame(self.main_frame)
        self.login_frame.pack(pady=20, padx=100, fill="x")
        
        ctk.CTkLabel(self.login_frame, text="Username:", font=ctk.CTkFont(size=16)).pack(pady=10)
        self.login_username_entry = ctk.CTkEntry(self.login_frame, width=300, height=40)
        self.login_username_entry.pack(pady=5)
        
        ctk.CTkLabel(self.login_frame, text="Password:", font=ctk.CTkFont(size=16)).pack(pady=10)
        self.login_password_entry = ctk.CTkEntry(self.login_frame, width=300, height=40, show="*")
        self.login_password_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(self.login_frame)
        button_frame.pack(pady=20)
        
        login_btn = ctk.CTkButton(button_frame, text="Login", command=self.login, 
                                width=140, height=40)
        login_btn.pack(side="left", padx=10)
        
        create_account_btn = ctk.CTkButton(button_frame, text="Create Account", 
                                         command=self.show_register_screen, 
                                         width=140, height=40)
        create_account_btn.pack(side="left", padx=10)
    
    def show_register_screen(self):
        """Display register screen"""
        self.current_view = "register"
        self.clear_main_frame()
        
        title_label = ctk.CTkLabel(self.main_frame, text="Utang Tracker - Register", 
                                 font=ctk.CTkFont(size=32, weight="bold"))
        title_label.pack(pady=30)
        
        author_label = ctk.CTkLabel(self.main_frame, text="By John Allen Esteleydes", 
                                  font=ctk.CTkFont(size=16, slant="italic"), 
                                  text_color="#D3D3D3")
        author_label.pack(pady=2)
        
        self.register_frame = ctk.CTkFrame(self.main_frame)
        self.register_frame.pack(pady=20, padx=100, fill="x")
        
        ctk.CTkLabel(self.register_frame, text="Username:", font=ctk.CTkFont(size=16)).pack(pady=10)
        self.register_username_entry = ctk.CTkEntry(self.register_frame, width=300, height=40)
        self.register_username_entry.pack(pady=5)
        
        ctk.CTkLabel(self.register_frame, text="Password:", font=ctk.CTkFont(size=16)).pack(pady=10)
        self.register_password_entry = ctk.CTkEntry(self.register_frame, width=300, height=40, show="*")
        self.register_password_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(self.register_frame)
        button_frame.pack(pady=20)
        
        register_btn = ctk.CTkButton(button_frame, text="Register", command=self.register, 
                                   width=140, height=40)
        register_btn.pack(side="left", padx=10)
        
        back_btn = ctk.CTkButton(button_frame, text="Back to Login", 
                               command=self.show_login_screen, 
                               width=140, height=40)
        back_btn.pack(side="left", padx=10)
    
    def login(self):
        """Handle user login"""
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        with open("users.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == username and row["password_hash"] == self.hash_password(password):
                    self.current_user = username
                    self.show_dashboard()
                    return
        
        messagebox.showerror("Error", "Invalid username or password")
    
    def register(self):
        """Handle user registration"""
        username = self.register_username_entry.get().strip()
        password = self.register_password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        with open("users.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == username:
                    messagebox.showerror("Error", "Username already exists")
                    return
        
        with open("users.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, self.hash_password(password), datetime.now().strftime("%Y-%m-%d")])
        
        messagebox.showinfo("Success", "Registration successful! You can now login.")
        self.show_login_screen()
    
    def show_dashboard(self):
        """Display main dashboard with tabs"""
        self.current_view = "dashboard"
        self.clear_main_frame()

        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        welcome_label = ctk.CTkLabel(header_frame, text=f"Welcome, {self.current_user}!",
                                font=ctk.CTkFont(size=24, weight="bold"))
        welcome_label.pack(side="left", padx=20, pady=15)

        logout_btn = ctk.CTkButton(header_frame, text="Logout", command=self.show_login_screen,
                                width=100, height=35)
        logout_btn.pack(side="right", padx=20, pady=15)

        # Tab view
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_view.add("Debts")
        self.tab_view.add("Analytics")
        self.tab_view.add("Profile")

        # Theme selection dropdown
        def change_theme(choice):
            ctk.set_appearance_mode(choice)

        theme_frame = ctk.CTkFrame(self.tab_view.tab("Debts"))
        theme_frame.pack(side="bottom", anchor="sw", pady=10, padx=10)

        theme_label = ctk.CTkLabel(theme_frame, text="Theme:", font=ctk.CTkFont(size=14))
        theme_label.pack(side="left", padx=5)

        theme_var = ctk.StringVar(value="Dark")
        theme_menu = ctk.CTkOptionMenu(theme_frame, variable=theme_var,
                                    values=["Dark", "Light", "System"],
                                    command=change_theme, width=150, height=35)
        theme_menu.pack(side="left", padx=5)

        # Debts tab content
        button_frame = ctk.CTkFrame(self.tab_view.tab("Debts"))
        button_frame.pack(pady=10)

        add_debt_btn = ctk.CTkButton(button_frame, text="Add New Debt",
                                command=self.show_add_debt_form, width=200, height=40)
        add_debt_btn.pack(side="left", padx=10)

        quick_add_btn = ctk.CTkButton(button_frame, text="Quick Add Debt",
                                command=self.show_quick_add_debt_form, width=200, height=40)
        quick_add_btn.pack(side="left", padx=10)
        
        # Search and filter frame
        filter_frame = ctk.CTkFrame(self.tab_view.tab("Debts"))
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(filter_frame, text="Search Name:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(filter_frame, width=350, height=35)
        self.search_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Relationship:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.filter_relationship_var = ctk.StringVar(value="All")
        relationship_menu = ctk.CTkOptionMenu(filter_frame, variable=self.filter_relationship_var,
                                            values=["All", "Who owes me", "Who I owe"],
                                            width=200, height=35, command=self.load_debts)
        relationship_menu.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Status:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.filter_status_var = ctk.StringVar(value="All")
        status_menu = ctk.CTkOptionMenu(filter_frame, variable=self.filter_status_var,
                                      values=["All", "Overdue", "Pending", "Paid"],
                                      width=200, height=35, command=self.load_debts)
        status_menu.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Min Amount:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.min_amount_entry = ctk.CTkEntry(filter_frame, width=200, height=35)
        self.min_amount_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Max Amount:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.max_amount_entry = ctk.CTkEntry(filter_frame, width=200, height=35)
        self.max_amount_entry.pack(side="left", padx=5)
        
        search_btn = ctk.CTkButton(filter_frame, text="Search", command=self.load_debts, width=200, height=35)
        search_btn.pack(side="left", padx=5)
        
        self.debt_scrollable_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Debts"))
        self.debt_scrollable_frame.pack(fill="both", expand=True, pady=10)
        
        # Analytics tab
        self.analytics_frame = ctk.CTkFrame(self.tab_view.tab("Analytics"))
        self.analytics_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Profile tab
        self.profile_frame = ctk.CTkFrame(self.tab_view.tab("Profile"))
        self.profile_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.show_profile_form()
        
        self.load_debts(self.debt_scrollable_frame)
        self.load_analytics()
    
    '''def show_contact_info(self):
        """Display contact information in a new window or frame"""
        contact_window = ctk.CTkToplevel(self.root)
        contact_window.title("Contact Information")
        contact_window.geometry("400x200")

        contact_frame = ctk.CTkFrame(contact_window)
        contact_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Phone number
        phone_label = ctk.CTkLabel(contact_frame, text="Phone: +1234567890", font=ctk.CTkFont(size=14))
        phone_label.pack(pady=5)

        # Email with hyperlink
        email_label = ctk.CTkLabel(contact_frame, text="Email: chelxiimusic@gmail.com", font=ctk.CTkFont(size=14), text_color="blue", cursor="hand2")
        email_label.pack(pady=5)
        email_label.bind("<Button-1>", lambda e: webbrowser.open("mailto:chelxiimusic@gmail.com"))

        # Facebook link with hyperlink
        facebook_label = ctk.CTkLabel(contact_frame, text="Facebook: John Allen", font=ctk.CTkFont(size=14), text_color="blue", cursor="hand2")
        facebook_label.pack(pady=5)
        facebook_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.facebook.com"))

        # YouTube channel link with hyperlink
        youtube_label = ctk.CTkLabel(contact_frame, text="YouTube: Chelxii Music", font=ctk.CTkFont(size=14), text_color="blue", cursor="hand2")
        youtube_label.pack(pady=5)
        youtube_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.youtube.com/@Chelxiiii"))
    '''

    import webbrowser

    def show_profile_form(self):
        """Show user profile information with option to change password and display contact info"""
        for widget in self.profile_frame.winfo_children():
            widget.destroy()

        # Initialize a flag to track the visibility of contact information
        self.contact_info_visible = False

        title_label = ctk.CTkLabel(self.profile_frame, text="User Profile",
                                font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # Get user information
        registration_date = "Unknown"
        with open("users.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == self.current_user:
                    registration_date = row.get("registration_date", "2024-10-10")
                    break

        # Calculate debt statistics
        consolidated_debts = self.get_consolidated_debts()
        total_debts = sum(1 for p in consolidated_debts["Who owes me"] + consolidated_debts["Who I owe"]
                        for debt in p["debt_history"] if debt["remaining"] > 0)
        total_remaining_who_owes_me = sum(p["remaining"] for p in consolidated_debts["Who owes me"])
        total_remaining_who_i_owe = sum(p["remaining"] for p in consolidated_debts["Who I owe"])

        # Create a frame to align info and button
        content_frame = ctk.CTkFrame(self.profile_frame)
        content_frame.pack(pady=20, padx=20, fill="x")

        # Display user information with aligned text
        info_text = (
            f"{'Username:':<25}{self.current_user}\n"
            f"{'Registration Date:':<25}{registration_date}\n"
            f"{'Total Active Debts:':<25}{total_debts}\n"
            f"{'Total Remaining Balance (Who Owes Me):':<25}₱{total_remaining_who_owes_me:.2f}\n"
            f"{'Total Remaining Balance (Who I Owe):':<25}₱{total_remaining_who_i_owe:.2f}"
        )
        info_label = ctk.CTkLabel(content_frame, text=info_text,
                                font=ctk.CTkFont(size=16, family="Arial"),
                                justify="left")
        info_label.pack(side="left", padx=20)

        # Buttons on the right
        button_frame = ctk.CTkFrame(content_frame)
        button_frame.pack(side="right", padx=20)

        change_password_btn = ctk.CTkButton(button_frame, text="Change Password",
                                            command=self.show_change_password_form,
                                            width=200, height=40)
        change_password_btn.pack(pady=10)

        # About section
        def toggle_contact_info():
            if hasattr(self, 'contact_info_visible'):
                if self.contact_info_visible:
                    # Hide contact information
                    for widget in self.profile_frame.winfo_children():
                        if isinstance(widget, ctk.CTkLabel) and "Contact Information" in widget.cget("text"):
                            widget.destroy()
                        if isinstance(widget, ctk.CTkLabel) and "YouTube" in widget.cget("text"):
                            widget.destroy()
                    self.contact_info_visible = False
                else:
                    # Show contact information
                    contact_info = (
                        "Contact Information:\n\n"
                        "Email: chelxiimusic@gmail.com\n"
                    )
                    contact_label = ctk.CTkLabel(self.profile_frame, text=contact_info,
                                                font=ctk.CTkFont(size=14, family="Arial", weight="bold"),
                                                justify="left")
                    contact_label.pack(pady=10)
                    # YouTube link
                    youtube_label = ctk.CTkLabel(self.profile_frame, text="YouTube: Chelxii Music",
                                                font=ctk.CTkFont(size=14, family="Arial", weight="bold"),
                                                text_color="white", cursor="hand2")
                    youtube_label.pack()
                    youtube_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.youtube.com/@Chelxiiii"))
                    self.contact_info_visible = True
        about_label = ctk.CTkLabel(self.profile_frame, text="About", font=ctk.CTkFont(size=16, family="Arial", weight="bold"),
                                    text_color="white", cursor="hand2")
        about_label.pack(side="bottom", pady=50)
        about_label.bind("<Button-1>", lambda e: toggle_contact_info()) 

        #mini_game_btn = ctk.CTkButton(button_frame, text="Play Mini-Game",
        #                             command=self.show_mini_game,
        #                             width=200, height=40)
        #mini_game_btn.pack(pady=10)
    '''''
    def show_mini_game(self):
        """Display the mini-game screen"""
        self.current_view = "mini_game"
        self.clear_main_frame()

        title_label = ctk.CTkLabel(self.main_frame, text="Number Guessing Game",
                                font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        self.game_frame = ctk.CTkFrame(self.main_frame)
        self.game_frame.pack(pady=20, padx=100, fill="x")

        self.game_instructions = ctk.CTkLabel(self.game_frame, text="Guess a number between 1 and 100",
                                            font=ctk.CTkFont(size=14))
        self.game_instructions.pack(pady=10)

        self.game_entry = ctk.CTkEntry(self.game_frame, width=200, height=35)
        self.game_entry.pack(pady=10)

        self.game_result = ctk.CTkLabel(self.game_frame, text="", font=ctk.CTkFont(size=14))
        self.game_result.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self.game_frame)
        self.button_frame.pack(pady=20)

        self.guess_btn = ctk.CTkButton(self.button_frame, text="Guess", command=self.check_guess,
                                    width=120, height=40)
        self.guess_btn.pack(side="left", padx=10)

        self.back_btn = ctk.CTkButton(self.button_frame, text="Back to Profile", command=self.show_profile_form,
                                width=120, height=40)
        self.back_btn.pack(side="left", padx=10)

        self.secret_number = random.randint(1, 100)
        self.attempts = 0

    def check_guess(self):
        """Check the user's guess in the mini-game"""
        try:
            guess = int(self.game_entry.get().strip())
        except ValueError:
            self.game_result.configure(text="Please enter a valid number.")
            return

        self.attempts += 1

        if guess < self.secret_number:
            self.game_result.configure(text="Too low! Try again.")
        elif guess > self.secret_number:
            self.game_result.configure(text="Too high! Try again.")
        else:
            self.game_result.configure(text=f"Congratulations! You guessed the number in {self.attempts} attempts.")
            self.game_entry.pack_forget()

            # Remove the guess button
            self.guess_btn.pack_forget()

            # Create a frame for the buttons if it doesn't exist
            if not hasattr(self, 'end_button_frame'):
                self.end_button_frame = ctk.CTkFrame(self.game_frame)
                self.end_button_frame.pack(pady=20)

            # Add the Play Again button
            play_again_btn = ctk.CTkButton(self.end_button_frame, text="Play Again", command=self.reset_game,
                                        width=120, height=40)
            play_again_btn.pack(side="left", padx=10)

            # Add the Back to Profile button
            back_btn = ctk.CTkButton(self.end_button_frame, text="Back to Profile", command=self.show_profile_form,
                                    width=120, height=40)
            back_btn.pack(side="left", padx=10)

    def reset_game(self):
        """Reset the mini-game"""
        # Remove the end game buttons if they exist
        if hasattr(self, 'end_button_frame'):
            self.end_button_frame.destroy()

        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.game_result.configure(text="")
        self.game_entry.delete(0, 'end')
        self.game_entry.pack(pady=10)

        # Show the guess button again
        self.guess_btn = ctk.CTkButton(self.button_frame, text="Guess", command=self.check_guess,
                                    width=120, height=40)
        self.guess_btn.pack(side="left", padx=10)
    '''


  
    def show_change_password_form(self):
        """Show password change form"""
        for widget in self.profile_frame.winfo_children():
            widget.destroy()
        
        title_label = ctk.CTkLabel(self.profile_frame, text="Change Password", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        form_frame = ctk.CTkFrame(self.profile_frame)
        form_frame.pack(pady=20, padx=100, fill="x")
        
        ctk.CTkLabel(form_frame, text="Current Password:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.current_password_entry = ctk.CTkEntry(form_frame, width=400, height=35, show="*")
        self.current_password_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="New Password:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.new_password_entry = ctk.CTkEntry(form_frame, width=400, height=35, show="*")
        self.new_password_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Confirm New Password:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.confirm_password_entry = ctk.CTkEntry(form_frame, width=400, height=35, show="*")
        self.confirm_password_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(button_frame, text="Save Changes", command=self.update_password,
                               width=120, height=40)
        save_btn.pack(side="left", padx=10)
        
        back_btn = ctk.CTkButton(button_frame, text="Back", command=self.show_profile_form,
                               width=120, height=40)
        back_btn.pack(side="left", padx=10)
    
    def update_password(self):
        """Update user's password in users.csv with confirmation"""
        current_password = self.current_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not all([current_password, new_password, confirm_password]):
            messagebox.showerror("Error", "Please fill all password fields")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New password and confirmation do not match")
            return
        
        # Verify current password
        with open("users.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == self.current_user:
                    if row["password_hash"] != self.hash_password(current_password):
                        messagebox.showerror("Error", "Current password is incorrect")
                        return
                    break
            else:
                messagebox.showerror("Error", "User not found")
                return
        
        # Confirm password change
        if not messagebox.askyesno("Confirm Password Change", "Are you sure you want to change your password?"):
            return
        
        # Update password
        users = []
        with open("users.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == self.current_user:
                    users.append({
                        "username": self.current_user,
                        "password_hash": self.hash_password(new_password),
                        "registration_date": row.get("registration_date", "2025-07-19")
                    })
                else:
                    users.append(row)
        
        with open("users.csv", "w", newline="") as file:
            fieldnames = ["username", "password_hash", "registration_date"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)
        
        messagebox.showinfo("Success", "Password updated successfully!")
        self.show_profile_form()
    
    def get_debt_status(self, debt):
        """Determine the status of a debt based on due date and remaining balance"""
        if debt["remaining"] == 0:
            return "Paid"
        if debt["due_date"] == "N/A":
            return "Pending"
        try:
            due_date = datetime.strptime(debt["due_date"], "%Y-%m-%d")
            today = datetime.now()
            if due_date < today:
                return "Overdue"
            return "Pending"
        except ValueError:
            return "Pending"
    
    def load_debts(self, parent_frame=None):
        """Load and display debt entries with filtering"""
        if parent_frame is None:
            parent_frame = self.debt_scrollable_frame
        
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        columns_frame = ctk.CTkFrame(parent_frame)
        columns_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        left_frame = ctk.CTkFrame(columns_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        owe_me_label = ctk.CTkLabel(left_frame, text="Who Owes Me", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        owe_me_label.pack(pady=10)
        
        right_frame = ctk.CTkFrame(columns_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        i_owe_label = ctk.CTkLabel(right_frame, text="Who I Owe", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        i_owe_label.pack(pady=10)
        
        # Apply filters
        search_name = self.search_entry.get().strip().lower() if hasattr(self, 'search_entry') else ""
        relationship_filter = self.filter_relationship_var.get() if hasattr(self, 'filter_relationship_var') else "All"
        status_filter = self.filter_status_var.get() if hasattr(self, 'filter_status_var') else "All"
        min_amount = self.min_amount_entry.get().strip() if hasattr(self, 'min_amount_entry') else ""
        max_amount = self.max_amount_entry.get().strip() if hasattr(self, 'max_amount_entry') else ""
        
        try:
            min_amount = float(min_amount) if min_amount else float('-inf')
            max_amount = float(max_amount) if max_amount else float('inf')
        except ValueError:
            min_amount = float('-inf')
            max_amount = float('inf')
        
        consolidated_debts = self.get_consolidated_debts()
        
        for person_data in consolidated_debts["Who owes me"]:
            if self.filter_debt(person_data, search_name, relationship_filter, status_filter, min_amount, max_amount):
                self.create_consolidated_debt_entry(left_frame, person_data)
        
        for person_data in consolidated_debts["Who I owe"]:
            if self.filter_debt(person_data, search_name, relationship_filter, status_filter, min_amount, max_amount):
                self.create_consolidated_debt_entry(right_frame, person_data)
    
    def filter_debt(self, person_data, search_name, relationship_filter, status_filter, min_amount, max_amount):
        """Filter debts based on search, relationship, status, and amount criteria"""
        if search_name and search_name not in person_data["full_name"].lower():
            return False
        if relationship_filter != "All" and person_data["relationship"] != relationship_filter:
            return False
        if person_data["remaining"] < min_amount or person_data["remaining"] > max_amount:
            return False
        if status_filter != "All":
            # Check if any debt in the person's history matches the status filter
            has_matching_status = False
            for debt in person_data["debt_history"]:
                debt_status = self.get_debt_status(debt)
                if debt_status == status_filter:
                    has_matching_status = True
                    break
            if not has_matching_status:
                return False
        return True
    
    def load_analytics(self):
        """Load analytics visualizations and statistics with date range filtering"""
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        # Clear previous matplotlib figure
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.canvas = None

        # Date range filter
        filter_frame = ctk.CTkFrame(self.analytics_frame)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(filter_frame, text="Start Date:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.analytics_start_date_entry = ctk.CTkEntry(filter_frame, width=150, height=35, placeholder_text="YYYY-MM-DD")
        self.analytics_start_date_entry.pack(side="left", padx=5)

        start_cal_button = ctk.CTkButton(filter_frame, text="📅", width=50, height=35,
                                    command=lambda: self.toggle_analytics_calendar("start"))
        start_cal_button.pack(side="left", padx=5)

        self.analytics_start_cal = Calendar(filter_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.analytics_start_cal.pack_forget()

        ctk.CTkLabel(filter_frame, text="End Date:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.analytics_end_date_entry = ctk.CTkEntry(filter_frame, width=150, height=35, placeholder_text="YYYY-MM-DD")
        self.analytics_end_date_entry.pack(side="left", padx=5)

        end_cal_button = ctk.CTkButton(filter_frame, text="📅", width=50, height=35,
                                command=lambda: self.toggle_analytics_calendar("end"))
        end_cal_button.pack(side="left", padx=5)

        self.analytics_end_cal = Calendar(filter_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.analytics_end_cal.pack_forget()

        apply_filter_btn = ctk.CTkButton(filter_frame, text="Apply Filter", command=self.load_analytics,
                                    width=100, height=35)
        apply_filter_btn.pack(side="left", padx=5)

        # Bind calendar selection events
        self.analytics_start_cal.bind("<<CalendarSelected>>",
                                    lambda e: self.update_date(self.analytics_start_date_entry, self.analytics_start_cal))
        self.analytics_end_cal.bind("<<CalendarSelected>>",
                                lambda e: self.update_date(self.analytics_end_date_entry, self.analytics_end_cal))

        # Get date range
        start_date = self.analytics_start_date_entry.get().strip()
        end_date = self.analytics_end_date_entry.get().strip()
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.min
            end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.max
        except ValueError:
            start_date = datetime.min
            end_date = datetime.max

        consolidated_debts = self.get_consolidated_debts(start_date, end_date)

        # Summary statistics
        total_owed = sum(p["total_owed"] for p in consolidated_debts["Who owes me"] + consolidated_debts["Who I owe"])
        total_paid = sum(p["total_paid"] for p in consolidated_debts["Who owes me"] + consolidated_debts["Who I owe"])
        total_remaining = sum(p["remaining"] for p in consolidated_debts["Who owes me"] + consolidated_debts["Who I owe"])
        active_debts = sum(1 for p in consolidated_debts["Who owes me"] + consolidated_debts["Who I owe"]
                        for debt in p["debt_history"] if debt["remaining"] > 0)
        interest_rates = [debt["interest_rate"] for p in consolidated_debts["Who owes me"] + consolidated_debts["Who I owe"]
                        for debt in p["debt_history"] if debt["remaining"] > 0]
        avg_interest = sum(interest_rates) / len(interest_rates) if interest_rates else 0

        # Separate amounts for "Who owes me" and "Who I owe"
        total_owed_who_owes_me = sum(p["total_owed"] for p in consolidated_debts["Who owes me"])
        total_owed_who_i_owe = sum(p["total_owed"] for p in consolidated_debts["Who I owe"])
        total_paid_who_owes_me = sum(p["total_paid"] for p in consolidated_debts["Who owes me"])
        total_paid_who_i_owe = sum(p["total_paid"] for p in consolidated_debts["Who I owe"])
        total_remaining_who_owes_me = sum(p["remaining"] for p in consolidated_debts["Who owes me"])
        total_remaining_who_i_owe = sum(p["remaining"] for p in consolidated_debts["Who I owe"])

        stats_text = f"""
    Summary Statistics:
    Total Owed (Who Owes Me): ₱{total_owed_who_owes_me:.2f}
    Total Owed (Who I Owe): ₱{total_owed_who_i_owe:.2f}
    Total Paid (Who Owes Me): ₱{total_paid_who_owes_me:.2f}
    Total Paid (Who I Owe): ₱{total_paid_who_i_owe:.2f}
    Total Remaining (Who Owes Me): ₱{total_remaining_who_owes_me:.2f}
    Total Remaining (Who I Owe): ₱{total_remaining_who_i_owe:.2f}
    Active Debts: {active_debts}
    Average Interest Rate: {avg_interest:.2f}%
    """
        stats_label = ctk.CTkLabel(self.analytics_frame, text=stats_text.strip(),
                                font=ctk.CTkFont(size=14), justify="left")
        stats_label.pack(pady=10, padx=20, anchor="w")

        # Create figure with three subplots
        self.fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4))

        # Pie chart: Debt distribution
        owe_me_total = sum(p["remaining"] for p in consolidated_debts["Who owes me"])
        i_owe_total = sum(p["remaining"] for p in consolidated_debts["Who I owe"])
        labels = ["Who Owes Me", "Who I Owe"]
        sizes = [owe_me_total, i_owe_total]
        colors = ["#4CAF50", "#FF5733"]
        if sum(sizes) > 0:
            ax1.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
            ax1.set_title("Debt Distribution")
        else:
            ax1.text(0.5, 0.5, "No Data", ha="center", va="center")

        # Bar chart: Remaining debt per person
        names = [p["full_name"] for p in consolidated_debts["Who owes me"] + consolidated_debts["Who I owe"]]
        amounts = [p["remaining"] for p in consolidated_debts["Who owes me"] + consolidated_debts["Who I owe"]]
        if amounts:
            ax2.bar(range(len(names)), amounts, color="#2196F3")
            ax2.set_xticks(range(len(names)))
            ax2.set_xticklabels(names, rotation=45, ha="right")
            ax2.set_title("Remaining Debt per Person")
            ax2.set_ylabel("Amount (₱)")
        else:
            ax2.text(0.5, 0.5, "No Data", ha="center", va="center")

        # Line plot: Payment history over time
        payments = self.get_payment_history_in_range(start_date, end_date)
        if payments:
            # Aggregate payments by month
            monthly_payments = {}
            for payment in payments:
                payment_date = datetime.strptime(payment["payment_date"], "%Y-%m-%d")
                month_key = payment_date.strftime("%Y-%m")
                monthly_payments[month_key] = monthly_payments.get(month_key, 0) + float(payment["payment_amount"])
            dates = [datetime.strptime(month, "%Y-%m") for month in sorted(monthly_payments.keys())]
            amounts = [monthly_payments[month] for month in sorted(monthly_payments.keys())]
            ax3.plot(dates, amounts, marker='o', color="#FF9800")
            ax3.set_title("Payment History")
            ax3.set_ylabel("Payment Amount (₱)")
            ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            ax3.xaxis.set_major_locator(mdates.MonthLocator())
            ax3.tick_params(axis='x', rotation=45)
        else:
            ax3.text(0.5, 0.5, "No Payment Data", ha="center", va="center")

        plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.analytics_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=20)

   
    def toggle_analytics_calendar(self, cal_type):
        """Toggle visibility of analytics calendar widget"""
        if cal_type == "start":
            calendar = self.analytics_start_cal
            other_calendar = self.analytics_end_cal
        else:
            calendar = self.analytics_end_cal
            other_calendar = self.analytics_start_cal

        if calendar.winfo_ismapped():
            calendar.pack_forget()
        else:
            if other_calendar.winfo_ismapped():
                other_calendar.pack_forget()
            calendar.pack(pady=5)



    
    def get_consolidated_debts(self, start_date=None, end_date=None):
        """Get debts consolidated by person and relationship within date range"""
        debts = self.get_user_debts()
        consolidated = {"Who owes me": {}, "Who I owe": {}}
        
        for debt in debts:
            debt_date = datetime.strptime(debt["date_added"], "%Y-%m-%d")
            if start_date and debt_date < start_date:
                continue
            if end_date and debt_date > end_date:
                continue
                
            relationship = debt["relationship"]
            name = debt["full_name"]
            
            if name not in consolidated[relationship]:
                consolidated[relationship][name] = {
                    "full_name": name,
                    "relationship": relationship,
                    "debt_history": [],
                    "total_amount": 0,
                    "total_paid": 0,
                    "total_owed": 0,
                    "remaining": 0,
                    "latest_due_date": debt["due_date"] if debt["due_date"] != "N/A" else "N/A"
                }
            
            debt_payments = self.get_total_payments(debt["debt_id"], start_date, end_date)
            debt_owed = float(debt["amount"]) * (1 + float(debt["interest_rate"]) / 100)
            debt_remaining = debt_owed - debt_payments
            
            consolidated[relationship][name]["debt_history"].append({
                "debt_id": debt["debt_id"],
                "amount": float(debt["amount"]),
                "interest_rate": float(debt["interest_rate"]),
                "date_added": debt["date_added"],
                "due_date": debt["due_date"],
                "notes": debt["notes"],
                "payments": debt_payments,
                "owed": debt_owed,
                "remaining": debt_remaining
            })
            
            consolidated[relationship][name]["total_amount"] += float(debt["amount"])
            consolidated[relationship][name]["total_paid"] += debt_payments
            consolidated[relationship][name]["total_owed"] += debt_owed
            consolidated[relationship][name]["remaining"] += debt_remaining
            
            if debt["due_date"] != "N/A" and (consolidated[relationship][name]["latest_due_date"] == "N/A" or 
                                              debt["due_date"] > consolidated[relationship][name]["latest_due_date"]):
                consolidated[relationship][name]["latest_due_date"] = debt["due_date"]
        
        result = {
            "Who owes me": list(consolidated["Who owes me"].values()),
            "Who I owe": list(consolidated["Who I owe"].values())
        }
        
        return result
    
    def get_user_debts(self):
        """Get all debts for current user"""
        debts = []
        with open("debt_data.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["user"] == self.current_user:
                    debts.append(row)
        return debts
    
    def create_consolidated_debt_entry(self, parent, person_data):
        """Create a consolidated debt entry widget for a person"""
        remaining = person_data["remaining"]
        
        debt_frame = ctk.CTkFrame(parent)
        debt_frame.pack(fill="x", pady=5, padx=10)
        
        summary_frame = ctk.CTkFrame(debt_frame)
        summary_frame.pack(fill="x", pady=5, padx=10)
        
        name_label = ctk.CTkLabel(summary_frame, text=person_data["full_name"], 
                                font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(side="left", padx=10)
        
        amount_text = f"₱{person_data['total_paid']:.2f}" if remaining == 0 else f"₱{remaining:.2f}"
        amount_color = "green" if remaining == 0 else "red"
        amount_label = ctk.CTkLabel(summary_frame, text=amount_text, 
                                  font=ctk.CTkFont(size=14), text_color=amount_color)
        amount_label.pack(side="left", padx=20)
        
        # Add status badge
        status = self.get_debt_status(person_data["debt_history"][-1])  # Use latest debt for status
        status_color = {"Overdue": "#FF0000", "Pending": "#FFFF00", "Paid": "#00FF00"}
        status_label = ctk.CTkLabel(summary_frame, text=status, 
                                  font=ctk.CTkFont(size=12), text_color=status_color[status])
        status_label.pack(side="left", padx=10)
        
        due_label = ctk.CTkLabel(summary_frame, text=f"Due: {person_data['latest_due_date']}", 
                               font=ctk.CTkFont(size=12))
        due_label.pack(side="left", padx=20)
        
        button_frame = ctk.CTkFrame(summary_frame)
        button_frame.pack(side="right", padx=10)
        
        view_btn = ctk.CTkButton(button_frame, text="View Details", 
                               command=lambda: self.toggle_consolidated_details(debt_frame, person_data),
                               width=100, height=30)
        view_btn.pack(side="left", padx=5)
        
        if remaining > 0:
            pay_btn = ctk.CTkButton(button_frame, text="Add Payment", 
                                  command=lambda: self.show_add_payment_form(person_data),
                                  width=100, height=30)
            pay_btn.pack(side="left", padx=5)
        else:
            reactivate_btn = ctk.CTkButton(button_frame, text="Reactivate", 
                                         command=lambda: self.show_reactivate_debt_form(person_data),
                                         width=100, height=30)
            reactivate_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(button_frame, text="Delete", 
                                 command=lambda: self.delete_person_debts(person_data),
                                 width=80, height=30, fg_color="red")
        delete_btn.pack(side="left", padx=5)
        
        details_frame = ctk.CTkFrame(debt_frame)
        details_frame.pack_forget()
        
        debt_frame.details_frame = details_frame
        debt_frame.details_visible = False
        
        self.create_consolidated_debt_details(details_frame, person_data)
    
    def create_consolidated_debt_details(self, parent, person_data):
        """Create detailed view of consolidated debt"""
        info_text = f"""
Full Name: {person_data['full_name']}
Relationship: {person_data['relationship']}

Financial Summary:
Total Amount Borrowed: ₱{person_data['total_amount']:.2f}
Total Owed (with interest): ₱{person_data['total_owed']:.2f}
Total Paid: ₱{person_data['total_paid']:.2f}
Remaining Balance: ₱{person_data['remaining']:.2f}
        """
        
        info_label = ctk.CTkLabel(parent, text=info_text, 
                                font=ctk.CTkFont(size=12), justify="left")
        info_label.pack(pady=10, padx=20)
        
        history_label = ctk.CTkLabel(parent, text="Debt History:", 
                                   font=ctk.CTkFont(size=14, weight="bold"))
        history_label.pack(pady=(10, 5))
        
        for i, debt in enumerate(person_data['debt_history'], 1):
            debt_frame = ctk.CTkFrame(parent)
            debt_frame.pack(fill="x", pady=2, padx=20)
            
            status = self.get_debt_status(debt)
            status_color = {"Overdue": "#FF0000", "Pending": "#FFFF00", "Paid": "#00FF00"}
            debt_text = f"""
Debt #{i} - Added: {debt['date_added']} (Status: {status})
Amount: ₱{debt['amount']:.2f} | Interest: {debt['interest_rate']}% | Due: {debt['due_date']}
Total Owed: ₱{debt['owed']:.2f} | Paid: ₱{debt['payments']:.2f} | Remaining: ₱{debt['remaining']:.2f}
Notes: {debt['notes'] if debt['notes'] else 'None'}
            """
            
            debt_label = ctk.CTkLabel(debt_frame, text=debt_text.strip(), 
                                    font=ctk.CTkFont(size=10), text_color=status_color[status])
            debt_label.pack(side="left", pady=5, padx=10)
            
            edit_btn = ctk.CTkButton(debt_frame, text="Edit", 
                                   command=lambda d=debt: self.show_edit_debt_form(person_data, d),
                                   width=80, height=30)
            edit_btn.pack(side="right", padx=5)
            
            payments = self.get_payment_history(debt["debt_id"])
            if payments:
                pay_text = "Payments: " + ", ".join([f"₱{p['payment_amount']} ({p['payment_date']})" for p in payments])
                pay_label = ctk.CTkLabel(debt_frame, text=pay_text, 
                                       font=ctk.CTkFont(size=9), text_color="gray")
                pay_label.pack(pady=(0, 5), padx=10)
    
    def toggle_consolidated_details(self, debt_frame, person_data):
        """Toggle visibility of consolidated debt details"""
        if debt_frame.details_visible:
            debt_frame.details_frame.pack_forget()
            debt_frame.details_visible = False
        else:
            debt_frame.details_frame.pack(fill="x", pady=5, padx=10)
            debt_frame.details_visible = True
    
    def get_total_payments(self, debt_id, start_date=None, end_date=None):
        """Calculate total payments for a debt within date range"""
        total = 0
        with open("payments.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["debt_id"] == debt_id:
                    payment_date = datetime.strptime(row["payment_date"], "%Y-%m-%d")
                    if (start_date is None or payment_date >= start_date) and \
                       (end_date is None or payment_date <= end_date):
                        total += float(row["payment_amount"])
        return total
    
    def get_payment_history(self, debt_id):
        """Get payment history for a debt"""
        payments = []
        with open("payments.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["debt_id"] == debt_id:
                    payments.append(row)
        return payments
    
    def get_payment_history_in_range(self, start_date, end_date):
        """Get payment history within date range for all debts"""
        payments = []
        with open("payments.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                payment_date = datetime.strptime(row["payment_date"], "%Y-%m-%d")
                if (start_date is None or payment_date >= start_date) and \
                   (end_date is None or payment_date <= end_date):
                    debt = next((d for d in self.get_user_debts() if d["debt_id"] == row["debt_id"]), None)
                    if debt and debt["user"] == self.current_user:
                        payments.append(row)
        return sorted(payments, key=lambda x: x["payment_date"])
    
    def show_add_debt_form(self):
        """Show add debt form"""
        self.current_view = "add_debt"
        self.clear_main_frame()
        
        title_label = ctk.CTkLabel(self.main_frame, text="Add New Debt", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        scrollable_form = ctk.CTkScrollableFrame(self.main_frame)
        scrollable_form.pack(fill="both", expand=True, pady=20, padx=20)
        
        form_frame = ctk.CTkFrame(scrollable_form)
        form_frame.pack(pady=20, padx=100, fill="x")
        
        ctk.CTkLabel(form_frame, text="Full Name:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.name_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.name_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Amount:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.amount_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.amount_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Relationship Type:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.relationship_var = ctk.StringVar(value="Who owes me")
        relationship_menu = ctk.CTkOptionMenu(form_frame, variable=self.relationship_var,
                                            values=["Who owes me", "Who I owe"],
                                            width=400, height=35)
        relationship_menu.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Interest Rate (%):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.interest_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.interest_entry.pack(pady=5)
        
        # Date added
        ctk.CTkLabel(form_frame, text="Date Added:", font=ctk.CTkFont(size=14)).pack(pady=5)
        date_frame = ctk.CTkFrame(form_frame)
        date_frame.pack(pady=5)
        
        self.date_added_entry = ctk.CTkEntry(date_frame, width=340, height=35)
        self.date_added_entry.pack(side="left", padx=(0, 5))
        
        self.date_added_cal_button = ctk.CTkButton(date_frame, text="📅", width=50, height=35,
                                                 command=lambda: self.toggle_calendar(form_frame, 
                                                    self.date_added_entry, "date_added"))
        self.date_added_cal_button.pack(side="left")
        
        self.date_added_cal = Calendar(form_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.date_added_cal.pack_forget()
        self.date_added_cal.bind("<<CalendarSelected>>", 
                                lambda e: self.update_date(self.date_added_entry, self.date_added_cal))
        
        # Due date
        ctk.CTkLabel(form_frame, text="Due Date (optional):", font=ctk.CTkFont(size=14)).pack(pady=5)
        due_date_frame = ctk.CTkFrame(form_frame)
        due_date_frame.pack(pady=5)
        
        self.due_date_entry = ctk.CTkEntry(due_date_frame, width=340, height=35, placeholder_text="N/A")
        self.due_date_entry.pack(side="left", padx=(0, 5))
        
        self.due_date_cal_button = ctk.CTkButton(due_date_frame, text="📅", width=50, height=35,
                                               command=lambda: self.toggle_calendar(form_frame, 
                                                  self.due_date_entry, "due_date"))
        self.due_date_cal_button.pack(side="left")
        
        self.due_date_cal = Calendar(form_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.due_date_cal.pack_forget()
        self.due_date_cal.bind("<<CalendarSelected>>", 
                              lambda e: self.update_date(self.due_date_entry, self.due_date_cal))
        
        ctk.CTkLabel(form_frame, text="Notes (optional):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.notes_entry = ctk.CTkTextbox(form_frame, width=400, height=80)
        self.notes_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(button_frame, text="Save Debt", command=self.save_debt,
                               width=120, height=40)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.show_dashboard,
                                 width=120, height=40)
        cancel_btn.pack(side="left", padx=10)
    
    def show_quick_add_debt_form(self):
        """Show quick add debt form with minimal fields"""
        self.current_view = "quick_add_debt"
        self.clear_main_frame()
        
        title_label = ctk.CTkLabel(self.main_frame, text="Quick Add Debt", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        scrollable_form = ctk.CTkScrollableFrame(self.main_frame)
        scrollable_form.pack(fill="both", expand=True, pady=20, padx=20)
        
        form_frame = ctk.CTkFrame(scrollable_form)
        form_frame.pack(pady=20, padx=100, fill="x")
        
        ctk.CTkLabel(form_frame, text="Full Name:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.quick_name_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.quick_name_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Amount:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.quick_amount_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.quick_amount_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Relationship Type:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.quick_relationship_var = ctk.StringVar(value="Who owes me")
        relationship_menu = ctk.CTkOptionMenu(form_frame, variable=self.quick_relationship_var,
                                            values=["Who owes me", "Who I owe"],
                                            width=400, height=35)
        relationship_menu.pack(pady=5)
        
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(button_frame, text="Save Debt", command=self.save_quick_debt,
                               width=120, height=40)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.show_dashboard,
                                 width=120, height=40)
        cancel_btn.pack(side="left", padx=10)
    
    def save_quick_debt(self):
        """Save quick debt entry with default values"""
        name = self.quick_name_entry.get().strip()
        amount = self.quick_amount_entry.get().strip()
        relationship = self.quick_relationship_var.get()
        
        if not all([name, amount]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        try:
            float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return
        
        debt_id = f"{self.current_user}_{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        with open("debt_data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self.current_user, name, amount, relationship, "0",
                           datetime.now().strftime("%Y-%m-%d"), "N/A", "", "active", debt_id])
        
        messagebox.showinfo("Success", "Debt added successfully!")
        self.show_dashboard()
    
    def toggle_calendar(self, parent, entry, cal_type):
        """Toggle visibility of calendar widget"""
        if cal_type == "date_added":
            calendar = self.date_added_cal
            other_calendar = self.due_date_cal if hasattr(self, 'due_date_cal') else None
        elif cal_type == "due_date":
            calendar = self.due_date_cal
            other_calendar = self.date_added_cal if hasattr(self, 'date_added_cal') else None
        else:
            calendar = self.edit_due_date_cal
            other_calendar = self.edit_date_added_cal if hasattr(self, 'edit_date_added_cal') else None
            
        if calendar.winfo_ismapped():
            calendar.pack_forget()
        else:
            if other_calendar and other_calendar.winfo_ismapped():
                other_calendar.pack_forget()
            calendar.pack(pady=5)
    
    def update_date(self, entry, calendar):
        """Update date entry with selected calendar date"""
        entry.delete(0, "end")
        entry.insert(0, calendar.get_date())
        calendar.pack_forget()


    
    def save_debt(self):
        """Save new debt entry"""
        name = self.name_entry.get().strip()
        amount = self.amount_entry.get().strip()
        relationship = self.relationship_var.get()
        interest = self.interest_entry.get().strip()
        date_added = self.date_added_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        notes = self.notes_entry.get("1.0", "end").strip()
        
        if not all([name, amount, interest, date_added]):
            messagebox.showerror("Error", "Please fill all required fields (Due Date is optional)")
            return
        
        try:
            float(amount)
            float(interest)
        except ValueError:
            messagebox.showerror("Error", "Amount and interest rate must be numbers")
            return
        
        try:
            datetime.strptime(date_added, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date added must be in YYYY-MM-DD format")
            return
        
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Due date must be in YYYY-MM-DD format")
                return
        else:
            due_date = "N/A"
        
        debt_id = f"{self.current_user}_{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        with open("debt_data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self.current_user, name, amount, relationship, interest,
                           date_added, due_date, notes, "active", debt_id])
        
        messagebox.showinfo("Success", "Debt added successfully!")
        self.show_dashboard()
    
    def show_add_payment_form(self, person_data):
        """Show add payment form in main window"""
        self.current_view = "add_payment"
        self.selected_person_data = person_data
        self.clear_main_frame()
        
        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(scrollable_frame, text=f"Add Payment for {person_data['full_name']}", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        balance_label = ctk.CTkLabel(scrollable_frame, text=f"Current Balance: ₱{person_data['remaining']:.2f}", 
                                   font=ctk.CTkFont(size=16), text_color="red")
        balance_label.pack(pady=10)
        
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(pady=20, padx=100, fill="x")
        
        ctk.CTkLabel(form_frame, text="Payment Amount:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.payment_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.payment_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Payment Date:", font=ctk.CTkFont(size=14)).pack(pady=5)
        payment_date_frame = ctk.CTkFrame(form_frame)
        payment_date_frame.pack(pady=5)
        
        self.payment_date_entry = ctk.CTkEntry(payment_date_frame, width=340, height=35)
        self.payment_date_entry.pack(side="left", padx=(0, 5))
        
        self.payment_date_cal_button = ctk.CTkButton(payment_date_frame, text="📅", width=50, height=35,
                                                   command=lambda: self.toggle_payment_calendar(form_frame))
        self.payment_date_cal_button.pack(side="left")
        
        self.payment_date_cal = Calendar(form_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.payment_date_cal.pack_forget()
        self.payment_date_cal.bind("<<CalendarSelected>>", 
                                  lambda e: self.update_date(self.payment_date_entry, self.payment_date_cal))
        
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(button_frame, text="Save Payment", command=self.save_payment,
                               width=120, height=40)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.show_dashboard,
                                 width=120, height=40)
        cancel_btn.pack(side="left", padx=10)
    
    def toggle_payment_calendar(self, parent):
        """Toggle visibility of payment date calendar"""
        if self.payment_date_cal.winfo_ismapped():
            self.payment_date_cal.pack_forget()
        else:
            self.payment_date_cal.pack(pady=5)
    
    def save_payment(self):
        """Save payment for selected person"""
        amount = self.payment_entry.get().strip()
        date = self.payment_date_entry.get().strip()
        
        if not amount or not date:
            messagebox.showerror("Error", "Please enter payment amount and date")
            return
        
        try:
            payment_amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Payment amount must be a number")
            return
        
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
            return
        
        remaining = self.selected_person_data["remaining"]
        
        if payment_amount > remaining:
            messagebox.showerror("Error", f"Payment amount (₱{payment_amount:.2f}) exceeds remaining balance (₱{remaining:.2f})")
            return
        
        if payment_amount <= 0:
            messagebox.showerror("Error", "Payment amount must be greater than zero")
            return
        
        remaining_payment = payment_amount
        for debt in self.selected_person_data['debt_history']:
            if remaining_payment <= 0:
                break
            if debt['remaining'] > 0:
                payment_to_apply = min(remaining_payment, debt['remaining'])
                
                with open("payments.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([debt["debt_id"], payment_to_apply, date])
                
                remaining_payment -= payment_to_apply
        
        messagebox.showinfo("Success", "Payment added successfully!")
        self.show_dashboard()
    
    def show_reactivate_debt_form(self, person_data):
        """Show reactivate debt form in main window"""
        self.current_view = "reactivate_debt"
        self.selected_person_data = person_data
        self.clear_main_frame()
        
        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(scrollable_frame, text=f"Add New Debt for {person_data['full_name']}", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(pady=20, padx=100, fill="x")
        
        ctk.CTkLabel(form_frame, text="Amount:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.reactivate_amount_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.reactivate_amount_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Interest Rate (%):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.reactivate_interest_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.reactivate_interest_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Due Date (optional):", font=ctk.CTkFont(size=14)).pack(pady=5)
        due_date_frame = ctk.CTkFrame(form_frame)
        due_date_frame.pack(pady=5)
        
        self.reactivate_due_date_entry = ctk.CTkEntry(due_date_frame, width=340, height=35, placeholder_text="N/A")
        self.reactivate_due_date_entry.pack(side="left", padx=(0, 5))
        
        self.reactivate_due_date_cal_button = ctk.CTkButton(due_date_frame, text="📅", width=50, height=35,
                                                          command=lambda: self.toggle_reactivate_calendar(form_frame))
        self.reactivate_due_date_cal_button.pack(side="left")
        
        self.reactivate_due_date_cal = Calendar(form_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.reactivate_due_date_cal.pack_forget()
        self.reactivate_due_date_cal.bind("<<CalendarSelected>>", 
                                        lambda e: self.update_date(self.reactivate_due_date_entry, 
                                                                 self.reactivate_due_date_cal))
        
        ctk.CTkLabel(form_frame, text="Notes (optional):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.reactivate_notes_entry = ctk.CTkTextbox(form_frame, width=400, height=80)
        self.reactivate_notes_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(button_frame, text="Add Debt", command=self.save_reactivated_debt,
                               width=120, height=40)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.show_dashboard,
                                 width=120, height=40)
        cancel_btn.pack(side="left", padx=10)
    
    def toggle_reactivate_calendar(self, parent):
        """Toggle visibility of reactivate due date calendar"""
        if self.reactivate_due_date_cal.winfo_ismapped():
            self.reactivate_due_date_cal.pack_forget()
        else:
            self.reactivate_due_date_cal.pack(pady=5)
    
    def save_reactivated_debt(self):
        """Save reactivated debt for selected person"""
        amount = self.reactivate_amount_entry.get().strip()
        interest = self.reactivate_interest_entry.get().strip()
        due_date = self.reactivate_due_date_entry.get().strip()
        notes = self.reactivate_notes_entry.get("1.0", "end").strip()
        
        if not all([amount, interest]):
            messagebox.showerror("Error", "Please fill all required fields (Due Date is optional)")
            return
        
        try:
            float(amount)
            float(interest)
        except ValueError:
            messagebox.showerror("Error", "Amount and interest rate must be numbers")
            return
        
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Due date must be in YYYY-MM-DD format")
                return
        else:
            due_date = "N/A"
        
        debt_id = f"{self.current_user}_{self.selected_person_data['full_name']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        with open("debt_data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self.current_user, self.selected_person_data['full_name'], amount, 
                           self.selected_person_data['relationship'], interest, 
                           datetime.now().strftime("%Y-%m-%d"), due_date, notes, "active", debt_id])
        
        messagebox.showinfo("Success", "New debt added successfully!")
        self.show_dashboard()
    
    def show_edit_debt_form(self, person_data, debt):
        """Show edit debt form in main window"""
        self.current_view = "edit_debt"
        self.selected_person_data = person_data
        self.selected_debt = debt
        self.clear_main_frame()
        
        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(scrollable_frame, text=f"Edit Debt for {person_data['full_name']}", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(pady=20, padx=100, fill="x")
        
        ctk.CTkLabel(form_frame, text="Amount:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.edit_amount_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.edit_amount_entry.insert(0, str(debt['amount']))
        self.edit_amount_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Interest Rate (%):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.edit_interest_entry = ctk.CTkEntry(form_frame, width=400, height=35)
        self.edit_interest_entry.insert(0, str(debt['interest_rate']))
        self.edit_interest_entry.pack(pady=5)
        
        ctk.CTkLabel(form_frame, text="Date Added:", font=ctk.CTkFont(size=14)).pack(pady=5)
        date_frame = ctk.CTkFrame(form_frame)
        date_frame.pack(pady=5)
        
        self.edit_date_added_entry = ctk.CTkEntry(date_frame, width=340, height=35)
        self.edit_date_added_entry.insert(0, debt['date_added'])
        self.edit_date_added_entry.pack(side="left", padx=(0, 5))
        
        self.edit_date_added_cal_button = ctk.CTkButton(date_frame, text="📅", width=50, height=35,
                                                      command=lambda: self.toggle_calendar(form_frame, 
                                                         self.edit_date_added_entry, "date_added"))
        self.edit_date_added_cal_button.pack(side="left")
        
        self.edit_date_added_cal = Calendar(form_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.edit_date_added_cal.pack_forget()
        self.edit_date_added_cal.bind("<<CalendarSelected>>", 
                                     lambda e: self.update_date(self.edit_date_added_entry, self.edit_date_added_cal))
        
        ctk.CTkLabel(form_frame, text="Due Date (optional):", font=ctk.CTkFont(size=14)).pack(pady=5)
        due_date_frame = ctk.CTkFrame(form_frame)
        due_date_frame.pack(pady=5)
        
        self.edit_due_date_entry = ctk.CTkEntry(due_date_frame, width=340, height=35, placeholder_text="N/A")
        self.edit_due_date_entry.insert(0, debt['due_date'])
        self.edit_due_date_entry.pack(side="left", padx=(0, 5))
        
        self.edit_due_date_cal_button = ctk.CTkButton(due_date_frame, text="📅", width=50, height=35,
                                                    command=lambda: self.toggle_calendar(form_frame, 
                                                       self.edit_due_date_entry, "due_date"))
        self.edit_due_date_cal_button.pack(side="left")
        
        self.edit_due_date_cal = Calendar(form_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.edit_due_date_cal.pack_forget()
        self.edit_due_date_cal.bind("<<CalendarSelected>>", 
                                   lambda e: self.update_date(self.edit_due_date_entry, self.edit_due_date_cal))
        
        ctk.CTkLabel(form_frame, text="Notes (optional):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.edit_notes_entry = ctk.CTkTextbox(form_frame, width=400, height=80)
        self.edit_notes_entry.insert("1.0", debt['notes'] if debt['notes'] else "")
        self.edit_notes_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(button_frame, text="Save Changes", command=self.save_edited_debt,
                               width=120, height=40)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.show_dashboard,
                                 width=120, height=40)
        cancel_btn.pack(side="left", padx=10)
    
    def save_edited_debt(self):
        """Save edited debt entry"""
        amount = self.edit_amount_entry.get().strip()
        interest = self.edit_interest_entry.get().strip()
        date_added = self.edit_date_added_entry.get().strip()
        due_date = self.edit_due_date_entry.get().strip()
        notes = self.edit_notes_entry.get("1.0", "end").strip()
        
        if not all([amount, interest, date_added]):
            messagebox.showerror("Error", "Please fill all required fields (Due Date is optional)")
            return
        
        try:
            float(amount)
            float(interest)
        except ValueError:
            messagebox.showerror("Error", "Amount and interest rate must be numbers")
            return
        
        try:
            datetime.strptime(date_added, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date added must be in YYYY-MM-DD format")
            return
        
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Due date must be in YYYY-MM-DD format")
                return
        else:
            due_date = "N/A"
        
        debts = []
        with open("debt_data.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["debt_id"] == self.selected_debt["debt_id"]:
                    debts.append({
                        "user": self.current_user,
                        "full_name": self.selected_person_data["full_name"],
                        "amount": amount,
                        "relationship": self.selected_person_data["relationship"],
                        "interest_rate": interest,
                        "date_added": date_added,
                        "due_date": due_date,
                        "notes": notes,
                        "status": "active",
                        "debt_id": self.selected_debt["debt_id"]
                    })
                else:
                    debts.append(row)
        
        with open("debt_data.csv", "w", newline="") as file:
            fieldnames = ["user", "full_name", "amount", "relationship", "interest_rate", 
                         "date_added", "due_date", "notes", "status", "debt_id"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(debts)
        
        messagebox.showinfo("Success", "Debt updated successfully!")
        self.show_dashboard()
    
    def delete_person_debts(self, person_data):
        """Delete all debt entries and payments for a person"""
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete ALL debts for {person_data['full_name']}?"):
            return
            
        debt_ids_to_delete = [debt["debt_id"] for debt in person_data["debt_history"]]
        
        # Filter out debts
        debts = []
        with open("debt_data.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["debt_id"] not in debt_ids_to_delete:
                    debts.append(row)
        
        with open("debt_data.csv", "w", newline="") as file:
            fieldnames = ["user", "full_name", "amount", "relationship", "interest_rate", 
                         "date_added", "due_date", "notes", "status", "debt_id"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(debts)
        
        # Filter out payments
        payments = []
        with open("payments.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["debt_id"] not in debt_ids_to_delete:
                    payments.append(row)
        
        with open("payments.csv", "w", newline="") as file:
            fieldnames = ["debt_id", "payment_amount", "payment_date"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(payments)
        
        messagebox.showinfo("Success", f"All debts for {person_data['full_name']} deleted successfully!")
        self.show_dashboard()
    
    def destroy(self):
        """Clean up resources and close the application"""
        if self.fig is not None:
            plt.close(self.fig)
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = UtangTracker()
    app.run()