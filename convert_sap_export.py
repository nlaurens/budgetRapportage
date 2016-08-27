import sys
import os
import model.ordergroup
import model.ksgroup
"""
Usage
    $ python convert_sap_export.py <directory with files to convert>

"""
if __name__ == "__main__":
    valid_input = False
    if len(sys.argv) == 3:
        target_dir = str(sys.argv[1])
        target_type = str(sys.argv[2])
        types_allowed = ['ordergroup', 'ksgroup']
        if os.path.isdir(target_dir) and target_type in types_allowed:
            valid_input = True

    if valid_input:
        print 'converting'
        for (dirpath, dirnames, filenames) in os.walk(target_dir):
            for name in filenames:
                target_input = os.path.join(dirpath, name)
                target_output = open(os.path.join(dirpath, name + '.converted'), 'w')
                if target_type == 'ordergroup':
                    ordergroup = model.ordergroup.load_sap(target_input)
                    ordergroup.save_as_txt(target_output)
                elif target_type == 'ksgroup':
                    ksgroup = model.ksgroup.load_sap(target_input)
                    ksgroup.save_as_txt(target_output)
                else:
                    assert False, "target type %s not recognized" % target_type

                print '%s - done' % target_input

        print 'all done'
    else:
        print 'error in arguments'
        print 'use convert_sap_export.py <directory> <type>'
        print 'types allowed: ordergroup, ksgroup'
