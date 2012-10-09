from django import template
from django.http import HttpRequest
from ..request.Parser import Parser
from redokes.controller import Front
import datetime
from django.utils.timezone import is_aware, utc
from django.utils.translation import ungettext, ugettext

register = template.Library()

def load_url(context, url, *args, **kwargs):
    #If args length is > 2 we should format the url
    front_controller = Front.Front(context['request'], url)
    
    # share request params with the sub request
    front_controller.request_parser.update_params(context['_front_controller'].request_parser.params)
    front_controller.request_parser.update_params(kwargs)
    return front_controller.run().content

register.simple_tag(takes_context=True)(load_url)


def timedelta(value, arg=None):
    if not value:
        return ''
    if arg:
        cmp = arg
    else:
        cmp = datetime.datetime.now()
    value = value.replace(tzinfo=None)
    
    if value > cmp:
        if cmp.year == value.year and cmp.month == value.month:
            if value.day == cmp.day:
                return 'Today' 
            elif value.day - cmp.day == 1:
                return 'Yesterday'
        return "in %s" % timesince(cmp,value)
    else:
        if cmp.year == value.year and cmp.month == value.month:
            if value.day == cmp.day:
                return 'Today' 
            elif cmp.day - value.day == 1:
                return 'Yesterday'
        return "%s ago" % timesince(value,cmp)
    
register.filter('timedelta',timedelta)

def timesince(d, now=None, reversed=False):
    chunks = (
      (60 * 60 * 24 * 365, lambda n: ungettext('year', 'years', n)),
      (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
      (60 * 60 * 24 * 7, lambda n : ungettext('week', 'weeks', n)),
      (60 * 60 * 24, lambda n : ungettext('day', 'days', n)),
      (60 * 60, lambda n: ungettext('hour', 'hours', n)),
      (60, lambda n: ungettext('minute', 'minutes', n))
    )
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now(utc if is_aware(d) else None)

    delta = (d - now) if reversed else (now - d)
    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return "Just now"
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    
    s = ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}
    return s
    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            s += ugettext(', %(number)d %(type)s') % {'number': count2, 'type': name2(count2)}
    return s
