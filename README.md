# Doc-Saver

This project makes automated saving of documents from simple websites into Dropbox easy. It sends mobile push notifications upon every save and can be automatically run after setup as a cron job.

The following environment variables must be configured for this script to function:
* DOCSAVER_DB_ACCESSTOKEN
* DOCSAVER_PUSHOVER_APPTOKEN
* PUSHOVER_USERKEY