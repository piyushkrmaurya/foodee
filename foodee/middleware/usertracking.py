"""
Custom middlewares
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.gis.geoip2 import GeoIP2
from django.shortcuts import render

#this function returns the user ip
def get_client_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META['REMOTE_ADDR']
    return ip

#this redirects to 404 Error page when a bad url is requested
class checkBadURLMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        location = None
        ip = get_client_ip(request)
        try:
            g = GeoIP2()
            location = g.city(ip)+", "+g.country(ip)
        except Exception as e:
            print(e)
            location = 'localhost'
        if response.status_code == 404:
            return render(request, '404.html', {'ip': ip, 'location': location})
        elif response.status_code == 500:
            return render(request, '500.html', {'ip': ip, 'location': location})
        else:
            return response


#this checks if the user is accessing the website from India
class checkLocationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        ip = get_client_ip(request)
        try:
            g = GeoIP2()
            location = {'ip': ip}
            location['city'] = g.city(location['ip'])
            location['country'] = g.country(location['ip'])

        except Exception as e:
            print(e)
            location = {'ip': ip, 'city': 'Varanasi', 'country': 'India'}
        
        if location['country'] != 'India':
            return render(request, 'sorry_not_india.html', {'location':location})
        else:
            return None
