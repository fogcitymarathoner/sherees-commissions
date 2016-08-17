from rrg.models import Invoice


def invoices_year_month(session, args):
    m = int(args.month)
    y = int(args.year)
    if m < 12:
        nexty = y
        nextm = m + 1
    else:
        nexty = int(y) + 1
        nextm = 1

    return  session.query(Invoice).filter(and_(Invoice.date >= dt(year=y, month=m, day=1),
        Invoice.date < dt(year=nexty, month=nextm, day=1))).all()
