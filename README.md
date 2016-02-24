# Doc-Saver

This project makes automated saving of documents from _simple_ websites into Dropbox easy. It sends mobile push notifications upon every save via Pushover and can be automatically run as a cron job. In the future, I'll customize it further to handle more complicated websites.

The following environment variables must be configured for this script to function:
* DOCSAVER_DB_ACCESSTOKEN
* DOCSAVER_PUSHOVER_APPTOKEN
* PUSHOVER_USERKEY
