import argparse
from enum import IntEnum

from superscore.backends.directory import DirectoryBackend
from superscore.client import Client
from superscore.model import Parameter

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

    client = Client(
        backend=DirectoryBackend(DESTINATION)
    )
    client.backend.reset()

    for line in lines[1:-1]:
        tags = {
            TagGroup.PROGRAM: set(),
            TagGroup.REGION: set(),
            TagGroup.AREA: set(),
            TagGroup.SUBSYSTEM: set(),
        }
        region, setpoint, readback, alias, area, subsystem, program_id = line.split(",")
        program = Program(int(program_id)).name
        program_tags = tag_groups[TagGroup.PROGRAM][2]
        if program not in program_tags.values():
            try:
                program_tag_id = max(program_tags.keys()) + 1
            except ValueError:
                program_tag_id = 0
            program_tags[program_tag_id] = program
            tags[TagGroup.PROGRAM].add(program_tag_id)

        region_tags = tag_groups[TagGroup.REGION][2]
        if region not in region_tags.values():
            try:
                region_tag_id = max(region_tags.keys()) + 1
            except ValueError:
                region_tag_id = 0
            region_tags[region_tag_id] = region
            tags[TagGroup.REGION].add(region_tag_id)

        area_tags = tag_groups[TagGroup.AREA][2]
        if area not in area_tags.values():
            try:
                area_tag_id = max(area_tags.keys()) + 1
            except ValueError:
                area_tag_id = 0
            area_tags[area_tag_id] = area
            tags[TagGroup.AREA].add(area_tag_id)

        subsystem_tags = tag_groups[TagGroup.SUBSYSTEM][2]
        if subsystem not in subsystem_tags.values():
            try:
                subsystem_tag_id = max(subsystem_tags.keys()) + 1
            except ValueError:
                subsystem_tag_id = 0
            subsystem_tags[subsystem_tag_id] = subsystem
            tags[TagGroup.SUBSYSTEM].add(subsystem_tag_id)

        readback_param = None
        if readback != "NA":
            readback_param = Parameter(
                pv_name=readback,
                description=alias,
                read_only=True,
            )
        if setpoint == "NA":
            client.backend.save_entry(readback_param, top_level=False)
        else:
            setpoint_param = Parameter(
                pv_name=setpoint,
                readback=readback_param,
                description=alias,
                tags=tags
            )
            client.backend.save_entry(setpoint_param, top_level=False)
