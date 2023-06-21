# Components with hierarchy

![](https://i.imgur.com/3pczkyM.png)

You can define components Parametric cells (waveguides, bends, couplers) with basic input parameters (width, length, radius ...) and reuse the PCells in more complex PCells.

```python
from functools import partial
import toolz

from gdsfactory.typings import ComponentSpec, Optional, CrossSectionSpec

import gdsfactory as gf
from gdsfactory.generic_tech import get_generic_pdk

gf.config.rich_output()
PDK = get_generic_pdk()
PDK.activate()
```


**Problem**

When using hierarchical cells where you pass `N` subcells with `M` parameters you can end up with `N*M` parameters. This is make code hard to read.


```python
@gf.cell
def bend_with_straight_with_too_many_input_parameters(
    bend=gf.components.bend_euler,
    straight=gf.components.straight,
    length: float = 3,
    angle: float = 90.0,
    p: float = 0.5,
    with_arc_floorplan: bool = True,
    npoints: Optional[int] = None,
    direction: str = "ccw",
    with_bbox: bool = True,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """ "As hierarchical cells become more complex, the number of input parameters can increase significantly."""
    c = gf.Component()
    b = bend(
        angle=angle,
        p=p,
        with_arc_floorplan=with_arc_floorplan,
        npoints=npoints,
        direction=direction,
        with_bbox=with_bbox,
        cross_section=cross_section,
    )
    s = straight(length=length, with_bbox=with_bbox, cross_section=cross_section)

    bref = c << b
    sref = c << s

    sref.connect("o2", bref.ports["o2"])
    c.info["length"] = b.info["length"] + s.info["length"]
    return c


c = bend_with_straight_with_too_many_input_parameters()
c
```


**Solution**

You can use a ComponentSpec parameter for every subcell. The ComponentSpec can be a dictionary with arbitrary number of settings, a string, or a function.

## ComponentSpec

When defining a `Parametric cell` you can use other `ComponentSpec` as an arguments. It can be a:

1. string: function name of a cell registered on the active PDK. `"bend_circular"`
2. dict: `dict(component='bend_circular', settings=dict(radius=20))`
3. function: Using `functools.partial` you can customize the default parameters of a function.


```python
@gf.cell
def bend_with_straight(
    bend: ComponentSpec = gf.components.bend_euler,
    straight: ComponentSpec = gf.components.straight,
) -> gf.Component:
    """Much simpler version.

    Args:
        bend: input bend.
        straight: output straight.
    """
    c = gf.Component()
    b = gf.get_component(bend)
    s = gf.get_component(straight)

    bref = c << b
    sref = c << s

    sref.connect("o2", bref.ports["o2"])
    c.info["length"] = b.info["length"] + s.info["length"]
    return c


c = bend_with_straight()
c
```

### 1. string

You can use any string registered in the `Pdk`. Go to the PDK tutorial to learn how to register cells in a PDK.

```python
c = bend_with_straight(bend="bend_circular")
c
```

### 2. dict

You can pass a dict of settings.

```python
c = bend_with_straight(bend=dict(component="bend_circular", settings=dict(radius=20)))
c
```

### 3. function

You can pass a function of a function with customized default input parameters `from functools import partial`

Partial lets you define different default parameters for a function, so you can modify the default settings for each child cell.

```python
c = bend_with_straight(bend=partial(gf.components.bend_circular, radius=30))
c
```

```python
bend20 = partial(gf.components.bend_circular, radius=20)
b = bend20()
b
```

```python
type(bend20)
```

```python
bend20.func.__name__
```

```python
bend20.keywords
```

```python
b = bend_with_straight(bend=bend20)
print(b.metadata["info"]["length"])
b
```

```python
# You can still modify the bend to have any bend radius
b3 = bend20(radius=10)
b3
```

## PDK custom fab

You can define a new PDK by creating function that customize partial parameters of the generic functions.

Lets say that this PDK uses layer (41, 0) for the pads (instead of the layer used in the generic pad function).

```python
pad_custom_layer = partial(gf.components.pad, layer=(41, 0))
```

```python
c = pad_custom_layer()
c
```

## Composing functions

You can combine more complex functions out of smaller functions.

Lets say that we want to add tapers and grating couplers to a wide waveguide.

```python
c1 = gf.components.straight()
c1
```

```python
straight_wide = partial(gf.components.straight, width=3)
c3 = straight_wide()
c3
```

```python
c1 = gf.components.straight(width=3)
c1
```

```python
c2 = gf.add_tapers(c1)
c2
```

```python
c2.metadata_child["changed"]  # You can still access the child metadata
```

```python
c3 = gf.routing.add_fiber_array(c2, with_loopback=False)
c3
```

```python
c3.metadata_child["changed"]  # You can still access the child metadata
```

Lets do it with a **single** step thanks to `toolz.pipe`

```python
add_fiber_array = partial(gf.routing.add_fiber_array, with_loopback=False)
add_tapers = gf.add_tapers

# pipe is more readable than the equivalent add_fiber_array(add_tapers(c1))
c3 = toolz.pipe(c1, add_tapers, add_fiber_array)
c3
```

we can even combine `add_tapers` and `add_fiber_array` thanks to `toolz.compose` or `toolz.compose`

For example:

```python
add_tapers_fiber_array = toolz.compose_left(add_tapers, add_fiber_array)
c4 = add_tapers_fiber_array(c1)
c4
```

is equivalent to

```python
c5 = add_fiber_array(add_tapers(c1))
c5
```

as well as equivalent to

```python
add_tapers_fiber_array = toolz.compose(add_fiber_array, add_tapers)
c6 = add_tapers_fiber_array(c1)
c6
```

or

```python
c7 = toolz.pipe(c1, add_tapers, add_fiber_array)
c7
```

```python
c7.metadata_child["changed"]  # You can still access the child metadata
```

```python
c7.metadata["child"]["child"]["name"]
```

```python
c7.metadata["child"]["child"]["function_name"]
```

```python
c7.metadata["changed"].keys()
```