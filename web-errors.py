"""
Write a Java, Python, Ruby, Php or Bash  script that will tail a NGINX, IIS or Apache log file and cumulatively aggregate 2XX, 3XX, 4XX & 5XX errors by minute. You can use a database. Push the code to Github and share.
"""

import re
import datetime
from sh import tail
from elasticsearch import Elasticsearch


# Read log file and search for errors
def read_log_file(log_file):

    errors = [0,0,0,0]
    counter = 0
    date_holder = datetime.datetime.now().replace(second=0)

    for line in tail("-f", log_file, _iter=True):
        
        # Find values 
        times = re.findall("([0-9]{2}\/[A-z]{3}\/[0-9]{4}\:[0-9]{2}\:[0-9]{2}\:[0-9]{2})", line)
        codes = re.findall(" [0-9]{3} |$", line)
        
        if times is not None:
            counter += 1

        if (codes[0][1] == '2'):
            errors[0] += 1
        if (codes[0][1] == '3'):
            errors[1] += 1
        if (codes[0][1] == '4'):
            errors[2] += 1
        if (codes[0][1] == '5'):
            errors[3] += 1

        error_datetime = datetime.datetime.now()

        # Check if a minute has passed
        if abs(date_holder - error_datetime) > datetime.timedelta(minutes=1):

            add_to_db(error_datetime.replace(second=0), errors)
            date_holder = error_datetime

            #Reset values
            counter = 0
            errors = [0,0,0,0]


def convert_to_time(input):

    # Convert string date into datetime format for calculation
    datetime_output = datetime.datetime.strptime(input, '%d/%b/%Y:%H:%M:%S')

    return datetime_output


def add_to_db(time, error):

    print time
    print error
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    k = ({
        "_index" : "errors",
        "_2xx"   : error[0],
        "_3xx"   : error[1],
        "_4xx"   : error[2],
        "_5xx"   : error[3]
    })

    es.bulk(k)
   


def main():
    apache_log_file = "/var/log/apache2/access.log"

    read_log_file(apache_log_file)


if __name__ == '__main__':
    main()