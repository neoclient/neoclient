from client import Person, greet

person: Person = Person(name="sam")

greeting: str = greet(person)

print(greeting)
