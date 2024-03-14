from case_1 import Library, UserList, BookCollection, Reservations, Loans, Reservation, Loan
import functools


def print_decorator(name='unknown'):
    def add_function(function):
        @functools.wraps(function)
        def decorator(*args, **kwargs):
            print()
            print(f'--------------------------')
            print(f'{name}:')
            return_values = function(*args, **kwargs)
            print(f'--------------------------')
            print()
            return return_values
        return decorator
    return add_function


class Driver:
    def __init__(self):
        self.library = Library()
        self.test_user_id = '1'
        self.test_isbn = '978-0-237-92646-5'

    def invoke_all_tests(self):
        self._test_library()
        self._test_user_collection()
        self._test_book_collection()
        self._test_reservation_collection()
        self._test_loan_collection()

    @print_decorator('Library')
    def _test_library(self):
        reservations_before = len(Reservations().search_reservations(isbn=self.test_isbn))
        self.library.make_reservation(user_id=self.test_user_id, isbn=self.test_isbn)
        reservations_after = len(Reservations().search_reservations(isbn=self.test_isbn))
        print(f'Make reservation: {reservations_before + 1 == reservations_after}')
        print()

        search_book_config = {'author': 'Kristin',
                              'title': 'difficult',
                              'isbn': self.test_isbn,
                              'year': '1605'}
        books = self.library.find_books(**search_book_config)
        print(f"Find books: {len(books) == 1}")
        print()

        search_user_config = {'user_id': 1,
                              'name': 'Kara',
                              'address': 'Stephanie'}
        search_user_config = {'user_id': 1}
        users = self.library.find_users(**search_user_config)
        print(f"Find users: {len(users) == 1}")
        print()

        print(f'Notifications:')
        notifications = self.library.get_notifications(user_id=1)
        for notification in notifications:
            print(notification)
        print()

        loans_before = len(Loans().search_loans(user_id=1, isbn=self.test_isbn))
        self.library.loan(user_id=1, isbn=self.test_isbn)
        loans_loan = len(Loans().search_loans(user_id=1, isbn=self.test_isbn))
        reservations_after_loan = len(Reservations().search_reservations(isbn=self.test_isbn))
        print(f'Reservation removed by loan: {reservations_after_loan == reservations_before}')
        print()


        print('Loan report')
        report = self.library.loan_report(user_id=1)
        print(report)
        print()

        self.library.return_book(user_id=1, isbn=self.test_isbn)
        loans_return = len(Loans().search_loans(user_id=1, isbn=self.test_isbn))

        print('Loan - return')
        print(loans_before + 1 == loans_loan)
        print(loans_loan - 1 == loans_return)
        print(loans_before == loans_return)

        # self.library.notify_loan_expiration()

    @print_decorator('Users')
    def _test_user_collection(self):
        user_list = UserList()

        users = user_list.search_users()
        users_ram = len(users)
        for user in users:
            pass
            # print(user)

        user_list.switch_mode('file')

        users = user_list.search_users()
        users_file = len(users)
        for user in users:
            pass
            # print(user)

        print(users_ram == users_file)

    @print_decorator('Books')
    def _test_book_collection(self):
        book_list = BookCollection()

        books = book_list.search_books()
        books_ram = len(books)
        for book in books:
            pass
            # print(book)

        book_list.switch_mode('file')

        books = book_list.search_books()
        books_file = len(books)
        for book in books:
            pass
            # print(book)

        print(books_ram == books_file)

    @print_decorator('Reservations')
    def _test_reservation_collection(self):
        reservation_list = Reservations()
        reservations_ram_start = len(reservation_list.search_reservations())

        reservation_list.add_reservation(Reservation(user_id=1, book_isbn='978-0-15-325882-4'))
        reservation_list.add_reservation(Reservation(user_id=1, book_isbn='978-0-15-325882-4'))
        reservations = reservation_list.search_reservations()
        for reservation in reservations:
            pass
            # print(reservation)
        reservations_ram_add = len(reservations)
        print()
        reservation_list.remove(reservations[0])
        reservations = reservation_list.search_reservations()
        for reservation in reservations:
            pass
            # print(reservation)
        reservations_ram_remove = len(reservations)
        print()

        reservation_list.switch_mode('file')

        reservations_file_start = len(reservation_list.search_reservations())

        reservation_list.add_reservation(Reservation(user_id=1, book_isbn='978-1-9851-4686-0'))
        reservation_list.add_reservation(Reservation(user_id=1, book_isbn='978-1-9851-4686-0'))
        reservations = reservation_list.search_reservations()
        for reservation in reservations:
            pass
            # print(reservation)
        reservations_file_add = len(reservations)
        print()

        reservation_list.remove(reservations[0])
        reservations = reservation_list.search_reservations()
        for reservation in reservations:
            pass
            # print(reservation)
        reservations_file_remove = len(reservations)
        print()

        print(reservations_ram_start + 2 == reservations_ram_add)
        print(reservations_ram_add - 1 == reservations_ram_remove)

        print(reservations_ram_remove == reservations_file_start)

        print(reservations_file_start + 2 == reservations_file_add)
        print(reservations_file_add - 1 == reservations_file_remove)

    @print_decorator('Loans')
    def _test_loan_collection(self):
        loan_list = Loans()
        loans_ram_start = len(loan_list.search_loans())

        loan_list.add_loan(Loan(user_id=1, isbn='978-0-15-325882-4'))
        loan_list.add_loan(Loan(user_id=1, isbn='978-0-15-325882-4'))
        loans = loan_list.search_loans()
        for loan in loans:
            pass
            # print(loan)
        loans_ram_add = len(loans)
        print()

        loan_list.remove(loans[0])
        loans = loan_list.search_loans()
        for loan in loans:
            pass
            # print(loan)
        loans_ram_remove = len(loans)
        print()

        loan_list.switch_mode('file')

        loans_file_start = len(loan_list.search_loans())
        loan_list.add_loan(Loan(user_id=1, isbn='978-1-9851-4686-0'))
        loan_list.add_loan(Loan(user_id=1, isbn='978-1-9851-4686-0'))
        loans = loan_list.search_loans()
        for loan in loans:
            pass
            # print(loan)
        loans_file_add = len(loans)
        print()

        loan_list.remove(loans[0])
        loans = loan_list.search_loans()
        for loan in loans:
            pass
            # print(loan)
        loans_file_remove = len(loans)
        print()

        print(loans_ram_start + 2 == loans_ram_add)
        print(loans_ram_add - 1 == loans_ram_remove)

        print(loans_ram_remove == loans_file_start)

        print(loans_file_start + 2 == loans_file_add)
        print(loans_file_add - 1 == loans_file_remove)

    def clean(self):
        pass
        # Reservations().remove(Reservation(user_id=self.test_user_id, book_isbn=self.test_isbn))
        # Loans().remove(Loan(user_id=self.test_user_id, isbn=self.test_isbn))


if __name__ == '__main__':
    driver = Driver()
    driver.invoke_all_tests()
    driver.clean()
