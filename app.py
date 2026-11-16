
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

import os
import sqlite3
import uuid
import secrets

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import init_db
from voice_auth import compare_voices


app = Flask(__name__)

# Use an environment variable for the secret key.
# A development fallback is provided for local testing.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "replace-this-development-key-before-deployment"
)

VOICE_FOLDER = "voice_samples"
os.makedirs(VOICE_FOLDER, exist_ok=True)

VOICE_THRESHOLD = 0.50


# ----------------------------------
# HOME
# ----------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------------
# REGISTRATION
# ----------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or len(password) < 8:
            return render_template(
                "register.html",
                message="Enter a username and a password of at least 8 characters."
            )

        password_hash = generate_password_hash(password)

        connection = sqlite3.connect("users.db")

        try:
            connection.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
                """,
                (username, password_hash)
            )

            connection.commit()

            # Authorise voice enrollment for this new account only.
            session.clear()
            session["enrollment_username"] = username

            return render_template(
                "register.html",
                username=username,
                message="Registration successful! Now record your voice."
            )

        except sqlite3.IntegrityError:

            session.clear()

            return render_template(
                "register.html",
                message="Username already exists. Choose another one."
            )

        finally:
            connection.close()

    session.clear()
    return render_template("register.html")


# ----------------------------------
# LOGIN
# ----------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = sqlite3.connect("users.db")

        user = connection.execute(
            """
            SELECT password_hash, voice_file
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        connection.close()

        if user is None:

            session.clear()

            return render_template(
                "login.html",
                message="Account not found."
            )

        if not check_password_hash(user[0], password):

            session.clear()

            return render_template(
                "login.html",
                message="Incorrect password."
            )

        if not user[1]:

            session.clear()

            return render_template(
                "login.html",
                username=username,
                message="No voice registered. Please register your voice first."
            )

        session.clear()
        session["pending_username"] = username

        return render_template(
            "login.html",
            username=username,
            message="Password correct! Now verify your voice."
        )

    session.clear()

    return render_template(
        "login.html",
        message=request.args.get("message")
    )


# ----------------------------------
# SAVE REGISTERED VOICE
# ----------------------------------

@app.route("/save-voice", methods=["POST"])
def save_voice():

    username = request.form.get("username", "").strip()

    # Only the account currently authorised for enrollment can upload.
    if not username or session.get("enrollment_username") != username:
        return jsonify({
            "message": "Voice enrollment not authorised. Please register first."
        }), 401

    if "audio" not in request.files:
        return jsonify({
            "message": "No audio file received."
        }), 400

    audio = request.files["audio"]

    if not audio.filename:
        return jsonify({
            "message": "No audio file selected."
        }), 400

    connection = sqlite3.connect("users.db")

    user = connection.execute(
        "SELECT voice_file FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if user is None:
        connection.close()

        return jsonify({
            "message": "User not found. Register first."
        }), 404

    filename = f"{uuid.uuid4()}.webm"
    filepath = os.path.join(VOICE_FOLDER, filename)

    old_voice = user[0]

    try:

        audio.save(filepath)

        connection.execute(
            """
            UPDATE users
            SET voice_file = ?
            WHERE username = ?
            """,
            (filename, username)
        )

        connection.commit()

        # End the enrollment permission after successful upload.
        session.pop("enrollment_username", None)

        # Remove the previous sample if one existed.
        if old_voice:
            old_path = os.path.join(VOICE_FOLDER, old_voice)

            if os.path.isfile(old_path):
                os.remove(old_path)

    except Exception:

        if os.path.exists(filepath):
            os.remove(filepath)

        raise

    finally:
        connection.close()

    return jsonify({
        "message": "Voice recording saved and linked to your account!"
    })


# ----------------------------------
# VOICE LOGIN VERIFICATION
# ----------------------------------

@app.route("/verify-voice", methods=["POST"])
def verify_voice():

    username = request.form.get("username", "").strip()

    if session.get("pending_username") != username:
        return jsonify({
            "message": "Please log in with your password first."
        }), 401

    if "audio" not in request.files:
        return jsonify({
            "message": "No audio received."
        }), 400

    connection = sqlite3.connect("users.db")

    user = connection.execute(
        "SELECT voice_file FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    connection.close()

    if user is None or not user[0]:
        return jsonify({
            "message": "No registered voice found."
        }), 404

    reference_path = os.path.join(VOICE_FOLDER, user[0])

    if not os.path.isfile(reference_path):
        return jsonify({
            "message": "Registered voice recording is missing."
        }), 404

    test_path = os.path.join(
        VOICE_FOLDER,
        f"verify_{uuid.uuid4()}.webm"
    )

    request.files["audio"].save(test_path)

    try:

        similarity = compare_voices(reference_path, test_path)

        if similarity >= VOICE_THRESHOLD:

            session.clear()
            session["username"] = username

            verified = True
            message = "Voice verified! Access granted."

        else:

            verified = False
            message = "Voice does not match. Access denied."

        return jsonify({
            "verified": verified,
            "similarity": round(similarity, 3),
            "message": message
        })

    except Exception as error:

        return jsonify({
            "message": f"Could not process voice recording: {error}"
        }), 400

    finally:

        if os.path.exists(test_path):
            os.remove(test_path)


# ----------------------------------
# DASHBOARD
# ----------------------------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


# ----------------------------------
# LOGOUT
# ----------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ----------------------------------
# FORGOT PASSWORD
# ----------------------------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        username = request.form.get("username", "").strip()

        connection = sqlite3.connect("users.db")

        user = connection.execute(
            "SELECT voice_file FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if user is None or not user[0]:

            session.clear()

            return render_template(
                "forgot_password.html",
                message="Account not found or no voice registered."
            )

        session.clear()
        session["recovery_pending"] = username

        return render_template(
            "forgot_password.html",
            username=username,
            voice_ready=True
        )

    session.clear()

    return render_template("forgot_password.html")


# ----------------------------------
# VERIFY VOICE FOR PASSWORD RECOVERY
# ----------------------------------

@app.route("/recover-verify", methods=["POST"])
def recover_verify():

    username = request.form.get("username", "").strip()

    if session.get("recovery_pending") != username:
        return jsonify({
            "message": "Please enter your username again."
        }), 401

    if "audio" not in request.files:
        return jsonify({
            "message": "No voice recording received."
        }), 400

    connection = sqlite3.connect("users.db")

    user = connection.execute(
        "SELECT voice_file FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    connection.close()

    if user is None or not user[0]:
        return jsonify({
            "message": "Registered voice not found."
        }), 404

    reference_path = os.path.join(VOICE_FOLDER, user[0])

    if not os.path.isfile(reference_path):
        return jsonify({
            "message": "Registered voice recording is missing."
        }), 404

    test_path = os.path.join(
        VOICE_FOLDER,
        f"recovery_{uuid.uuid4()}.webm"
    )

    request.files["audio"].save(test_path)

    try:

        similarity = compare_voices(reference_path, test_path)

        if similarity >= VOICE_THRESHOLD:

            session.pop("recovery_pending", None)
            session["recovery_verified"] = username

            verified = True
            message = "Identity verified! You can reset your password."

        else:

            verified = False
            message = "Voice does not match. Password recovery denied."

        return jsonify({
            "verified": verified,
            "similarity": round(similarity, 3),
            "message": message
        })

    except Exception as error:

        return jsonify({
            "message": f"Could not process voice recording: {error}"
        }), 400

    finally:

        if os.path.exists(test_path):
            os.remove(test_path)


# ----------------------------------
# RESET PASSWORD
# ----------------------------------

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    username = session.get("recovery_verified")

    if not username:
        return redirect(url_for("forgot_password"))

    if request.method == "POST":

        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(password) < 8:

            return render_template(
                "reset_password.html",
                message="Password must contain at least 8 characters."
            )

        if password != confirm_password:

            return render_template(
                "reset_password.html",
                message="Passwords do not match."
            )

        password_hash = generate_password_hash(password)

        connection = sqlite3.connect("users.db")

        connection.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE username = ?
            """,
            (password_hash, username)
        )

        connection.commit()
        connection.close()

        session.clear()

        return redirect(url_for(
            "login",
            message="Password reset successful! Please log in."
        ))

    return render_template("reset_password.html")


# ----------------------------------
# START APPLICATION
# ----------------------------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)
