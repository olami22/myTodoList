"""Create the initial users, todos, and notes schema."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(), nullable=False),
            sa.Column("password_hash", sa.String(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_users_id", "users", ["id"], unique=False)
        op.create_index("ix_users_username", "users", ["username"], unique=True)

    if "todos" not in tables:
        op.create_table(
            "todos",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("task", sa.String(), nullable=False),
            sa.Column("completed", sa.Boolean(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_todos_id", "todos", ["id"], unique=False)

    if "notes" not in tables:
        op.create_table(
            "notes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("content", sa.String(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("todo_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["todo_id"], ["todos.id"], name="fk_notes_todo_id_todos"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_notes_user_id_users"),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade():
    connection = op.get_bind()
    for table_name in ("notes", "todos", "users"):
        if not sa.inspect(connection).has_table(table_name):
            continue
        table = sa.table(table_name)
        row_count = connection.scalar(sa.select(sa.func.count()).select_from(table))
        if row_count == 0:
            op.drop_table(table_name)
