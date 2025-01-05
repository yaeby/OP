import signal
import random
import string
import sys


def process_signal_one(sig_type, stack_frame):
    print("SIGUSR1 received")


def process_signal_two(sig_type, stack_frame):
    generated_output = ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=100
        )
    )
    print(generated_output)
    sys.exit(0)

signal.signal(signal.SIGUSR1, process_signal_one)
signal.signal(signal.SIGUSR2, process_signal_two)

if __name__ == "__main__":
    print("Program running, send SIGUSR1 or SIGUSR2 to test")
    
    while True:
        pass