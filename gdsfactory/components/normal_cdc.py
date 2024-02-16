from __future__ import annotations
import math
from functools import partial
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.components.straight import straight as straight_function
from gdsfactory.cross_section import CrossSectionSpec


def round_up(number, decimals=0):
    multiplier = 10**decimals
    return math.ceil(number * multiplier) / multiplier


def round_down(number, decimals=0):
    multiplier = 10**decimals
    return math.floor(number * multiplier) / multiplier


@gf.cell
def simple_contra_dc(
    w1 = 0.450, #width of waveguide 1
    w2 = 0.350, #width of waveguide 2
    gap= 0.200, #gap between waveguides and between the middle of the corrugations from waveguide 1 and 2
    dw1 = 0.050, #corrugation width of waveguide 1
    dw2 = 0.050, # corrugation width of waveguide 2
    wg_io = 0.500, #system waveguide
    n = 100, #number of corrugations
    p = 0.3, #period/pitch of corrugations
    cross_section: CrossSectionSpec = "xs_sc_no_pins",
    **kwargs,
) -> gf.Component:
    """ Contra-Directional Coupler

    Args:
    w1: width of waveguide 1
    w2: width of waveguide 2
    gap: gap between waveguides and between the middle of the corrugations from waveguide 1 and 2
    dw1: corrugation width of waveguide 1
    dw2: corrugation width of waveguide 2
    wg_io: system waveguide
    n: number of corrugations
    p: period/pitch of corrugations
    layer_core: core layer
    layer_port: port layer
    """

    sbend_h = 3  # Height of the SBend
    sbend_l = 12  # Length of the SBend
    tapper_l = 15  # Length of the taper

    length_a = round_up((p / 2), decimals=3)
    length_b = round_down((p / 2), decimals=3)

    dw1 = (round((dw1 / 4) * 1000) / 1000) * 4
    dw2 = (round((dw2 / 4) * 1000) / 1000) * 4

    profile1 = dw1 / 2
    profile2 = dw2 / 2

    c = gf.Component("contra_dc")

    halfp_ref = []

    wgt = gf.Component(name="TopWG")
    wgb = gf.Component(name="BotWG")

    # --- Draw bragg waveguides ---
    # - Top waveguide
    for i in range(0, n, 1):
        halfp_l = gf.components.straight(
            length_a, width=w1, cross_section=cross_section, add_pins=False
        )
        halfp_ref.append(wgt << halfp_l)

        if i >= 1:
            halfp_ref[-1].xmin = halfp_ref[-2].xmax

        halfp_ref[-1].movey(profile1)

        halfp_r = gf.components.straight(
            length_b, width=w1, cross_section=cross_section, add_pins=False
        )

        halfp_ref.append(wgt << halfp_r)
        halfp_ref[-1].xmin = halfp_ref[-2].xmax

        halfp_ref[-1].movey(-profile1)

        del halfp_r, halfp_l

    # --- Fanout waveguides ---
    # -  Top waveguide
    aux_cs = partial(gf.cross_section.cross_section, width=w1, cross_section=cross_section)
    bndwg = gf.components.bend_s(
        (sbend_l, sbend_h), cross_section=aux_cs, add_pins=False
    )
    inwgb_r_w1 = wgt << bndwg.mirror((0, 1), (0, 0))
    aux_cs = partial(gf.cross_section.cross_section, width=w1, cross_section=cross_section)
    obndwg = gf.components.bend_s(
        (sbend_l, sbend_h), cross_section=aux_cs, add_pins=False
    )
    outwgb_r_w1 = wgt << obndwg

    inwgb_r_w1.connect("o1", halfp_ref[0].ports["o1"])

    outwgb_r_w1.connect("o1", halfp_ref[-1].ports["o2"])

    taperwgi = gf.components.taper(
        length=tapper_l,
        width2=w1,
        width1=wg_io,
        cross_section=aux_cs,
        add_pins=False,
    )
    taperwgo = gf.components.taper(
        length=tapper_l,
        width2=w1,
        width1=wg_io,
        cross_section=aux_cs,
        add_pins=False,
    )
    itappert_r = wgt << taperwgi
    otappert_r = wgt << taperwgo

    # - Bot waveguide
    halfp_ref = []
    for i in range(0, n, 1):
        halfp_l = gf.components.straight(
            length_a, width=w2, cross_section=cross_section, add_pins=False
        )
        halfp_ref.append(wgb << halfp_l)

        if i >= 1:
            halfp_ref[-1].xmin = halfp_ref[-2].xmax

        halfp_ref[-1].movey(-profile2 - gap - w1 / 2 - w2 / 2)

        halfp_r = gf.components.straight(
            length_b, width=w2, cross_section=cross_section, add_pins=False
        )

        halfp_ref.append(wgb << halfp_r)
        halfp_ref[-1].xmin = halfp_ref[-2].xmax

        halfp_ref[-1].movey(profile2 - gap - w1 / 2 - w2 / 2)

        del halfp_r, halfp_l

    # --- Fanout waveguides ---
    # - Bottom waveguide
    aux_cs = partial(gf.cross_section.cross_section, width=w2, cross_section=cross_section)
    bndwg = gf.components.bend_s(
        (sbend_l, sbend_h), cross_section=aux_cs, add_pins=False
    )
    taperwgi = gf.components.taper(
        length=tapper_l,
        width2=wg_io,
        width1=w2,
        cross_section=cross_section,
        add_pins=False,
    )
    taperwgo = gf.components.taper(
        length=tapper_l,
        width2=wg_io,
        width1=w2,
        cross_section=cross_section,
        add_pins=False,
    )
    inwgb_r = wgb << bndwg
    aux_cs = partial(gf.cross_section.cross_section, width=w2, cross_section=cross_section)
    obndwg = gf.components.bend_s(
        (sbend_l, sbend_h), cross_section=aux_cs, add_pins=False
    )
    outwgb_r = wgb << obndwg
    itapperb_r = wgb << taperwgi
    otapperb_r = wgb << taperwgo

    inwgb_r.connect("o2", halfp_ref[0].ports["o1"])
    outwgb_r.mirror_y()
    outwgb_r.connect("o1", halfp_ref[-1].ports["o2"])


    inwgb_r_w1.ymin = -w1 / 2
    outwgb_r_w1.ymin = -w1 / 2
    inwgb_r.y = inwgb_r.y + profile2
    outwgb_r.y = outwgb_r.y - profile2


    itappert_r.connect("o2", inwgb_r_w1.ports["o2"])
    otappert_r.connect("o2", outwgb_r_w1.ports["o2"])

    wgt.add_port("o1", port=itappert_r.ports["o1"])
    wgt.add_port("o2", port=otappert_r.ports["o1"])

    itapperb_r.connect("o1", inwgb_r.ports["o1"])
    otapperb_r.connect("o1", outwgb_r.ports["o2"])

    wgb.add_port("o1", port=itapperb_r.ports["o2"])
    wgb.add_port("o2", port=otapperb_r.ports["o2"])

    # Add wavegudies to contraDC component
    wgt_r = c << wgt
    wgb_r = c << wgb

    # Add optical ports to cdc component
    c.add_port("in", port=wgt_r.ports["o2"])
    c.add_port("drop", port=wgb_r.ports["o2"])
    c.add_port("through", port=wgt_r.ports["o1"])
    c.add_port("add", port=wgb_r.ports["o1"])
    c.auto_rename_ports()
    return c.flatten()


if __name__ == "__main__":
    c = simple_contra_dc()
    c.show(show_ports=True, show_subports=True)