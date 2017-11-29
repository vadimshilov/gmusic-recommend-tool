# gmusic-recommend-tool

Google music recommendation tool uses unofficial api https://github.com/simon-weber/gmusicapi.

To make `gmusic-recommend-tool` work you have to install gmusicapi. You can use `pip` to do this: `pip install gmusicapi`.

Next fill your google account data in settings.ini. Note what password is an application password, not the password you use to login in your google account. Application password can be created in security settings in google accout. It can be created if have two-factor authentication turned on.

Now you can run `main.py`. All artists which you liked on google music will be loaded. Besides all related artists will be loaded too. And recommended playlist will be created in your google music library.
