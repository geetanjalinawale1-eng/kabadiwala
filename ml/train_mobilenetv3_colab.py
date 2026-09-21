import tensorflow as tf

DATASET_DIR = "/content/dataset"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42
CLASSES = [
    "pcb","copper_cable","battery","lcd_crt",
    "motor","mobile_phone","charger_adapter","keyboard_mouse"
]

train = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR, class_names=CLASSES, validation_split=0.2,
    subset="training", seed=SEED, image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)
val = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR, class_names=CLASSES, validation_split=0.2,
    subset="validation", seed=SEED, image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

base = tf.keras.applications.MobileNetV3Small(
    input_shape=IMG_SIZE+(3,), include_top=False,
    weights="imagenet", pooling="avg"
)
base.trainable = False

inputs = tf.keras.Input(shape=IMG_SIZE+(3,))
x = tf.keras.layers.RandomFlip("horizontal")(inputs)
x = tf.keras.layers.RandomRotation(0.08)(x)
x = tf.keras.applications.mobilenet_v3.preprocess_input(x)
x = base(x, training=False)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(len(CLASSES), activation="softmax")(x)
model = tf.keras.Model(inputs, outputs)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)
model.fit(train, validation_data=val, epochs=8)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite = converter.convert()

with open("/content/ewaste_mobilenetv3.tflite", "wb") as f:
    f.write(tflite)

print("Saved /content/ewaste_mobilenetv3.tflite")
print("Class order:", CLASSES)
