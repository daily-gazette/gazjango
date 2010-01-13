##### migration: v2009 => v2010

# ALTER DATABASE gazette CHARACTER SET 'utf8';

# add missing apps/tables
./manage.py syncdb

# convert to staff_state column for positions
./manage.py dbshell <<'SQL'
BEGIN;
ALTER TABLE `accounts_position` ADD COLUMN 
            `staff_state` varchar(1) NOT NULL DEFAULT 'n';
UPDATE `accounts_position` SET `staff_state`='n';
UPDATE `accounts_position` SET `staff_state`='e' WHERE `is_editor`=1;
UPDATE `accounts_position` SET `staff_state`='s' WHERE `name` 
        IN ('Staff Reporter', 'Staff Photographer');
UPDATE `accounts_position` SET `staff_state`='x' WHERE `name` 
        IN ('Editor Emeritus', 'Ex-Staff');
ALTER TABLE `accounts_position` DROP COLUMN `is_editor`;
COMMIT;
SQL

# add speaking_officially column for comments
./manage.py dbshell <<'SQL'
BEGIN;
ALTER TABLE `comments_publiccomment' ADD COLUMN
            `speaking_officially` bool NOT NULL AFTER `email`;
COMMIT;
SQL
./manage.py shell <<'PYTHON'
from interactive_load import *
for c in PublicComment.objects.filter(name=None, user__user__is_staff=True):
    if c.user.staff_status(c.time):
        c.speaking_officially = True
        c.save()
PYTHON


# add num_full column for issues
./manage.py dbshell <<'SQL'
BEGIN;
ALTER TABLE `issues_issue` ADD COLUMN 
            `num_full` integer NOT NULL DEFAULT 3
            AFTER `id`;
COMMIT;
SQL

# add our livecustomer ads
./manage.py shell <<'ADS'
from interactive_load import *
TextLinkAd.objects.create(source='c', link='http://www.acairoots.com', text='acai')
TextLinkAd.objects.create(source='c', link='http://www.r4-ds-card.ca', text='r4')
TextLinkAd.objects.create(source='c', link='http://www.framesdirect.com/sunglasses/', text='sunglasses')
ADS

# make sure that admin permissions are right, etc
./manage.py syncdb
