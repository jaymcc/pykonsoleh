# pykonsoleh
pseudo api for hetzner.co.za's konsoleH 

Needed to move several hundred domains to a Hetzner Dedicated Managed Server, and to my surprise found that there is no API, so I wrote a class to interface with the web panel to get it done. I've only implemented the peices that I needed, so it is in no way feature complete, and has only been tested for our specific use case. If there's interest I'll invest more time in improving the library.

```
from pykonsoleh import pykonsoleh
k = pykonsoleh()
k.login('myemail@domain.com','MyKonsolHPassword')

# Get a list of services/domains
print k.getServices()

# add a domain to the konsoleH
registrant = {
                'selected_contact':'contactID',
		'category':'legal',
		'title':'Mr',
		'first_name':'Joe',
		'surname':'Soap',
		'company_name':'ACME',
		'street': 'PO Box 123',
		'suburb':'Brooklyn',
		'postal_code':'7405',
		'city':'Cape Town', 
		'country':'ZA',
		'state':'',
		'telephone':'+27 21 123 1234',
		'email':'dns-admin@mydomain.com'
	}
k.transferDomain('mydomain.co.za',registrant)

# assign a domain to a dedicated server
k.assignDomaintoDedi('mydomain.co.za','domainID')

# import zone file - keeps ns, soa and autodiscover records as is
add= [
        'plinkyplonk.mydomain.co.za. 120        IN      A       127.0.0.62',
        'mydomain.co.za.                60      IN      A       127.0.0.123',
        'www.mydomain.co.za.    3600    IN      CNAME   web3.otherdomain.co.za.',
        'derp.mydomain.co.za.   86400   IN      A       10.0.0.1'
        ]
k.importZone('mydomain.co.za','domainID','PackageName','dediHostname','dediID',add=add)
```
