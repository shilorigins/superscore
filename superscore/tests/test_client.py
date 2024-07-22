import os
from pathlib import Path
from unittest.mock import patch

import pytest

from superscore.backends.filestore import FilestoreBackend
from superscore.client import Client
from superscore.errors import CommunicationError
from superscore.model import Parameter, Readback, Root, Setpoint

from .conftest import MockTaskStatus

SAMPLE_CFG = Path(__file__).parent / 'config.cfg'


@pytest.fixture(scope='function')
def xdg_config_patch(tmp_path):
    config_home = tmp_path / 'xdg_config_home'
    config_home.mkdir()
    return config_home


@pytest.fixture(scope='function')
def sscore_cfg(xdg_config_patch: Path):
    # patch config discovery paths
    xdg_cfg = os.environ.get("XDG_CONFIG_HOME", '')
    sscore_cfg = os.environ.get("SUPERSCORE_CFG", '')

    os.environ['XDG_CONFIG_HOME'] = str(xdg_config_patch)
    os.environ['SUPERSCORE_CFG'] = ''

    sscore_cfg_path = xdg_config_patch / "superscore.cfg"
    sscore_cfg_path.symlink_to(SAMPLE_CFG)

    yield str(sscore_cfg_path)

    # reset env vars
    os.environ["SUPERSCORE_CFG"] = str(sscore_cfg)
    os.environ["XDG_CONFIG_HOME"] = xdg_cfg


def test_apply(mock_client: Client, sample_database: Root, setpoint_with_readback):
    mock_client.cl.shims['ca'].put.return_value = MockTaskStatus()
    snap = sample_database.entries[3]
    with patch('superscore.control_layers.core.ControlLayer.put', side_effect=mock_client.cl.put) as put_mock:
        mock_client.apply(snap)
        assert put_mock.call_count == 1
        assert mock_client.cl.shims['ca'].put.call_count == 3
        call_args = put_mock.call_args[0]
        assert len(call_args[0]) == len(call_args[1]) == 3

        put_mock.reset_mock()
        mock_client.cl.shims['ca'].put.reset_mock()

        mock_client.apply(snap, sequential=True)
        assert put_mock.call_count == 3
        assert mock_client.cl.shims['ca'].put.call_count == 3

        put_mock.reset_mock()
        mock_client.cl.shims['ca'].put.reset_mock()
        mock_client.apply(setpoint_with_readback, sequential=True)
        assert put_mock.call_count == 1
        assert mock_client.cl.shims['ca'].put.call_count == 1


def test_snap(
    mock_client: Client,
    sample_database: Root,
    parameter_with_readback: Parameter
):
    # mock_shim is shared between shim keys, so we only have to set one
    mock_client.cl.shims['ca'].get.side_effect = range(5)

    coll = sample_database.entries[2]
    coll.children.append(parameter_with_readback)

    snapshot = mock_client.snap(coll)
    assert mock_client.cl.shims['ca'].get.call_count == 5
    assert all([snapshot.children[i].data == i for i in range(4)])  # children saved in order
    setpoint = snapshot.children[-1]
    assert isinstance(setpoint, Setpoint)
    assert isinstance(setpoint.readback, Readback)
    assert setpoint.readback.data == 4  # readback saved after setpoint


def test_snap_exception(mock_client: Client, sample_database: Root):
    mock_client.cl.shims['ca'].get.side_effect = [0, 1, CommunicationError, 3, 4]
    coll = sample_database.entries[2]
    snapshot = mock_client.snap(coll)
    assert snapshot.children[2].data is None


def test_from_cfg(sscore_cfg: str):
    client = Client.from_config()
    assert isinstance(client.backend, FilestoreBackend)
    assert 'ca' in client.cl.shims


def test_find_config(sscore_cfg: str):
    assert sscore_cfg == Client.find_config()

    # explicit SUPERSCORE_CFG env var supercedes XDG_CONFIG_HOME
    os.environ['SUPERSCORE_CFG'] = 'other/cfg'
    assert 'other/cfg' == Client.find_config()
