class CapitalGroup:
    cg_companies = []
    def __init__(self, is_cg, cg_name=None, cg_num=0):
        self.is_cg = is_cg
        self.cg_name = cg_name
        self.cg_num = cg_num

    def __str__(self):
        if self.is_cg:
            return f'Grupa Kapitałowa: \033[34m{self.cg_name}\033[0m\nLiczba przedsiębiorstw wchodzących w skład grupy: \033[34m{self.cg_num}\033[0m'
        else:
            return f'Brak grupy kapitałowej'

    def update_cg(self, is_cg):
        clear_companies()
        if is_cg:
            self.is_cg = is_cg
            self.cg_name = input('Podaj nazwę grupy kapitałowej:')
            self.cg_num = int(input('Podaj liczbę przedsiębiorstw wchodzących w skład grupy kapitałowej:'))
            for x in range(self.cg_num):
                companies.append(Company(co_id=x, cg_name=cg.cg_name))
            for company in companies:
                company.update_co()
        else:
            self.is_cg = is_cg
            companies.append(Company(co_id=0, cg_name='-----'))
            companies[0].update_co()


class Company:
    def __init__(self, co_id, co_name=None, cg_name=None, co_country=None, co_city=None, co_street=None, co_zip=None, co_tel=None,
                 co_mail=None, co_krs=None, co_regon=None, co_nip=None):
        self.co_id = co_id
        self.co_name = co_name
        self.co_country = co_country
        self.co_city = co_city
        self.co_street = co_street
        self.co_zip = co_zip
        self.co_tel = co_tel
        self.co_mail = co_mail
        self.co_krs = co_krs
        self.co_regon = co_regon
        self.co_nip = co_nip
        self.cg_name = cg_name
        cg.cg_companies.append(self.co_name)

    def update_co(self):
        self.co_name = input('Podaj nazwę firmy:')
        self.co_country = input('Podaj państwo:')
        self.co_city = input('Podaj miasto:')
        self.co_street = input('Podaj ulicę i numer:')
        self.co_zip = input('Podaj kod pocztowy:')
        self.co_tel = input('Podaj numer telefonu:')
        self.co_mail = input('Podaj adres e-mail:')
        self.co_krs = input('Podaj numer KRS:')
        self.co_regon = input('Podaj numer REGON:')
        self.co_nip = input('Podaj numer NIP: ')
        return

    def __str__(self):
        return f'║{str(self.co_id):^2.2}│ {self.co_name:^20.20} │ {self.co_country:^15.15} │ {self.co_city:^15.15} │ {self.co_street:^15.15} │{str(self.co_zip):^8.8}│ {str(self.co_tel):^15.15} │ {str(self.co_mail):^15.15} │ {str(self.co_krs):^10.10} │ {str(self.co_regon):^9.9} │ {str(self.co_nip):^10.10} │ {self.cg_name:^20.20} ║'


cg = CapitalGroup(False)
companies = []

def clear_companies():
    cg.is_cg = False
    cg.cg_name = None
    cg.cg_num = 0
    companies.clear()

# Funkcja testowa, do zastąpienia importem z *.csv
def import_companies():
    clear_companies()
    cg.cg_name = 'ABC Enterprise'
    cg.is_cg = True
    cg.cg_num = 5
    companies.append(Company(co_id=0, co_name='ABC Solutions', co_country='Polska', co_city='Darłowo', co_street='Morska 10', co_zip='76-150', co_tel='+48 789 456 123', co_mail='kontak@abc.pl', co_krs='1023456789', co_regon='987654321', co_nip='1234567890', cg_name=cg.cg_name))
    companies.append(Company(co_id=1, co_name='XYZ Company', co_country='USA', co_city='New York', co_street='11 Wall Street', co_zip='10005', co_tel='+48 789 456 123', co_mail='kontak@abc.pl', co_krs='1023456789', co_regon='987654321', co_nip='1234567890', cg_name=cg.cg_name))
    companies.append(Company(co_id=2, co_name='ABC Limited', co_country='Wielka Brytania', co_city='Londyn', co_street='10 Paternoster Sq', co_zip='EC4M 7LS', co_tel='+44 (0)207 797 1000', co_mail='kontak@abc.pl', co_krs='1023456789', co_regon='987654321', co_nip='1234567890', cg_name=cg.cg_name))
    companies.append(Company(co_id=3, co_name='Firma AAA', co_country='Polska', co_city='Gdańsk', co_street='Podwale Grodzkie 2', co_zip='80-886', co_tel='+48 789 456 123', co_mail='kontak@abc.pl', co_krs='1023456789', co_regon='987654321', co_nip='1234567890', cg_name=cg.cg_name))
    companies.append(Company(co_id=4, co_name='Firma BBB', co_country='Polska', co_city='Warszawa', co_street='Książęca 4', co_zip='00-498', co_tel='+48 22 537 75 82', co_mail='info@abc.pl', co_krs='1023456789', co_regon='987654321', co_nip='1234567890', cg_name=cg.cg_name))
