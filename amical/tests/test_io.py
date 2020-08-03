from pathlib import Path

import munch
import numpy as np
import pytest
from astropy.io import fits

import amical
from amical import load, loadc
from amical.get_infos_obs import get_pixel_size

TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / "data"
example_oifits = TEST_DATA_DIR / "test.oifits"
example_fits = TEST_DATA_DIR / "test.fits"


@pytest.mark.parametrize("filepath", [example_oifits])
def test_load_file(filepath):
    s = load(filepath)
    assert isinstance(s, dict)


@pytest.mark.parametrize("filepath", [example_fits])
def test_open_fits(filepath):
    hdu = fits.open(filepath)
    cube = hdu[0].data
    hdu.close()
    assert isinstance(cube, np.ndarray)


@pytest.mark.slow
@pytest.mark.parametrize("filepath", [example_fits])
def test_extraction(filepath):
    hdu = fits.open(filepath)
    cube = hdu[0].data
    hdu.close()
    method = ['fft', 'gauss', 'square']
    for m in method:
        params_ami = {"peakmethod": m,
                      "bs_multi_tri": False,
                      "maskname": "g7",
                      "fw_splodge": 0.7,
                      }
        bs = amical.extract_bs(cube, filepath, targetname='test',
                               **params_ami, display=False)
        assert isinstance(bs, munch.Munch)


@pytest.mark.slow
@pytest.mark.parametrize("filepath", [example_fits])
def test_calibration(filepath):
    hdu = fits.open(filepath)
    cube = hdu[0].data
    hdu.close()
    params_ami = {"peakmethod": 'fft',
                  "bs_multi_tri": False,
                  "maskname": "g7",
                  "fw_splodge": 0.7,
                  }
    bs = amical.extract_bs(cube, filepath, targetname='test',
                           **params_ami, display=False)
    cal = amical.calibrate(bs, bs)
    assert isinstance(cal, munch.Munch)


@pytest.mark.slow
@pytest.mark.parametrize("filepath", [example_fits])
def test_show(filepath):
    hdu = fits.open(filepath)
    cube = hdu[0].data
    hdu.close()
    params_ami = {"peakmethod": 'fft',
                  "bs_multi_tri": False,
                  "maskname": "g7",
                  "fw_splodge": 0.7,
                  }
    bs = amical.extract_bs(cube, filepath, targetname='test',
                           **params_ami, display=False)
    cal = amical.calibrate(bs, bs)
    amical.show(cal)


@pytest.mark.slow
@pytest.mark.parametrize("filepath", [example_fits])
def test_save(filepath):
    hdu = fits.open(filepath)
    cube = hdu[0].data
    hdu.close()
    params_ami = {"peakmethod": 'fft',
                  "bs_multi_tri": False,
                  "maskname": "g7",
                  "fw_splodge": 0.7,
                  }
    bs = amical.extract_bs(cube, filepath, targetname='test',
                           **params_ami, display=False)
    cal = amical.calibrate(bs, bs)
    amical.save(cal, fake_obj=True)


@pytest.mark.parametrize("filepath", [example_oifits])
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_candid(filepath):

    param_candid = {'rmin': 20,
                    'rmax': 250,
                    'step': 100,
                    'ncore': 1
                    }
    fit1 = amical.candid_grid(filepath, **param_candid)
    assert isinstance(fit1, dict)


@pytest.mark.parametrize("filepath", [example_oifits])
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_candid_multiproc(filepath):

    param_candid = {'rmin': 20,
                    'rmax': 250,
                    'step': 100,
                    'ncore': 4
                    }
    fit1 = amical.candid_grid(filepath, **param_candid)
    assert isinstance(fit1, dict)


@pytest.mark.parametrize("filepath", [example_oifits])
def test_pymask(filepath):
    fit1 = amical.pymask_grid(str(filepath))
    assert isinstance(fit1, dict)
    fit2 = amical.pymask_grid([filepath])
    assert isinstance(fit2, dict)


@pytest.mark.parametrize("filepath", [example_oifits])
def test_loadc_file(filepath):
    s = loadc(filepath)
    assert isinstance(s, munch.Munch)


@pytest.mark.parametrize("ins", ['NIRISS', 'SPHERE', 'VAMPIRES'])
def test_getPixel(ins):
    p = get_pixel_size(ins)
    assert isinstance(p, float)
