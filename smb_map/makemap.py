import pygeoip

rawdata = pygeoip.GeoIP('GeoLiteCity.dat')
errors = 0

webpage = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>SMB connections</title>
    <style>
      #map {
        height: 100%;
      }
      html, body {
        height: 100%;
        margin: 0;
        padding: 0;
      }
    </style>
  </head>

  <body>
    <div id="map"></div>
    <script>

      var map;

      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          zoom: 3,
          center: {lat: 48.866667, lng: 2.333333},
        });
	%MARKER%
      }

    </script>
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=[YOUR_KEY]&libraries=visualization&callback=initMap">
    </script>
  </body>
</html>
'''

def ipquery(ip):
    global errors
    data = rawdata.record_by_name(ip)
    if data is not None:
	return "new google.maps.Marker({ position: {lat: %s, lng: %s}, map: map, title: '%s'})\n" % (str(data['latitude']), str(data['longitude']), ip.strip())
    else:
	return None


def get_smb_data(f):
    l = open(f, "r").readlines()
    ips = set()
    for line in l:
	ip = ipquery(line)
	if ip:
            ips.add(ip)
    return ips

print "[+] Reading smb data"
data = get_smb_data("/var/www/smb.txt")

print "[+] IPs : %d" % len(data)
print "[+] Errors : %d" % errors

print "[+] Creating web page"
f = open("/var/www/smb.html", "w")
f.write(webpage.replace("%MARKER%", ",\n".join(data)))
f.close()

print "[+] Done"

