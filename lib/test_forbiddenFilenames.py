import os
import time
import tempfile


__doc__ = """ Add invalid named files to a directory and check consistency. """

from smashbox.utilities import *
from smashbox.utilities.hash_files import *
from smashbox.utilities.monitoring import push_to_monitoring

forbidden_charsets = {
		'backslash' : '\\',
                 'colon' : ':',
                 'questionmark' : '?',
                 'asterisk' : '*',
                 'doublequote' : '"',
                 'greater' : '>',
                 'smaller' : '<',
                 'pipe'    : '|'
}

nfiles = len(forbidden_charsets)

@add_worker
def worker0(step):

    # do not cleanup server files from previous run
    reset_owncloud_account()

    # cleanup all local files for the test
    reset_rundir()

    step(1,'Preparation')
    d = make_workdir()
    run_ocsync(d)
    k0 = count_files(d)



    step(2,'Add %s files to %s and check if we still have k1+nfiles after resync'%(nfiles,d))
    logger.log(35,"Timestamp %f Files %d",time.time(),nfiles)

    for c in forbidden_charsets:
        print d+'/'+forbidden_charsets[c]
        createfile(d+'/'+forbidden_charsets[c], 'a', 1, 3)
#    print '/\\'
#    print '/:'
#    print '/?'
#    print '/*'
#    print '/"'
#    print '/>'
#    print '/<'
#    print '/|'

#    createfile(d+'/\\', 'a', 1, 3)
#    createfile(d+'/:', 'a', 1, 3)
#    createfile(d+'/?', 'a', 1, 3)
#    createfile(d+'/*', 'a', 1, 3)
#    createfile(d+'/"', 'a', 1, 3)
#    createfile(d+'/>', 'a', 1, 3)
#    createfile(d+'/<', 'a', 1, 3)
#    createfile(d+'/|', 'a', 1, 3)
#    createfile(d+'/newFile', 'a', 1, 3)

    run_ocsync(d)

    ncorrupt = analyse_hashfiles(d)[2]
    
    k1 = count_files(d)

    error_check(k1-k0==nfiles,'Expecting to have %d files more in %s: see k1=%d k0=%d'%(nfiles,d,k1,k0))

    fatal_check(ncorrupt==0, 'Corrupted files (%s) found'%ncorrupt)

    logger.info('SUCCESS: %d files found',k1)


@add_worker
def worker1(step):
    step(1,'Preparation')
    d = make_workdir()
    run_ocsync(d)
    k0 = count_files(d)

    step(3,'Resync and check files added by worker0')

    run_ocsync(d)

    ncorrupt = analyse_hashfiles(d)[2]
    k1 = count_files(d)
                       
    error_check(k1-k0==nfiles,'Expecting to have %d files more: see k1=%d k0=%d'%(nfiles,k1,k0))

    fatal_check(ncorrupt==0, 'Corrupted files (%d) found'%ncorrupt)


