__doc__ = """ 
This test is to reproduce the read write lock with samba on windows
"""

from smashbox.utilities import *
from smashbox.utilities.hash_files import *
import time

nfiles = int(config.get('rwlock_smb_nfiles',4)) # The number of files to be created should be 4-1000
delay = int(config.get('rwlock_smb_delay',1)) # this is the delay used to keep files open
smbpath = config.get('rwlock_smb_smbpath',"Z:/smb-rw-lock/")
clean_previous_run = True
path = smbpath + "/officeSimulation_word/"


def count_office_files(path):
    n=0
    for filename in os.listdir(path):
        if not filename.endswith("tmp"):
            n = n + 1
    return n

def open_office_files(mode):
    try:
        for filename in os.listdir(path):
            if not filename.endswith("tmp"):
                file = path + filename
                process = subprocess.Popen(
                    os.getcwd()[:-3] + "\win-tools\KeepOfficeOpen\KeepItOpen.exe " + mode + " delay1" + " " + str(
                        delay) + " " + "s" + " " + "file" + " " + file)

    except Exception as e:
        logger.exception('Error opening the word file to ' + mode + 'on it ')


@add_worker
def worker0(step):

    step(1, 'Preparation')
    k0 = count_office_files(path)

    step(2, 'Create nfiles office files and write some content on it')
    process = subprocess.Popen(os.getcwd()[:-3] + "/win-tools/OfficeUsersSimulation/OfficeUsersSimulation_C.exe nof" + " " + str(nfiles) +  " " + "crtfls usewd wrkdir " + smbpath)

    k1=0
    while(abs(k1-k0) != nfiles):
      k1=count_office_files(path)
      time.sleep(1)

    process.kill() # Avoid the program to be locked by the execution of the program

    step(4, 'Open the nfiles office files with delay to write on it')

    open_office_files("w")

    time.sleep(10)

    step(5, 'Open the nfiles office files with delay to read on it')

    open_office_files("r")



@add_worker
def worker1(step):

    step(1, 'Preparation')

    k0 = count_office_files(path)

    step(3, 'Resync and check files added by worker0')

    ncorrupt = analyse_hashfiles(path)[2]
    k1 = count_office_files(path)

    error_check(k1 - k0 == nfiles, 'Expecting to have %d files more: see k1=%d k0=%d' % (abs(k1 - 1), k1, k0))
    fatal_check(ncorrupt == 0, 'Corrupted files (%d) found' % ncorrupt)