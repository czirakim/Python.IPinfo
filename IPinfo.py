import json
import requests
import flask
import datetime

def main(request):
    clientip = request.environ['HTTP_X_FORWARDED_FOR']
    ip = request.args.get('ip', clientip)   
    reply = asn(request)
    info= json.loads(reply.text)
    asnumber = info['data']['prefixes'][0]['asn']['asn']
    isp = info['data']['prefixes'][0]['asn']['name']
    country = info['data']['maxmind']['country_code']
    city = info['data']['maxmind']['city']
    as_info = ASnum(asnumber)
    res_uptime,upstream  = as_info.event()
    result = {
    "Your IP is": ip,
    "AS number": asnumber, 
    "ISP": isp,
    "City": city,
    "Country": country,
    "Upstream AS" : upstream,
    "Upstream AS events": res_uptime
    }
    y=json.dumps(result, indent=4)
    return flask.Response(y, mimetype='application/json')

def asn(request):
    clientip = request.environ['HTTP_X_FORWARDED_FOR']
    ip = request.args.get('ip', clientip)
    api_url = 'https://api.bgpview.io/ip/' + ip
    response = requests.get(api_url)
    return  response  

class ASnum:
    def __init__(self,number):
	    self.number = number
        
    def asn_upstream(self):
        api_url= 'https://api.bgpview.io/asn/'+str(self.number)+'/upstreams'
        response = requests.get(api_url)
        return  response  

    def asn_uptime(self,number):
        api_url= 'https://ioda.caida.org/ioda/data/events?annotateMeta=true&human=true&meta=asn/'+str(number)
        response = requests.get(api_url)
        info1= json.loads(response.text)
        m=info1['data']['events']
        y = []
        for n in m:
            ts = datetime.datetime.fromtimestamp(n['start']).strftime('%Y-%m-%d %H:%M:%S')
            d= datetime.datetime.fromtimestamp(n['duration']).strftime('%H:%M:%S')
            output = {"asn": n['location_code'],"Description": n['location_name'],"Start time(UTC)": ts, "Duration": d,"Status": n['status']}
            y.append(output)
        return y   
    
    def event(self):
        res_uptime = []
        info1= json.loads(self.asn_upstream().text)
        upstream = info1['data']['ipv4_upstreams']
        for i in upstream:
            a = self.asn_uptime(i['asn'])
            res_uptime.append(a)
        return  res_uptime, upstream       
        
