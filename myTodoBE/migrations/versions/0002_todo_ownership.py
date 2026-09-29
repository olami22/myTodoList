"""Add ownership to existing todos without losing legacy rows."""

from alembic import op
import sqlalchemy as sa

revision = "0002_todo_owner"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = {column["name"] for column in inspector.get_columns("todos")}

    if "user_id" not in columns:
        op.add_column("todos", sa.Column("user_id", sa.Integer(), nullable=True))

    unowned_count = connection.scalar(
        sa.text("SELECT COUNT(*) FROM todos WHERE user_id IS NULL")
    )
    if unowned_count:
        user_ids = connection.scalars(sa.text("SELECT id FROM users ORDER BY id")).all()
        if len(user_ids) != 1:
            raise RuntimeError(
                "Cannot safely assign legacy todos: create or select a single owner before migrating."
            )
        connection.execute(
            sa.text("UPDATE todos SET user_id = :user_id WHERE user_id IS NULL"),
            {"user_id": user_ids[0]},
        )

    inspector = sa.inspect(connection)
    foreign_key_exists = any(
        foreign_key["constrained_columns"] == ["user_id"]
        and foreign_key["referred_table"] == "users"
        for foreign_key in inspector.get_foreign_keys("todos")
    )
    index_exists = any(
        index["column_names"] == ["user_id"]
        for index in inspector.get_indexes("todos")
    )

    if connection.dialect.name == "sqlite":
        with op.batch_alter_table("todos", recreate="always") as batch_op:
            batch_op.alter_column(
                "user_id",
                existing_type=sa.Integer(),
                nullable=False,
            )
            if not foreign_key_exists:
                batch_op.create_foreign_key(
                    "fk_todos_user_id_users",
                    "users",
                    ["user_id"],
                    ["id"],
                )
            if not index_exists:
                batch_op.create_index("ix_todos_user_id", ["user_id"])
        return

    op.alter_column(
        "todos",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    if not foreign_key_exists:
        op.create_foreign_key(
            "fk_todos_user_id_users",
            "todos",
            "users",
            ["user_id"],
            ["id"],
        )
    if not index_exists:
        op.create_index("ix_todos_user_id", "todos", ["user_id"])


def downgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    foreign_key_exists = any(
        foreign_key["constrained_columns"] == ["user_id"]
        and foreign_key["referred_table"] == "users"
        for foreign_key in inspector.get_foreign_keys("todos")
    )
    index_exists = any(
        index["column_names"] == ["user_id"]
        for index in inspector.get_indexes("todos")
    )

    if connection.dialect.name == "sqlite":
        with op.batch_alter_table("todos", recreate="always") as batch_op:
            if foreign_key_exists:
                batch_op.drop_constraint("fk_todos_user_id_users", type_="foreignkey")
            if index_exists:
                batch_op.drop_index("ix_todos_user_id")
            batch_op.drop_column("user_id")
        return

    if foreign_key_exists:
        op.drop_constraint("fk_todos_user_id_users", "todos", type_="foreignkey")
    if index_exists:
        op.drop_index("ix_todos_user_id", table_name="todos")
    op.drop_column("todos", "user_id")