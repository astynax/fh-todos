import os
from pathlib import Path

from fasthtml.common import fast_app, Request, serve
from fasthtml import ft

from .db import Store


app, rt, todos, TodoItem = fast_app(
    debug=True,
    db_file=str(Path(__file__).absolute().parent.parent / "db.sqlite3"),
    todos={
        "columns": {
            "id": int,
            "title": str,
            "done": bool,
        },
        "pk": "id",
        "not_null": {"title", "done"},
    }
)


db = Store[TodoItem](todos, TodoItem)


@rt('/')
def get():
    return (
        ft.Title("Todos"),
        ft.Main(
            ft.Section(
                ft.H2("Todos"),
                ft.Table(
                    ft.Thead(
                        ft.Th("Done", role="col", style="width: 1%;"),
                        ft.Th("Task", role="col"),
                        ft.Th("Actions", role="col", style="width: 1%;"),
                    ),
                    ft.Tbody((
                        item(i) for i in db.list_items()
                    ),
                        id="item-table",
                    )
                )),
            ft.Section(
                ft.H3("New task"),
                ft.Fieldset(
                    ft.Input(name="title", type="text"),
                    ft.Button(
                        "Add",
                        hx_post="/",
                        hx_include="previous [name='title']",
                        hx_target="previous [name='title']",
                        hx_swap="outerHTML",
                    ),
                    role="group",
                ),
            ),
            cls="container",
        ))


def item(record: TodoItem):
    return ft.Tr(
        ft.Td(
            done_checkbox(record.id, record.done),
        ),
        ft.Td(record.title),
        ft.Td(
            ft.Button(
                "Delete",
                hx_delete=f"/{record.id}",
                hx_confirm="Are you sure?",
                hx_target=f"#tr-{record.id}",
                hx_swap="delete",
            )
        ),
        id=f"tr-{record.id}",
    )


def done_checkbox(item_id, done):
    return ft.Input(
        type="checkbox",
        checked=done,
        hx_trigger="click",
        hx_put=f"/{item_id}",
        hx_swap="outerHTML",
    )


@rt("/")
async def post(request: Request):
    f = await request.form()
    title = f.get("title")
    # TODO: replace with Bad Request
    assert title
    new_item = db.add_item(title)
    return (
        ft.Tbody(
        item(new_item),
            hx_swap_oob="beforeend:#item-table",
        ),
        ft.Input(name="title", type="text"),
    )


@rt("/{item_id}")
def delete(item_id: int):
    db.delete_item(item_id)


@rt("/{item_id}")
def put(item_id: int):
    done = db.toggle_item(item_id)
    return done_checkbox(item_id, done=done)


def main():
    serve(host="localhost", port=8000)
