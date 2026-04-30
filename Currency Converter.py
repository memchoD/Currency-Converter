import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import datetime

API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
HISTORY_FILE = "history.json"

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_rates():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()["rates"]
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить курсы валют: {e}")
        return None

def convert_currency():
    amount_str = entry_amount.get()
    from_curr = combo_from.get()
    to_curr = combo_to.get()

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))
        return

    rates = get_rates()
    if not rates:
        return

    if from_curr not in rates or to_curr not in rates:
        messagebox.showerror("Ошибка", "Выбрана недоступная валюта")
        return

    # Конвертация через USD (базовая валюта API)
    result = amount * (rates[to_curr] / rates[from_curr])
    label_result.config(text=f"Результат: {result:.2f} {to_curr}")

    # Сохранение в историю
    history = load_history()
    history.append({
        "from": from_curr,
        "to": to_curr,
        "amount": amount,
        "result": result,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_history(history)
    update_history_table()

def update_history_table():
    for i in table_history.get_children():
        table_history.delete(i)
    history = load_history()
    for item in history:
        table_history.insert("", "end", values=(
            item["date"],
            f"{item['amount']} {item['from']}",
            f"{item['result']:.2f} {item['to']}"
        ))

# --- GUI ---
root = tk.Tk()
root.title("Currency Converter")

# Валюты
currencies = ["USD", "EUR", "GBP", "JPY", "CNY", "RUB"]

tk.Label(root, text="Из:").grid(row=0, column=0, padx=5, pady=5)
combo_from = ttk.Combobox(root, values=currencies, width=5)
combo_from.set("USD")
combo_from.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="В:").grid(row=0, column=2, padx=5, pady=5)
combo_to = ttk.Combobox(root, values=currencies, width=5)
combo_to.set("EUR")
combo_to.grid(row=0, column=3, padx=5, pady=5)

tk.Label(root, text="Сумма:").grid(row=1, column=0, padx=5, pady=5)
entry_amount = tk.Entry(root, width=15)
entry_amount.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

btn_convert = tk.Button(root, text="Конвертировать", command=convert_currency)
btn_convert.grid(row=2, column=0, columnspan=4, pady=10)

label_result = tk.Label(root, text="Результат: ")
label_result.grid(row=3, column=0, columnspan=4, pady=5)

# Таблица истории
columns = ("Дата", "Операция", "Результат")
table_history = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    table_history.heading(col, text=col)
table_history.grid(row=4, column=0, columnspan=4, pady=10)

update_history_table()

root.mainloop()