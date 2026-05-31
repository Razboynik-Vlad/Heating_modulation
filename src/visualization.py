from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


ELEMENT_COLORS = {
    "insulator": "white",
    "conductor": "black",
    "cooler": "cyan",
}


def value_of(item, name):
    if isinstance(item, dict):
        return item[name]
    return getattr(item, name)


def draw_rect(ax, x: int, y: int, w: int, h: int, label: str, edgecolor: str) -> None:
    rect = patches.Rectangle(
        (x, y),
        w,
        h,
        linewidth=1.8,
        edgecolor=edgecolor,
        facecolor="none",
    )
    ax.add_patch(rect)
    ax.text(
        x + w / 2,
        y + h / 2,
        label,
        ha="center",
        va="center",
        fontsize=8,
        color=edgecolor,
        weight="bold",
    )


def plot_temperature_frame(temperature, result, config, elements, title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 6))

    vmax = max(35.0, float(result.max_temperature), float(np.max(temperature)))

    image = ax.imshow(
        temperature,
        origin="lower",
        cmap="coolwarm",
        vmin=-8,
        vmax=vmax,
    )

    draw_rect(
        ax,
        config.ice_x,
        config.ice_y,
        config.ice_size,
        config.ice_size,
        "ice",
        "deepskyblue",
    )

    ax.scatter(
        [config.source_x],
        [config.source_y],
        s=120,
        c="red",
        marker="*",
        label="heat source",
    )

    for element in elements:
        element_type = value_of(element, "type")
        draw_rect(
            ax,
            int(value_of(element, "x")),
            int(value_of(element, "y")),
            int(value_of(element, "w")),
            int(value_of(element, "h")),
            element_type,
            ELEMENT_COLORS[element_type],
        )

    ax.set_title(title)
    ax.set_xlabel("x cell")
    ax.set_ylabel("y cell")
    ax.set_xlim(0, config.n - 1)
    ax.set_ylim(0, config.n - 1)
    fig.colorbar(image, ax=ax, label="temperature, c")
    fig.tight_layout()
    return fig


def plot_temperature(result, config, elements) -> plt.Figure:
    return plot_temperature_frame(
        result.final_temperature,
        result,
        config,
        elements,
        "final temperature field",
    )


def plot_ice_curve(result, config, until_index: int | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 3))

    full_time_axis = np.linspace(
        0,
        config.steps * config.dt,
        len(result.ice_fraction_history),
    )

    if until_index is None:
        time_axis = full_time_axis
        ice_values = result.ice_fraction_history
    else:
        until_index = max(1, min(until_index, len(result.ice_fraction_history)))
        time_axis = full_time_axis[:until_index]
        ice_values = result.ice_fraction_history[:until_index]

    ax.plot(time_axis, ice_values * 100.0, linewidth=2)
    ax.set_title("ice mass over time")
    ax.set_xlabel("time, s")
    ax.set_ylabel("ice left, percent")
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
