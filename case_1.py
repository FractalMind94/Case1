from datetime import date


class Book:
    def __init__(self, title, author, year, isbn):
        self.title = title
        self.author = author
        self.year = year
        self.isbn = isbn


class User:
    def __init__(self, user_id, name, address, loan_status=[]):
        self.user_id = user_id
        self.name = name
        self.address = address
        self.loan_status = loan_status


def log(function):
    def wrapper(*args, **kwargs):
        print()
        function(*args, **kwargs)
        pass
        print()
    return wrapper


class Library:
    def __init__(self) -> None:
        self.books = BookCollection()
        self.users = UserList()
        self.reservations = []
        self.loans = []

        # self.reservations.append({'bruger': id, 'book': bog})
    def make_reservation(self, user, isbn):

        self.reservations.append(Reservation(user, isbn))

    def loan_report(self, user):
        pass

    @log
    def loan(self, user_id, isbn):
        user = self.users.search_users(user_id)
        book = self.books.search_books(isbn)

        # TODO Implement for multiple books of the same type
        for re in self.loans:
            if book.isbn == re.book.isbn:
                False

        for re in self.reservations:
            if book.isbn == re.book.isbn:
                if user.user_id == re.user.user_id:
                    # remove from reservations
                    break
                else:
                    return
        # TODO add two weeks to date
        self.loans.append(Loan(user, book, date.date()))

        # make Loan
        # add loan to Library
        # add loan to user
        pass

    def return_book(self):
        pass

    def notify_reservation(self):
        pass

    def notify_loan_expiration(self):
        pass


class BookCollection:
    book_path = r"C:/Users/KOM/Desktop/Opgaver/Case1\books.txt"

    def read_book_list(self):
        with open(self.book_path, "r") as books:
            for book in books:
                book_object = Book(*book.strip().split(':'))
                yield book_object

    def search_books(self, isbn):
        for book in self.read_book_list():
            if isbn == book.isbn:
                return book
            
        # SELECT * FROM Books WHERE ISBN equal id


class UserList:
    pass
    user_path = r"C:/Users/KOM/Desktop/Opgaver/Case1\\users.txt"

    def read_user_list(self):
        with open(self.user_path, "r") as users:
            for user in users:
                user_object = User(*user.strip().split(':'))
                yield user_object

    def search_users(self, user_id):
        for user in self.read_user_list():
            if user_id == user.user_id:
                return user


class Loan:
    def __init__(self, user, book, expiration_date) -> None:
        self.user = user
        self.book = book
        self.date = date.date()
        self.expiration_date = expiration_date


class Reservation:
    def __init__(self, user, book) -> None:
        self.user = user
        self.book = book
        self.dat = date.date()
        

class Menu:
    pass
