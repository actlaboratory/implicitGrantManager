import implicitGrantManager
import time
import webbrowser

# generate implicitGrantManager instance with clientID, authorizationURL, local portnumber
manager = implicitGrantManager.ImplicitGrantManager(CLIENT_ID,AUTHORIZE_URL,LOCAL_PORT)

# get pageUrl and open web browser
url = manager.getUrl()
webbrowser.open(url, new=1, autoraise=True)

# polling
while(True):
	time.sleep(0.01)

	# return dict, "" or None
	token=manager.getToken()
	if token=="":
		print("Authorization failed.  May be user disagreed.")
		break
	elif token:
		print(manager.getToken())
		break
	# if token==None: continue polling
	manager.shutdown()
