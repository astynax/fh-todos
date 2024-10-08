from contextlib import contextmanager
import json


def _read_db():
    with open("db.json") as f:
        return json.load(f)


def _save_db(data):
    with open("db.json", "w") as f:
        return json.dump(data, f)


@contextmanager
def _context():
    data = _read_db()
    yield data
    _save_db(data)


def list_items():
    return sorted((int(k), v) for k, v in _read_db()["items"].items())


def delete_item(item_id):
    with _context() as data:
        del data["items"][item_id]


def add_item(title):
    with _context() as data:
        next_id = data["seq"]
        data["seq"] += 1
        data["items"][str(next_id)] = {
            "title": title,
            "done": False,
        }


def toggle_item(item_id: str) -> bool:
    with _context() as data:
        new_state = not data["items"][item_id]["done"]
        data["items"][item_id]["done"] = new_state
        return new_state
