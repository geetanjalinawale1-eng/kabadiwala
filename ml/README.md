# KabadiSetu Person 3 - ML/AI

## Prototype pipeline
Photo -> MobileNetV3 -> e-waste material -> confidence

## E-waste classes
1. PCB
2. Copper Cable
3. Battery
4. LCD/CRT
5. Motor
6. Mobile Phone
7. Charger/Adapter
8. Keyboard/Mouse

The output contract is:
```json
{"material":"pcb","confidence":0.91}
```

## IMPORTANT
The team's old `recycling_model.tflite` was trained for:
cardboard, glass, metal, paper, plastic.

It cannot be converted into an e-waste model simply by changing class names.
A new model must be trained/fine-tuned on labelled e-waste images.

The trained file must be placed at:
`ml/models/ewaste_mobilenetv3.tflite`

Then test:
```bash
pip install -r ml/requirements.txt
python ml/classify.py sample.jpg
```

For the SIH prototype, this is the correct ML structure:
dataset -> MobileNetV3 training -> TFLite -> classify.py -> backend /classify -> Flutter.
