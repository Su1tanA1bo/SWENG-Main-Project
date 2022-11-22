from pynput.keyboard import Listener
from time import sleep

string = ""
log = []
erased = 0


def add_to_list(key_input):
    key = str(key_input)
    key = key.replace("'", "")
    key = key.replace("Key.", "")

    global string
    global erased
    if key == "space":
        string += " "
    elif key == "enter":
        string += "\n"
    elif key == "tab":
        string += "    "
    elif key == "backspace":
        erased += 1
        if len(log) > 0 and log[-1] == "tab":
            string = string[:-4]
        elif len(string) > 0:
            string = string[:-1]

    elif len(key) == 1:
        string += key

    log.append(key)
    print(string)
    print(log)


if __name__ == '__main__':
    with Listener(on_press=add_to_list) as listener:
        listener.join()

    while len(log < 30):
        sleep(1)

    listener.stop()
