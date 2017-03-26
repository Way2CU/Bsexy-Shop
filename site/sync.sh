#!/bin/sh
echo Clearing cache...
rm html/site/cache/*

echo Synchronizing files...
rsync --verbose --exclude=.htaccess --exclude=config.php --exclude=cache/ --exclude=gallery/ --exclude=config.php.old --recursive --owner --group test/site/ html/site/

echo Updating Caracal...
cd html
git pull
