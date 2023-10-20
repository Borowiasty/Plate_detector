'''
    Class used to simple database emulation, also Plates_local_databe.add_plate chceck if license plate is valid (meet established criteria)
'''

class Plates_local_databe:
    def __init__(self, show = 0):
        self._plates = []
        self._show_operated_number = show
    
    def _check_plate_number(self, plate_to_be_checked):                         # checker if plate is in class's list used as databe
        is_in_database = False

        for plate in self._plates:
            if plate == plate_to_be_checked:
                is_in_database = True
                break
            else:
                continue

        return is_in_database

    def add_plate(self, plate_to_add ):                                         # only metod accesable from outside of class, check criteria and add plate to list 
        
        if self._show_operated_number == 1: print(plate_to_add)                 # print full readed text

        if len(plate_to_add) >= 5:                                              # first critiron length of license over 5
            plate_to_add = plate_to_add.upper()                                 # upper the readed letters, license has to be capital
            if not plate_to_add.isalpha() or not plate_to_add.isnumeric():      # check is license is only alphabetical or numerical
                no_special = True
                for charr in plate_to_add:                                      # check char after char
                    if charr.isalpha():                                         # is alphabetical? Pass, we do not care
                        continue
                    elif charr.isnumeric():                                     # is numeric? Pass, we do not care
                        continue
                    elif charr == ' ' or charr == '-':                          # is space or '-'? Pass, we do not care (we allow to it)
                        continue
                    else:                                                       # now, if char can't meet our criteria, we know it is special and break loop
                        no_special = False
                        break

                if no_special:

                    if self._show_operated_number == 2: print(plate_to_add)     # print added plate                                                  # if string met our criteria we allow to write into database
                    
                    if not self._check_plate_number(plate_to_add):              # check if license in not in local database allready
                        self._plates.append(plate_to_add)                       # and add it into list
                        return True
                    else:
                        return False
            else:                                                               # if string met our criteria we allow to write into database
                if not self._check_plate_number(plate_to_add):                  # check if license in not in local database allready
                    self._plates.append(plate_to_add)                           # and add it into list
                    return True                                                     
                else:
                    return False
    
    def delete_plate(self, plate_to_delete):                                    # deleter particullar plate from list [TODO]
            if self._check_plate_number(plate_to_delete):                       # check if plate is in database so we don't get error
                self._plates.pop(plate_to_delete)                               # and delete [TODO]
                return True
            else:
                return False

    def print_plates(self):
        print('Local plates:')
        for plate in self._plates:
            print(plate)

    