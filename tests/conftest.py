import pytest
import laspy
from pathlib import Path
import subprocess

_TEST_DIR = Path(__file__).parent
_TEST_DATA_DIR = _TEST_DIR.joinpath('data')
INPUT_FILE_DIR = _TEST_DATA_DIR.joinpath('input')
EXPECTED_FILE_DIR = _TEST_DATA_DIR.joinpath('expected')

COLORIZATION_RASTER_PATH = INPUT_FILE_DIR.joinpath('color.tif')
LAS_WITH_OLD_EB_NO_SRS_PATH = INPUT_FILE_DIR.joinpath('las_with_old_eb_no_srs.las')
LAZ_WITH_NEW_EB_PATH = INPUT_FILE_DIR.joinpath('laz_with_new_eb.laz')
LAZ_WITH_CLASS_34_PATH = INPUT_FILE_DIR.joinpath('laz_with_class_34.laz')
INPUT_PC_PATHS = [
    LAS_WITH_OLD_EB_NO_SRS_PATH,
    LAZ_WITH_NEW_EB_PATH,
    LAZ_WITH_CLASS_34_PATH,
]

EXPECTED_COLORIZED_PC_PATH = EXPECTED_FILE_DIR.joinpath('expected_colorized.las')

# Convenience fixtures providing laspy.lasdata.LasData representation for the
# input, actual output, and expected output
@pytest.fixture(scope='session')
def input_lasdata(input_path):
    lasdata = laspy.read(input_path)
    return lasdata

@pytest.fixture(scope='session')
def output_lasdata(output_path):
    lasdata = laspy.read(output_path)
    return lasdata

@pytest.fixture(scope='session')
def expected_lasdata():
    lasdata = laspy.read(EXPECTED_COLORIZED_PC_PATH)
    return lasdata

# Fixtures to exercise the different combinations of input arguments
@pytest.fixture(scope='session', params=[None, COLORIZATION_RASTER_PATH])
def colorization_raster(request):
    return request.param

@pytest.fixture(scope='session', params=[False, True])
def retain_extra_dims(request):
    return request.param

@pytest.fixture(scope='session', params=[False, True])
def write_compressed(request):
    return request.param

# The input pointcloud file, with the various formats
@pytest.fixture(scope='session', params=INPUT_PC_PATHS)
def input_path(request):
    return request.param

# The availability of the output_path fixture implies that the file has been written
@pytest.fixture(scope='session')
def output_path(input_path, colorization_raster, retain_extra_dims, write_compressed, tmp_path_factory):
    if write_compressed:
        output_extension = 'laz'
    else:
        output_extension = 'las'
    tmp_output_dir = tmp_path_factory.mktemp('tmp_output_dir')
    _output_path = tmp_output_dir.joinpath(f'output.{output_extension}')

    call_args = [
        'dvrwarp',
        str(input_path),
        str(_output_path),
    ]
    if colorization_raster is not None:
        call_args += [
            '--color-raster',
            str(colorization_raster),
        ]
    if retain_extra_dims:
        call_args += ['--retain-extra-dims']

    # Print resulting argument list for easier debugging (will be captured by
    # pytest unless it is called with the -s flag)
    print('call:\n{}'.format(' '.join(call_args)))

    subprocess.check_call(call_args)

    return _output_path
