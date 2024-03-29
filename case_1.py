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
    def __init__(self, author, title, year, isbn, stock):
        self.title = title
        self.author = author
        self.year = str(year)
        self.isbn = isbn
        self.stock = int(stock)

    def __str__(self):
        return f'Title: {self.title}, author: {self.author}, year: {self.year}, ISBN: {self.isbn}'


class User:
    def __init__(self, user_id, name, address, loan_status=[]):
        self.user_id = str(user_id)
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
        self.loans = Loans(mode='ram')
        self.reservations = Reservations(mode='ram')
        self.books = BookCollection(mode='ram')

        self.users = UserList(mode='ram')

    def shutdown(self):
        self.loans.switch_mode('file')
        self.reservations.switch_mode('file')
        self.books.switch_mode('file')
        self.users.switch_mode('file')

    def make_reservation(self, user_id, isbn):
        user_id = str(user_id)
        self.reservations.add_reservation(Reservation(user_id=user_id, book_isbn=isbn))

    def loan_report(self, user_id):
        user_id = str(user_id)
        user = self.users.search_users(user_id=user_id)[0]
        report = f'name: {user.name}, id: {user.user_id}\n'
        report += f'loans: \n'
        for loan in user.loan_status:
            report += f'\t Expiration: {loan.expiration_date}, ISBN: {loan.isbn}\n'

        return report

    @log_decorator
    def loan(self, user_id, isbn):
        user_id = str(user_id)
        user = self.users.search_users(user_id=user_id)[0]
        book = self.books.search_books(isbn=isbn)[0]

        available_copies = book.stock

        for _ in self.loans.search_loans(isbn=isbn):
            available_copies -= 1

        if available_copies > 0:
            for reservation in self.reservations.search_reservations(isbn=isbn):
                if user_id == reservation.user_id:
                    self.reservations.remove(reservation)
                    break
                else:
                    available_copies -= 1

        if available_copies > 0:
            loan = Loan(user_id, isbn)
            self.loans.add_loan(loan)
            user.loan_status.append(loan)
            return True
        else:
            return False


    @log_decorator
    def return_book(self, user_id, isbn):
        user_id = str(user_id)
        user = self.users.search_users(user_id=user_id)[0]
        book = self.books.search_books(isbn=isbn)[0]

        for loan in self.loans.search_loans(isbn=isbn, user_id=user_id):
            self.loans.remove(loan)

        for loan in user.loan_status:
            if book.isbn == loan.isbn:
                user.loan_status.remove(loan)

        self._notify_reservation(book)

        return True

    def _notify_reservation(self, book):
        for reservation in self.reservations.search_reservations(isbn=book.isbn):
            notified = reservation.notify(book)
            if notified:
                return True

        return False

    def notify_loan_expiration(self):
        # TODO call this from somewhere
        for loan in self.loans.search_loans():
            loan.notify_expiration()

    def get_notifications(self, user_id):
        user_id = str(user_id)
        # TODO call this from somewhere
        user = self.users.search_users(user_id=user_id)[0]
        return user.get_notifications()

    def find_users(self, user_id):
        user_id = str(user_id)
        user = self.users.search_users(user_id=user_id)
        return user

    # def find_books(self, isbn=None, title=None, author=None, year=None):
    def find_books(self, **kwargs):
        books = self.books.search_books(**kwargs)
        return books

    def find_loans(self, **kwargs):
        loans = self.loans.search_loans(**kwargs)
        return loans


@singleton
class Loans:
    _loan_path = r"./data/loans.txt"
    _loans = list()

    def __init__(self, mode='file'):
        self._mode = mode
        if mode == 'ram':
            self._loans = [loan for loan in self._read_loans()]

    def switch_mode(self, mode):
        if self._mode == 'file' and mode == 'ram':
            self._loans = [loan for loan in self._read_loans()]
            self._mode = mode
            return True
        elif self._mode == 'ram' and mode == 'file':
            with open(f'{self._loan_path}.new', "w") as loans:
                for loan in self._loans:
                    loans.write(f'{loan.user_id}:'
                                f'{loan.isbn}:'
                                f'{loan.date}:'
                                f'{loan.expiration_date}:'
                                f'{loan.notified_expiration}\n')

            os.remove(self._loan_path)
            os.rename(f'{self._loan_path}.new', f'{self._loan_path}')
            self._mode = mode
            self._loans = list()
            return True
        else:
            return False

    def _read_loans(self):
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

    def search_loans(self, user_id='', isbn=None):
        user_id = str(user_id)

        loans = self._loans
        if not loans:
            loans = self._read_loans()

        if isbn:
            loans = filter(lambda loan: isbn == loan.isbn, loans)
        if user_id:
            loans = filter(lambda loan: user_id == loan.user_id, loans)

        loans = [loan for loan in loans]

        # if len(loans) == 1:
        #     return loans[0]

        return loans

    def remove(self, loan):
        if self._loans:
            self._remove_list(loan)
        else:
            self._remove_file(loan)

    def _remove_list(self, loan):
        self._loans.remove(loan)

    def _remove_file(self, loan):
        file_loans = self._read_loans()
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


@singleton
class Reservations:
    _reservations_path = r"./data/reservations.txt"
    _reservations = list()

    def __init__(self, mode='file'):
        self._mode = mode
        if mode == 'ram':
            self._reservations = [reservation for reservation in self._read_reservations()]

    def switch_mode(self, mode):
        if self._mode == 'file' and mode == 'ram':
            self._reservations = [reservation for reservation in self._read_reservations()]
            self._mode = mode
            return True
        elif self._mode == 'ram' and mode == 'file':
            with open(f'{self._reservations_path}.new', "w") as reservations:
                for reservation in self._reservations:
                    reservations.write(f'{reservation.user_id}:'
                                       f'{reservation.isbn}:'
                                       f'{reservation.date}:'
                                       f'{reservation.notified}\n')

            os.remove(self._reservations_path)
            os.rename(f'{self._reservations_path}.new', f'{self._reservations_path}')
            self._mode = mode
            self._reservations = list()
            return True
        else:
            return False

    def _read_reservations(self):
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

    def search_reservations(self, user_id='', isbn=None):
        user_id = str(user_id)

        reservations = self._reservations
        if not reservations:
            reservations = self._read_reservations()

        if isbn:
            reservations = filter(lambda reservation: isbn == reservation.isbn, reservations)
        if user_id:
            reservations = filter(lambda reservation: user_id == reservation.user_id, reservations)

        reservations = [reservation for reservation in reservations]

        # if len(reservations) == 1:
        #     return reservations[0]

        return reservations

    def remove(self, reservation):
        if self._reservations:
            self._remove_list(reservation)
        else:
            self._remove_file(reservation)

    def _remove_list(self, reservation):
        self._reservations.remove(reservation)

    def _remove_file(self, reservation):
        file_reservations = self._read_reservations()
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


@singleton
class BookCollection:
    _book_path = r"./data/books.txt"
    _books = dict()

    def __init__(self, mode='file'):
        self._mode = mode
        if mode == 'ram':
            books = self._read_book_list()

            for book in books:
                self._books[book.isbn] = book

    def switch_mode(self, mode):
        if self._mode == 'file' and mode == 'ram':
            self._books = [reservation for reservation in self._read_book_list()]
            self._mode = mode
            return True
        elif self._mode == 'ram' and mode == 'file':
            with open(f'{self._book_path}.new', "w") as books:
                for isbn, book in self._books.items():
                    books.write(f'{book.author}:'
                                f'{book.title}:'
                                f'{book.year}:'
                                f'{book.isbn}:'
                                f'{book.stock}\n')

            os.remove(self._book_path)
            os.rename(f'{self._book_path}.new', f'{self._book_path}')
            self._mode = mode
            self._books = dict()
            return True
        else:
            return False

    def _read_book_list(self):
        with open(self._book_path, "r") as books:
            for book in books:
                book_object = Book(*book.strip().split(':'))
                yield book_object

    def search_books(self, isbn=None, title=None, author=None, year=''):
        year= str(year)

        # SQL would look like
        # SELECT * FROM Books WHERE ISBN equal id
        if self._mode == 'file' or not self._books:
            books = self._search_file(isbn, title, author, year)
        elif self._mode == 'ram' and self._books:
            books = self._search_dict(isbn, title, author, year)
        else:
            return None

        # if len(books) == 1:
        #     return books[0]

        return books

    def _search_dict(self, isbn=None, title=None, author=None, year=None):
        if isbn:
            try:
                book = self._books[isbn]

                return [book]
            except KeyError:
                pass

        books = self._apply_filters(self._books.values(), isbn, title, author, year)

        # for key, book in self._books.items():
        #     print(author)
        #     print(book.author)
        #     print(author in book.author)

        return [book for book in books]

    def _search_file(self, isbn=None, title=None, author=None, year=None):
        books = self._read_book_list()
        books = self._apply_filters(books, isbn, title, author, year)

        return [book for book in books]

    def _apply_filters(self, books, isbn=None, title=None, author=None, year=None):
        if isbn:
            books = filter(lambda book: isbn == book.isbn, books)

        if year:
            books = filter(lambda book: year == book.year, books)

        if title:
            books = filter(lambda book: title in book.title, books)
        if author:
            books = filter(lambda book: author in book.author, books)
        return books


@singleton
class UserList():
    _user_path = r"data/users.txt"
    _users = dict()

    def __init__(self, mode='file'):
        self._mode = mode
        if mode == 'ram':
            users = self._read_user_list()
            users = self._add_loans(users)

            for user in users:
                self._users[user.user_id] = user

    def switch_mode(self, mode):
        if self._mode == 'file' and mode == 'ram':
            users = self._read_user_list()
            users = self._add_loans(users)
            self._users = [reservation for reservation in users]
            self._mode = mode
            return True
        elif self._mode == 'ram' and mode == 'file':
            new_filename = f'{self._user_path}.new'
            with open(new_filename, "w") as users:
                for user_id, user in self._users.items():
                    users.write(f'{user.user_id}:'
                                f'{user.name}:'
                                f'{user.address}\n')

            os.remove(self._user_path)
            os.rename(f'{self._user_path}.new', f'{self._user_path}')
            self._mode = mode
            self._users = dict()
            return True
        else:
            return False

    def _read_user_list(self):
        with open(self._user_path, "r") as users:
            for user in users:
                user_object = User(*user.strip().split(':'))
                yield user_object

    def search_users(self, user_id='', name=None, address=None):
        user_id = str(user_id)

        if self._mode == 'file' or not self._users:
            return self._search_file(user_id, name, address)
        elif self._mode == 'ram' and self._users:
            return self._search_list(user_id, name, address)
        else:
            return None

    def _search_list(self, user_id=None, name=None, address=None):
        if user_id:
            try:
                user = self._users[user_id]
                return [user]
            except KeyError:
                pass

        users = (self._users.values())
        users = self._apply_filters(users, user_id, name, address)

        users = [reservation for reservation in users]

        return users

    def _search_file(self, user_id=None, name=None, address=None):
        users = self._read_user_list()
        users = self._apply_filters(users, user_id, name, address)
        users = self._add_loans(users)

        users = [reservation for reservation in users]

        # if len(users) == 1:
        #     return users[0]

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
        self.user_id = str(user_id)
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
        self.user_id = str(user_id)
        self.isbn = book_isbn

        if not reservation_date:
            reservation_date = date.today()
        self.date = reservation_date

        if type(notified) is str:
            if notified.lower() == 'false':
                notified = False
            elif notified.lower() == 'true':
                notified = True

        self.notified = bool(notified)

    def notify(self, book):
        if not self.notified and self.isbn == book.isbn:
            user = UserList().search_users(user_id=self.user_id)
            self.notified = True
            print(f'Notify reservation. User_id: {self.user_id}, ISBN: {self.isbn}')
            # TODO send notification
            return True
        else:
            return False

    def __str__(self):
        return f'user_id: {self.user_id}, isbn: {self.isbn}, date: {self.date}, Notified: {self.notified}'


class Menu:

    def __init__(self):
        self.library = Library()
        # self.submenu1 =

    def choose_book(self, books, user_id): #From search_book
        for count, book in enumerate(books):
            print(f'{count}: \t {book}')

        while True:
            print("Any integer. Choose one of the books")
            print("exit. exit the menu")
            choice = input("choose choice").strip()

            if choice == "exit":
                break
            else:
                try:
                    book = books[int(choice)]
                    self.book_of_choice(book, user_id)
                    break
                except Exception as e:
                    print('invalid input')

    def book_of_choice(self, book, user_id): #from choose_book
        while True:
            print("1. Loan the book")
            print("2. Make a reservation")
            print("3. Exit")
            choice = input()
            if choice == '1':
                success = self.library.loan(user_id=user_id, isbn=book.isbn)

                if success:
                    print('success')
                    break
                else:
                    print('book not available')
            elif choice == '2':
                self.library.make_reservation(user_id=user_id, isbn=book.isbn)
                break
            elif choice == '3':
                break
            else:
                print("Invalid Number - Try Again: ")
                continue


    def search_book(self, user_id): # from menu_user
        isbn = ''
        author = ''
        title = ''
        year = ''

        while True:
            print("---Search Menu---")
            print(f"1. Search by ISBN: {isbn}")
            print(f"2. Search by Author: {author}")
            print(f"3. Search by Title: {title}")
            print(f"4. Search by Year: {year}")
            print(f"5. Perform Search")
            print(f"6. Exit")

            choice = input("Select option:").strip()
            kwargs = {'isbn': isbn, 'author': author, 'title': title, 'year': year}

            if choice == '1':
                isbn = input('Write ISBN:').strip()
            elif choice == '2':
                author = input('Write author:').strip()
            elif choice == '3':
                title=input("Write Title of Book: ").strip()
            elif choice == '4':
                year=input("Write year of book: ").strip()
            elif choice == '5':
                books = self.library.find_books(**kwargs)
                if len(books) > 1:
                    self.choose_book(books, user_id)
                elif len(books) == 1:
                    self.book_of_choice(books[0], user_id)
                else:
                    print("No Book Found Matching Criteria - Try Again: ")
            elif choice == '6':
                break


    def menu_user(self):
        while True:
            user_id = input("Enter User ID: ").strip()

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
                if choice == '1':
                    self.search_book(user_id=user_id)
                elif choice == '2':
                    report = self.library.loan_report(user_id=user_id)
                    print(report)
                    isbn = input('Enter ISBN:')
                    self.library.return_book(user_id=user_id, isbn=isbn)
                elif choice == '3':
                    report = self.library.loan_report(user_id=user_id)
                    print(report)
                elif choice == '4':
                    break
                else:
                    print("Invalid Number - Try Again:")
                    continue


if __name__ == '__main__':
    menu = Menu()
    menu.menu_user()
