from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from src.materials import ELEMENT_TYPES


@dataclass
class Element:
    type: str
    x: int
    y: int
    w: int
    h: int


@dataclass
class SimulationConfig:
    n: int
    material_alpha: float
    ambient_temp: float
    initial_ice_temp: float
    ice_x: int
    ice_y: int
    ice_size: int
    source_x: int
    source_y: int
    source_power: float
    source_sigma: float
    steps: int
    dt: float
    latent_temperature: float
    boundary_loss: float
    elements: list[Element]


@dataclass
class SimulationResult:
    temperature_history: np.ndarray
    final_temperature: np.ndarray
    ice_fraction_history: np.ndarray
    ice_mask: np.ndarray
    source_field: np.ndarray
    alpha_map: np.ndarray
    cooling_map: np.ndarray
    score: float
    max_temperature: float
    final_ice_percent: float
    melted_at_step: int | None


def rect_mask(n: int, x: int, y: int, w: int, h: int) -> np.ndarray:
    mask = np.zeros((n, n), dtype=bool)
    x0 = max(0, int(x))
    y0 = max(0, int(y))
    x1 = min(n, int(x + w))
    y1 = min(n, int(y + h))
    mask[y0:y1, x0:x1] = True
    return mask


def make_maps(config: SimulationConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = config.n
    alpha_map = np.ones((n, n), dtype=float) * config.material_alpha
    cooling_map = np.ones((n, n), dtype=float) * config.boundary_loss

    for element in config.elements:
        params = ELEMENT_TYPES[element.type]
        mask = rect_mask(n, element.x, element.y, element.w, element.h)
        alpha_map[mask] *= params["alpha_multiplier"]
        cooling_map[mask] += params["cooling"]

    yy, xx = np.mgrid[0:n, 0:n]
    source_field = config.source_power * np.exp(
        -((xx - config.source_x) ** 2 + (yy - config.source_y) ** 2)
        / (2.0 * config.source_sigma ** 2)
    )

    ice_mask = rect_mask(
        n,
        config.ice_x,
        config.ice_y,
        config.ice_size,
        config.ice_size,
    )

    return alpha_map, cooling_map, source_field, ice_mask


def laplacian(field: np.ndarray) -> np.ndarray:
    padded = np.pad(field, 1, mode="edge")
    return (
        padded[1:-1, 2:]
        + padded[1:-1, :-2]
        + padded[2:, 1:-1]
        + padded[:-2, 1:-1]
        - 4.0 * field
    )


def run_simulation(config: SimulationConfig) -> SimulationResult:
    n = config.n
    alpha_map, cooling_map, source_field, ice_mask = make_maps(config)

    temperature = np.ones((n, n), dtype=float) * config.ambient_temp
    temperature[ice_mask] = config.initial_ice_temp

    liquid_fraction = np.zeros((n, n), dtype=float)

    temperature_history = []
    ice_fraction_history = []
    melted_at_step = None

    record_every = max(1, config.steps // 120)

    for step in range(config.steps + 1):
        if step % record_every == 0 or step == config.steps:
            temperature_history.append(temperature.copy())
            ice_left = 1.0 - float(liquid_fraction[ice_mask].mean())
            ice_fraction_history.append(max(0.0, ice_left))

        if step == config.steps:
            break

        diffusion = alpha_map * laplacian(temperature)
        cooling = cooling_map * (temperature - config.ambient_temp)
        delta_temp = config.dt * (diffusion + source_field - cooling)

        new_temperature = temperature + delta_temp

        cold_ice = ice_mask & (liquid_fraction < 1.0) & (new_temperature < 0.0)
        melting_ice = ice_mask & (liquid_fraction < 1.0) & (new_temperature >= 0.0)

        excess = np.maximum(new_temperature[melting_ice], 0.0)
        liquid_fraction[melting_ice] += excess / config.latent_temperature
        liquid_fraction[melting_ice] = np.clip(liquid_fraction[melting_ice], 0.0, 1.0)

        still_melting = ice_mask & (liquid_fraction < 1.0) & (new_temperature >= 0.0)
        new_temperature[still_melting] = 0.0
        new_temperature[cold_ice] = new_temperature[cold_ice]

        temperature = new_temperature

        current_ice_left = 1.0 - float(liquid_fraction[ice_mask].mean())
        if melted_at_step is None and current_ice_left <= 0.02:
            melted_at_step = step

    final_ice_percent = ice_fraction_history[-1] * 100.0
    max_temperature = float(temperature.max())
    score = final_ice_percent - 0.2 * max(0.0, max_temperature - 50.0)

    return SimulationResult(
        temperature_history=np.array(temperature_history),
        final_temperature=temperature,
        ice_fraction_history=np.array(ice_fraction_history),
        ice_mask=ice_mask,
        source_field=source_field,
        alpha_map=alpha_map,
        cooling_map=cooling_map,
        score=score,
        max_temperature=max_temperature,
        final_ice_percent=final_ice_percent,
        melted_at_step=melted_at_step,
    )


def build_config_from_preset(
    preset: dict,
    material_alpha: float,
    ambient_temp: float,
    steps: int,
    dt: float,
    elements: list[dict] | None = None,
) -> SimulationConfig:
    selected_elements = elements if elements is not None else preset["elements"]

    return SimulationConfig(
        n=80,
        material_alpha=material_alpha,
        ambient_temp=ambient_temp,
        initial_ice_temp=-8.0,
        ice_x=preset["ice"]["x"],
        ice_y=preset["ice"]["y"],
        ice_size=preset["ice"]["size"],
        source_x=preset["source"]["x"],
        source_y=preset["source"]["y"],
        source_power=preset["source"]["power"],
        source_sigma=preset["source"]["sigma"],
        steps=steps,
        dt=dt,
        latent_temperature=80.0,
        boundary_loss=0.005,
        elements=[
            Element(
                type=item["type"],
                x=item["x"],
                y=item["y"],
                w=item["w"],
                h=item["h"],
            )
            for item in selected_elements
        ],
    )


def find_best_insulator_position(
    preset: dict,
    material_alpha: float,
    ambient_temp: float,
    steps: int,
    dt: float,
) -> tuple[dict, SimulationResult]:
    candidates = []
    base_elements = [item for item in preset["elements"] if item["type"] != "insulator"]

    for x in range(24, 56, 8):
        for y in range(16, 56, 8):
            elements = base_elements + [
                {"type": "insulator", "x": x, "y": y, "w": 10, "h": 24},
            ]
            config = build_config_from_preset(
                preset,
                material_alpha,
                ambient_temp,
                steps,
                dt,
                elements=elements,
            )
            result = run_simulation(config)
            candidates.append((result.score, elements[-1], result))

    candidates.sort(key=lambda item: item[0], reverse=True)
    _, best_element, best_result = candidates[0]
    return best_element, best_result
