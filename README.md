# pykonsoleh
pseudo api for hetzner.co.za's konsoleH 

Needed to move several hundred domains to a Hetzner Dedicated Managed Server, and to my surprise found that there is no API, so I wrote a class to interface with the web panel to get it done. I've only implemented the peices that I needed, so it is in no way feature complete, but if there's interest I'll invest more time in adding functionality.

```
from pykonsoleh import pykonsoleh
k = pykonsoleh()
k.login('myemail@domain.com','MyKonsolHPassword')

# Get a list of services/domains
print k.getServices()

# add a domain to the konsoleH
k.transferDomain('mydomain.co.za')

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
