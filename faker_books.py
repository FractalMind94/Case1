from faker import Faker 
# import random


def generate_books(books):
    with open(r"data/books.txt", "w") as output:  # definér hvilken sti den skal bruge
        output.write(f'author:title:year:ISBN:stock\n')  # gemmer i ny linje efter hver gennemgang

        # books_list = []
        faker = Faker()
        isbns = set()
        for i in range(1, books):
            ISBN = False
            while ISBN in isbns:
                ISBN = faker.isbn13()
            isbns.add(ISBN)

            author = faker.name()
            title = faker.sentence()
            year = faker.random_int(min=1, max=2024, step=1)
            stock = faker.random_int(min=1, max=3, step=1)
            # book = Book(title, author, year, ISBN)

            output.write(f'{author}:{title}:{year}:{ISBN}:{stock}\n')  # gemmer i ny linje efter hver gennemgang


data = generate_books(1000)
