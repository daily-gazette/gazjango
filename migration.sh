##### migration: v2009 => v2010

# ALTER DATABASE gazette CHARACTER SET 'utf8';

echo "making changes to articles table (and stackedpages)"
./manage.py dbshell <<'SQL'
BEGIN;
# extend short_summary to 210 chars
ALTER TABLE `articles_article` MODIFY `short_summary` varchar(210) NOT NULL;

# shorten short_title to 40 chars
UPDATE `articles_article` SET `short_title`=''
                          WHERE length(`short_title`) > 40;
ALTER TABLE `articles_article` MODIFY `short_title` varchar(40) NOT NULL;

# add a swat_only field
#ALTER TABLE `articles_article` ADD COLUMN `swat_only` longtext NOT NULL
#                               AFTER `comments_allowed`;

# drop unused fields
ALTER TABLE `articles_article` DROP `long_summary`;
ALTER TABLE `articles_article` DROP `possible_position`;

# denormalize formats from articles
ALTER TABLE `articles_article` ADD COLUMN `format` varchar(1) NOT NULL 
                               AFTER `format_id`;
UPDATE `articles_article` SET `format`='h' WHERE `format_id`=1;
UPDATE `articles_article` SET `format`='t' WHERE `format_id`=2;
ALTER TABLE `articles_article` DROP `format_id`;

# do the same for stackedpages
ALTER TABLE `stackedpages_page` ADD COLUMN `format` varchar(1) NOT NULL 
                                AFTER `format_id`;
UPDATE `stackedpages_page` SET `format`='h' WHERE `format_id`=1;
UPDATE `stackedpages_page` SET `format`='t' WHERE `format_id`=2;
ALTER TABLE `stackedpages_page` DROP `format_id`;

DROP TABLE `articles_format`;

COMMIT;
SQL


echo "dropping the unused 'by the numbers' section"
./manage.py shell <<'SHELL'
from interactive_load import *
Subsection.objects.get(slug='btn').delete()
SHELL


echo "moving the multimedia section into features"

multi_id=$(echo 'SELECT id FROM `articles_section` WHERE slug="multimedia";' | ./manage.py dbshell | tail -n 1)
features_id=$(echo 'SELECT id FROM `articles_section` WHERE slug="features";' | ./manage.py dbshell | tail -n 1)

./manage.py dbshell <<SQL
UPDATE articles_subsection SET section_id=$features_id WHERE section_id=$multi_id;
UPDATE articles_article SET section_id=$features_id WHERE section_id=$multi_id;
SQL

./manage.py shell <<'SHELL'
from interactive_load import *
Section.objects.get(slug='multimedia').delete()
SHELL


echo "converting to staff_state column for positions"
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

echo "adding speaking_officially and superhidden columns for comments"
./manage.py dbshell <<'SQL'
BEGIN;
ALTER TABLE `comments_publiccomment` ADD COLUMN
            `speaking_officially` bool NOT NULL AFTER `email`;
ALTER TABLE `comments_publiccomment` ADD COLUMN
            `superhidden` bool NOT NULL;
COMMIT;
SQL
./manage.py shell <<'PYTHON'
from interactive_load import *
for c in PublicComment.objects.filter(name=None, user__user__is_staff=True):
    if c.user.staff_status(c.time):
        c.speaking_officially = True
        c.save()
PYTHON


echo "adding num_full column for issues"
./manage.py dbshell <<'SQL'
BEGIN;
ALTER TABLE `issues_issue` ADD COLUMN 
            `num_full` integer NOT NULL DEFAULT 3
            AFTER `id`;
COMMIT;
SQL

echo "adding all the other new tables, etc"
./manage.py syncdb

echo "moving the coop ad into the uploads folder"
mkdir -p uploads/advertisements
cp static/images/ads/coop-index-230.png uploads/advertisements/

echo "adding our livecustomer and banner ads"
./manage.py shell <<'ADS'
from interactive_load import *
TextLinkAd.objects.create(source='c', 
    link='http://www.acairoots.com', text='acai')
TextLinkAd.objects.create(source='c',
    link='http://www.r4-ds-card.ca', text='r4')
TextLinkAd.objects.create(source='c',
    link='http://www.framesdirect.com/sunglasses/', text='sunglasses')

bucket = MediaBucket.objects.create(slug='ads', name='Ads')

BannerAd.front.create(
    publisher="The Swarthmore Coop",
    link="http://swarthmore.coop",
    render_type='i',
    image=ImageFile.objects.create(
        data="advertisements/coop-index-230.png",
        name="Coop Ad",
        slug="coop-ad",
        bucket=bucket,
        author_name="The Swarthmore Coop",
        license_type='p',
    ),
    date_start=datetime.date(2008, 9, 1),
    date_end  =datetime.date(2010, 3, 1),
)
ADS

echo "making sure that everything's just right :)"
./manage.py syncdb
