from auth import auth
from model.functions import db

tables = [
    """
    DROP TABLE IF EXISTS `user`;
    """,
    """
    CREATE TABLE user (
        user_id             int NOT NULL AUTO_INCREMENT PRIMARY KEY,
        user_login          varchar(64) NOT NULL,
        user_password       varchar(255) NOT NULL,
        user_email          varchar(64),  # Optional, see settings
        user_status         varchar(16) NOT NULL DEFAULT 'active',
        user_last_login     datetime NOT NULL
    )
    """,

    """
    DROP TABLE IF EXISTS `permission`;
    """,
    """
    CREATE TABLE permission (
        permission_id           int NOT NULL AUTO_INCREMENT PRIMARY KEY,
        permission_codename     varchar(50),  # Example: 'can_vote'
        permission_desc         varchar(50)   # Example: 'Can vote in elections'
    )
    """,

    """
    DROP TABLE IF EXISTS `user_permission`;
    """,
    """
    CREATE TABLE user_permission (
        up_user_id          int REFERENCES user (user_id),
        up_permission_id    int REFERENCES permission (permission_id),
        PRIMARY KEY (up_user_id, up_permission_id)
    )
    """
]


if __name__ == '__main__':
    for table in tables:
        db.query(table)

    auth.create_permission('admin', 'Has access to admin panel')

    auth.create_user('admin', password=None, perms=['admin'])
