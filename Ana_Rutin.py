import datetime
import os

import gradio as gr
import keras
import numpy as np
from PIL import Image

import RakamKirpmaVeOnIsleme
import Veritabani_islemleri

model = keras.models.load_model("mnist_model.h5")  # Egitilen modeli yukluyorum
resimler = os.getcwd() + "\\static\\"


def rakam_tanima(Resim, Resim_Kaydedilsin_mi):
    islenmis_resim = RakamKirpmaVeOnIsleme.resimden_rakam_kirpma(Resim)
    islenmis_resim = (
        RakamKirpmaVeOnIsleme.resime_cerceve_ekleme_ve_yeniden_boyutlandirma(
            islenmis_resim
        )
    )

    islenmis_resim = islenmis_resim.reshape(1, 28, 28, 1).astype("float32")
    islenmis_resim = islenmis_resim / 255

    tahmin1 = model.predict(islenmis_resim).tolist()[0]
    tahmin2 = model.predict([islenmis_resim])[0]
    tahmin_edilen_rakam, rakam_dogrulugu = np.argmax(tahmin2), max(tahmin2)

    tahmin_edilen_rakam = str(tahmin_edilen_rakam)
    rakam_dogrulugu = "%" + str(round(rakam_dogrulugu * 100, 2))

    if Resim_Kaydedilsin_mi == "Evet":
        sabit_isim = "resim"
        ek_isim = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
        resim_adi = "_".join([sabit_isim, ek_isim])

        resim_veri = Image.fromarray(Resim)
        resim_veri.save(resimler + resim_adi + ".png", format="png")

        resim_yol = resim_adi + ".png"

        Veritabani_islemleri.degiskenleri_al(
            resim_yol, tahmin_edilen_rakam, rakam_dogrulugu
        )
        Veritabani_islemleri.veritabani_kayit_ekle()
    Veritabani_islemleri.calistir_threading()

    return {str(i): tahmin1[i] for i in range(10)}


output_component = gr.outputs.Label(label="Tahmin", type="auto", num_top_classes=2)
gr.Interface(
    fn=rakam_tanima,
    inputs=["sketchpad", gr.inputs.Radio(["Hayır", "Evet"])],
    outputs=output_component,
    allow_screenshot=False,
    allow_flagging=False,
    theme="compact",
    article="""# **El Yazısı Rakam Tanıma Projesine Hoşgeldiniz.**
- Beyaz Alana bir Rakam Çizin (0 - 9 arasında).
- Submit butonuna tıklayarak sonucu görebilirsiniz. En yakın 2 sonuç gösterilir.
- Resimi Veritabanına kaydetmek için "Evet" kutusunu işaretleyip tekrar Submit butonuna basın.
- Veritabanında resim, resim tahmini, tahminin doğruluğu bilgileri tutulmaktadır. 
- Ayrıca veritabanında doğru tanınan resimler, onay kutusu ile işaretlenerek başarı oranı hesaplanmaktadır.""",
).launch(inbrowser=True, share=False)
