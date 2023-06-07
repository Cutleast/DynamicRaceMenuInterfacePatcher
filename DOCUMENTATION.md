# Overview

##### This documentation always refers to the latest version of the patcher!

Patches are done in two major steps. At first they are created in FFDec itself and then they get documented in a "patch.json" file for the automated patcher.
A patch consists of two parts; a "patch.json" with the specifications and instructions for the patcher and a "shapes" folder containing the shapes that will replace the RaceMenu shapes.

### Requirements for creating patches

- FFDec
  - you have to know how to use it, of course
- (Skyrim) UI modding in general
- basic knowledge about JSON syntax

### Things that can be patched automatically using the patcher

- Shapes (svg files recommended; use png files at your own risk!)
- Shape Bounds
- Sprite Matrixes
- Color Transforms
- Texts (font and color)

# Patch file structure

A patch.json contains a list of all SWF files that are modified by the patch and their respective modifications. An example patch.json can be found below.

`patch.json`:

```json
{
    "racesex_menu.swf": { // File name of the file that gets modified
        "shapes": [
            {
                "index": [1], // Shape IDs to apply shape file to
                "filePath": "shapes/shape1.svg",
                "shapeBounds": { // This gets applied 1:1 to the SWF
                    "Xmax": "200",
                    "Ymax": "200",
                    "Xmin": "0",
                    "Ymin": "0"
                }
            }
        ],
        "text": [
            {
                "index": [3], // Can contain multiple indexes
                "font": "54", // Font ID used in FFDec
                "useOutlines": "true", // Either "true" or "false"
                "color": "000000ff" // Hex color without '#' but with alpha (last two digits)
            }
        ],
        "sprites": [
            {
                "SpriteID": "1",
                "CharacterID": ["20"], // Can contain multiple ids or "*" for all characters
                "Depth": ["1"], // Can contain multiple depths or "*" for all depths
                "MATRIX": { // This gets applied 1:1 to the SWF
                    "translateX": "100",
                    "translateY": "-100",
                    "scaleX": "1",
                    "scaleY": "45",
                    "rotateSkew0": "90",
                    "rotateSkew1": "175",
                    "hasScale": "true",
                    "hasRotate": "true"
                },
                "colorTransform": { // This gets applied 1:1 to the SWF
                    "hasAddTerms": "false",
                    "hasMultTerms": "true",
                    "redMultTerm": "256"
                }
            }
        ]
    }
}
```

# Patch folder structure

A patch folder consists of the patch.json in the root folder and the shapes in a "shapes" folder.

`Example patch`:

```
data (in Skyrim's installation directory)
└── Example patch (root folder)
    ├── patch.json
    └── shapes
        ├── shape_1.svg
        └── shape_2.svg
```
