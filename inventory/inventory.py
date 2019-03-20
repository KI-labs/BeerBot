import json
import os

from shapely.geometry import Point

DISTANCE_THRESHOLD = 1


def __inventory_details_path():
    return "{}/inventory_details.json".format(os.getenv("DATA_DIR"))


def get_current_inventory():
    try:
        with open(__inventory_details_path(), "r") as f:
            return json.loads(f.read())
    except IOError:
        return {}


def __get_inventory_update_files():
    path = "{}/inventory".format(os.getenv("DATA_DIR"))
    return [os.path.join(path, basename) for basename in os.listdir(path)]


def __get_latest_inventory_update():
    paths = __get_inventory_update_files()
    if not paths:
        return None
    latest_file = max(paths, key=os.path.getctime)
    return latest_file


def __process_update_line(line):
    x, y = line.split(",")
    return {"x": x, "y": y}


def __bottle_positions(inventory_update_file):
    with open(inventory_update_file, "r") as f:
        return list(map(__process_update_line, f.read().splitlines()))


def __file_name(file_path):
    return os.path.basename(file_path).split(".")[0]


def __point_from_bottle(bottle):
    return Point(float(bottle["x"]), float(bottle["y"]))


def __find_match(bottle, old_bottles):
    bottle_point = __point_from_bottle(bottle)
    print("Trying to find match for {}".format(bottle_point))
    for idx, old_bottle in enumerate(old_bottles):
        old_bottle_point = __point_from_bottle(old_bottle)
        distance = bottle_point.distance(old_bottle_point)
        if distance < DISTANCE_THRESHOLD:
            print("{} {} => MATCH".format(old_bottle_point, distance))
            return old_bottle, idx
        print("{} {} => NO match".format(old_bottle_point, distance))

    print("Couldn't find match, adding as new bottle")
    return None, -1


def __process_inventory_update(
    current_inventory, latest_update_timestamp, new_bottle_positions
):
    new_inventory = {"timestamp": latest_update_timestamp, "bottles": []}
    secs_since_last_update = (
        (int(latest_update_timestamp) - int(current_inventory["timestamp"]))
        if current_inventory.get("timestamp")
        else 0
    )
    current_inventory_bottles = current_inventory.get("bottles", [])
    for new_bottle in new_bottle_positions:
        match, match_pos = __find_match(new_bottle, current_inventory_bottles)
        if match:
            del current_inventory_bottles[match_pos]
        new_inventory_record = {
            "x": new_bottle["x"],
            "y": new_bottle["y"],
            "age": 0 if not match else match["age"] + secs_since_last_update,
        }
        new_inventory["bottles"].append(new_inventory_record)
    return new_inventory


def __store_inventory(inventory):
    with open(__inventory_details_path(), "w") as f:
        f.write(json.dumps(inventory))


def update_inventory():
    current_inventory = get_current_inventory()
    current_inventory_timestamp = current_inventory.get("timestamp")
    latest_update_file = __get_latest_inventory_update()
    if not latest_update_file:
        return

    latest_update_timestamp = __file_name(latest_update_file)

    if current_inventory_timestamp == latest_update_timestamp:
        return current_inventory

    new_bottle_positions = __bottle_positions(latest_update_file)
    new_inventory = __process_inventory_update(
        current_inventory, latest_update_timestamp, new_bottle_positions
    )

    __store_inventory(new_inventory)
    return new_inventory

