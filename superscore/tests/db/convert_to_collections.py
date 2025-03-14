import argparse
from enum import IntEnum

from superscore.backends.filestore import FilestoreBackend
from superscore.client import Client
from superscore.model import Collection, Parameter


class Program(IntEnum):
    LCLS = 1
    FACET = 2
    LCLS2 = 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    with open(args.file, 'r') as f:
        lines = f.read().split('\n')
    lcls = Collection(
        title="LCLS",
        description="",
    )
    facet = Collection(
        title="FACET",
        description="",
    )
    lcls2 = Collection(
        title="LCLS-II",
        description="",
    )
    cache = {}
    for line in lines[1:-1]:
        region, setpoint, readback, alias, area, subsystem, program_id = line.split(",")
        if region not in cache:
            cache[region] = Collection(title=region)
            match int(program_id):
                case Program.LCLS:
                    lcls.children.append(cache[region])
                case Program.FACET:
                    facet.children.append(cache[region])
                case Program.LCLS2:
                    lcls2.children.append(cache[region])
        region_coll = cache[region]
        if (region, area) not in cache:
            cache[(region, area)] = Collection(title=area, description=f"{area} within {region}")
            region_coll.children.append(cache[(region, area)])
        area_coll = cache[(region, area)]
        if (region, area, subsystem) not in cache:
            cache[(region, area, subsystem)] = Collection(title=subsystem, description=f"{subsystem} in {area} within {region}")
            area_coll.children.append(cache[(region, area, subsystem)])
        subsystem_coll = cache[(region, area, subsystem)]

        readback_param = None
        if readback != "NA":
            readback_param = Parameter(
                pv_name=readback,
                description=alias,
                read_only=True,
            )
        if setpoint == "NA":
            subsystem_coll.children.append(readback_param)
        else:
            setpoint_param = Parameter(
                pv_name=setpoint,
                readback=readback_param,
                description=alias,
            )
            subsystem_coll.children.append(setpoint_param)

    client = Client(
        backend=FilestoreBackend("prod_linac.json")
    )
    client.save(lcls)
    client.save(facet)
    client.save(lcls2)
