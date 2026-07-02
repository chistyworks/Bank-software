import streamlit as st
import json
import os
import random


st.set_page_config(page_title="Bank Management System", page_icon="🏦", layout="centered")

DATA_FILE = "accounts.json"



def load_accounts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_accounts(accounts):
    with open(DATA_FILE, "w") as f:
        json.dump(accounts, f, indent=4)


if "all_acc" not in st.session_state:
    st.session_state.all_acc = load_accounts()



def open_acc(cnic, title, initial_deposite):
    account = {
        "CNIC": cnic,
        "Title": title,
        "Balance": initial_deposite,
        "account_num": random.randint(100000001, 99999999999),
        "pin": random.randint(1001, 9999),
    }
    st.session_state.all_acc.append(account)
    save_accounts(st.session_state.all_acc)
    return account


def find_acc(account_num):
    for acc in st.session_state.all_acc:
        if acc["account_num"] == account_num:
            return acc
    return None


def check_balance(account_num, pin):
    acc = find_acc(account_num)
    if acc is None:
        return "invalid account number", None
    if acc["pin"] != pin:
        return "invalid pin", None
    return None, acc["Balance"]


def withdraw(account_num, pin, amt):
    acc = find_acc(account_num)
    if acc is None:
        return "invalid account number", None
    if acc["pin"] != pin:
        return "invalid pin", None
    if acc["Balance"] < amt:
        return "Insufficient Balance", None
    acc["Balance"] -= amt
    save_accounts(st.session_state.all_acc)
    return None, acc["Balance"]


def deposite(account_num, pin, amt):
    acc = find_acc(account_num)
    if acc is None:
        return "invalid account number", None
    if acc["pin"] != pin:
        return "invalid pin", None
    acc["Balance"] += amt
    save_accounts(st.session_state.all_acc)
    return None, acc["Balance"]


def forgot_pin(account_num, cnic):
    acc = find_acc(account_num)
    if acc is None:
        return "invalid account number", None
    if acc["CNIC"] != cnic:
        return "CNIC does not match our records", None
    return None, acc["pin"]

st.sidebar.title("🏦 Bank Menu")
menu = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📝 Open Account", "💰 Check Balance", "⬇️ Deposit", "⬆️ Withdraw", "🔑 Forgot PIN", "📋 All Accounts"],
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Total Accounts: {len(st.session_state.all_acc)}")


if menu == "🏠 Home":
    st.title("🏦 Bank Management System")
    st.write("Welcome! Use the sidebar to open an account, check balance, deposit or withdraw money.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Accounts", len(st.session_state.all_acc))
    with col2:
        total_balance = sum(acc["Balance"] for acc in st.session_state.all_acc)
        st.metric("Total Bank Balance", f"Rs. {total_balance:,.0f}")


elif menu == "📝 Open Account":
    st.title("📝 Open a New Account")

    with st.form("open_account_form", clear_on_submit=True):
        cnic = st.text_input("CNIC")
        title = st.text_input("Account Title (Full Name)")
        initial_deposite = st.number_input("Initial Deposit (Rs.)", min_value=500, step=100)
        submitted = st.form_submit_button("Open Account")

        if submitted:
            if not cnic.strip() or not title.strip():
                st.error("Please fill all the fields.")
            else:
                account = open_acc(cnic, title, float(initial_deposite))
                st.success("✅ Your account is successfully created!")
                st.info(f"**Account Number:** {account['account_num']}")
                st.info(f"**PIN:** {account['pin']}")
                st.warning("⚠️ Please save your account number and PIN safely. You will need both for every transaction.")


elif menu == "💰 Check Balance":
    st.title("💰 Check Balance")

    account_num = st.number_input("Account Number", min_value=0, step=1, format="%d")
    pin = st.number_input("PIN", min_value=0, step=1, format="%d")

    if st.button("Check Balance"):
        error, balance = check_balance(int(account_num), int(pin))
        if error:
            st.error(f"❌ {error}")
        else:
            st.success("Balance fetched successfully")
            st.metric("Available Balance", f"Rs. {balance:,.0f}")


elif menu == "⬇️ Deposit":
    st.title("⬇️ Deposit Money")

    account_num = st.number_input("Account Number", min_value=0, step=1, format="%d")
    pin = st.number_input("PIN", min_value=0, step=1, format="%d")
    amt = st.number_input("Amount to Deposit (Rs.)", min_value=1, step=100)

    if st.button("Deposit"):
        error, balance = deposite(int(account_num), int(pin), float(amt))
        if error:
            st.error(f"❌ {error}")
        else:
            st.success(f"✅ Rs.{amt:,.0f} is deposited successfully!")
            st.metric("New Balance", f"Rs. {balance:,.0f}")


elif menu == "⬆️ Withdraw":
    st.title("⬆️ Withdraw Money")

    account_num = st.number_input("Account Number", min_value=0, step=1, format="%d")
    pin = st.number_input("PIN", min_value=0, step=1, format="%d")
    amt = st.number_input("Amount to Withdraw (Rs.)", min_value=1, step=100)

    if st.button("Withdraw"):
        error, balance = withdraw(int(account_num), int(pin), float(amt))
        if error:
            st.error(f"❌ {error}")
        else:
            st.success(f"✅ Rs.{amt:,.0f} withdrawn successfully!")
            st.metric("New Balance", f"Rs. {balance:,.0f}")


elif menu == "🔑 Forgot PIN":
    st.title("🔑 Forgot PIN")
    st.write("Enter your Account Number and CNIC to recover your PIN.")

    account_num = st.number_input("Account Number", min_value=0, step=1, format="%d")
    cnic = st.text_input("CNIC")

    if st.button("Recover PIN"):
        if not cnic.strip():
            st.error("Please enter your CNIC.")
        else:
            error, pin = forgot_pin(int(account_num), cnic)
            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ Identity verified!")
                st.info(f"**Your PIN is:** {pin}")

elif menu == "📋 All Accounts":
    st.title("📋 All Accounts")

    if not st.session_state.all_acc:
        st.info("No accounts opened yet.")
    else:
        for acc in st.session_state.all_acc:
            with st.expander(f"{acc['Title']} — A/C No: {acc['account_num']}"):
                st.write(f"**CNIC:** {acc['CNIC']}")
                st.write(f"**Balance:** Rs. {acc['Balance']:,.0f}")
                st.caption("PIN is hidden here for security. Only the account holder should know it.")
