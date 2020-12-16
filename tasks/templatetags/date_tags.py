from django import template
from datetime import datetime, timedelta

theYear = datetime.now().year
register = template.Library()

@register.simple_tag
def lastWeek(format):
	lastWeek = datetime.utcnow() - timedelta(days=7)
	return lastWeek.strftime(format)
	
@register.simple_tag
def year():
	return theYear