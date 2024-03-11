from datetime import date


class Bog:
    def __init__(self, title, forfatter, aarstal, ISBN):
        self.title=title
        self.forfatter=forfatter
        self.aarstal=aarstal
        self.ISBN=ISBN


class Bruger:
    def __init__(self,bruger_id, navn, adresse, laane_status=[]):
        self.bruger_id=bruger_id
        self.navn=navn
        self.adresse=adresse
        self.laane_status=laane_status



def log(funktion):
    def wrapper(*args, **kwargs):
        print()
        funktion(*args, **kwargs)
        print()
    return wrapper


class Bibliotek:
    def __init__(self) -> None:
        self.bogsamling=Bogsamling()
        self.brugere=BrugerListe()
        self.reservations = []

       # self.reservations.append({'bruger': id, 'book': bog})
    def make_reservation(user, isbn):

        self.reservations.append(Reservation(user, book))

    @log
    def laan():
        pass

    def returner():
        pass

    def notify_reservation():
        pass

    def notify_loan_expiration():
        pass




       


class Bogsamling:
    pass

    def read_book_list():
        with open() as books:
             for book in books:
                yield book


    def search_books(isbn):
        for book in self.read_book_list():
            if isbn == book.ISBN:
                return book
            
        # SELECT * FROM Books WHERE ISBN equal id



class BrugerListe:
    pass

    def read_bruger_list():
        with open() as brugere:
             for bruger in brugere:
                yield bruger

    def search_bruger(bruger_id):
        for bruger in self.read_bruger_list():
            if bruger_id == bruger.bruger_id:
                return bruger

class Udlaan:
    def __init__(self, bruger, book, expiration_date) -> None:
        self.bruger = bruger
        self.book = book
        self.dato = date.date()
        self.expiration_date = expiration_date


class Reservation:
    def __init__(self, bruger, book) -> None:
        self.bruger = bruger
        self.book = book
        self.dato = date.date()
        

