class fruit:
    def __init__(self, filler1, color, name, filler2, yummieness):
        fruit.name = name
        fruit.color = color
        fruit.tastieness = yummieness

    def give_me_ungodly_powers(self, person_name):
        print("sv_cheats", 1)
        print("there you go", person_name)

apple = fruit("a", "red", "apple", "with a tastieness of", 100)

answer = input("do you want ungodly powers? (y/n)\n")

if answer == "y":
    apple.give_me_ungodly_powers("john")

elif answer == "n":
    print("if you say so!")

else:
    print("I have zero clue what you just said")