#!/usr/bin/env python
import requests
import urllib
import json

class pykonsoleh:

    def __init__(self):
	self.cookies = {}

    def login(self,user,passwd):
	url = "https://secure.konsoleh.co.za/frameset_home.php"
	r = requests.get(url)
	self.bakeCookies(r.cookies)
	url = 'https://secure.konsoleh.co.za/login.php'
	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Origin': 'https://secure.konsoleh.co.za',
		'Upgrade-Insecure-Requests': 1,
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Referer': 'https://secure.konsoleh.co.za/frameset_home.php',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'en,en-GB;q=0.8'
	}
	r = requests.post(url,data='login_act_as_client_number=&login_user_inputbox='+urllib.quote_plus(user)+'&login_pass_inputbox='+urllib.quote_plus(passwd),cookies=self.cookies,headers=headers)
	if '<frame src="frame_menu.php" name="leftFrame" frameborder="no" scrolling="no" noresize marginwidth="0" marginheight="0" >' in r.text:
		return True
	else:
		raise ValueError('Login failed, username or password incorrect?')

    def getServices(self):      
	url = 'https://secure.konsoleh.co.za/frame_top.php'
	r = requests.get(url,cookies=self.cookies)
	url = 'https://secure.konsoleh.co.za/frame_menu.php'
        r = requests.get(url,cookies=self.cookies)
	url = 'https://secure.konsoleh.co.za/frame_center.php'
        r = requests.get(url,cookies=self.cookies)
	url='https://secure.konsoleh.co.za/controller/domain_listing_controller.php?action=categories'
	r = requests.get(url,cookies=self.cookies)
	services = {}
	for cat in json.loads(r.text)[u'categories']:
		url='https://secure.konsoleh.co.za/controller/domain_listing_controller.php?action=fetch_services_by_category&category='+cat
		r = requests.get(url,cookies=self.cookies)
		result = json.loads(r.text)[u'domain_listings'][cat]
		rcount=0
  		for s in result:
			if u'has_children' in s.keys():
				if s[u'has_children']:
					url='https://secure.konsoleh.co.za/controller/domain_listing_controller.php?action=fetch_services_by_parent&category=%s&identifier=%s' % (cat,s[u'identifier'])
					r = requests.get(url,cookies=self.cookies)
					result[rcount][u'children'] =  json.loads(r.text)[u'domain_listings'][cat]
				del result[rcount][u'has_children']
			rcount+=1
		services[cat] = result
	return services

    def bakeCookies(self,c,pl):
	cookies = {}
	for cookie in self.cookies.keys():
                cookies[cookie] = oldcookies[cookie]

	for cookie in c.keys():
                cookies[cookie] = c[cookie]
	self.cookies = cookies

    def transferDomain(self,domain):
    	url = 'https://secure.konsoleh.co.za/controller/order_controller.php'
	payload = {
		'step':'choose_product',
		'product':2,
		'location':'za',
		'order_identifier':''
	}
        r = requests.post(url,cookies=self.cookies,data=payload)
	for l in r.iter_lines():
		if l.startswith('  var data = "{'):
			orderid = json.loads(l.strip('  var data = "').strip('";').replace('\\"','"'))[u'order_identifier']
	r = requests.get('https://secure.konsoleh.co.za/controller/order_controller.php?action=check_order_allowed&domains%%5B%%5D=%s&domain_action=transfer&server_id=&order_identifier=%s' % (domain,orderid),cookies=self.cookies)
	if json.loads(r.text)[u'viability'] != 'allowed':
		raise ValueError('Cannot transfer domain %s: %s' % (domain,r.text))
	payload = {
		'primary_domain':domain,
		'domain_action':'register_with_assistance',
		'domain_action':'transfer',
		'domain_name':domain.split('.')[0],
		'tld':domain.replace(domain.split('.')[0],''),
		'contact_me_name':'',
		'contact_me_phone':'',
		'domains[]': domain,
		'order_identifier': orderid
	}
	r = requests.post(url,cookies=self.cookies,data=payload)
	success=False
	for l in r.iter_lines():
		if l == '    This step involves processing the domain name(s) with the appropriate Registry.<br>':
			success=True
	if not success:
		raise ValueError('Failed to complete order form at the "Choose Domain" page')
	payload = pl
	payload['is_default'] = 'true'
	payload['domain_admin_check'] = 'true'
	payload['agreement'] = 'true'
	payload['order_identifier'] = orderid
	r = requests.post(url,cookies=self.cookies,data=payload)
	success=False
        for l in r.iter_lines():
                if l == '    <div id="www"><b>Payment Details</b></div>':
                        success=True
        if not success:
                raise ValueError('Failed to complete order form at the "Domain Owner" page')
	payload = {
		'order_identifier':orderid
	}
	r = requests.post(url,cookies=self.cookies,data=payload)
	success=False
        for l in r.iter_lines():
                if l == '        <div id="www"><b>Confirm Order Details</b></div>':
                        success=True
        if not success:
                raise ValueError('Failed to complete order form at the "Payment Details" page')
	payload = {
		'agreement':'true',
		'action':'submit_order_setup',
		'order_identifier':orderid
	}
	r = requests.post(url,cookies=self.cookies,data=payload)
	r = requests.get('https://secure.konsoleh.co.za/frameset_home.php?order='+orderid,cookies=self.cookies)
	r = requests.get('https://secure.konsoleh.co.za/frame_top.php',cookies=self.cookies)
	r = requests.get('https://secure.konsoleh.co.za/frame_menu.php',cookies=self.cookies)
	r = requests.get('https://secure.konsoleh.co.za/frame_center.php',cookies=self.cookies)
	success=False
        for l in r.iter_lines():
                if l == "                        Thank you for your order. Domain Registrations are dependent on successful registration at the appropriate Registry. Click on '<u>info</u>' to view your account details.":
                        success=True
        if not success:
                raise ValueError('Failed to complete order form at the "Confirm Order" page')
	return r

    def assignDomaintoDedi(self,domain,domID,dediID,dediHost,acctype='micro'):
	url = 'https://myaccount.hetzner.co.za/controller/domain_listing_controller.php?action=fetch_services_by_parent&category=managed&identifier=' + dediID
	r = requests.get(url,cookies=self.cookies)
	url = 'https://myaccount.hetzner.co.za/frame_menu.php?hosting=Managed&domain='+dediHost+'&cadmin=show&domain_number='+dediID+'&status=Ready'
	r = requests.get(url,cookies=self.cookies) 
	url = 'https://myaccount.hetzner.co.za/domainadmin.php'
	payload = {
		'account_type':acctype,
		'action':'change',
		'save':'yes',
		'domain_number_to_use':domID,
		'domain_name_to_use':domain,
		'old_account_type':'regonly',
		'select_account_type':acctype
	}
	r = requests.post(url,cookies=self.cookies,data=payload)
	success=False
        for l in r.iter_lines():
                if l == '		<td>Change submitted successfully</td>':
			success=True
	if not success:
                raise ValueError('Failed to assign domain: %s' % r.text)
        return r

    def importZone(self,domain,domID,hostType,dedHost,dedID,keeper=[],add=[]):
	if keeper == []:
		keeper = ['$TTL 7200',
    'IN SOA',
    '; serial',
    '; refresh',
    '; retry',
    '; expire',
    '; minimum',
    '\tIN\tNS\t',
    '_autodiscover._tcp  \t      \tIN\tSRV\t0 100 443 mailconfig.konsoleh.co.za.',
    'autoconfig          \t      \tIN\tCNAME\tmailconfig.konsoleh.co.za.'
		]
	url = 'https://myaccount.hetzner.co.za/controller/domain_listing_controller.php?action=fetch_services_by_parent&category=managed&identifier=%s' % (dedID)
	r = requests.get(url,cookies=self.cookies)
	url = 'https://myaccount.hetzner.co.za/frame_menu.php?hosting=Managed&domain=%s&cadmin=show&domain_number=%s&status=Ready' % (dedHost,dedID)
	r = requests.get(url,cookies=self.cookies)
	url = 'https://myaccount.hetzner.co.za/frame_menu.php?hosting=%s&domain=%s&domain_number=%s&status=Dedicated' % (hostType,domain,domID)
	r = requests.get(url,cookies=self.cookies)
	url = 'https://myaccount.hetzner.co.za/dns_shared.php?dnsaction=dns'
	r = requests.get(url,cookies=self.cookies)
	url = 'https://myaccount.hetzner.co.za/dns_shared.php'
	payload = {
		'domain_to_use':domain,
		'dnsaction':'dns',
		'dnsaction2':'editintextarea'
	}
	r = requests.post(url,cookies=self.cookies,data=payload)
	success = False
	keep = False
	zone=[]
        for l in r.iter_lines():
                if l.startswith('<td align="center"><textarea wrap="off" name="zone_file1" class="er">'):
			success=True
			keep=True
			l = l.replace('<td align="center"><textarea wrap="off" name="zone_file1" class="er">','')
		elif l == '</textarea></td>':
			keep=False
		if keep:
			zone.append(l)
        if not success:
                raise ValueError('Failed to assign domain: %s' % r.text)
	newzone = []
	for r in zone:
		for k in keeper:
		    if k in r:
			newzone.append(r)
			continue
	for r in add:
		newzone.append(r)
	zonedata = ''
	for r in newzone:
		zonedata+=r+'\r\n'
	zonedata = zonedata.strip('\r\n')
	url = 'https://myaccount.hetzner.co.za/dns_shared.php'
	payload = {
		'zone_file1': zonedata,
		'domain_to_use':domain,
		'dnsaction':'dns',
		'dnsaction2':'zonereplace',
		'update':'update domain'
	}
	r = requests.post(url,cookies=self.cookies,data=payload)
	success = False
	for l in r.iter_lines():
		if 'Domain replaced successfully' in l:
			success=True
	if not success:
                raise ValueError('Failed to update dns')
	return zonedata
