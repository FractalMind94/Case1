import functools
import os
import time
from datetime import date


def singleton(cls):
    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        if not wrapper.instance:
            wrapper.instance = cls(*args, **kwargs)
        return wrapper.instance
    wrapper.instance = None
    return wrapper


class Book:
    def __init__(self, title, author, year, ISBN, stock):
        self.title = title
        self.author = author
        self.year = year
        self.ISBN = ISBN
        self.stock = stock

    def __str__(self):
        return f'Title: {self.title}, author: {self.author}, year: {self.year}, ISBN: {self.ISBN}'


class User:
    def __init__(self, user_id, name, address, loan_status=[]):
        self.user_id = user_id
        self.name = name
        self.address = address
        self.loan_status = loan_status

    def add_loans(self, loans):
        if type(loans) is list:
            self.loan_status.extend(loans)
        else:
            self.loan_status.append(loans)
        return True

    def get_notifications(self):
        notifications = list()
        reservations = Reservations().search_reservations(user_id=self.user_id)

        for reservation in reservations:
            if reservation.notified:
                notifications.append(reservation)

        return notifications


def log_decorator(function):
    log_path = r"./log.txt"

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        with open(log_path, mode='a') as logger:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)

            logger.write(f'{function.__name__}({signature})')
            try:
                value = function(*args, **kwargs)
                logger.write(f' returned {repr(value)}\n')
            except Exception as e:
                logger.write(f' \tERROR: {e}\n')
                raise e

            return value

    return wrapper


class Library:
    def __init__(self) -> None:
        self.books = BookCollection(mode='ram')
        self.users = UserList(mode='ram')
        self.reservations = Reservations(mode='ram')
        self.loans = Loans(mode='ram')

    def make_reservation(self, user_id, isbn):
        # user = self.users.search_users(user_id=user_id)
        # book = self.books.search_books(isbn=isbn)
        # self.reservations.append(Reservation(user, book))
        self.reservations.add_reservation(Reservation(user_id=user_id, book_isbn=isbn))

    def loan_report(self, user_id):
        user = self.users.search_users(user_id=user_id)
        print(f'name: {user.name}')
        print(f'id: {user.user_id}')
        print(f'loans: ')
        for book in user.loan_status:
            print(f'\t {book}')

    @log_decorator
    def loan(self, user_id, isbn):
        user = self.users.search_users(user_id=user_id)
        book = self.books.search_books(isbn=isbn)

        available_copies = book.stock

        for _ in self.loans.search_loans(isbn=isbn):
            available_copies -= 1

        for reservation in self.reservations.search_reservations(isbn=isbn):
            if user.user_id == reservation.user_id:
                self.reservations.remove(reservation)
                break
            else:
                available_copies -= 1

        if available_copies > 0:
            loan = Loan(user, book)
            self.loans.add_loan(loan)
            user.loan_status.append(loan)

        return None

    @log_decorator
    def return_book(self, user_id, isbn):
        user = self.users.search_users(user_id=user_id)
        book = self.books.search_books(isbn=isbn)

        for loan in self.loans.search_loans(isbn=isbn, user_id=user_id):
            self.loans.remove(loan)

        for loan in user.loan_status:
            if book.ISBN == loan.isbn:
                user.loan_status.remove(loan)

        self.notify_reservation(book)

    def notify_reservation(self, book):
        for reservation in self.reservations.search_reservations(isbn=book.ISBN):
            notified = reservation.notify(book)
            if notified:
                return True

        return False

    def notify_loan_expiration(self):
        # TODO call this from somewhere
        for loan in self.loans.search_loans():
            loan.notify_expiration()

    def get_notifications(self, user_id):
        # TODO call this from somewhere
        user = self.users.search_users(user_id=user_id)
        return user.get_notifications()

    def find_users(self, user_id):
        user = self.users.search_users(user_id=user_id)
        return user

    # def find_books(self, isbn=None, title=None, author=None, year=None):
    def find_books(self, **kwargs):
        books = self.books.search_books(**kwargs)
        return books

    def find_loans(self, **kwargs):
        loans = self.loans.search_loans(**kwargs)
        return loans

    #TODO search stock in books file
    def find_in_stock(self, **kwargs):
        #in_stock = self.in_stock.search_books(stock)
        #return in_stock
        pass


@singleton
class Loans:
    _loan_path = r"./data/loans.txt"
    _loans = list()
    _mode = 'file'

    def __init__(self, mode='file'):
        self._mode = mode
        if mode == 'ram':
            self._loans = [self.read_loans()]

    def switch_mode(self, mode):
        if self._mode == 'file' and mode == 'ram':
            self._loans = [self.read_loans()]
            self._mode = mode
            return True
        elif self._mode == 'ram' and mode == 'file':
            with open(f'{self._loan_path}.new', "w") as loans:
                # TODO look at this, I believe it should work, but IDE is warning
                for loan in self._loans:
                    loans.write(f'{loan.user_id}:'
                                f'{loan.isbn}:'
                                f'{loan.date}:'
                                f'{loan.expiration_date}:'
                                f'{loan.notified_expiration}\n')

            os.remove(self._loan_path)
            # TODO only rename not remove??
            os.rename(f'{self._loan_path}.new', f'{self._loan_path}')
            os.remove(f'{self._loan_path}.new')
            self._mode = mode
            self._loans = list()
            return True
        else:
            return False

    def read_loans(self):
        with open(self._loan_path, "r") as loans:
            for loan in loans:
                loan_object = Loan(*loan.strip().split(':'))
                yield loan_object

    def add_loan(self, loan):
        if self._loans:
            self._add_list(loan)
        else:
            self._add_file(loan)

    def _add_file(self, loan):
        with open(f'{self._loan_path}', 'a') as loans:
            loans.write(f'{loan.user_id}:'
                        f'{loan.isbn}:'
                        f'{loan.date}:'
                        f'{loan.expiration_date}:'
                        f'{loan.notified_expiration}\n')

    def _add_list(self, loan):
        self._loans.append(loan)

    def search_loans(self, user_id=None, isbn=None):
        loans = self._loans
        if not loans:
            loans = self.read_loans()

        if isbn:
            loans = filter(lambda loan: isbn == loan.isbn, loans)
        if user_id:
            loans = filter(lambda loan: user_id == loan.user_id, loans)

        loans = [loans]

        if len(loans) == 1:
            return loans[0]

        return loans

    def remove(self, loan):
        if self._loans:
            self._remove_list(loan)
        else:
            self._remove_file(loan)

    def _remove_list(self, loan):
        self._loans.remove(loan)

    def _remove_file(self, loan):
        file_loans = self.read_loans()
        removed = False

        with open(f'{self._loan_path}.new', "w") as new_loans:
            for file_loan in file_loans:
                if not removed and file_loan.user_id == loan.user_id and file_loan.isbn == loan.isbn:
                    removed = True
                    continue
                else:
                    new_loans.write(f'{file_loan.user_id}:'
                                    f'{file_loan.isbn}:'
                                    f'{file_loan.date}:'
                                    f'{file_loan.expiration_date}:'
                                    f'{file_loan.notified_expiration}\n')

        os.remove(self._loan_path)
        os.rename(f'{self._loan_path}.new', f'{self._loan_path}')
        os.remove(f'{self._loan_path}.new')


@singleton
class Reservations:
    _reservations_path = r"./data/reservations.txt"
    _reservations = list()
    _mode = 'file'

    def __init__(self, mode='file'):
        self._mode = mode
        if mode == 'ram':
            self._reservations = [self.read_reservations()]

    def switch_mode(self, mode):
        if self._mode == 'file' and mode == 'ram':
            self._reservations = [self.read_reservations()]
            self._mode = mode
            return True
        elif self._mode == 'ram' and mode == 'file':
            with open(f'{self._reservations_path}.new', "w") as reservations:
                # TODO look at this, I believe it should work, but IDE is warning
                for reservation in self._reservations:
                    reservations.write(f'{reservation.user_id}:'
                                       f'{reservation.isbn}:'
                                       f'{reservation.date}:'
                                       f'{reservation.notified}\n')

            os.remove(self._reservations_path)
            os.rename(f'{self._reservations_path}.new', f'{self._reservations_path}')
            os.remove(f'{self._reservations_path}.new')
            self._mode = mode
            self._reservations = list()
            return True
        else:
            return False

    def read_reservations(self):
        with open(self._reservations_path, "r") as reservations:
            for reservation in reservations:
                reservation_object = Reservation(*reservation.strip().split(':'))
                yield reservation_object

    def add_reservation(self, reservation):
        if self._reservations:
            self._add_list(reservation)
        else:
            self._add_file(reservation)

    def _add_file(self, reservation):
        with open(f'{self._reservations_path}', 'a') as reservations:
            reservations.write(f'{reservation.user_id}:'
                               f'{reservation.isbn}:'
                               f'{reservation.date}:'
                               f'{reservation.notified}\n')

    def _add_list(self, reservation):
        self._reservations.append(reservation)

    def search_reservations(self, user_id=None, isbn=None):
        reservations = self._reservations
        if not reservations:
            reservations = self.read_reservations()

        if isbn:
            reservations = filter(lambda reservation: isbn == reservation.isbn, reservations)
        if user_id:
            reservations = filter(lambda reservation: user_id == reservation.user_id, reservations)

        reservations = [reservations]

        if len(reservations) == 1:
            return reservations[0]

        return reservations

    def remove(self, reservation):
        if self._reservations:
            self._remove_list(reservation)
        else:
            self._remove_file(reservation)

    def _remove_list(self, reservation):
        self._reservations.remove(reservation)

    def _remove_file(self, reservation):
        file_reservations = self.read_reservations()
        removed = False

        with open(f'{self._reservations_path}.new', "w") as new_reservations:
            for file_reservation in file_reservations:
                if not removed and file_reservation.user_id == reservation.user_id and file_reservation.isbn == reservation.isbn:
                    removed = True
                    continue
                else:
                    new_reservations.write(f'{file_reservation.user_id}:'
                                           f'{file_reservation.isbn}:'
                                           f'{file_reservation.date}:'
                                           f'{file_reservation.notified}\n')

        os.remove(self._reservations_path)
        os.rename(f'{self._reservations_path}.new', f'{self._reservations_path}')
        os.remove(f'{self._reservations_path}.new')


@singleton
class BookCollection:
    _book_path = r"./data/books.txt"
    _books = dict()
    _mode = 'file'

    def __init__(self, mode='file'):
        self._mode = mode
        if mode == 'ram':
            books = self.read_book_list()

            for book in books:
                self._books[book.ISBN] = book

    def switch_mode(self, mode):
        if self._mode == 'file' and mode == 'ram':
            self._books = [self.read_book_list()]
            self._mode = mode
            return True
        elif self._mode == 'ram' and mode == 'file':
            with open(f'{self._book_path}.new', "w") as books:
                for isbn, book in self._books:
                    books.write(f'{book.title}:'
                                f'{book.author}:'
                                f'{book.year}:'
                                f'{book.ISBN}:'
                                f'{book.stock}\n')

            os.remove(self._book_path)
            os.rename(f'{self._book_path}.new', f'{self._book_path}')
            os.remove(f'{self._book_path}.new')
            self._mode = mode
            self._books = dict()
            return True
        else:
            return False

    def read_book_list(self):
        with open(self._book_path, "r") as books:
            for book in books:
                book_object = Book(*book.strip().split(':'))
                yield book_object

    def search_books(self, isbn=None, title=None, author=None, year=None):
        # SQL would look like
        # SELECT * FROM Books WHERE ISBN equal id
        if self._mode == 'file' or not self._books:
            books = self._search_file(isbn, title, author, year)
        elif self._mode == 'list' and self._books:
            books = self._search_dict(isbn, title, author, year)
        else:
            return None

        if len(books) == 1:
            return books[0]

        return books

    def _search_dict(self, isbn=None, title=None, author=None, year=None):
        if isbn:
            try:
                book = self._books[isbn]
                return book
            except KeyError:
                pass

        books = self._apply_filters(self._books.values(), isbn, title, author, year)

        return [books]

    def _search_file(self, isbn=None, title=None, author=None, year=None):
        books = self.read_book_list()
        books = self._apply_filters(books, isbn, title, author, year)

        return [books]

    def _apply_filters(self, books, isbn=None, title=None, author=None, year=None):
        if isbn:
            books = filter(lambda book: isbn == book.ISBN, books)

        if year:
            books = filter(lambda book: year == book.year, books)

        if title:
            books = filter(lambda book: title in book.title, books)
        if author:
            books = filter(lambda book: author in book.author, books)
        return books


@singleton
class UserList:
    _user_path = r"./data/users.txt"
    _users = dict()
    _mode = 'file'

    def __init__(self, mode='file'):
        self._mode = mode
        if mode == 'ram':
            users = self.read_user_list()
            users = self._add_loans(users)

            for user in users:
                self._users[user.user_id] = user

    def switch_mode(self, mode):
        if self._mode == 'file' and mode == 'ram':
            users = self.read_user_list()
            users = self._add_loans(users)
            self._users = [users]
            self._mode = mode
            return True
        elif self._mode == 'ram' and mode == 'file':
            with open(f'{self._user_path}.new', "w") as users:
                for user_id, user in self._users:
                    users.write(f'{user.user_id}:'
                                f'{user.name}:'
                                f'{user.address}\n')

            os.remove(self._user_path)
            os.rename(f'{self._user_path}.new', f'{self._user_path}')
            os.remove(f'{self._user_path}.new')
            self._mode = mode
            self._users = dict()
            return True
        else:
            return False

    def read_user_list(self):
        with open(self._user_path, "r") as users:
            for user in users:
                user_object = User(*user.strip().split(':'))
                yield user_object

    def search_users(self, user_id=None, name=None, address=None):
        if self._mode == 'file' or not self._users:
            return self._search_file(user_id, name, address)
        elif self._mode == 'list' and self._users:
            return self._search_list()
        else:
            return None

    def _search_list(self, user_id=None, name=None, address=None):
        if user_id:
            try:
                user = self._users[user_id]
                return user
            except KeyError:
                pass

        users = (self._users.values())
        users = self._apply_filters(users, user_id, name, address)

        users = [users]

        if len(users) == 1:
            return users[0]

        return users

    def _search_file(self, user_id=None, name=None, address=None):
        users = self.read_user_list()
        users = self._apply_filters(users, user_id, name, address)
        users = self._add_loans(users)

        users = [users]

        if len(users) == 1:
            return users[0]

        return users

    def _apply_filters(self, users, user_id=None, name=None, address=None):
        if user_id:
            users = filter(lambda user: user_id == user.user_id, users)
        if name:
            users = filter(lambda user: name in user.name, users)
        if address:
            users = filter(lambda user: address in user.address, users)
        return users

    def _add_loans(self, users):
        return (user for user in users if user.add_loans(Loans().search_loans(user_id=user.user_id)))


class Loan:
    def __init__(self, user_id, isbn, loan_date=None, expiration_date=None, notified_expiration=False) -> None:
        self.user_id = user_id
        self.isbn = isbn

        if not loan_date:
            loan_date = date.today()
        self.date = loan_date

        if not expiration_date:
            expiration_date = date.fromtimestamp(time.time() + 2 * 7 * 24 * 60 * 60)
        self.expiration_date = expiration_date

        self.notified_expiration = notified_expiration

    def notify_expiration(self):
        # TODO send notification if date is close
        if not self.notified_expiration:
            user = UserList().search_users(user_id=self.user_id)
            # TODO send notification
            self.notified_expiration = True
            return True
        else:
            return False


class Reservation:
    def __init__(self, user_id, book_isbn, reservation_date=None, notified=False) -> None:
        self.user_id = user_id
        self.isbn = book_isbn

        if not reservation_date:
            reservation_date = date.today()
        self.date = reservation_date

        self.notified = notified

    def notify(self, book):
        if not self.notified and self.isbn == book.ISBN:
            user = UserList().search_users(user_id=self.user_id)
            self.notified = True
            # TODO send notification
            return True
        else:
            return False

# TODO make menu
class Menu:

    def __init__(self):
        self.library = Library()
        # self.submenu1 =

    def choose_book(self, books): #From search_book
        #TODO choose book from list of the search and pass into book of choice
        #books=[book for book in books]
        #print(books)
        pass
    def book_of_choice(self): #from choose_book
        while True:
            print("1. Loan the book")
            print("2. Make a reservation")
            print("3. Exit")
            loan=input()
            if loan == 1:
                loans = self.library.find_loans()
                in_stock = self.library.find_in_stock() #TODO
                if loans != in_stock: #something with stock
                    self.library.loan()
                if loans == in_stock:
                    while True:
                        print("Book is not in stock")
                        print("Choose from one of three options instead: ")
                        print("1. Make a reservation")
                        print("2. Search another book")
                        print("3. Exit")
                        reserve = input()
                        if reserve == 1:
                            self.library.make_reservation(#TODO something in here)
                        if reserve == 2:
                            self.search_book()
                        if reserve == 3:
                            break
                        else:
                            print("Invalid Number - Try Again: ")
                            continue
            if loan == 2:
                self.library.make_reservation()

            if loan == 3:
                break
            else:
                print("Invalid Number - Try Again: ")
                continue


    def search_book(self): # from menu_user
        kwargs = {'isbn': 1111, 'author': 'bob'}
        book = ""
        while True:
            book=input("Enter Author or ISBN: ")
            #TODO something with invalid values
            while book:
                books = self.library.find_books(#something)
                if not books:
                    print("No Book Found Matching Criteria - Try Again: ")
                    continue
                if books:
                    self.choose_book(books)



    def menu_user(self):

        user_id=""

        while True:
            user_id=input("Enter User ID: ")

            if user_id is int:
                user_id = int(user_id)
                print('invalid id format')
                continue

            user = self.library.find_users(user_id=user_id)


            if not user:
                print("Invalid User ID - Try Again: ")
                continue


            while user:
                print("---Library Menu---")
                print("1. Look-Up book")
                print("2. Return a book")
                print("3. View loan report")
                print("4. Exit")

                choice = input()
                if choice == 1:
                    self.search_book()
                elif choice == 2:
                    self.library.return_book()
                elif choice == 3:
                    self.library.loan_report(user_id=user_id)
                elif choice == 4:
                    break
                else:
                    print("Invalid Number - Try Again:")
                    continue





