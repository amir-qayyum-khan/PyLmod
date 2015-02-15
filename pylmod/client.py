"""
Python interface to MIT Learning Module
"""
import json
import logging

import requests


log = logging.getLogger(__name__)


class Client(object):
    """
    Python class representing interface to MIT Learning Modules.

    Example usage:

    sg = Client('ichuang-cert.pem')
    ats = sg.get('academicterms')
    tc = ats['data'][0]['termCode']
    sg.get('academicterm',termCode=tc)

    students = sg.get_students()
    assignments = sg.get_assignments()
    sg.create_assignment('midterm1', 'mid1', 1.0, 100.0, '11-04-2013')

    sid, student = sg.get_student_by_email(email)
    aid, assignment = sg.get_assignment_by_name('midterm1')
    sg.set_grade(aid, sid, 95.2)

    sg.spreadsheet2gradebook(datafn)

    """

    GETS = {'academicterms': '',
            'academicterm': '/{termCode}',
            'gradebook': '?uuid={uuid}',
            }

    GBUUID = 'STELLAR:/project/mitxdemosite'
    TIMEOUT = 200  # connection timeout, seconds

    verbose = True
    gradebookid = None

    def __init__(
        self, cert, urlbase=None
    ):
        """
        Initialize Client instance.

          - urlbase:    URL base for gradebook API (defaults to self.URLBASE)
            (still needs certs); default False
          - gbuuid:     gradebook UUID (eg STELLAR:/project/mitxdemosite)

        """
        # pem with private and public key application certificate for access
        self.cert = cert

        if urlbase is not None:
            self.URLBASE = urlbase
        self.ses = requests.Session()
        self.ses.cert = cert
        self.ses.timeout = self.TIMEOUT  # connection timeout
        self.ses.verify = True  # verify site certificate

        log.debug("------------------------------------------------------")
        log.info("[Client] init base=%s" % urlbase)

    def rest_action(self, fn, url, **kwargs):
        """Routine to do low-level REST operation, with retry"""
        cnt = 1
        while cnt < 10:
            cnt += 1
            try:
                return self.rest_action_actual(fn, url, **kwargs)
            except requests.ConnectionError, err:
                log.error(
                    "[Client] Error - connection error in "
                    "rest_action, err=%s" % err
                )
                log.info("                   Retrying...")
            except requests.Timeout, err:
                log.exception(
                    "[Client] Error - timeout in "
                    "rest_action, err=%s" % err
                )
                log.info("                   Retrying...")
        raise Exception(
            "[Client] rest_action failure: exceeded max retries"
        )

    def rest_action_actual(self, fn, url, **kwargs):
        """Routine to do low-level REST operation"""
        log.info('Running request to %s' % url)
        r = fn(url, timeout=self.TIMEOUT, verify=False, **kwargs)
        try:
            retdat = json.loads(r.content)
        except Exception, err:
            log.exception(r.content)
            raise err
        return retdat

    def get(self, service, params=None, **kwargs):
        """
        Generic GET operation for retrieving data from Gradebook API
        Example:
          sg.get('students/{gradebookId}', params=params, gradebookId=gbid)
        """
        urlfmt = '{base}/' + service + self.GETS.get(service, '')
        url = urlfmt.format(base=self.URLBASE, **kwargs)
        if params is None:
            params = {}
        return self.rest_action(self.ses.get, url, params=params)

    def post(self, service, data, **kwargs):
        """
        Generic POST operation for sending data to Gradebook API.
        data should be a JSON string or a dict.  If it is not a string,
        it is turned into a JSON string for the POST body.
        """
        urlfmt = '{base}/' + service
        url = urlfmt.format(base=self.URLBASE, **kwargs)
        if not (type(data) == str or type(data) == unicode):
            data = json.dumps(data)
        headers = {'content-type': 'application/json'}
        return self.rest_action(self.ses.post, url, data=data, headers=headers)

    def delete(self, service, data, **kwargs):
        """
        Generic DELETE operation for Gradebook API.
        """
        urlfmt = '{base}/' + service
        url = urlfmt.format(base=self.URLBASE, **kwargs)
        if not (type(data) == str or type(data) == unicode):
            data = json.dumps(data)
        headers = {'content-type': 'application/json'}
        return self.rest_action(
            self.ses.delete, url, data=data, headers=headers
        )


# todo.remove these methods once refactoring is done
class SGClient(object):
    def get_academic_terms(self):
        raise NotImplementedError

    def get_assignment_by_name(self):
        raise NotImplementedError

    def get_assignments(self):
        raise NotImplementedError

    def get_gradebook_id(self, gbuuid):
        raise NotImplementedError

    def get_grades(self):
        raise NotImplementedError

    def get_section_by_name(self):
        raise NotImplementedError

    def get_sections(self):
        raise NotImplementedError

    def get_student_by_email(self):
        raise NotImplementedError

    def get_students(self):
        raise NotImplementedError

    def create_assignment(self):
        raise NotImplementedError

    def delete_assignment(self):
        raise NotImplementedError

    def set_grade(self):
        raise NotImplementedError

    def set_multigrades(self):
        raise NotImplementedError



