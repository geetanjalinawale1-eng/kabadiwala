# Person 3 testing

Before claiming the ML part is complete:

- Add the real `ewaste_mobilenetv3.tflite`.
- Test at least one image from every class.
- Confirm output is `{material, confidence}`.
- Record actual validation/test accuracy.
- Do not invent accuracy values.
- Ensure the model output class order matches `labels.txt`.

Backend contract:
POST /classify
multipart field: image

Example response:
{"material":"pcb","confidence":0.91}
