# Thesis_Code_Data_6866018
Code snippets (.py and .R) for the Msc thesis of Sten Dijk (SN-6866810)

Certain scripts were generated using AI prompts or a combination of manual and generated input, which is indicated in each script.
The scripts have been tested and checked for consistency, but might not work or need to be slightly adjusted when using other models or data formats.

Training and Detection scripts were slightly altered from the original given by Theuerkauf et al (2023) (https://github.com/alexander-g/Tofsi-POST) (https://doi.org/10.1177/09596836231211876).

All the classes list for first run:
# ===============================
# CLASSES (MATCH JSON EXACTLY)
# ===============================
classes_of_interest = [
    "Cor", "Aln", "Ile", "Rob", "Spo", "Pin", "Phi", "Poa", "Che",
    "Bet", "Dry", "Ole", "Pub", "Car", "Lyc", "Pic", "Pih", "For",
    "Ulm", "Spr", "Ost", "Pch", "Ace", "Rod", "Fra", "Lig", "Fag",
    "Sph", "Jug", "Glo", "Spa", "Cyp", "Hip", "Sal", "Cer", "Vit",
    "Din", "Vul", "Crc", "Tub", "Aqu", "The", "Men", "Eri", "Frx",
    "Art", "Tas", "Oen", "Gal", "Api", "Rum", "Til", "Pot", "Hyp",
    "Bra", "Cas", "Ran", "Ros", "Lan", "Asp", "Tri", "Tha", "Jac",
    "Cir", "Abi", "Abh"
]

classes_nonpollen = ["Nonpollen"]
classes_lowconf = ["Ind"]

With conditions:
epochs=10, lr=0.01, num_workers=0, )

Classes second run:
# ===============================
# CLASSES (ONLY PRESENT IN 3 CORRECTED SLIDES)
# ===============================
classes_of_interest = [
    "Lyc", "Spo", "Rob", "Poa", "Aln", "Fag", "Dry", "Ost", "Cyp",
    "Pch", "Ile", "For", "Lig", "Cor", "Glo", "Pih", "Pin", "Crc",
    "Phi", "Jug", "Aqu", "Sal", "Che", "Ole", "Sph", "Spa", "Car",
    "Ulm", "Art", "Rod", "Pic", "Tas", "Din", "Tub", "Hyp", "Ros",
    "Bet", "Cas", "Rum", "Frx", "Med", "Gal", "Api", "Oen", "Fra"
]
With conditions:

    epochs=4,   # small number of epochs for 3 slides
    lr=0.003,   # gentle fine-tuning
    num_workers=0,
)
    "Ulm", "Art", "Rod", "Pic", "Tas", "Din", "Tub", "Hyp", "Ros",
    "Bet", "Cas", "Rum", "Frx", "Med", "Gal", "Api", "Oen", "Fra"
