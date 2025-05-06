import argparse
from enum import IntEnum

from superscore.backends.directory import DirectoryBackend
from superscore.client import Client
from superscore.model import Collection, Parameter

DESTINATION = '.prod_pvs/'


class Program(IntEnum):
    LCLS = 1
    FACET = 2
    LCLS2 = 3


class TagGroup(IntEnum):
    PROGRAM = 0
    REGION = 1
    AREA = 2
    SUBSYSTEM = 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    with open(args.file, 'r') as f:
        lines = f.read().split('\n')

    tag_groups = {
        0: ["Program", "", {}],
        1: ["Region", "", {}],
        2: ["Area", "", {}],
        3: ["Subsystem", "", {}],
    }

    global_coll = Collection(description="Placeholder Collection before data model refactor")

    for line in lines[1:-1]:
        region, setpoint, readback, alias, area, subsystem, program_id = line.split(",")
        program = Program(program_id).name
        program_tags = tag_groups[TagGroup.PROGRAM][2]
        if program not in program_tags.values():
            program_tag_id = max(program_tags.key()) + 1
            program_tags.update(program_tag_id=program)

        region_tags = tag_groups[TagGroup.REGION][2]
        if region not in region_tags.values():
            region_tag_id = max(region_tags.key()) + 1
            region_tags.update(region_tag_id=region)

        area_tags = tag_groups[TagGroup.AREA][2]
        if area not in area_tags.values():
            area_tag_id = max(area_tags.key()) + 1
            area_tags.update(area_tag_id=area)

        subsystem_tags = tag_groups[TagGroup.SUBSYSTEM][2]
        if subsystem not in subsystem_tags.values():
            subsystem_tag_id = max(subsystem_tags.key()) + 1
            subsystem_tags.update(subsystem_tag_id=subsystem)

        readback_param = None
        if readback != "NA":
            readback_param = Parameter(
                pv_name=readback,
                description=alias,
                read_only=True,
            )
        if setpoint == "NA":
            global_coll.children.append(readback_param)
        else:
            setpoint_param = Parameter(
                pv_name=setpoint,
                readback=readback_param,
                description=alias,
                tags={
                    TagGroup.PROGRAM: {program_tag_id},
                    TagGroup.REGION: {region_tag_id},
                    TagGroup.AREA: {area_tag_id},
                    TagGroup.SUBSYSTEM: {subsystem_tag_id},
                }
            )
            global_coll.children.append(setpoint_param)

    client = Client(
        backend=DirectoryBackend(DESTINATION)
    )
    client.save(global_coll)
