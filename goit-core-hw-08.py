from collections import UserDict
import re
from datetime import datetime
from datetime import timedelta
import pickle


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Потрібно ПІБ!"
        except KeyError:
            return "Нема такого ПІБ!"
        except ValueError as e:
            return "Потрібно ПІБ та тел.!"

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Phone(Field):
    def __init__(self, value):
        if (
            len(value) != 10 or not value.isdigit()
        ):  # перевірка на 10 символів і це цифри
            raise ValueError(
                "Phone number must contain 10 digits."
            )  # якщо ValueError перериваємо програму і виводимо повідомлення
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # додаемо ДР
    def add_birthday(self, sdate):
        self.birthday = Birthday(sdate)

    # додаемо тел
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    # видалення тел
    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    # редагування тел
    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone) == old_phone:
                phone.value = new_phone
                break

    # пошук за номером
    def find_phone(self, phone_number):
        for phone in self.phones:
            if str(phone) == phone_number:
                return phone

    # повернення інфо
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
            return self.data[name]

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def add_dr(self, name, dr):
        rec = self.find(name)
        if rec == None:
            rec = Record(name)
            rec.add_birthday(dr)
            self.add_record(rec)
        else:
            rec.add_birthday(dr)
        return "ДР додано"

    def add_contact(self, name, phone):
        rec = self.find(name)
        if rec == None:
            rec = Record(name)
            rec.add_phone(phone)
            self.add_record(rec)
        else:
            rec.add_phone(phone)
            self.add_record(rec)
        return "Контакт додано"

    def get_upcoming_birthdays(self):
        listall = []
        if self.data == None:
            return listall
        now = datetime.today().date()  # поточна дата
        for rec in self.data:
            date_user = self.data[rec].birthday.value  # аналіз дат народження
            date_user = date_user.replace(year=now.year)  # міняемо год на поточний
            days_since = (
                date_user.toordinal() - now.toordinal()
            )  # рахуємо кількость днів
            if days_since >= 0 and days_since <= 7:  # яка доба
                iday = int(date_user.weekday())  # перетв дня тижня
                if iday == 5:
                    date_user = date_user + timedelta(days=2)  # дод 2 дні
                elif iday == 6:
                    date_user = date_user + timedelta(days=1)  # дод 1 день
                sdate = date_user.strftime("%d.%m.%Y")  # нова дата ДН
                s1 = f"Name: {self.data[rec].name} - DR: {sdate}"
                listall.append(s1)
        return "\n".join(listall)


def all_contact(self) -> str:
    listall = [f"{self.data[el1]}" for el1 in self.data]
    return "\n".join(listall)


@input_error
def phone_contact(book: AddressBook, args):
    name = args[0]
    return book.find(name)


@input_error
def change_contact(book: AddressBook, args):
    name, oldphone, newphone = args
    record = book.find(name)
    if record != None:
        record.edit_phone(oldphone, newphone)
        book.data[name] = record
        return "Контакт змінено"
    else:
        raise ValueError("Контакт не знайдено!")


@input_error
def add_contact(book: AddressBook, args):
    name, phone = args
    return book.add_contact(name, phone)


@input_error
def add_birthday(book: AddressBook, args):
    name, dr = args
    return book.add_dr(name, dr)


@input_error
def show_birthday(book: AddressBook, args):
    name = args[0]
    return book.find(name)


@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)  # Викликати перед виходом з програми
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(book, args))

        elif command == "change":
            print(change_contact(book, args))

        elif command == "phone":
            print(phone_contact(book, args))

        elif command == "all":
            print(all_contact(book))

        elif command == "add-birthday":
            print(add_birthday(book, args))

        elif command == "show-birthday":
            print(show_birthday(book, args))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
