# Utang Tracker

Utang Tracker is a desktop application for managing and tracking personal debts and payments. It provides a user-friendly interface to record, analyze, and visualize debts, and payments.

## Features

- **User Registration & Login:** Secure user authentication with password hashing.
- **Debt Management:** Add, edit, delete, and reactivate debts. Track who owes you and who you owe.
- **Payment Tracking:** Record payments for each debt and view payment history.
- **Analytics Dashboard:** Visualize debt distribution, payment history, and summary statistics with interactive charts.
- **Profile Management:** View user profile, change password, and see debt statistics.
- **CSV Data Storage:** All data is stored in CSV files for portability and easy backup.

## File Structure

- `utang_tracker.py` - Main application source code.
- `users.csv` - Stores user credentials and registration dates.
- `debt_data.csv` - Stores all debt records.
- `payments.csv` - Stores payment records for debts.
- `README.md` - Project documentation.

## Requirements

- Python 3.8+
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- [tkcalendar](https://github.com/j4321/tkcalendar)
- [matplotlib](https://matplotlib.org/)
- [pandas](https://pandas.pydata.org/)
- [numpy](https://numpy.org/)

Install dependencies with:

```sh
pip install customtkinter tkcalendar matplotlib pandas numpy
```

## Usage

### Option 1: Ready-to-Use EXE (Recommended for Windows Users)
1. Download the latest `utang_tracker.exe` from the `dist` folder in this repository.
2. Double-click `utang_tracker.exe` to launch the application—no Python installation required!
### Option 2: Run from Source
1. Run the application:

    ```sh
    python utang_tracker.py
    ```

2. Register a new account or log in with an existing one.
3. Use the dashboard to add debts, record payments, and view analytics.

## Notes

- All data is stored locally in CSV files in the project directory.
- The app uses SHA-256 for password hashing.
- Analytics and charts are generated using matplotlib.

## Author

By John Allen Esteleydes

---

For questions or suggestions, contact: esteleydesjohnallen0@gmail.com
