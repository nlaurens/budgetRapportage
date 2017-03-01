from model.functions import db


tables = [

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
CREATE TABLE permission (
    permission_id           int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    permission_codename     varchar(50),  # Example: 'can_vote'
    permission_desc         varchar(50)   # Example: 'Can vote in elections'
)
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
    # create db tables
    for table in tables:
        db.query(table)
