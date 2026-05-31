PRESETS = {
    "balanced defense": {
        "ice": {"x": 58, "y": 38, "size": 14},
        "source": {"x": 20, "y": 18, "power": 15.0, "sigma": 5.0},
        "elements": [
            {"type": "insulator", "x": 40, "y": 28, "w": 10, "h": 22},
            {"type": "cooler", "x": 55, "y": 18, "w": 18, "h": 8},
            {"type": "conductor", "x": 20, "y": 45, "w": 10, "h": 20},
        ],
    },
    "bad layout": {
        "ice": {"x": 58, "y": 38, "size": 14},
        "source": {"x": 24, "y": 32, "power": 16.0, "sigma": 5.0},
        "elements": [
            {"type": "conductor", "x": 41, "y": 35, "w": 12, "h": 20},
            {"type": "insulator", "x": 10, "y": 55, "w": 14, "h": 12},
            {"type": "cooler", "x": 8, "y": 8, "w": 16, "h": 10},
        ],
    },
    "strong shield": {
        "ice": {"x": 62, "y": 44, "size": 14},
        "source": {"x": 18, "y": 18, "power": 18.0, "sigma": 5.0},
        "elements": [
            {"type": "insulator", "x": 43, "y": 28, "w": 12, "h": 34},
            {"type": "cooler", "x": 56, "y": 24, "w": 20, "h": 10},
            {"type": "insulator", "x": 38, "y": 17, "w": 8, "h": 16},
        ],
    },
}
