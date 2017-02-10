"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rrg',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.172',
    description='Utility Library for Taking AR report generating out of CakePHP DB',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/fogcitymarathoner/rrg',

    # Author details
    author='Marc Condon',
    author_email='marc@sfgeek.net',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 1 - Planning',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='CakePHP MySQL XML',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(
        exclude=['contrib', 'docs', 'tests', 'scripts', 'fabfile', 'python']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['s3_mysql_backup', 'sqlalchemy',
                      'tabulate', 'mysql-python', 'python-keyczar', 'Flask', 'Flask-Script', 'gunicorn'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'rrg-create-test-db=rrg.utils:create_db',
            'rrg-ar=rrg.scripts.ar_report:ar_report',

            'rrg-cache-clients-ar=rrg.scripts.cache_clients_ar:cache_client_accounts_receivable',
            'rrg-cache-comm-items=rrg.scripts.cache_comm_items:cache_comm_items',
            'rrg-cache-comm-payments=rrg.scripts.cache_comm_payments:cache_comm_payments',
            'rrg-cache-invoices=rrg.scripts.cache_invoices:cache_invoices',
            'rrg-cache-invoices-items=rrg.scripts.cache_invoices_items:cache_invoices_items',
            'rrg-cache-invoices-payments=rrg.scripts.cache_invoices_payments:cache_invoice_payments',
            'rrg-cache-clients-checks=rrg.scripts.cache_clients_checks:cache_checks',
            'rrg-cache-clients=rrg.scripts.cache_clients:cache_clients',
            'rrg-cache-clients-memos=rrg.scripts.cache_client_memos:cache_client_memos',
            'rrg-cache-clients-managers=rrg.scripts.cache_clients_managers:cache_client_managers',
            'rrg-cache-employees=rrg.scripts.cache_employees:cache_employees',
            'rrg-cached-employees=rrg.scripts.cached_employees:cached_employees',
            'rrg-cached-employee=rrg.scripts.cached_employee:cached_employee',
            'rrg-cache-employees-payments=rrg.scripts.cache_employees_payments:cache_employees_payments',
            'rrg-cache-employees-memos=rrg.scripts.cache_employee_memos:cache_employee_memos',
            'rrg-cache-contracts=rrg.scripts.cache_contracts:cache_contracts',
            'rrg-cache-expenses=rrg.scripts.cache_expenses:cache_expenses',
            'rrg-cache-payrolls=rrg.scripts.cache_payrolls:cache_payrolls',
            'rrg-cache-vendors=rrg.scripts.cache_vendors:cache_vendors',
            'rrg-cache-states=rrg.scripts.cache_states:cache_states',
            'rrg-cache-contract-items=rrg.scripts.cache_contract_items:cache_contract_items',
            'rrg-cached-contracts=rrg.scripts.cached_contracts:cached_contracts',
            'rrg-cached-contract=rrg.scripts.cached_contract:cached_contract',

            'rrg-assemble-contracts=rrg.scripts.assemble_contracts_cache:assemble_contracts_cache',
            'rrg-assemble-employees=rrg.scripts.assemble_employees_cache:assemble_employees_cache',
            'rrg-assemble-clients=rrg.scripts.assemble_clients_cache:assemble_clients_cache',
            'rrg-comm=rrg.scripts.commissions:comm',

            'rrg-comm-monthlies=rrg.scripts.commissions_monthly_summaries:monthlies_summary',
            'rrg-comm-monthly=rrg.scripts.commissions_monthly_summary:monthly_detail',

            'rrg-get-last-db-backup=rrg.scripts.get_last_backup:get_last_db_backup',
            'rrg-backup-db=rrg.scripts.backup_db:backup_db',
            'rrg-backup-dir=rrg.scripts.backup_dir:backup_dir',

            'rrg-sherees-notes-db=rrg.scripts.notes_report:notes',
            'rrg-reminders=rrg.scripts.reminders:reminders',
            'rrg-timecards=rrg.scripts.timecards:timecards',
            'rrg-employees=rrg.scripts.employees:employees',
            'rrg-open_invoices=rrg.scripts.open_invoices:open_invoices',
            'rrg-sherees-payroll=rrg.scripts.sherees_payroll:sherees_payroll',
            'rrg-invoices-monthly='
            'rrg.scripts.invoices_monthly:invoices_monthly',

            'rrg-sheree-total-due=rrg.scripts.sheree_monies_due:monies_due',
            'rrg-sheree-total-due-full=rrg.scripts.sherees_monies_due_full_report:monies_due',
            'rrg-cache-sherees-invoices=rrg.scripts.cache_sherees_invoices:cache_invoices',
            'rrg-cache-sherees-invoices-items=rrg.scripts.cache_sherees_invoices_items:cache_invoices_items',
            'rrg-sherees-invoices-items=rrg.scripts.sherees_invoices_items:invoices_items',

            'rrg-sherees-inv-monthlies=rrg.scripts.sheree_inv_monthly_summaries:monthlies_summary',
            'rrg-sherees-inv-monthly=rrg.scripts.sheree_inv_monthly_summary:monthly_detail',

            'rrg-forget-reminder=rrg.scripts.forget_reminder:forget_numbered_reminder',
            'rrg-void-timecard=rrg.scripts.void_timecard:void_timecard',
            'rrg-workers-comp-report=rrg.scripts.workers_comp_report:workers_comp_report',
            'rrg-reminder-to-timecard=rrg.scripts.reminder_to_timecard:reminder_to_timecard',
            'rrg-view-timecard=rrg.scripts.view_timecard:view_timecard',
            'rrg-edit-timecard=rrg.scripts.edit_timecard:edit_timecard',
            'rrg-edit-employee=rrg.scripts.edit_employee:edit_employee',
            'rrg-edit-open_invoice=rrg.scripts.edit_open_invoice:edit_open_invoice',
            'rrg-recover-joomla-files=rrg.scripts.recover_joomla_documents:recover_joomla_documents',
            'rrg-delete-old-voided-invoices=rrg.scripts.delete_old_voided_inv:delete_old_voided_invoices',
            'rrg-delete-zero-invoice-items=rrg.scripts.delete_old_zero_iitems:delete_zero_invoice_items'
        ],
    },
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],
    scripts=['rrg/scripts/ar_report.py', 
             'rrg/scripts/assemble_clients_cache.py',
             'rrg/scripts/assemble_contracts_cache.py',
             'rrg/scripts/assemble_employees_cache.py',
             'rrg/scripts/backup_db.py',
             'rrg/scripts/backup_data_to_s3.py',
             'rrg/scripts/cache_client_memos.py',
             'rrg/app.py',
        ],
)
