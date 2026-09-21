from pathlib import Path
import numpy as np
from PIL import Image
import tensorflow as tf

# IMPORTANT: this model must be trained on the e-waste classes below.
E_WASTE_CLASSES = [
    "pcb",
    "copper_cable",
    "battery",
    "lcd_crt",
    "motor",
    "mobile_phone",
    "charger_adapter",
    "keyboard_mouse",
]

MODEL_PATH = Path(__file__).parent / "models" / "ewaste_mobilenetv3.tflite"

class EWasteClassifier:
    def __init__(self, model_path=MODEL_PATH):
        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Missing model: {model_path}. "
                "Add the trained e-waste TFLite model first."
            )
        self.interpreter = tf.lite.Interpreter(model_path=str(model_path))
        self.interpreter.allocate_tensors()
        self.input = self.interpreter.get_input_details()[0]
        self.output = self.interpreter.get_output_details()[0]
        shape = self.input["shape"]
        self.height, self.width = int(shape[1]), int(shape[2])

    def classify(self, image_path):
        image = Image.open(image_path).convert("RGB")
        image = image.resize((self.width, self.height))
        arr = np.asarray(image, dtype=np.float32)

        if self.input["dtype"] == np.uint8:
            arr = arr.astype(np.uint8)
        else:
            arr = (arr / 127.5) - 1.0

        arr = np.expand_dims(arr, axis=0)
        self.interpreter.set_tensor(self.input["index"], arr)
        self.interpreter.invoke()
        scores = self.interpreter.get_tensor(self.output["index"])[0]
        scores = np.asarray(scores, dtype=np.float32)

        # Convert logits to probabilities if necessary.
        if np.any(scores < 0) or not np.isclose(scores.sum(), 1.0, atol=0.05):
            e = np.exp(scores - scores.max())
            scores = e / e.sum()

        index = int(np.argmax(scores))
        return {
            "material": E_WASTE_CLASSES[index],
            "confidence": round(float(scores[index]), 2),
        }

_classifier = None

def classify_image(image_path):
    global _classifier
    if _classifier is None:
        _classifier = EWasteClassifier()
    return _classifier.classify(image_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    args = parser.parse_args()
    print(classify_image(args.image))
