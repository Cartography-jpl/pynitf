from pynitf import (
    NitfImageWriteNumpy,
    NitfImageSegment,
    NitfDesSegment,
    DesCSEPHB,
    DesCSATTB,
    NitfResRaw,
    NitfResSegment,
    NitfGraphicSegment,
    NitfGraphicRaw,
    NitfTextStr,
    NitfTextSegment,
    TreUSE00A,
)
import json
import numpy as np
import subprocess
import pytest
import re
from importlib import util


def cmd_exists(cmd):
    """Check if a cmd exists by using type, which returns a nonzero status if
    the program isn't found"""
    return (
        subprocess.call(
            "type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        == 0
    )


def create_image_seg(
    f, security=None, iid1="", row_offset=10, bias=0, adjust=None, nrow=9, ncol=10
):
    """Create a small image segment. The security setting can be passed in,
    otherwise the default unclassified version is used. The IID can be passed.
    The values filled in can be controlled by row_offset, bias, and adjust."""
    img = NitfImageWriteNumpy(nrow, ncol, np.uint8)
    for i in range(nrow):
        for j in range(ncol):
            img[0, i, j] = i * row_offset + j
    iseg = NitfImageSegment(img, security=security)
    iseg.iid1 = iid1
    f.image_segment.append(iseg)
    return iseg


def create_tre(f, angle_to_north=270):
    """Create a sample TRE. We use TreUSE00A because it is a simple TRE. You
    can pass in different values to angle_to_north to get "different" TREs.
    """
    t = TreUSE00A()
    t.angle_to_north = angle_to_north
    t.mean_gsd = 105.2
    t.dynamic_range = 2047
    t.obl_ang = 34.12
    t.roll_ang = -21.15
    t.n_ref = 0
    t.rev_num = 3317
    t.n_seg = 1
    t.max_lp_seg = 6287
    t.sun_el = 68.5
    t.sun_az = 131.3
    f.tre_list.append(t)


def create_text_segment(f, first_name="Guido", textid="ID12345", security=None):
    """Create a text segment"""
    d = {
        "first_name": first_name,
        "second_name": "Rossum",
        "titles": ["BDFL", "Developer"],
    }
    ts = NitfTextSegment(NitfTextStr(json.dumps(d)), security=security)
    ts.subheader.textid = textid
    ts.subheader.txtalvl = 0
    ts.subheader.txtitl = "sample title"
    f.text_segment.append(ts)


def create_graphic_segment(
    f, graphic_data=b"fake graph data", graphicid="GID12345", security=None
):
    """Create a graphic segment"""
    gs = NitfGraphicSegment(NitfGraphicRaw(graphic_data), security=security)
    gs.subheader.sid = graphicid
    gs.subheader.sname = "Fake graphic"
    gs.subheader.salvl = 0
    f.graphic_segment.append(gs)


def create_res_segment(f, res_data=b"fake res data", resid="GID12345", security=None):
    """Create a res segment"""
    rs = NitfResSegment(NitfResRaw(res_data), security=security)
    rs.subheader.resid = resid
    f.res_segment.append(rs)


def create_des(f, date_att=20170501, q=0.1, num=5, security=None):
    """Create a DES segment"""
    des = DesCSATTB()
    ds = des.user_subheader
    ds.id = "4385ab47-f3ba-40b7-9520-13d6b7a7f311"
    ds.numais = "010"
    for i in range(int(ds.numais)):
        ds.aisdlvl[i] = 5 + i
    ds.reservedsubh_len = 0

    des.qual_flag_att = 1
    des.interp_type_att = 1
    des.att_type = 1
    des.eci_ecf_att = 0
    des.dt_att = 900.5
    des.date_att = 20170501
    des.t0_att = 235959.100001000
    des.num_att = num
    for n in range(des.num_att):
        des.q1[n] = q
        des.q2[n] = q
        des.q3[n] = q
        des.q4[n] = q
    des.reserved_len = 0

    de = NitfDesSegment(des, security=security)
    f.des_segment.append(de)


def create_csephb(f, date_att=20170501, e=0.1, num=5, security=None):
    """Create a DES segment"""
    des = DesCSEPHB()
    ds = des.user_subheader
    ds.id = "4385ab47-f3ba-40b7-9520-13d6b7a7f311"
    ds.numais = "010"
    for i in range(int(ds.numais)):
        ds.aisdlvl[i] = 5 + i
    ds.reservedsubh_len = 0

    des.qual_flag_eph = 1
    des.interp_type_eph = 1
    des.ephem_flag = 1
    des.eci_ecf_ephem = 0
    des.dt_ephem = 900.5
    des.date_ephem = 20170501
    des.t0_ephem = 235959.100001000
    des.num_ephem = num
    for n in range(des.num_ephem):
        des.ephem_x[n] = e
        des.ephem_y[n] = e
        des.ephem_z[n] = e
    des.reserved_len = 0

    de = NitfDesSegment(des, security=security)
    f.des_segment.append(de)


def gdal_value(f, line, sample, band=None):
    """Return value at the given location, according to gdal. This is
    return as a bytes, which you can then cast to the desired type
    (e.g., int())"""
    cmd = ["gdallocationinfo", "-valonly"]
    if band is not None:
        cmd.extend(["-b", str(band + 1)])
    cmd.extend([f, str(sample), str(line)])
    res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE).stdout
    # Complex numbers need special handling, because gdallocationinfo doesn't
    # write a string that python knows how to parse.
    if b"+" in res or b"i" in res:
        res = (b"(" + re.sub(b"i", b"j", res.rstrip()) + b")\n").decode("utf-8")
    return res


require_gdal_value = pytest.mark.skipif(
    not cmd_exists("gdallocationinfo"),
    reason="Require gdallocationinfo",
)

require_git = pytest.mark.skipif(not cmd_exists("git"), reason="Require git")

require_h5py = pytest.mark.skipif(
    util.find_spec("h5py") is None, reason="need to have h5py available to run."
)
