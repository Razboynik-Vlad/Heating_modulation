from dataclasses import dataclass


@dataclass(frozen=True)
class BoardMaterial:
    name: str
    alpha: float
    description: str


MATERIALS = {
    "gel": BoardMaterial(
        name="gel",
        alpha=0.16,
        description="среда со средней теплопроводностью",
    ),
    "water": BoardMaterial(
        name="water",
        alpha=0.22,
        description="тепло распространяется быстрее",
    ),
    "dense paste": BoardMaterial(
        name="dense paste",
        alpha=0.10,
        description="тепло распространяется медленнее",
    ),
}


ELEMENT_TYPES = {
    "insulator": {
        "alpha_multiplier": 0.20,
        "cooling": 0.00,
        "label": "insulator",
    },
    "conductor": {
        "alpha_multiplier": 2.20,
        "cooling": 0.00,
        "label": "conductor",
    },
    "cooler": {
        "alpha_multiplier": 1.00,
        "cooling": 0.18,
        "label": "cooler",
    },
}
