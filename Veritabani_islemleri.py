import os
import sqlite3
import sys
import threading
import webbrowser

from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import InternalServerError

sys.tracebacklimit = 0  # traceback görüntülenmemesi için
vt = sqlite3.connect("veritabani.db", check_same_thread=False)
im = vt.cursor()
im.execute("""SELECT * FROM resim_tahmin__tablo""")
veriler = (
    im.fetchall()
)  # tablodaki verileri fetchall fonksiyonu ile veriler değişkenine alıyorum


def veri_guncelle():
    global vt, im
    im.execute("""SELECT * FROM resim_tahmin__tablo""")
    return (
        im.fetchall()
    )  # tablodaki verileri fetchall fonksiyonu ile veriler değişkenine alıyorum


app = Flask("veritabani")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///veritabani.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class resim_tahmin__tablo(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    resim_yol = db.Column(db.String, unique=True, nullable=False)
    tahmin = db.Column(db.String, unique=False, nullable=False)
    dogruluk = db.Column(db.String, unique=False, nullable=False)
    tahmin_dogru_mu = db.Column(
        db.String, unique=False, nullable=False, default="unchecked"
    )


class basari_orani_tablo(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    basari_orani = db.Column(db.String, unique=False, nullable=False)


db.create_all()

gelen_resim_yol = ""
gelen_tahmin_edilen_rakam = ""
gelen_rakam_dogrulugu = ""


def degiskenleri_al(resim_yol, tahmin_edilen_rakam, rakam_dogrulugu):
    global gelen_resim_yol
    gelen_resim_yol = resim_yol

    global gelen_tahmin_edilen_rakam
    gelen_tahmin_edilen_rakam = tahmin_edilen_rakam

    global gelen_rakam_dogrulugu
    gelen_rakam_dogrulugu = rakam_dogrulugu


def veritabani_kayit_ekle():
    veri = (gelen_resim_yol, gelen_tahmin_edilen_rakam, gelen_rakam_dogrulugu)

    im.execute(
        """INSERT INTO resim_tahmin__tablo (resim_yol,tahmin,dogruluk) VALUES
                (?, ?, ?)""",
        veri,
    )
    vt.commit()


@app.route("/giris", methods=["GET", "POST"])
def giris():
    hata = None
    if request.method == "POST":
        if request.form["username"] != "admin" or request.form["password"] != "admin":
            hata = "Giriş Bilgileri Yanlış. Tekrar Deneyin!"
        else:
            return redirect(url_for("Veritabani_Goruntule"))
    return render_template("giris_sayfasi.html", hata=hata)


@app.route("/")
def Veritabani_Goruntule():
    Veritabani_Goruntule = resim_tahmin__tablo.query.paginate()
    basari_orani_filtre = basari_orani_tablo.query.filter_by(id=1).first()
    return render_template(
        "veritabani_sayfasi.html",
        Veritabani_Goruntule=Veritabani_Goruntule,
        basari_orani=basari_orani_filtre.basari_orani,
    )


id_listesi = []


@app.route("/", methods=["GET", "POST"])
def tablo_guncelleme():
    if request.method == "POST":
        veritabani_tum_veriler = veri_guncelle()
        chckbox_secili_liste = request.form.getlist("thmn")

        global id_listesi
        for i in range(len(veritabani_tum_veriler)):
            id_listesi.append(veritabani_tum_veriler[i][0])

        if len(veritabani_tum_veriler) == 0:
            basari_orani = "Veri Yok"
            im.execute(
                """UPDATE basari_orani_tablo SET basari_orani = (?) WHERE id = 1""",
                (basari_orani,),
            )
            vt.commit()
        else:
            basari_orani_int = (
                len(chckbox_secili_liste) / len(veritabani_tum_veriler)
            ) * 100
            basari_orani = "%" + str(round(basari_orani_int, 2))

            im.execute(
                """UPDATE basari_orani_tablo SET basari_orani = (?) WHERE id = 1""",
                (basari_orani,),
            )
            vt.commit()

        for i in chckbox_secili_liste:
            veri = i
            im.execute(
                """UPDATE resim_tahmin__tablo SET tahmin_dogru_mu = 'checked' WHERE id = (?)""",
                (veri,),
            )
            vt.commit()

        for y in id_listesi:
            y = str(y)
            if y not in chckbox_secili_liste:
                veri = y
                im.execute(
                    """UPDATE resim_tahmin__tablo SET tahmin_dogru_mu = 'unchecked' WHERE id = (?)""",
                    (veri,),
                )
                vt.commit()
        id_listesi = []

    return redirect(url_for("Veritabani_Goruntule"))


app.secret_key = "super secret key"


@app.route("/delete/<int:id>", methods=["POST", "GET"])
def Veritabani_SatirSil(id):
    try:
        veri = resim_tahmin__tablo.query.get(id)
        id_satir = resim_tahmin__tablo.query.filter_by(id=id).first()
        resim_adi = id_satir.resim_yol
        yol = os.path.join(os.getcwd() + "\\static\\", resim_adi)
        os.remove(yol)

        db.session.delete(veri)
        db.session.commit()
        return redirect(url_for("Veritabani_Goruntule"))
    except Exception as e:
        print("Hata: " + str(e))


@app.errorhandler(InternalServerError)
def handle_500(e):
    original = getattr(e, "Hata", None)
    return render_template("hata_sayfasi.html", e=original)


i = 0


def calistir():
    global i
    i = i + 1
    if i == 1:
        webbrowser.open_new("http://127.0.0.1:5000/giris")
        app.run(debug=False)


def calistir_threading():
    t1 = threading.Thread(target=calistir)
    t1.start()
