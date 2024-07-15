import shutil
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

import pytest

from superscore.backends.core import _Backend
from superscore.backends.filestore import FilestoreBackend
from superscore.backends.test import TestBackend
from superscore.client import Client
from superscore.control_layers._base_shim import _BaseShim
from superscore.control_layers.core import ControlLayer
from superscore.model import (Collection, Parameter, Readback, Root, Setpoint,
                              Snapshot)


@pytest.fixture(scope='function')
def linac_backend():
    lasr_gunb_pv1 = Parameter(
        uuid="5544c58f-88b6-40aa-9076-f180a44908f5",
        pv_name="LASR:GUNB:TEST1",
        description="First LASR pv in GUNB",
    )

    now = lasr_gunb_pv1.creation_time

    lasr_gunb_pv2 = Parameter(
        uuid="7cb3760c-793c-4974-a8ae-778e5d491e4a",
        pv_name="LASR:GUNB:TEST2",
        description="Second LASR pv in GUNB",
        creation_time=now,
    )

    lasr_gunb_col = Collection(
        uuid="d5bade05-d992-4e44-87d8-0db2937209bf",
        description="LASR devices within GUNB",
        creation_time=now,
        title="LASR",
        children=[
            lasr_gunb_pv1,
            lasr_gunb_pv2,
        ]
    )

    mgnt_gunb_pv = Parameter(
        uuid="930b137f-5ae2-470e-8b82-c4b4eb7e639e",
        pv_name="MGNT:GUNB:TEST0",
        description="Only MGNT pv in GUNB",
        creation_time=now,
    )

    mgnt_gunb_col = Collection(
        uuid="981d52d1-4d3c-4f85-89d7-8c04a0d588d0",
        description="MGNT devices within GUNB",
        creation_time=now,
        title="MGNT",
        children=[
            mgnt_gunb_pv,
        ]
    )

    vac_gunb_pv1 = Parameter(
        uuid="8f3ac401-68f8-4def-b65a-3c8116c80ba7",
        pv_name="VAC:GUNB:TEST1",
        description="First VAC pv in GUNB",
        creation_time=now,
    )

    vac_gunb_pv2 = Parameter(
        uuid="06448272-cd38-4bb4-9b8d-292673a497e9",
        pv_name="VAC:GUNB:TEST2",
        description="Second VAC pv in GUNB",
        creation_time=now,
    )

    vac_gunb_col = Collection(
        uuid="e09cf046-fbf6-4d37-9ee1-c3c2dd977798",
        description="VAC devices within GUNB",
        creation_time=now,
        title="VAC",
        children=[
            vac_gunb_pv1,
            vac_gunb_pv2,
        ]
    )

    gunb_col = Collection(
        uuid="6f09255f-3424-4fc2-bbd7-ae677c8a06b9",
        description="Injector sector for LCLS-SC",
        creation_time=now,
        title="GUNB",
        children=[
            vac_gunb_col,
            mgnt_gunb_col,
            lasr_gunb_col,
        ]
    )

    vac_l0b_pv = Parameter(
        uuid="5ec33c74-7f4c-4905-a106-44fbfe138140",
        pv_name="VAC:L0B:TEST0",
        description="Only VAC pv in L0B",
        creation_time=now,
    )

    vac_l0b_col = Collection(
        uuid="aa11f29a-3e7e-4647-bfc9-133257647fb7",
        description="First transport sector for LCLS-SC",
        creation_time=now,
        title="VAC",
        children=[
            vac_l0b_pv,
        ]
    )

    l0b_col = Collection(
        uuid="5e84544b-4cfa-471c-b827-80063801d27b",
        description="First transport sector for LCLS-SC",
        creation_time=now,
        title="L0B",
        children=[
            vac_l0b_col,
        ]
    )

    vac_bsy_pv = Parameter(
        uuid="030786df-153b-4d29-bc1f-66deeb116724",
        pv_name="VAC:BSY:TEST0",
        description="Only VAC pv in BSY",
        creation_time=now,
    )

    vac_bsy_col = Collection(
        uuid="22c2d597-2139-4c02-ac86-27f474728fad",
        description="Vacuum devices in the BSY",
        creation_time=now,
        title="VAC",
        children=[
            vac_bsy_pv,
        ]
    )

    bsy_col = Collection(
        uuid="2506d87a-5980-4470-b29a-63eea183f53d",
        description="Sector in which beam is directed towards an endpoint",
        creation_time=now,
        title="BSY",
        children=[
            vac_bsy_col,
        ]
    )

    lcls_sc_col = Collection(
        uuid="4732fed6-c321-4a5c-b45b-c2bf704b7fe3",
        description="The superconducting LINAC",
        creation_time=now,
        title="LCLS-SC",
        children=[
            gunb_col,
            l0b_col,
            bsy_col,
        ]
    )

    vac_li10_pv = Parameter(
        uuid="2c83a9be-bec6-4436-8233-79df300af670",
        pv_name="VAC:LI10:TEST0",
        description="Only VAC pv in LI10",
        creation_time=now,
    )

    vac_li10_col = Collection(
        uuid="214ec7c5-29d5-4827-b9dc-8da00664b462",
        description="Vacuum devices in LI10",
        creation_time=now,
        title="VAC",
        children=[
            vac_li10_pv,
        ]
    )

    li10_col = Collection(
        uuid="596c4935-92eb-4bfd-a96e-b38f55f6c0a4",
        description="First transport sector for FACET",
        creation_time=now,
        title="LI10",
        children=[
            vac_li10_col,
        ]
    )

    lasr_in10_pv = Parameter(
        uuid="f802dee1-569b-4c6b-a32f-c213af10ecec",
        pv_name="LASR:IN10:TEST0",
        description="Only laser pv in IN10",
        creation_time=now,
    )

    lasr_in10_col = Collection(
        uuid="213b8629-8b6d-4b2a-a7a4-0201a568e8cd",
        description="Laser devices in IN10",
        creation_time=now,
        title="LASR",
        children=[
            lasr_in10_pv,
        ]
    )

    in10_col = Collection(
        uuid="8395ad87-b9e9-4064-8996-316ccce9dc27",
        description="Injector sector for FACET",
        creation_time=now,
        title="IN10",
        children=[
            lasr_in10_col,
        ]
    )

    facet_col = Collection(
        uuid="fe9485e0-bc36-45a4-89ec-31a4fc92ef7b",
        description="The FACET LINAC",
        creation_time=now,
        title="FACET",
        children=[
            in10_col,
            li10_col,
        ]
    )

    lasr_in20_pv = Parameter(
        uuid="a13ef8a5-b8df-4caa-80f5-395b16eaa5f1",
        pv_name="LASR:IN20:TEST0",
        description="Only laser pv in IN20",
        creation_time=now,
    )

    lasr_in20_col = Collection(
        uuid="2290a098-0475-403d-a902-a26481068f25",
        description="Laser devices in IN20",
        creation_time=now,
        title="LASR",
        children=[
            lasr_in20_pv,
        ]
    )

    in20_col = Collection(
        uuid="4cd08663-ee26-41ed-87d2-5ff0777e0e35",
        description="Injector sector for LCLS-NC",
        creation_time=now,
        title="IN20",
        children=[
            lasr_in20_col,
        ]
    )

    vac_li21_pv = Parameter(
        uuid="8dba63d5-98e8-4647-ae44-ff0a38a4805d",
        pv_name="VAC:LI21:TEST0",
        description="Only VAC pv in LI21",
        creation_time=now,
    )

    vac_li21_col = Collection(
        uuid="be3d4655-7813-4974-bb10-19e4787f8a8e",
        description="VAC devices within LI21",
        creation_time=now,
        title="VAC",
        children=[
            vac_li21_pv,
        ]
    )

    li21_col = Collection(
        uuid="8b434f17-fc67-430c-aa33-d1afb64dbad2",
        description="First transport sector for LCLS-NC",
        creation_time=now,
        title="LI21",
        children=[
            vac_li21_col,
        ]
    )

    lcls_nc_col = Collection(
        uuid="973ce16b-61ff-469b-a5f2-cd64783dcec5",
        description="The normal-conducting LINAC",
        creation_time=now,
        title="LCLS-NC",
        children=[
            in20_col,
            li21_col,
            bsy_col,
        ]
    )

    all_col = Collection(
        uuid="441ff79f-4948-480e-9646-55a1462a5a70",
        description="All three facilities in the SLAC LINAC: LCLS-NC, FACET, and LCLS-SC",
        creation_time=now,
        title="Accelerator Directorate",
        children=[
            lcls_nc_col,
            facet_col,
            lcls_sc_col,
        ]
    )

    lasr_gunb_value1 = Setpoint(
        uuid="927ef6cb-e45f-4175-aa5f-6c6eec1f3ae4",
        pv_name=lasr_gunb_pv1.pv_name,
        description=lasr_gunb_pv1.description,
        data="Off",
    )

    now = lasr_gunb_value1.creation_time

    lasr_gunb_value2 = Setpoint(
        uuid="a221f6fa-6bc1-40ad-90fb-2041c29a5f67",
        pv_name=lasr_gunb_pv2.pv_name,
        description=lasr_gunb_pv2.description,
        creation_time=now,
        data=5,
    )

    lasr_gunb_snapshot = Snapshot(
        uuid="2f709b4b-79da-4a8b-8693-eed2c389cb3a",
        description=lasr_gunb_col.description,
        creation_time=now,
        title=lasr_gunb_col.title,
        children=[
            lasr_gunb_value1,
            lasr_gunb_value2,
        ]
    )

    mgnt_gunb_value = Setpoint(
        uuid="502d9fc3-455a-47ea-8c48-e1a26d4d3350",
        pv_name=mgnt_gunb_pv.pv_name,
        description=mgnt_gunb_pv.description,
        creation_time=now,
        data=True,
    )

    mgnt_gunb_snapshot = Snapshot(
        uuid="4e25ec00-3d8e-4e87-b19f-8541cb25e83b",
        description=mgnt_gunb_col.description,
        creation_time=now,
        title=mgnt_gunb_col.title,
        children=[
            mgnt_gunb_value,
        ]
    )

    vac_gunb_value1 = Setpoint(
        uuid="cc187dbf-fa41-49d7-8c7b-49c8989c6a2f",
        pv_name=vac_gunb_pv1.pv_name,
        description=vac_gunb_pv1.description,
        creation_time=now,
        data="Ion Pump",
    )

    vac_gunb_value2 = Setpoint(
        uuid="7c87960d-8b58-4b29-8d5e-e1f3223e356a",
        pv_name=vac_gunb_pv2.pv_name,
        description=vac_gunb_pv2.description,
        creation_time=now,
        data=False,
    )

    vac_gunb_snapshot = Snapshot(
        uuid="8463a578-d327-4b92-8867-58e01c80f3c2",
        description=vac_gunb_col.description,
        creation_time=now,
        title=vac_gunb_col.title,
        children=[
            vac_gunb_value1,
            vac_gunb_value2,
        ]
    )

    gunb_snapshot = Snapshot(
        uuid="7d8655e1-c086-45a1-b89d-d5261e8375d0",
        description=gunb_col.description,
        creation_time=now,
        title=gunb_col.title,
        children=[
            vac_gunb_snapshot,
            mgnt_gunb_snapshot,
            lasr_gunb_snapshot,
        ]
    )

    vac_l0b_value = Setpoint(
        uuid="2ef43192-40c9-4e79-96e7-2d7f6df58cd9",
        pv_name=vac_l0b_pv.pv_name,
        description=vac_l0b_pv.description,
        creation_time=now,
        data=-10,
    )

    vac_l0b_snapshot = Snapshot(
        uuid="ed223bb4-ce6f-4b58-b53e-c2c538b1a2c7",
        description=vac_l0b_col.description,
        creation_time=now,
        title=vac_l0b_col.title,
        children=[
            vac_l0b_value,
        ]
    )

    l0b_snapshot = Snapshot(
        uuid="cb2a6de0-84b4-4f9c-b7b7-ec67ccfd622f",
        description=l0b_col.description,
        creation_time=now,
        title=l0b_col.title,
        children=[
            vac_l0b_snapshot,
        ]
    )

    vac_bsy_value = Setpoint(
        uuid="6bebcb59-884f-4e68-927d-f3053effd698",
        pv_name=vac_bsy_pv.pv_name,
        description=vac_bsy_pv.description,
        creation_time=now,
        data="",
    )

    vac_bsy_snapshot = Snapshot(
        uuid="aca9400b-d37c-4b86-ada7-4801cdc6aa72",
        description=vac_bsy_col.description,
        creation_time=now,
        title=vac_bsy_col.title,
        children=[
            vac_bsy_value,
        ]
    )

    bsy_snapshot = Snapshot(
        uuid="a62f1386-39de-4d19-9ea4-82f0212169a7",
        description=bsy_col.description,
        creation_time=now,
        title=bsy_col.title,
        children=[
            vac_bsy_snapshot,
        ]
    )

    lcls_sc_snapshot = Snapshot(
        uuid="f01dd01b-bf48-49b2-bbb0-68dcc0b737f8",
        description=lcls_sc_col.description,
        creation_time=now,
        title=lcls_sc_col.title,
        children=[
            gunb_snapshot,
            l0b_snapshot,
            bsy_snapshot,
        ]
    )

    vac_li10_value = Setpoint(
        uuid="ee56d60b-b8b9-447d-b857-6117e22f1462",
        pv_name=vac_li10_pv.pv_name,
        description=vac_li10_pv.description,
        creation_time=now,
        data=.25,
    )

    vac_li10_snapshot = Snapshot(
        uuid="fb3a429c-1d2b-4505-8265-3d8988df2db1",
        description=vac_li10_col.description,
        creation_time=now,
        title=vac_li10_col.title,
        children=[
            vac_li10_value,
        ]
    )

    li10_snapshot = Snapshot(
        uuid="c407e473-9287-4462-b3d3-9036008ea7f1",
        description=li10_col.description,
        creation_time=now,
        title=li10_col.title,
        children=[
            vac_li10_snapshot,
        ]
    )

    lasr_in10_value = Setpoint(
        uuid="fb809d22-76fb-493e-b7f2-b522319e5e2f",
        pv_name=lasr_in10_pv.pv_name,
        description=lasr_in10_pv.description,
        creation_time=now,
        data=645.26,
    )

    lasr_in10_snapshot = Snapshot(
        uuid="b815aed4-82b4-4dc2-9eeb-0e54bcbeb5c5",
        description=lasr_in10_col.description,
        creation_time=now,
        title=lasr_in10_col.title,
        children=[
            lasr_in10_value,
        ]
    )

    in10_snapshot = Snapshot(
        uuid="5d1763cc-41a2-4c6e-bffb-4197a3994b2d",
        description=in10_col.description,
        creation_time=now,
        title=in10_col.title,
        children=[
            lasr_in10_snapshot,
        ]
    )

    facet_snapshot = Snapshot(
        uuid="c48a332a-9c79-4b6f-850a-844237b83737",
        description=facet_col.description,
        creation_time=now,
        title=facet_col.title,
        children=[
            in10_snapshot,
            li10_snapshot,
        ]
    )

    lasr_in20_value = Setpoint(
        uuid="4d2f7bf2-af71-492b-8528-ba9b6e3ab964",
        pv_name=lasr_in20_pv.pv_name,
        description=lasr_in20_pv.description,
        creation_time=now,
        data=0,
    )

    lasr_in20_snapshot = Snapshot(
        uuid="278875de-7adf-4c52-bc88-5b188eb26d4f",
        description=lasr_in20_col.description,
        creation_time=now,
        title=lasr_in20_col.title,
        children=[
            lasr_in20_value,
        ]
    )

    in20_snapshot = Snapshot(
        uuid="f9965c8f-55eb-4e5c-8d52-cc939eed76db",
        description=in20_col.description,
        creation_time=now,
        title=in20_col.title,
        children=[
            lasr_in20_snapshot,
        ]
    )

    vac_li21_readback = Readback(
        uuid="de66d08e-09c3-4c45-8978-900e51d00248",
        pv_name=vac_li21_pv.pv_name,
        description=vac_li21_pv.description,
        creation_time=now,
        data=0.0,
    )

    vac_li21_setpoint = Setpoint(
        uuid="4bffe9a5-f198-41d8-90ab-870d1b5a325b",
        pv_name=vac_li21_pv.pv_name,
        description=vac_li21_pv.description,
        creation_time=now,
        data=5.0,
        readback=vac_li21_readback,
    )

    vac_li21_snapshot = Snapshot(
        uuid="97833e7b-e49d-4898-a602-bb39c493b0ee",
        description=vac_li21_col.description,
        creation_time=now,
        title=vac_li21_col.title,
        children=[
            vac_li21_setpoint,
            vac_li21_readback,
        ]
    )

    li21_snapshot = Snapshot(
        uuid="63a4fab8-17f9-4066-92c7-311e2eb6a44f",
        description=li21_col.description,
        creation_time=now,
        title=li21_col.title,
        children=[
            vac_li21_snapshot,
        ]
    )

    lcls_nc_snapshot = Snapshot(
        uuid="7f86856a-8963-4cf2-9830-f3cce6c1b4b2",
        description=lcls_nc_col.description,
        creation_time=now,
        title=lcls_nc_col.title,
        children=[
            in20_snapshot,
            li21_snapshot,
            bsy_snapshot,
        ]
    )

    all_snapshot = Snapshot(
        uuid="06282731-33ea-4270-ba14-098872e627dc",
        description=all_col.description,
        title=all_col.title,
        children=[
            lcls_nc_snapshot,
            facet_snapshot,
            lcls_sc_snapshot,
        ]
    )

    return TestBackend([all_col, all_snapshot])


@pytest.fixture(scope='function')
def sample_database() -> Root:
    """
    A sample superscore database, including all the Entry types.
    Corresponds to a caproto.ioc_examples.fake_motor_record, which mimics an IMS
    motor record
    """
    root = Root()
    param_1 = Parameter(
        description='parameter 1 in root',
        pv_name='MY:MOTOR:mtr1.ACCL'
    )
    root.entries.append(param_1)
    value_1 = Setpoint.from_parameter(
        origin=param_1,
        data=2,
    )
    root.entries.append(value_1)
    coll_1 = Collection(
        title='collection 1',
        description='collection 1 defining some motor fields',
    )
    snap_1 = Snapshot(
        title='snapshot 1',
        description='Snapshot 1 created from collection 1',
    )
    for fld, data in zip(['ACCL', 'VELO', 'PREC'], [2, 2, 6]):  # Defaults[1, 1, 3]
        sub_param = Parameter(
            description=f'motor field {fld}',
            pv_name=f'MY:PREFIX:mtr1.{fld}'
        )
        sub_value = Setpoint.from_parameter(
            origin=sub_param,
            data=data,
        )
        coll_1.children.append(sub_param)
        snap_1.children.append(sub_value)
    root.entries.append(coll_1)
    root.entries.append(snap_1)

    return root


@pytest.fixture(scope='function')
def parameter_with_readback() -> Parameter:
    """
    A simple setpoint-readback parameter pair
    """
    readback = Parameter(
        uuid="64772c61-c117-445b-b0c8-4c17fd1625d9",
        pv_name="RBV",
        description="A readback PV",
    )
    setpoint = Parameter(
        uuid="b508344d-1fe9-473b-8d43-9499d0e8e23f",
        pv_name="SET",
        description="A setpoint PV",
        readback=readback,
    )
    return setpoint


@pytest.fixture(scope='function')
def filestore_backend(tmp_path: Path) -> FilestoreBackend:
    fp = Path(__file__).parent / 'db' / 'filestore.json'
    tmp_fp = tmp_path / 'tmp_filestore.json'
    shutil.copy(fp, tmp_fp)
    print(tmp_path)
    return FilestoreBackend(path=tmp_fp)


@pytest.fixture(scope='function')
def test_backends(filestore_backend: FilestoreBackend) -> List[_Backend]:
    return [filestore_backend,]


@pytest.fixture(scope='function')
def backends(request, test_backends: List[_Backend]):
    i = request.param
    return test_backends[i]


class DummyShim(_BaseShim):
    """Shim that does nothing"""
    async def get(self, *args, **kwargs):
        return

    async def put(self, *args, **kwargs):
        return

    def monitor(self, *args, **kwargs):
        return


@pytest.fixture(scope='function')
def dummy_cl() -> ControlLayer:
    cl = ControlLayer()
    cl.shims['ca'] = DummyShim()
    cl.shims['pva'] = DummyShim()
    return cl


@pytest.fixture(scope='function')
def mock_backend() -> _Backend:
    bk = _Backend()
    bk.delete_entry = MagicMock()
    bk.save_entry = MagicMock()
    bk.get_entry = MagicMock()
    bk.search = MagicMock()
    bk.update_entry = MagicMock()


class MockTaskStatus:
    def exception(self):
        return None

    @property
    def done(self):
        return True


@pytest.fixture(scope='function')
def mock_client(mock_backend: _Backend) -> Client:
    client = Client(backend=mock_backend)
    return client
