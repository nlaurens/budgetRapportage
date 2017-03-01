from model.functions import db


db_schemas = [
    """
    CREATE TABLE if not exists sessions (
        session_id varchar(128) UNIQUE NOT NULL,
        atime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
        data text
    );
    """,

    """
    CREATE TABLE if not exists user (
        user_id             integer PRIMARY KEY,
        user_login          varchar(64) NOT NULL,
        user_password       varchar(255) NOT NULL,
        user_email          varchar(64),  -- Optional, see settings
        user_status         varchar(16) NOT NULL DEFAULT 'active',
        user_last_login     datetime NOT NULL DEFAULT (datetime('now', 'localtime'))
    );
    """,

    """
    CREATE TABLE if not exists permission (
        permission_id           integer PRIMARY KEY,
        permission_codename     varchar(50),  -- Example: 'can_vote'
        permission_desc         varchar(50)   -- Example: 'Can vote in elections'
    );
    """,

    """
    CREATE TABLE if not exists user_permission (
        up_user_id          integer REFERENCES user (user_id),
        up_permission_id    integer REFERENCES permission (permission_id),
        PRIMARY KEY (up_user_id, up_permission_id)
    );
    """
]


if __name__ == '__main__':
    # create db tables
    for schema in db_schemas:
        db.query(schema)
