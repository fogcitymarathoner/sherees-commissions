from rrg import session
from rrg.models import Contract


def clear_out_bad_contracts():
    """
    removed contracts from the database that have either employee_id or client_id 0 or None
    """
    session.query(Contract).filter(Contract.employee_id == 0, Contract.client_id ==0).delete(synchronize_session=False)
    session.commit()
