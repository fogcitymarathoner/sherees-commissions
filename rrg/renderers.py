from tabulate import tabulate


def format_employee(employee_dict):
    """

    :param employee_dict:
    :return:
    """
    res = ''
    res += 'id="%s", first="%s", last="%s"' % (
        employee_dict['id'], employee_dict['firstname'], employee_dict['lastname'])
    res += '\n'
    res += 'street1="%s"' % employee_dict['street1']
    res += '\n'
    res += 'street2="%s"' % employee_dict['street2']
    res += '\n'
    res += 'city="%s", state="%s", zip="%s"' % (employee_dict['city'], employee_dict['state'], employee_dict['zip'])
    res += '\n'
    res += 'startdate="%s"' % employee_dict['startdate']
    res += '\n'
    res += 'enddate="%s"' % employee_dict['enddate']
    res += '\n'
    res += 'dob="%s"' % employee_dict['dob']
    res += '\n'
    if employee_dict['memos']:
        res += 'Memos'
        res += '\n'
        res += tabulate(employee_dict['memos'], headers='keys', tablefmt='plain')
        res += '\n'
    if employee_dict['contracts']:
        res += 'Contracts'
        res += '\n'
        res += tabulate(employee_dict['contracts'], headers='keys', tablefmt='plain')
        res += '\n'
    if employee_dict['payments']:
        res += 'Payments'
        res += '\n'
        res += tabulate(employee_dict['payments'], headers='keys', tablefmt='plain')
        res += '\n'
    return res
