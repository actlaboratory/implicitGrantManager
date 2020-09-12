import threading
import uuid
import wsgiref.util
from oauthlib.oauth2 import MobileApplicationClient,OAuth2Error
from wsgiref.simple_server import make_server

class ImplicitGrantManager:
	def __init__(self,cid,oauthPageUrl,receivePort):
		"""
			Args:
				cid (string): The client id from Authorization provider
				oauthPageUrl (string): The authorization Page url
				receivedPort (string): The port number to receive request
		"""
		self.result=None

		self.clientId = cid
		self.oauthPageUrl = oauthPageUrl
		self.port = receivePort

		#generate CSRF token
		self.token = str(uuid.uuid4())

		#generate request URL
		self.oauth = MobileApplicationClient(self.clientId)
		self.url, headers, body = self.oauth.prepare_authorization_request(
				self.oauthPageUrl,
				redirect_url="http://localhost:%s" % self.port,
				state=self.token
			)

		#start local web server
		self.wsgi_app = _RedirectWSGIApp(
				self.port,
				self.oauth,
				self._registToken
			)
		self.localServer = wsgiref.simple_server.make_server("localhost", self.port, self.wsgi_app, handler_class=_WSGIRequestHandler)
		thread = threading.Thread(target=self._localServerThread,args=(self.localServer,))
		thread.start()

	def setMessage(self,lang,success,failed,transfer):
		"""
			Set Message that viewd in browser
			Args:
				lang (string): The message language code (ex:ja,en,...)
				success (string): The success message
				failed (string): The failed message
				transfer (string): The transfer error message that appear in old or Javascript disabled browser
		"""
		self.wsgi_app.setMessage(lang,success,failed,transfer)

	def getUrl(self):
		"""
			Get Authorization url
			Returns:
				AuthorizationUrl (string)

		"""
		return self.url

	def getToken(self):
		"""
			Get accesstoken (success) or None (waiting / failed)
			Returns:
				tokenData (dict) or None
		"""
		if self.result!=None:
			self._shutdown()
		return self.result

	def _registToken(self,result):
		self.result=result

	def __del__(self):
		self._shutdown()

	def _shutdown(self):
		if self.localServer:
			self.localServer.shutdown()
			self.localServer=None

	def _localServerThread(self,server):
		server.serve_forever()

class _WSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):
	def __init__(self,*args,**argv):
		super().__init__(*args,*argv)
		#コネクションは毎回切断する
		self.close_connection=True

	def log_message(self, *args):
		#disable logger
		pass

class _RedirectWSGIApp(object):
	"""
		WSGI app to handle the authorization redirect.
		Stores the request URI and displays the given success message.
	"""
	def __init__(self, port, oauth, hook):
		"""
			Args:
				port (int): The port number That receive request
				oauth (oauthlib.oauth2): The oAuth object using validation request
				hook (callable): The function when got token
		"""
		self.successMessage="Authorization successfully.  Close browser and go back application."
		self.failedMessage="Authorization failed.  Please try again."
		self.transferMessage="If the screen does not switch after a while, open this page in another browser."
		self.lang = "ja"

		self.port = port
		self.oauth = oauth
		self.hook = hook

	def setMessage(self,lang,success,failed,transfer):
		"""
			Set Message that viewd in browser
			Args:
				lang (string): The message language code (ex:ja,en,...)
				success (string): The success message
				failed (string): The failed message
				transfer (string): The transfer error message that appear in old or Javascript disabled browser
		"""
		self.lang=lang
		self.successMessage=success
		self.failedMessage=failed
		self.transferMessage=transfer

	def __call__(self, environ, start_response):
		"""
			WSGI Callable.

			Args:
				environ (Mapping[str, Any]): The WSGI environment.
				start_response (Callable[str, list]): The WSGI start_response
					callable.
			Returns:
				Iterable[bytes]: The response body.
		"""
		if environ["QUERY_STRING"]=="":
			#JSでリダイレクト
			start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
			response=[("<!DOCTYPE HTML><html lang='"+self.lang+"'><head><title>Authorization transfer</title><meta charset='utf-8'>").encode("utf-8")]
			response.append("<script type='text/javascript'><!--\n".encode('utf-8'))
			response.append(("location.href=(\"http://localhost:%s?\" + location.hash.slice(1));\n" % self.port ).encode('utf-8'))
			response.append(("--> </script></head><body>"+self.transferMessage+"</body></html>").encode('utf-8'))
			return response
		else:
			try:
				uri = wsgiref.util.request_uri(environ).replace("http://","https://")
				uri = uri.replace("/?","/#")
				ret = self.oauth.parse_request_uri_response(uri)

				#例外発生しなければ正当なリクエスト
				start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
				#サーバ側で処理
				self.hook(ret)
				return [("<html lang='"+self.lang+"'><head><title>Authorization result</title><meta charset='utf-8'></head><body>"+self.successMessage+"</body></html>").encode('utf-8')]
			except OAuth2Error as e:
				start_response('400 Bad Request', [('Content-type', 'text/html; charset=utf-8')])
				return [("<html lang='"+self.lang+"'><head><title>Authorization result</title><meta charset='utf-8'></head><body>"+self.failedMessage+"</body></html>").encode('utf-8')]

if __name__ == '__main__':
	import time
	import webbrowser
	a = ImplicitGrantManager("1268961439.c17ebb283f3fe3659061d0ee173e42e24ac997afa6d45d1ea8880a426104d739","https://apiv2.twitcasting.tv/oauth2/authorize",9338)
	url = a.getUrl()
	webbrowser.open(url, new=1, autoraise=True)
	while(True):
		time.sleep(0.01)
		if a.getToken():
			print(a.getToken())
			break