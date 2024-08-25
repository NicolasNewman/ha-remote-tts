# Demo: glados-tts

Based off of the GLaDOS TSS model by [R2D2FISH](https://github.com/R2D2FISH/glados-tts)

## Usage

1. Download the models from the above repository and place them in `/examples/glados-tts/models/`
2. Install dependencies & start the demo:

```sh
# in pyproject.toml, ensure python version is set to ">=3.10,<3.12"
poetry install --with demo-glados-tts
cd ./examples/glados-tts
python demo.py
```
