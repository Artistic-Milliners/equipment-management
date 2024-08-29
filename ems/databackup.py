import json
from django.core.management import call_command
from io import StringIO
import os
import django



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ems.settings')
django.setup()

# Initialize a StringIO to capture the output of dumpdata
out = StringIO()

# Call the dumpdata command
call_command('dumpdata', stdout=out)

# Get the output from the StringIO object
output = out.getvalue()

# Write the output to a file with UTF-8 encoding
with open('backup.json', 'w', encoding='utf-8') as f:
    f.write(output)
