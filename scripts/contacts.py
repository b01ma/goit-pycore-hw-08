import re
import datetime as dt
from datetime import datetime as dtdt
from colorama import Fore, Back, Style
from scripts.decorators import input_error, check_arguments, exception_handler

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

#  Field
class Field():
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)

# Name
class Name(Field):
    def __init__(self, name: str):
        super().__init__(name)
    
# Phone  
class Phone(Field):
    def __init__(self, phone: str):
        self.validate_phone(phone)
        super().__init__(phone)
    def validate_phone(self, phone):
        if not re.match(r'^\d{10}$', phone):
            raise ValueError(f'Invalid phone number: {phone}. Phone must be exactly 10 digits')

# Birthday
class Birthday(Field): 
    def __init__(self, value: str):
            self.validate_date(value)
            super().__init__(value)
    
    def validate_date(self, value):
        try:
            dtdt.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError('Invalid date format. Use DD.MM.YYYY')
       
# Record
class Record():
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    @exception_handler
    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
      
    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    @exception_handler
    def edit_phone(self, phone: str, new_phone: str):
        for p in self.phones:
            if p.value == phone:
                p.value = new_phone
                return
        raise ValueError(f'Phone number {phone} is not found')
       
    @exception_handler
    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)
             
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

# AddressBook
class AddressBook():
    def __init__(self):
        self.data = {}
    
    def add_record(self, record: Record):
        self.data[record.name.value] = record
    
    @exception_handler
    def find(self, name: str):
        if name in self.data:
            return self.data[name]
        return None
        
    @exception_handler
    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f'Record {name} is not found')
    
    @exception_handler
    def get_upcoming_birthdays(self) -> list:
        result = []
        today = dt.date.today()
        current_year = today.year
        
        # Calculate the range for next Monday to Friday
        days_to_monday = (7 - today.weekday()) % 7
        next_monday = today + dt.timedelta(days=days_to_monday)
        next_friday = next_monday + dt.timedelta(days=4)
        days_to_next_friday = (next_friday - today).days
        
        for record in self.data.values():
            if not record.birthday:
                continue
            try:
                birthday_str = record.birthday.value
                birthday_obj = dtdt.strptime(birthday_str, "%d.%m.%Y").date()
            except ValueError: 
                raise ValueError(f"Invalid date format for {record.name.value}")
            # get birthday this year
            birthday_this_year = dt.date(current_year, birthday_obj.month,birthday_obj.day)
            if birthday_this_year < today:
                birthday_this_year = dt.date(current_year + 1, birthday_obj.month, birthday_obj.day)
                
            days_to_birthday = (birthday_this_year - today).days
            day_of_birthday = birthday_this_year.weekday()
            
            if days_to_birthday < days_to_next_friday:
                congratulation_date = birthday_this_year
                # If birthday is on Saturday (5) or Sunday (6), move to Monday
                if day_of_birthday in [5, 6]:
                    congratulation_date = next_monday

                result.append({'name': record.name.value, 'congratulation_date': congratulation_date.strftime("%d.%m.%Y")})

        return result
    
    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

book = AddressBook()   
# 1 add
@check_arguments(2)
@input_error
def add(*args: tuple):
    *name_parts, phone = args
    name = " ".join(name_parts)
    
    record = book.find(name)
    message = "Contact updated."
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    print(message)
    return 0

# 2 change
@check_arguments(3)
@input_error
def change(*args: tuple):
    *name_parts, old_phone, new_phone = args
    name = " ".join(name_parts) 
    
    record = book.find(name)
    if record is None:
        raise ValueError(f'Contact {name} cannot be found')
    record.edit_phone(old_phone, new_phone)
    print(f'Contact updated')
    return 0

#3 phone
@check_arguments(1)
@input_error
def phone(*args: tuple):
    name = " ".join(args)
    
    record = book.find(name)
    if record is None:
        raise ValueError(f'Contact {name} cannot be found')
    else:
        print(f'Phone of {name}:')
        for phone in record.phones:
            print(phone)
    return 0

#4 all
@input_error
def all():
    
    if not book.data:
        print(f'No records found')
        return 1
    
    for record in book.data.values():
        print(f'{record.name}:')
        for phone in record.phones:
            print(f'--tel:{phone}')
            
    return 0

# 5 add-birthday
@check_arguments(2)
@input_error
def add_birthday(*args:tuple):
    *name_parts, birthday = args
    name = " ".join(name_parts) 
    
    record = book.find(name)
    
    if not record:
        print(Fore.RED + f'Error: Contact "{name}" not found. Cannot add birthday.' + Style.RESET_ALL)
        return 1
    
    record.add_birthday(birthday)
    print(f'Birthday added')
            
    return 0

# 6 show-birthday
@check_arguments(1)
@input_error
def show_birthday(*args:tuple):
    name = " ".join(args) 
    
    record = book.find(name)
    if not record:
        print(f'Record {name} is not found')
        return 1
    birthday = record.birthday
    print(f'Birthday of {name}: {birthday}')
            
    return 0

# 7 birthdays
@input_error
def birthdays():
    birthdays = book.get_upcoming_birthdays()
    for birthday in birthdays:
        print(f"{birthday['name']} has birthday on {birthday['congratulation_date']}")
    return 0

def close():
    print(Back.LIGHTWHITE_EX + Fore.BLACK + 'Goodbye.' + Style.RESET_ALL)
    return 0