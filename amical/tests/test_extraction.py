import astropy
import munch
import pytest
from astropy.io import fits
from packaging.version import Version

from amical.mf_pipeline.bispect import _add_infos_header


# Astropy versions for
ASTROPY_VERSION = Version(astropy.__version__)
ASTROPY_WORKING = Version("5.0rc")


@pytest.fixture()
def infos():
    # SimulatedData avoids requiring extra keys in infos
    return munch.Munch(orig="SimulatedData", instrument="unknown")


@pytest.fixture()
def commentary_hdr():
    # Create a fits header with commentary card
    hdr = fits.Header()
    hdr["HISTORY"] = "History is a commentary card"
    return hdr


@pytest.fixture()
def commentary_infos(infos, commentary_hdr):

    # Add hdr to infos placeholders for everything but hdr
    mf = munch.Munch(pixelSize=1.0)

    return _add_infos_header(
        infos, commentary_hdr, mf, 1.0, "afilename", "amaskname", 1
    )


def test_add_infos_simulated(infos):
    # Ensure that keys are passed to infos for simulated data, but only when available

    # Create a fits header with two keywords that are usually passed to infos
    hdr = fits.Header()
    hdr["DATE-OBS"] = "2021-06-23"
    hdr["TELESCOP"] = "FAKE-TEL"

    # Add hdr to infos placeholders for everything but hdr
    mf = munch.Munch(pixelSize=1.0)
    infos = _add_infos_header(infos, hdr, mf, 1.0, "afilename", "amaskname", 1)

    assert infos["date-obs"] == hdr["DATE-OBS"]
    assert infos["telescop"] == hdr["TELESCOP"]
    assert "observer" not in infos  # Keys that are not in hdr should not be in infos
    assert "observer" not in infos.hdr  # Keys that are not in hdr should still not be


def test_add_infos_header_commentary(commentary_infos):
    # Make sure that _add_infos_header handles _HeaderCommentaryCards from astropy

    # Convert everything to munch object
    munch.munchify(commentary_infos)


@pytest.mark.skipif(
    ASTROPY_VERSION < ASTROPY_WORKING,
    reason="Munch cannot handle commentary cards for Astropy < 5.0",
)
def test_commentary_infos_keep(commentary_infos):
    assert "HISTORY" in commentary_infos.hdr


@pytest.mark.skipif(
    ASTROPY_VERSION >= ASTROPY_WORKING,
    reason="Munch can handle commentary cards for Astropy 5.0+",
)
@pytest.mark.xfail(
    ASTROPY_VERSION < ASTROPY_WORKING,
    reason="AMICAL removes commentary cards from header with Astropy < 5.0",
)
def test_commentary_infos_drops(commentary_infos):
    assert "HISTORY" in commentary_infos.hdr


def test_astropy_version_warning(infos, commentary_hdr, capfd):
    # Test that AMICAL warns about astropy < 5.0 removing commentary cards

    # Add hdr to infos placeholders for everything but hdr
    mf = munch.Munch(pixelSize=1.0)

    infos = _add_infos_header(
        infos, commentary_hdr, mf, 1.0, "afilename", "amaskname", 1
    )
    captured = capfd.readouterr()

    if ASTROPY_VERSION < ASTROPY_WORKING:
        # NOTE: Adding colors codes because output with cprint has them
        msg = (
            "\x1b[32mCommentary cards are removed from the header with astropy"
            f" version < {ASTROPY_WORKING}. Your astropy version is"
            f" {ASTROPY_VERSION}\x1b[0m\n"
        )
        assert captured.out == msg
    else:
        assert not captured.out
