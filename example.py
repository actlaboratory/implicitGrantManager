import implicitGrantManager
import time
import webbrowser

# generate implicitGrantManager instance with clientID, authorizationURL, local portnumber
manager = implicitGrantManager.ImplicitGrantManager("1268961439.c17ebb283f3fe3659061d0ee173e42e24ac997afa6d45d1ea8880a426104d739","https://apiv2.twitcasting.tv/oauth2/authorize",9338)

# get pageUrl and open web browser
url = manager.getUrl()
webbrowser.open(url, new=1, autoraise=True)

# polling
while(True):
	time.sleep(0.01)

	# return dict or None
	token=manager.getToken()
	if token=="":
		print("Authorization failed.  May be user disagreed.")
		break
	elif token:
		print(manager.getToken())
		break
