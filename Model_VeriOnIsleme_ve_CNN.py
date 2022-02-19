from keras.datasets import mnist
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.models import Sequential
from keras.utils import np_utils

# MNIST Veri Setini Yükleme
(X_train, y_train), (X_test, y_test) = mnist.load_data()

X_train = X_train.reshape(X_train.shape[0], 28, 28, 1).astype("float32")
X_test = X_test.reshape(X_test.shape[0], 28, 28, 1).astype("float32")

X_train = X_train / 255
X_test = X_test / 255

y_train = np_utils.to_categorical(y_train)
y_test = np_utils.to_categorical(y_test)

sinif_sayisi = y_test.shape[1]


def model():
    # modeli olustuyorum
    model = Sequential()
    model.add(Conv2D(30, (5, 5), input_shape=(28, 28, 1)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D())
    model.add(Conv2D(15, (3, 3)))
    model.add(Activation("relu"))
    model.add(MaxPooling2D())

    model.add(Flatten())
    model.add(Dense(375))
    model.add(Activation("relu"))
    model.add(Dropout(0.3))
    model.add(Dense(150))
    model.add(Activation("relu"))
    model.add(Dropout(0.1))
    model.add(Dense(sinif_sayisi, activation="softmax"))

    # modeli derliyorum
    model.compile(
        loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
    )
    return model


model = model()

# Modeli MNIST Veri Seti ile egitiyorum
model.fit(
    X_train,
    y_train,
    validation_data=(X_test, y_test),
    epochs=20,
    batch_size=150,
    shuffle=True,
)
model.save("mnist_model.h5")  # Modeli klasore kaydediyorum

# Modeli MNIST Test verisi ile test edip basari oranini olcuyorum
scores = model.evaluate(X_test, y_test, verbose=0)
print("Başarı Oranı:  %{0:.2f}".format(scores[1] * 100))

# Modelin Genel yapisi
# keras.utils.plot_model(model, "model.png", show_shapes=True)

# model.summary()
