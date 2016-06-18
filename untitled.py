import urlparse

def uri_connect_auth1(u):
    k = urlparse.urlparse(u)
    m = urlparse.parse_qs(k.query)
    client_id = m['access_token'][0]
    token = m['redirect_uri'][0]
    return '/connect/auth?client_id=%s&response_type=code&access_token=%s&redirect_uri=nucleus:rest' % (client_id, token)

def uri_upid(u):
    k = urlparse.urlparse(u)
    m = urlparse.parse_qs(k.query)
    client_id = m['a'][0]
    return '/connect/upidtoken?client_id=%s' % (client_id)

def uri_auth_mobileupid(u):
    k = urlparse.urlparse(u)
    m = urlparse.parse_qs(k.query)
    token = m['a'][0]
    client_id = m['b'][0]
    return '/connect/auth?mobile_login_type=mobile_game_UPID&mobile_UPIDToken=%s&client_id=%s&response_type=code&redirect_uri=nucleus:rest' % (token, client_id)

def upidgen():
    data = 'a6a6a47f-c00f-43f1-b61a-df4a39877b15'
    k = ["HTTP/1.1 200 OK",
    "X-NEXUS-SEQUENCE: 104.236.77.120:1453128487704",
    "X-NEXUS-HOSTNAME: eanprdaccounts04",
    'P3P: CP="ALL DSP COR IVD IVA PSD PSA TEL TAI CUS ADM CUR CON SAM OUR IND"',
    'Pragma: no-cache',
    'Expires: Thu, 01 Jan 1970 00:00:00 GMT',
    'Cache-Control: no-cache',
    'Cache-Control: no-store',
    'Content-Type: text/plain;charset=ISO-8859-1',
    'Content-Length: '+str(len(data)),
    'Date: Mon, 18 Jan 2016 14:48:07 GMT',
    'Server: Powered by Electronic Arts',
    '',
    data]
    return "\r\n".join(k)

def static_blaze():
    data = '<?xml version="1.0" encoding="UTF-8"?>\n<serverinstanceinfo>\n    <address member="0">\n        <valu>\n            <hostname>508454-gosprapp1211.ea.com</hostname>\n            <ip>3561002230</ip>\n            <port>10041</port>\n        </valu>\n    </address>\n    <secure>0</secure>\n    <trialservicename></trialservicename>\n    <defaultdnsaddress>0</defaultdnsaddress>\n</serverinstanceinfo>\n'
    k = ["HTTP/1.1 200 OK",
    "Content-Type: application/xml",
    "X-BLAZE-COMPONENT: redirector",
    "X-BLAZE-COMMAND: getServerInstance",
    "Content-Length: "+str(len(data)),
    "X-BLAZE-SEQNO: 0",
    '', 
    data]
    return "\r\n".join(k)

def bzeserver():
    data="""<?xml version="1.0" encoding="UTF-8"?>
    <serverinstancerequest>
        <blazesdkversion>14.2.1.4.0</blazesdkversion>
        <blazesdkbuilddate>Nov 17 2015 18:36:01</blazesdkbuilddate>
        <clientname>FIFA_15_iOS</clientname>
        <clienttype>CLIENT_TYPE_GAMEPLAY_USER</clienttype>
        <clientplatform>ios</clientplatform>
        <clientskuid>EAX06709607</clientskuid>
        <clientversion>-1</clientversion>
        <dirtysdkversion>14.2.1.4.2</dirtysdkversion>
        <environment>prod</environment>
        <clientlocale>1701729619</clientlocale>
        <name>fifa-2015-ios</name>
        <platform>iPhone</platform>
        <connectionprofile>standardSecure_v4</connectionprofile>
    </serverinstancerequest>"""

    r = requests.post("https://spring14.gosredirector.ea.com:42230/redirector/getServerInstance", data=data, headers = {'User-Agent': 'ProtoHttp 1.3/DS 14.2.1.4.2 (AppleIOS)', 'Content-Type': 'application/xml'}, verify=False).content

    print r
    root = ET.fromstring(r)

    valu = list(root.iter('valu'))[0]
    ip = [a for a in valu if a.tag == 'ip'][0].text
    port = [a for a in valu if a.tag == 'port'][0].text

    host = ".".join([str((int(ip) >> (24 - a*8)) & 255)  for a in range(0,4) ])
    port = int(port)

    return (host, port)