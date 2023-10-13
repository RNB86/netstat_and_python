import csv
import logging
import os
import sys

# Init the logger
logging.basicConfig(filename='error.log', level=logging.ERROR)
# Init system arguments
cmd_args = sys.argv
# Init log files array
logs_list_array = []
# set current directory
current_directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
html_report = ""
# decription urls
wiki_description_url = "https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers"
alt_description_url1 = "https://www.speedguide.net/port.php?port="
alt_description_url2 = "https://www.adminsub.net/tcp-udp-port-finder/"
iana_description_url = "https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.txt"

page_style = "<style>h1, h2{text-align: center;} \
                     body{background-color:powderblue;} \
                     div{width: 98%;margin-left: 10px;margin-right: 15px;} \
                     table {font-family: arial, sans-serif; border-collapse: collapse; position: relative; box-shadow: 2px 2px 10px #000;} \
                     th{background-color: #72d2ec; position: sticky;top: 0; } \
                     td, th {border: 1px solid #00b1e1; text-align: left; padding: 8px; } \
                     tr:nth-child(odd) {background-color: #8bd7ec;} \
                     tr:nth-child(even) {background-color: #a7e7f9;} \
                     .html_table{margin: auto;} \
                     .footer{margin: 30px;} \
                     .references{margin-left: 40px;}</style>"

# get a port description
def get_port_description(a_port):
    # exception handling in case the description is missing
    int_port = 0
    description = ""
    if (a_port == '*'):
        return description

    try:
        int_port = int(a_port)
        if int_port == 0:
            return description
    except Exception as e:
        logging.error(f'Error conversion to integer for data {a_port}. {e}')

    try:
        # categorise the port: Well known, Registered, Dynamic
        port_short = ""
        if int_port <= 1023:
            port_short = "well-know port"
        elif (int_port >= 1024) and (int_port <= 49151):
            port_short = "registered port"
        else:
            port_short = "dynamic/ephemeral port"
        # load the element from a list
        port = ports_description[int_port]
        proto_tcp = port['TCP']
        proto_udp = port['UDP']
        descr = port['Description']
        description = f"port {a_port}</b> is a {port_short}. TCP: {proto_tcp} UDP: {proto_udp} <br>"
        # expanded description
        description += (f"<blockquote cite={wiki_description_url}><b>Usage:</b> {descr}"
                        )

    # no entry in the list with the provided key
    except KeyError:
        description = (f"port {a_port}</b> is a {port_short}. <blockquote cite={wiki_description_url}>Description is not found.")
    # common part of description
    description += (f"<br><i>Check alternative description <a href={alt_description_url1}{a_port} target='_blank'><b>here</b></a> or"
                    f"<a href={alt_description_url2}{a_port} target='_blank'><b> here</b></a></i></blockquote>"
                    )
    # return the port description
    return description

# some formatting to the date
def make_date_pretty(file_name):
    formatted_date = ""
    months = {
        '1': "January",
        '2': "Febuary",
        '3': "March",
        '4': "April",
        '5': "May",
        '6': "June",
        '7': "July",
        '8': "August",
        '9': "September",
        '10': "October",
        '11': "November",
        '12': "December"
    }

    try:
        #code
        a_date = file_name.split('_')[2]

        tmp_date = a_date.split('.log')[0]
        split_tmp_date = tmp_date.split('-')
        year = split_tmp_date[0]
        month_value = split_tmp_date[1].lstrip('0')
        month = months.get(month_value)
        # day
        day = split_tmp_date[2].lstrip('0')
        int_day = int(day)

        if int_day >= 1 and int_day <= 31:
            if (int_day == 1) or (int_day == 21) or (int_day == 31):
                day += "st"
            elif (int_day == 2) or (int_day == 22):
                day += "nd"
            elif (int_day == 3) or (int_day == 23):
                day += "rd"
            else:
                day += "th"

        formatted_date = " ".join([day, month, year])
    except Exception as e:
        formatted_date = f"Is the date has a correct format? \nDate in a filename needs to have following format [yyyy-mm-dd]"
        logging.error(type(e))
        logging.error(e)
        logging.error(f"An unexpected error occurred while processing {file_name}. \n{e}")

    return formatted_date

# load the file with ports description
def load_port_db(port_database):
    p_descr = {}
    try:
        with open(port_database, 'r', newline='') as file_data:
            csvreader = csv.DictReader(file_data, delimiter=';')
            # Store the port description as a dictionary
            for row in csvreader:
                port = int(row['Port'])
                protocol_type_tcp = row['TCP']
                protocol_type_udp = row['UDP']
                description = row['Description']
                p_descr[port] = {
                    'TCP': protocol_type_tcp,
                    'UDP': protocol_type_udp,
                    'Description': description
                }
    except FileNotFoundError as e:
        print(f"Error: {e}. The file {port_database} does not exist.")
    except Exception as e:
        logging.error(type(e))
        logging.error(e)
        logging.error(f"An unexpected error occurred while reading {port_database}: {e}")
    # return list
    return p_descr

# search directory and append if it is a netstat log to logs_list_array
def search_logs(my_path):
    current_file_list = os.listdir(my_path)
    for a_file in current_file_list:
        process_argument_as_name(a_file)

def process_argument_as_name(an_argument):
    if an_argument.endswith('.log') and an_argument.startswith('netstat'):
        logs_list_array.append(an_argument)
        print(an_argument)

# Process an argument as a filename and add it to the logs_list_array if it meets the criteria
def process_argument_as_name(an_argument):
    _, file_extension = os.path.splitext(an_argument)

    if file_extension.lower() == '.log' and an_argument.startswith('netstat'):
        logs_list_array.append(an_argument)
        print(f"Added log file: {an_argument}")
    else:
        print(f"Ignored non-netstat log file: {an_argument}")

# process the lines in log
def process_lines(csv_reader):
    print("Reading the lines and processing them")
    tmp_html_report = ""
    #global ports_description
    for row in csv_reader:
        try:
            source_port = ''
            destination_port = ''
            if '[' not in row['SourceStack'] and ']' not in row['SourceStack']:
                source_ip, source_port = row['SourceStack'].split(':')
            else:
                # ipv6 address
                source_ip, source_port = row['SourceStack'].lstrip('[').split(']:')

            if '[' not in row['DestinationStack'] and ']' not in row['DestinationStack']:
                destination_ip, destination_port = row['DestinationStack'].split(':')
            else:
                destination_ip, destination_port = row['DestinationStack'].lstrip('[').split(']:')

            destination_description = ""
            source_description = ""

            source_description = get_port_description(source_port)
            destination_description = get_port_description(destination_port)

            tmp_html_report += '\n<tr>\n'
            tmp_html_report += f'<td>{row["Protocol"]}</td>'
            # put source ip and port into td tags
            tmp_html_report += f'<td>{source_ip}</td>'
            tmp_html_report += f'<td>{source_port}</td>'
            # put destination ip and port into td tags
            tmp_html_report += f'<td>{destination_ip}</td>'
            tmp_html_report += f'<td>{destination_port}</td>'
            # put connection status, pid, pid name into td tags

            connection_status = ""
            if row["ConnectionState"].lower() != "null":
                connection_status = row["ConnectionState"]

            tmp_html_report += f'<td>{connection_status}</td>'

            tmp_html_report += f'<td>{row["PIDNumber"]}</td>'
            tmp_html_report += f'<td>{row["PIDName"]}</td>'

            # concatenate description in td tags
            tmp_html_report += '<td>'

            if (source_description != ''):
                tmp_html_report += f'<b>Source {source_description}'
            if (destination_description != ''):
                tmp_html_report += f'<br><b>Destination {destination_description}'
            # close description and row

            tmp_html_report += '</td>'
            # finalize the row aka close tr tag
            tmp_html_report += '</tr>'
        except Exception as e:
            logging.error(type(e))
            logging.error(e)
            logging.error(f"An unexpected error occurred while processing row {row}. \n{e}")
        # return html formated text
    tmp_html_report += '</table></div>'
    return tmp_html_report


# Process the log file
def process_the_log(a_log_file):
    print(f"Processing the log file: {a_log_file}")
    hostname = ""
    date = ""
    report = ""
    log_file_full_path = current_directory + '\\' + a_log_file
    # try to open the file and then process it
    try:
        with open(log_file_full_path, 'r', encoding='UTF-8') as log_file_data:
            hostname = str(a_log_file).split('_')[1]
            date = str(a_log_file).split('_')[2]
            csvreader = csv.DictReader(log_file_data, delimiter=';')
            #somehow check the csv header
            report = process_lines(csvreader)
    # file not found exception
    except FileNotFoundError as e:
        logging.error(f"Error processing log file {log_file_full_path}: {e}")
    # dark magic exception
    except Exception as e:
        logging.error(type(e))
        logging.error(e)
        logging.error(f"An unexpected error occurred while processing {log_file_full_path}: {e}")
    return [report,hostname,date]

# Process command-line arguments
def proceed_arguments(some_args):
    i = 1
    if (len(some_args) > 1):
        while (i < len(some_args)) :
            tmp_file_name = some_args[i]
            # * search directory and append any netstat log into the array
            if ("*" in tmp_file_name):
                search_logs(current_directory)
            #if name is good, then add it in a file
            if (os.path.isfile(tmp_file_name)):
                process_argument_as_name(tmp_file_name)
            else:
                logging.error(f"File {tmp_file_name} does not exist.")
            i +=1
    else:
        print("No arguments given, parsing all logs in current directory ")
        search_logs(current_directory)

def init_html_output():
    global html_report
    html_report = f'<html><head>{page_style}<title>Netstat Activity Report</title></head><body>'

def add_html_output(text):
    global html_report
    html_report += text

def get_html_output():
    global html_report
    return html_report

def finialise_html_output():
    tmp_html = ""
    tmp_html += "\n".join(
        [
            '\n<div class="footer">',
            '<h3>Additional references:</h3>',
            '<div class="references"><b>IANA port description:</b>',
            '<blockquote>',
            f'<a href={iana_description_url} target="_blank"><i>Internet Assigned Numbers Authority. Service Name and Transport Protocol Port Number Registry</i></a>',
            '</blockquote><b>Wikipedia port description:</b><blockquote>',
            f'<a href={wiki_description_url} target="_blank"><i>List of TCP and UDP port numbers</i></a>',
            '</blockquote></div></div>',
            '</body>',
            '</html>'
        ]
    )
    add_html_output(tmp_html)

# load port description
ports_description = load_port_db('port_db.csv')
# Main function
def main():
    proceed_arguments(cmd_args)

    if len(logs_list_array) != 0:
        print("Processing the log files")
        for f in logs_list_array:
            init_html_output()
            # format: [report,hostname,date]
            # open a log file
            report_array = process_the_log(f)
            host_name = report_array[1]
            file_date = report_array[2].split(".")[0]
            report_date = make_date_pretty(f)
            # initiate html header
            add_html_output(f'<h1>Netstat Activity Report for {host_name}</h1>')
            add_html_output(f'<h2>{report_date}</h2>')
            add_html_output('\n'.join([
                            '\n<div class="html_table">'
                            '<table border="1">',
                            '<tr>',
                                '<th>Protocol</th>',
                                '<th>Source IP </th>',
                                '<th> Source Port</th>',
                                '<th>Destination IP </th>',
                                '<th>Destination Port</th>',
                                '<th>State</th>',
                                '<th>PID</th>',
                                '<th>Process</th>',
                                '<th>Description</th>',
                            '</tr>'
                            ]
            ))
            # concatenate the html header with generated report
            # I want separate paragraph for it
            add_html_output(report_array[0])
            # close html page tags
            finialise_html_output()
            # save the report to a file
            html_file = current_directory + '\\' + host_name + "_" + file_date + '.html'
            with open(html_file, "w") as f:
                f.writelines(get_html_output())

    else:
        print("Nothing to process. Exiting...")

if __name__ == "__main__":
    main()
