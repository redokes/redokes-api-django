import sys
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = ''
    help = 'Testing'

    def handle(self, *args, **options):
        print 'just testing'
