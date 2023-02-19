from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.components.straight import straight


@gf.cell
def coupler_straight_asymmetric(
    length: float = 10.0,
    gap: float = 0.27,
    width_top: float = 0.5,
    width_bot: float = 1,
    **kwargs,
) -> Component:
    """Coupler_straight_asymmetric with two parallel straights of different widths.

    Args:
        length: of straight.
        width_top: of top straight.
        width_bot: of bottom straight.
        gap: between straights.
        kwargs: cross_section settings.
    """
    component = Component()
    # straight_component = straight(length=length, **kwargs)

    top = component << straight(length=length, width=width_top, **kwargs)
    bot = component << straight(length=length, width=width_bot, **kwargs)

    top.movey(0.5 * abs(width_top - width_bot) + gap + width_top)

    component.add_port("o1", port=bot.ports["o1"])
    component.add_port("o2", port=top.ports["o1"])
    component.add_port("o3", port=bot.ports["o2"])
    component.add_port("o4", port=top.ports["o2"])
    component.auto_rename_ports()
    return component


if __name__ == "__main__":
    c = coupler_straight_asymmetric(length=5)
    c.show(show_ports=True)