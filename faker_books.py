from faker import Faker 
#import random


def Generate_books(books):
    with open(r"C:/Users/KOM/Desktop/Opgaver/Case1\books.txt", "w") as output: # definér hvilken sti den skal bruge              
        output.write(f'author:title:year:ISBN\n')# gemmer i ny linje efter hver gennemgang

        #books_list=[]
        faker=Faker()
        for i in range(1,books):
            author=faker.name()
            title=faker.sentence()
            ISBN=faker.isbn13()
            year=faker.random_int(min=1, max=2024, step=1)
            #book = Book(title, author, year, ISBN)
            

            output.write(f'{author}:{title}:{year}:{ISBN}\n')# gemmer i ny linje efter hver gennemgang

    

data = Generate_books(1000)
