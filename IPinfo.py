import json
import requests
import flask
import datetime

def main(request):
    clientip = request.environ['HTTP_X_FORWARDED_FOR']
    asnumber = asn(request)
    reply = asn(request)
    info= json.loads(reply.text)
    asnumber = info['data']['prefixes'][0]['asn']['asn']
    isp = info['data']['prefixes'][0]['asn']['name']
    country = info['data']['maxmind']['country_code']
    city = info['data']['maxmind']['city']
    as_info = asn_upstream(asnumber) 
    info1= json.loads(as_info.text)
    upstream = info1['data']['ipv4_upstreams']
    res_uptime = []
    for i in upstream:
         a = asn_uptime(i['asn'])
         res_uptime.append(a)
    result = {
    "Your IP is": clientip,
    "AS number": asnumber, 
    "ISP": isp,
    "City": city,
    "Country": country,
    "Upstream AS" : upstream,
    "Upstream AS outages": res_uptime
    }
    y=json.dumps(result, indent=4)
    return flask.Response(y, mimetype='application/json')

def asn(request):
    clientip = request.environ['HTTP_X_FORWARDED_FOR']
    api_url= 'https://api.bgpview.io/ip/'+clientip
    response = requests.get(api_url)
    return  response  

def asn_upstream(number):
    import requests
    api_url= 'https://api.bgpview.io/asn/'+str(number)+'/upstreams'
    response = requests.get(api_url)
    return  response  

def asn_uptime(number):
    api_url= 'https://ioda.caida.org/ioda/data/alerts?annotateMeta=true&human=true&meta=asn/'+str(number)
    response = requests.get(api_url)
    info1= json.loads(response.text)
    m=info1['data']['alerts']
    y = []
    for n in m:
        ts = datetime.datetime.fromtimestamp(n['time']).strftime('%Y-%m-%d %H:%M:%S')
        output = {"asn": n['metaCode'],"time": ts, "Level": n['level']}
        y.append(output)
    return y   
        
