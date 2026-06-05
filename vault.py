from flask import Flask, render_template, request, redirect, session
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import mysql.connector
import bcrypt, re
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "anyrandomstring123"
load_dotenv()
db = mysql.connector.connect(host="localhost",user="root",password="password123",database="SecureVaultDB")
FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY)

def password_strength(value):
    score = 0
    if len(value) >= 12:
        score += 1
    if re.search(r'[A-Z]', value):
        score += 1
    if re.search(r'[a-z]', value):
        score += 1
    if re.search(r'[0-9]', value):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        score += 1
    if score <= 2:
        return "weak"
    elif score <= 4:
        return "medium"
    return "strong"

def valid(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):  # checks uppercase
        return False
    if not re.search(r'[a-z]', password):  # checks lowercase
        return False
    if not re.search(r'[0-9]', password):  # checks number
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # checks special character
        return False
    return True

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']        
        email = request.form['email']      
        master = request.form['master']    
        confirm = request.form['confirm'] 
        if master != confirm:
            return "<script>alert('Passwords do not match'); window.location.href('/signup');</script>"  # you can make this nicer later
        if not valid(master):  
            return "<script>alert('Password does not meet requirements'); window.location.href('/signup');</script>"
        hashed = bcrypt.hashpw(master.encode('utf-8'), bcrypt.gensalt())
        cursor = db.cursor()
        cursor.execute("INSERT INTO Users (User_Name, User_Email, User_Password) VALUES (%s, %s, %s)",(name, email, hashed))
        db.commit()
        return redirect('/login') 
    return render_template('signup.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        master = request.form['master']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users WHERE User_Email = %s", (email,))
        user = cursor.fetchone()  # gets the first matching row
        # If no user found or password wrong
        if user is None:
            return "<script>alert('Invalid Email or no such user found!'); window.location.href('/login');</script>"  # make this nicer later
        # Check password against stored hash
        # user[3] is password_hash column (id=0, name=1, email=2, password_hash=3)
        stored_hash = user[3]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode()
        if not bcrypt.checkpw(master.encode(), stored_hash):
            return "<script>alert('Incorrect Password!'); window.location.href('/login');</script>"
        # If correct — save user in session (like a temporary memory of who is logged in)
        session['User_ID'] = user[0]    # stores their id
        session['User_Name'] = user[1]  # stores their name
        return redirect('/dashboard')
    return render_template("login.html")

@app.route('/save', methods=['POST'])  
def save(): 
    user_id = session.get('User_ID')
    if 'User_ID' not in session:
        return redirect('/login')
    new_uname = request.form.get('username')
    new_email = request.form.get('email')
    cursor = db.cursor()
    cursor.execute(
        "UPDATE Users SET User_Name=%s, User_Email=%s, Updated_At=NOW() WHERE User_ID=%s",
        (new_uname, new_email, user_id))
    db.commit()
    session['location'] = request.form.get('location')
    session['acctype'] = request.form.get('acctype')
    return redirect('/settings')

@app.route('/verify', methods=['POST'])
def verify_otp():
    otp = request.form['otp']
    if str(otp) == str(session.get('otp')):
        session['otp_verified'] = True
    else:
        session['otp_verified'] = False
    return redirect('/settings')

@app.route('/change', methods=['POST'])
def change_password():
    if not session.get('otp_verified'):
        return redirect('/dashboard')
    new_pass = request.form['new_password']
    confirm_pass = request.form['confirm_password']
    if new_pass != confirm_pass:
        return "<script>alert('Passwords do not match!'); window.location.href='/dashboard';</script>"
    if not valid(new_pass):
        return "<script>alert('Password does not meet requirements'); window.location.href='/settings';</script>"
    hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt())
    user_id = session['User_ID']
    cursor = db.cursor()
    cursor.execute("UPDATE Users SET User_Password=%s WHERE User_ID=%s",(hashed, user_id))
    db.commit()
    session['otp_verified'] = False
    session['otp_sent'] = False
    return redirect('/settings')

def send_otp_email(to_email, otp):
    sender_email = "intruder.alert.sender@gmail.com"
    app_password = "ewhxslnavnrilmhg"
    msg = MIMEText(f"Your OTP for password reset is: {otp}")
    msg['Subject'] = "SecureVault OTP Verification"
    msg['From'] = sender_email
    msg['To'] = to_email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, to_email, msg.as_string())
    server.quit()

@app.route('/send-otp')
def send_otp():
    if 'User_ID' not in session:
        return redirect('/login')
    user_id = session['User_ID']
    cursor = db.cursor()
    cursor.execute("SELECT User_Email FROM Users WHERE User_ID=%s", (user_id,))
    email = cursor.fetchone()[0]
    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['otp_verified'] = False
    session['otp_sent'] = True
    send_otp_email(email, otp)
    return redirect('/settings')

@app.route('/vault',methods=["GET","POST"])
def vault():
    return render_template("vault.html")

@app.route('/dashboard')
def dashboard(): 
    if 'User_ID' not in session:
        return redirect('/login')
    user_id = session['User_ID']
    otp_verified = session.get('otp_verified', False)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM WebsiteVault WHERE User=%s", (user_id,))
    pwd_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM CardVault WHERE User=%s", (user_id,))
    card_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM NoteVault WHERE User=%s", (user_id,))
    note_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ApiVault WHERE User=%s", (user_id,))
    api_count = cursor.fetchone()[0]
    total_credentials = pwd_count + card_count + note_count + api_count
    vault_count = sum([
        pwd_count > 0,
        card_count > 0,
        note_count > 0,
        api_count > 0
    ])
    strong = medium = weak = 0
    cursor.execute("SELECT Password FROM WebsiteVault WHERE User=%s", (user_id,))
    encrypted_passwords = cursor.fetchall()
    for (enc_pw,) in encrypted_passwords:
        try:
            decrypted_pw = fernet.decrypt(enc_pw.encode()).decode()
            level = password_strength(decrypted_pw)
        except Exception as e:
            print("Decrypt error:", e)
            level = "weak"
        if level == "strong":
            strong += 1
        elif level == "medium":
            medium += 1
        else:
            weak += 1
    cursor.execute("SELECT API_Key FROM ApiVault WHERE User=%s", (user_id,))
    encrypted_keys = cursor.fetchall()
    for (enc_key,) in encrypted_keys:
        try:
            decrypted_key = fernet.decrypt(enc_key.encode()).decode()
            level = password_strength(decrypted_key)
        except:
            level = "weak"
        if level == "strong":
            strong += 1
        elif level == "medium":
            medium += 1
        else:
            weak += 1
    total = strong + medium + weak
    if total == 0:
        score = 0
    else:
        score = int(((strong * 1) + (medium * 0.6) + (weak * 0.2)) / total * 100)
    if score >= 80:
        grade = "Excellent"
    elif score >= 60:
        grade = "Good"
    elif score >= 40:
        grade = "Moderate"
    else:
        grade = "Weak"
    vaults = []
    cursor.execute("SELECT COUNT(*), MIN(Created_At), MAX(Created_At) FROM WebsiteVault WHERE User=%s", (user_id,))
    pwd_count, pwd_created, pwd_newentry = cursor.fetchone()
    if pwd_count > 0:
        vaults.append(("Password Vault", pwd_count, pwd_created, pwd_newentry))
    cursor.execute("SELECT COUNT(*), MIN(Created_At), MAX(Created_At) FROM CardVault WHERE User=%s", (user_id,))
    card_count, card_created, card_newentry = cursor.fetchone()
    if card_count > 0:
        vaults.append(("Card Vault", card_count, card_created, card_newentry))
    cursor.execute("SELECT COUNT(*), MIN(Created_At), MAX(Created_At) FROM NoteVault WHERE User=%s", (user_id,))
    note_count, note_created, note_newentry = cursor.fetchone()
    if note_count > 0:
        vaults.append(("Notes Vault", note_count, note_created, note_newentry))
    cursor.execute("SELECT COUNT(*), MIN(Created_At), MAX(Created_At) FROM ApiVault WHERE User=%s", (user_id,))
    api_count, api_created, api_newentry = cursor.fetchone()
    if api_count > 0:
        vaults.append(("API Vault", api_count, api_created, api_newentry))
    return render_template(
        "dashboard.html",
        username=session['User_Name'],
        number=total_credentials,
        vault_count=vault_count,
        strong=strong,
        medium=medium,
        weak=weak,
        score=score,
        grade=grade,
        vaults=vaults,
        otp_verified=otp_verified
    )

@app.route('/logout')
def logout():
    session.clear()         
    return redirect('/')    

@app.route('/settings')
def settings():
    if 'User_ID' not in session:
        return redirect('/login')
    user_id = session['User_ID']
    location = session.get('location', 'Not provided')
    acctype = session.get('acctype', 'Basic')
    otp_verified = session.get("otp_verified", False)
    otp_sent = session.get("otp_sent", False)
    cursor = db.cursor()
    cursor.execute("SELECT User_Name, User_Email FROM Users WHERE User_ID=%s", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM WebsiteVault WHERE User=%s", (user_id,))
    w = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM CardVault WHERE User=%s", (user_id,))
    c = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM NoteVault WHERE User=%s", (user_id,))
    n = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ApiVault WHERE User=%s", (user_id,))
    a = cursor.fetchone()[0]
    total_creds = w + c + n + a
    vault_count = sum([w > 0, c > 0, n > 0, a > 0])
    cursor.execute("SELECT Created_At, Updated_At FROM Users WHERE User_ID=%s", (user_id,))
    dates = cursor.fetchone()
    return render_template(
        "settings.html",
        username=user[0],
        email=user[1],
        created_at=dates[0],
        updated_at=dates[1],
        count=vault_count,
        credcount=total_creds,
        otp_verified=otp_verified,
        otp_sent=otp_sent,
        location=location,
        acctype=acctype
    )

@app.route('/password-vault', methods=["GET","POST"])
def passwordvault():
    if 'User_ID' not in session:
        return redirect('/login')
    if request.method == "POST":
        user_id = session.get('User_ID')
        website = request.form['website']
        username = request.form['username']
        password = request.form['password']
        encrypted_pw = fernet.encrypt(password.encode()).decode()
        cursor = db.cursor()
        cursor.execute("INSERT INTO WebsiteVault(User, Website_URL, Username, Password) VALUES(%s, %s, %s, %s)",(user_id,website,username,encrypted_pw))
        db.commit()
        return redirect("/dashboard")
    return render_template("vault.html")

@app.route('/card-vault', methods=["GET","POST"])
def cardvault():
    if 'User_ID' not in session:
        return redirect('/login')
    if request.method == "POST":
        user_id = session.get('User_ID')
        cname = request.form['cname']
        cardno = request.form['cardno']
        expiry = request.form['expiry']
        remainder = request.form['remainder']
        cursor = db.cursor()
        cursor.execute("INSERT INTO CardVault(User, CardHolder, CardNo, Expiry, Remainder) VALUES(%s, %s, %s, %s, %s)",(user_id, cname, cardno, expiry, remainder))
        db.commit()
        return redirect("/dashboard")
    return render_template("vault.html")

@app.route('/note-vault', methods=["GET","POST"])
def notevault():
    if 'User_ID' not in session:
        return redirect('/login')
    if request.method == "POST":
        user_id = session.get('User_ID')
        note = request.form['note']
        cursor = db.cursor()
        cursor.execute("INSERT INTO NoteVault(User, Notes) VALUES(%s, %s)",(user_id,note))
        db.commit()
        return redirect("/dashboard")
    return render_template("vault.html")

@app.route('/api-vault', methods=["GET","POST"])
def apivault():
    if 'User_ID' not in session:
        return redirect('/login')
    if request.method == "POST":
        user_id = session.get('User_ID')
        service = request.form['service']
        apikey = request.form['apikey']
        encrypted_key = fernet.encrypt(apikey.encode()).decode()
        cursor = db.cursor()
        cursor.execute("INSERT INTO ApiVault(User, Service, API_Key) VALUES(%s, %s, %s)",(user_id,service,encrypted_key))
        db.commit()
        return redirect("/dashboard")
    return render_template("vault.html")

@app.route('/vault-details')
def vault_details():
    if 'User_ID' not in session:
        return redirect('/login')

    user_id = session['User_ID']
    cursor = db.cursor()
    cursor.execute("""
        SELECT ID, Website_URL, Username, Password
        FROM WebsiteVault
        WHERE User=%s
        ORDER BY Created_At DESC LIMIT 3
    """, (user_id,))
    pwd_rows = cursor.fetchall()
    passwords = [(r[0], r[1], r[2], fernet.decrypt(r[3].encode()).decode()) for r in pwd_rows]
    cursor.execute("""
        SELECT CNO, CardNo, Expiry, Remainder
        FROM CardVault
        WHERE User=%s
        ORDER BY Created_At DESC LIMIT 3
    """, (user_id,))
    cards = cursor.fetchall()
    cursor.execute("""
        SELECT NoteNo, Notes
        FROM NoteVault
        WHERE User=%s
        ORDER BY Created_At DESC LIMIT 3
    """, (user_id,))
    notes = cursor.fetchall()
    cursor.execute("""
        SELECT APINo, Service, API_Key
        FROM ApiVault
        WHERE User=%s
        ORDER BY Created_At DESC LIMIT 3
    """, (user_id,))
    api_rows = cursor.fetchall()
    apis = [(r[0], r[1], fernet.decrypt(r[2].encode()).decode()) for r in api_rows]
    return render_template(
        "vault-details.html",
        passwords=passwords,
        cards=cards,
        notes=notes,
        apis=apis
    )

@app.route('/update/password/<int:id>', methods=['POST'])
def update_password(id):
    user_id = session['User_ID']
    website = request.form['site']
    username = request.form['username']
    password = request.form['password']

    encrypted_pw = fernet.encrypt(password.encode()).decode()

    cursor = db.cursor()
    cursor.execute("""
        UPDATE WebsiteVault 
        SET Website_URL=%s, Username=%s, Password=%s, Updated_At=NOW()
        WHERE ID=%s AND User=%s
    """, (website, username, encrypted_pw, id, user_id))
    db.commit()

    return redirect('/vault-details')

@app.route('/update/card/<int:id>', methods=['POST'])
def update_card(id):
    user_id = session['User_ID']
    card_no = request.form['card_no']
    expiry = request.form['expiry']
    note = request.form['note']

    cursor = db.cursor()
    cursor.execute("""
        UPDATE CardVault 
        SET CardNo=%s, Expiry=%s, Remainder=%s, Updated_At=NOW()
        WHERE CNO=%s AND User=%s
    """, (card_no, expiry, note, id, user_id))
    db.commit()

    return redirect('/vault-details')

@app.route('/update/note/<int:id>', methods=['POST'])
def update_note(id):
    user_id = session['User_ID']
    note = request.form['note']

    cursor = db.cursor()
    cursor.execute("""
        UPDATE NoteVault 
        SET Notes=%s, Updated_At=NOW()
        WHERE NoteNo=%s AND User=%s
    """, (note, id, user_id))
    db.commit()

    return redirect('/vault-details')

@app.route('/update/api/<int:id>', methods=['POST'])
def update_api(id):
    user_id = session['User_ID']
    service = request.form['service']
    apikey = request.form['apikey']

    encrypted_key = fernet.encrypt(apikey.encode()).decode()

    cursor = db.cursor()
    cursor.execute("""
        UPDATE ApiVault 
        SET Service=%s, API_Key=%s, Updated_At=NOW()
        WHERE APINo=%s AND User=%s
    """, (service, encrypted_key, id, user_id))
    db.commit()
    return redirect('/vault-details')

@app.route('/delete_website/<int:id>', methods=['POST'])
def delete_website(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM WebsiteVault WHERE id = %s", (id,))
    db.commit()
    return redirect('/vault-details')


@app.route('/delete_card/<int:id>', methods=['POST'])
def delete_card(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM CardVault WHERE CNO = %s", (id,))
    db.commit()
    return redirect('/vault-details')


@app.route('/delete_note/<int:id>', methods=['POST'])
def delete_note(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM NoteVault WHERE noteno = %s", (id,))
    db.commit()
    return redirect('/vault-details')


@app.route('/delete_api/<int:id>', methods=['POST'])
def delete_api(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM APIVault WHERE apino = %s", (id,))
    db.commit()
    return redirect('/vault-details')

if __name__ == "__main__":
    app.run(debug=True)
