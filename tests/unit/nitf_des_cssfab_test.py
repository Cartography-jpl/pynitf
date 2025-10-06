from pynitf import NitfFile


def test_read_rip(nitf_sample_rip):
    """Test reading the reference SNIP sample file"""
    f = NitfFile(nitf_sample_rip)
    des = [d for d in f.des_segment if d.subheader.desid == "CSSFAB"][0]
    print(des)
