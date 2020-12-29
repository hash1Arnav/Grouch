import requests
from bs4 import BeautifulSoup

class Course:
    def __init__(self, name: str, crn: str):
        self.name, self.crn = name, crn
        self.term = '202102' # default
    
    def __get_registration_info(self, term: str):
        url = 'https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?term_in='
        url += term + '&crn_in=' + self.crn

        with requests.Session() as s:
            with s.get(url) as page:
                soup = BeautifulSoup(page.content, 'html.parser')
                table = soup.find('caption', string='Registration Availability').find_parent('table')

                if len(table) == 0: raise ValueError()

                data = [int(info.getText()) for info in table.findAll('td', class_='dddefault')]
                return data

    def get_registration_info(self, term: str):
        self.term = term
        data = self.__get_registration_info(term)

        if len(data) < 6: raise ValueError()

        waitlist_data = {
            'seats': data[3],
            'taken': data[4],
            'vacant': data[5]
        }
        load = {
            'seats': data[0],
            'taken': data[1],
            'vacant': data[2],
            'waitlist': waitlist_data
        }
        return load

    def is_open_by_term(self, term: str) -> bool:
        return self.__get_registration_info(term)[2] > 0

    def is_open(self) -> bool:
        return self.is_open_by_term(self.term)

    def waitlist_available_by_term(self, term: str) -> bool:
        waitlist_data = self.get_registration_info(term)['waitlist']
        return waitlist_data['vacant'] > 0

    def waitlist_available(self) -> bool:
        return self.waitlist_available_by_term(self.term)

    def __str__(self) -> str:
        data = self.get_registration_info(self.term)
        res = "{}\n".format(self.name)
        for name in data:
            if name == 'waitlist': continue
            res += "{}:\t{}\n".format(name, data[name])
        res += "waitlist open: {}".format('yes' if self.waitlist_available() else 'no')
        return res

class CourseList:
    def __init__(self, *courses):
        self.courses = courses

    # TODO: set up course list (this will be used for running the script)