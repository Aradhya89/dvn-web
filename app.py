from flask import Flask , render_template, request, redirect, session 
import dotenv
import cloudinary.uploader
import cloudinary 
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g
# from flask_wtf.csrf import CSRFProtect



def team_data():
    mycon = get_db()
    with mycon.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("select * from team_data ORDER BY id ")
        data = cur.fetchall()

    #to sort the data in the dictionary into key(id) and value (remaing data) form
    team_dict = {
        row["id"]: {k: v for k, v in row.items() if k != "id"}
        for row in data}
    return team_dict



# loading data from json file
# '''
# with open("team-data.json", "r") as f:
#     data = json.load(f)
# '''

dotenv.load_dotenv()
#mysql setup for database
# USER = os.getenv("SUPABASE_USER")
# PASSWORD = os.getenv("SUPABASE_PASSWORD")
# HOST = os.getenv("SUPABASE_HOST")
# PORT = os.getenv("SUPABASE_PORT")
# DBNAME = os.getenv("SUPABASE_DB")

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            os.environ["DATABASE_URL"],
            sslmode="require"
        )
    return g.db
# mycon = mq.connect(host= "localhost", user = "root", password = "root", database = "dvn")

# cloundinary setup for image uploading

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


app = Flask(__name__)
app.secret_key = os.getenv("SECRETKEY")
# csrf = CSRFProtect(app)

# to get to the main page
@app.route("/")
def home():
    return render_template("index.html",data = team_data() )


# to get to the team page
@app.route("/team")
def about():
    return render_template("team.html",data = team_data())

@app.route("/admin-login")
def admin_login_input():
    return render_template("adminlogin.html")

@app.route("/admin-login", methods=["POST"])
def admin_login():
    email = request.form["email"]
    password = request.form["password"]

    if email == os.getenv("Admin_Email") and password == os.getenv("Admin_Password"):
        session["admin"] = True
        return redirect("/admin")

    return "Invalid login"

@app.route("/delete/<uuid:id>", methods=["POST"])
def delete_message(id):
    mycon = get_db()
    with mycon.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("DELETE FROM contact WHERE id=%s", (str(id),))
        mycon.commit()
    return "", 204

@app.route("/admin-main")
def admin_main():
    if not session.get("admin"):
        return redirect("/admin-login")

    mycon = get_db()
    with mycon.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""SELECT name, email, message,TO_CHAR(time, 'DD Mon YYYY') AS date, TO_CHAR(time, 'HH12:MI AM') AS time_of_msg, id FROM contact ORDER BY time DESC """)
        data = cur.fetchall()
    return render_template("admin1.html", msg_data = data)
    
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin-login")

    return render_template("admin.html",data = team_data())

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



@app.route("/contact", methods=["POST"])
def contact():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]
    mycon = get_db()
    with mycon.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("insert into contact (name, email, message) values (%s,%s,%s)",(name,email,message))
        mycon.commit()
    return redirect("/?msg=success")


#when clicking edit button so redirect to editing page
@app.route("/admin/edit/<id>")
def edit_profile(id):
    if not session.get("admin"):
        return redirect("/admin-login")
    mycon = get_db()
    with mycon.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM team_data WHERE id=%s", (id,))
        member = cur.fetchone()
        print(member)
    return render_template("edit.html", member=member)


#backend for editing page 
@app.route("/admin/edit/<id>", methods=["POST"])
def update_profile(id):
    if not session.get("admin"):
        return redirect("/admin-login")
    name = request.form["name"]
    bio = request.form["bio"]
    ac1 = request.form["achievement1"]
    ac2 = request.form["achievement2"]
    ac3 = request.form["achievement3"]
    role = request.form["role"]
    image = request.files["image"]

    mycon = get_db()

    if image and image.filename != "":
        
        with mycon.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT public_id FROM team_data WHERE id=%s", (id,))
            old_public_id = cur.fetchone()["public_id"]

        # to delete the old photo from cloud database
        if old_public_id:
            cloudinary.uploader.destroy(old_public_id)

        #uploading new photo in cloud database
        result = cloudinary.uploader.upload(image,
                folder="club_profiles" #folder name

                ,transformation=[{
                "width": 300,
                "height": 300,
                "crop": "fill",
                "gravity": "face"}],
                quality="auto",
                fetch_format="auto"

                )

        image_url = result["secure_url"]
        image_publicid = result["public_id"]

        with mycon.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                    UPDATE team_data
                    SET name=%s, bio=%s, ac1=%s, ac2 = %s, ac3 = %s,photo_url=%s, public_id = %s,role = %s
                    WHERE id=%s
                """, (name, bio, ac1,ac2,ac3, image_url, image_publicid,role,id))
    else:
        with mycon.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                UPDATE team_data
                SET name=%s, bio=%s, ac1=%s, ac2 = %s, ac3 = %s,role = %s
                WHERE id=%s
            """, (name, bio, ac1,ac2,ac3,role,id))

    mycon.commit()
    return redirect("/admin")


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db:
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)