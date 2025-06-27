from django.utils.deprecation import MiddlewareMixin
from django.contrib.gis.geoip2 import GeoIP2
from .models import VisitorSession

class GeoIPMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key

        if 'visitor_country' not in request.session:
            ip = self.get_client_ip(request)
            country = self.get_country_from_ip(ip)
            request.session['visitor_country'] = country

        # if not VisitorSession.objects.filter(session_key=session_key).exists():
        #     ip = self.get_client_ip(request)
        #     country = self.get_country_from_ip(ip)
        #     VisitorSession.objects.create(ip_address=ip, country=country, session_key=session_key)

        ip = self.get_client_ip(request)
        if not VisitorSession.objects.filter(ip_address=ip).exists():
            country = self.get_country_from_ip(ip)
            VisitorSession.objects.create(ip_address=ip, country=country, session_key=session_key)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0] 
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_country_from_ip(self, ip):
        try:
            geo = GeoIP2()
            country = geo.country(ip)['country_name']
        except Exception:
            country = "Unknown"
        return country
