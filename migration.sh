##### migration: v2009 => v2010

# ALTER DATABASE gazette CHARACTER SET 'utf8';

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

# add num_full column for issues
./manage.py dbshell <<'SQL'
BEGIN;
ALTER TABLE `issues_issue` ADD COLUMN 
            `num_full` integer NOT NULL DEFAULT 3
            AFTER `id`;
COMMIT;
SQL

# add the community app
./manage.py sqlall community | ./manage.py dbshell

# add the ads app
./manage.py sqlall ads | ./manage.py dbshell
./manage.py shell <<'ADS'
from interactive_load import *
TextLinkAd.objects.create(source='c', link='http://www.acairoots.com', text='acai')
TextLinkAd.objects.create(source='c', link='http://www.r4-ds-card.ca', text='r4')
ADS

# add posters
./manage.py dbshell <<'SQL'
BEGIN;
CREATE TABLE `announcements_poster` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `title` varchar(100) NOT NULL,
    `poster_id` integer,
    `sponsor_url` varchar(200) NOT NULL,
    `sponsor_user_id` integer NOT NULL,
    `date_start` date NOT NULL,
    `date_end` date NOT NULL,
    `is_published` bool NOT NULL,
    `related_event_id` integer NOT NULL
)
;
ALTER TABLE `announcements_poster` ADD CONSTRAINT `poster_id_refs_id_edc8472e` FOREIGN KEY (`poster_id`) REFERENCES `media_imagefile` (`id`);
ALTER TABLE `announcements_poster` ADD CONSTRAINT `sponsor_user_id_refs_id_d23acd80` FOREIGN KEY (`sponsor_user_id`) REFERENCES `accounts_userprofile` (`id`);
ALTER TABLE `announcements_poster` ADD CONSTRAINT `related_event_id_refs_id_344f307` FOREIGN KEY (`related_event_id`) REFERENCES `announcements_announcement` (`id`);
COMMIT;
SQL

# makes sure that admin permissions are right, etc
./manage.py syncdb
