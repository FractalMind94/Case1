from faker import Faker 
# import random


def generate_user(users):
    with open(r"C:/Users/KOM/Desktop/Opgaver/Case1\\users.txt", "w") as output:  # definér hvilken sti den skal bruge
            
        faker = Faker()

        for i in range(1, users):
            name = faker.name().replace('\n', ' ')
            user_id = i
            address = faker.address().replace('\n', ' ')
            
            # user = User(user_id, name, address)
            
            output.write(f'{user_id}:{name}:{address}\n')  # gemmer i ny linje efter hver gennemgang


data = generate_user(1000)
