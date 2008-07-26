import MySQLdb as db

conn = db.connect(
    host="daily.swarthmore.edu",
    user="gazette_main",
    passwd="Firyraptor97",
    db="gazette_daily"
)

cursor = conn.cursor()

### Users

users = {}
cursor.execute("SELECT id, user_nicename, user_email, display_name FROM gazette_users")
while True:
    row = cursor.fetchone()
    if row is None:
        break
    old_id, username, email, display_name = row
    
    users[int(old_id)] = {
        'username': username,
        'email': email,
        'display_name': display_name
    }

cursor.execute("SELECT user_id, meta_key, meta_value FROM gazette_usermeta WHERE NOT meta_key IN ('rich_editing', 'admin_color', 'closedpostboxes_post', 'gazette_autosave_draft_ids')")
while True:
    row = cursor.fetchone()
    if row is None:
        break
    old_id, key, val = row
    users[old_id][key] = val


### Posts

posts = {}
cursor.execute("SELECT id, post_author, post_date, post_title, post_content, post_excerpt, post_status, post_name, post_modified FROM ")


cursor.close()
conn.close()