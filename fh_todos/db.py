from dataclasses import dataclass
from typing import Iterable, cast, Callable, Mapping

from fastlite import Table


@dataclass
class Store[T]:
    table: Table
    model: T

    def list_items(self) -> Iterable[T]:
        return cast(Callable, self.table)(order_by="id")

    def add_item(self, title: str) -> T:
        return self.table.insert(self.model(title=title, done=False))

    def delete_item(self, item_id: int):
        self.table.delete(item_id)

    def toggle_item(self, item_id: int) -> bool:
        self.table.db.execute(
            "UPDATE todos SET done = not(done) where id = ?",
            [item_id],
        )
        return cast(Mapping, self.table)[item_id].done
