import os
import sqlite3
import hashlib
import pyotp
import qrcode
# Function to generate TOTP URI
def generate_totp_uri(email, key, app):
    totp = pyotp.totp.TOTP(key)
    uri = totp.provisioning_uri(name=email, issuer_name='FlaskProject')

    # Save QR code image to a file
    img = qrcode.make(uri)
    img_path = os.path.join(app.static_folder, 'qrcodes', 'QRcode.png')
    img.save(img_path)

    return uri, img_path


def get_totp_secret_for_user(user):
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()

    cur.execute("SELECT totp_secret FROM users WHERE email=? OR username=?", (user[1], user[2]))
    totp_secret = cur.fetchone()

    con.close()

    return totp_secret[0] if totp_secret else None





def verify_totp(totp_secret, totp_input):
    print("TOTP Secret:", totp_secret)
    print("Input TOTP:", totp_input)

    totp = pyotp.TOTP(totp_secret)
    result = totp.verify(totp_input)

    print("Verification Result:", result)

    return result


def get_user_by_username_or_email(identity):
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email=? OR username=?", (identity, identity))
    user = cur.fetchone()
    con.close()
    return user


def store_totp_secret(email, totp_secret):
    con = sqlite3.connect('Blog.db')
    cur = con.cursor()
    cur.execute("UPDATE users SET totp_secret=? WHERE email=?", (totp_secret, email))
    con.commit()
    con.close()
