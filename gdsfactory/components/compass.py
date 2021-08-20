from typing import Tuple

import gdsfactory as gf
from gdsfactory.cell import cell
from gdsfactory.component import Component
from gdsfactory.types import Layer


@cell
def compass(
    size: Tuple[float, float] = (4.0, 2.0),
    layer: Layer = gf.LAYER.WG,
    prefix: str = "e",
) -> Component:
    """Rectangular contact pad with centered ports on rectangle edges
    (north, south, east, and west)

    Args:
        size: tuple (4, 2)
        layer: tuple (int, int)

    """

    c = gf.Component()
    r = gf.components.rectangle(size=size, layer=layer)
    dx = size[0]
    dy = size[1]

    rr = r.ref(position=(-dx / 2, -dy / 2))
    c.add(rr)
    c.add_port(
        name=f"{prefix}1",
        midpoint=[-dx / 2, 0],
        width=dy,
        orientation=180,
        layer=layer,
    )
    c.add_port(
        name=f"{prefix}2", midpoint=[0, dy / 2], width=dx, orientation=90, layer=layer
    )
    c.add_port(
        name=f"{prefix}3", midpoint=[dx / 2, 0], width=dy, orientation=0, layer=layer
    )
    c.add_port(
        name=f"{prefix}4",
        midpoint=[0, -dy / 2],
        width=dx,
        orientation=-90,
        layer=layer,
    )
    return c


if __name__ == "__main__":
    c = compass(size=(1, 2), layer=gf.LAYER.WG)
    c.show()
