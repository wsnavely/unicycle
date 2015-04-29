"""Some common solver templates"""

import unicycle
import logging

def brute_force(\
        cmd,\
        args,\
        cycle,\
        guess,\
        choose,\
        success,\
        alphabet,\
        pad=0):
    """A brute force instruction counting solver template.

    This function takes two additional functions as input.  Theses
    functions should have the following signatures.

    choose:
        list -> iterable

        Takes a list of 2-tuples, of the form (ch, count), where ch
        is a character and count is in integer.  This list represents
        the instruction counts for each character in this iteration
        of the brute force attempt.  The function should return
        the characters from the list that the brute forcer should add
        to the password next, in order of preference.

    success:
        tuple -> bool

        Takes a 3-tuple of the form (stdout, stderr, rc), where stdout and
        stderr represent the output of the binary (strings), and rc is the
        return code (int).  Returns true if the output represents a successful
        run of the program, false otherwise.

    Args:
        cmd: The command to execute.
        args: The arguments to the command.
        cycle: Path to the unicycle to ride.
        guess: The current guess.
        choose: A function to choose which character guesses to keep.
        success: A function to determine whether a given run was successful.
        alphabet: The input alphabet.
    """

    logging.info("Guess{" + guess + "}")
    counts = []
    for next_ch in alphabet:
        next_guess = (guess + next_ch).ljust(pad, "X") + "\n"
        result = unicycle.ride(cycle, cmd, args, stdin=(next_guess))
        logging.debug(result)
        if success(result):
            return (True, next_guess)
        stderr = result[1]
        lines = stderr.split("\n")
        count = int(lines[-1])
        counts.append((next_ch, count))

    for cand in choose(counts):
        rec_guess = guess + cand[0]
        return brute_force(\
                cmd,\
                args,\
                cycle,\
                rec_guess,\
                choose,\
                success,\
                alphabet,\
                pad)
