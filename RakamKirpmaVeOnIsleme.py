import cv2 as cv
import numpy as np
from PIL import Image


def resimden_rakam_kirpma(resim_ndarray):
    ilk_satir = np.nonzero(resim_ndarray)[0].min()
    son_satir = np.nonzero(resim_ndarray)[0].max()

    ilk_sutun = np.nonzero(resim_ndarray)[1].min()
    son_sutun = np.nonzero(resim_ndarray)[1].max()

    resim_array = resim_ndarray[ilk_satir : son_satir + 1, ilk_sutun : son_sutun + 1]

    return resim_array


def resime_cerceve_ekleme_ve_yeniden_boyutlandirma(resim_ndarray):
    # Kirpilan rakama 6px boyutunda siyah cerceve ekliyorum
    siyah = [0, 0, 0]
    resim_cerceve = cv.copyMakeBorder(
        resim_ndarray, 6, 6, 6, 6, cv.BORDER_CONSTANT, value=siyah
    )

    # Rakam kirpildigi ve cerceve eklendigi icin resim boyutunu 28*28 yapiyorum
    resim = Image.fromarray(resim_cerceve)
    resim = resim.resize((28, 28), Image.LANCZOS)

    return np.array(resim)
