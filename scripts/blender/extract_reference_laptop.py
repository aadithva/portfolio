"""Rectify only the printed laptop lid; exclude the desk, edge bevel and shadows.

The source offers about 190 pixels across this surface. The 512px output is a
filtered web texture, not recovered detail. No generative fill or invented art.
"""
from pathlib import Path
import argparse
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--photo', type=Path, default=Path('/Users/aadith/Downloads/IMG_4813 2.jpg'))
args = parser.parse_args()
photo = Image.open(args.photo).convert('RGB')
width, height = 512, 328
# TL, TR, BR, BL, measured inside the lid's border in the supplied 1206x1548 image.
corners = [(527, 951), (684, 931), (712, 1017), (527, 1042)]
source = [(x * photo.width / 1206, y * photo.height / 1548) for x, y in corners]
destination = [(0, 0), (width, 0), (width, height), (0, height)]
matrix, values = [], []
for (x, y), (u, v) in zip(destination, source):
    matrix.extend([[x, y, 1, 0, 0, 0, -u*x, -u*y], [0, 0, 0, x, y, 1, -v*x, -v*y]])
    values.extend([u, v])
augmented = [list(map(float, row)) + [float(value)] for row, value in zip(matrix, values)]
for column in range(8):
    pivot = max(range(column, 8), key=lambda row: abs(augmented[row][column]))
    augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
    divisor = augmented[column][column]
    augmented[column] = [value / divisor for value in augmented[column]]
    for row in range(8):
        if row == column:
            continue
        factor = augmented[row][column]
        augmented[row] = [a - factor*b for a, b in zip(augmented[row], augmented[column])]
coefficients = [row[-1] for row in augmented]
lid = photo.transform((width, height), Image.Transform.PERSPECTIVE, coefficients, Image.Resampling.BICUBIC)
# Restrained white balance removes the lamp's warm cast from printed whites.
# There is no hard cast shadow on this selected face, so no fabricated relighting.
lid = Image.merge('RGB', tuple(channel.point(lambda value, gain=gain: round(min(255, value*gain)))
                              for channel, gain in zip(lid.split(), [.96, 1.015, 1.13])))
output = ROOT / 'public/textures/workspace/reference-laptop-albedo.jpg'
lid.save(output, quality=94, optimize=True)
print(output)
