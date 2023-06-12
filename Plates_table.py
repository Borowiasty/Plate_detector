class Plates_local_databe:
    def __init__(self):
        self._plates = []
    
    def _check_plate_number(self, plate_to_be_checked):
        is_in_database = False

        for plate in self._plates:
            if plate == plate_to_be_checked:
                is_in_database = True
                break
            else:
                continue

        return is_in_database

    def add_plate(self, plate_to_add ):
        if len(plate_to_add) >= 5:
            plate_to_add.upper()
            if not plate_to_add.isalpha() or not plate_to_add.isnumeric():
                no_special = True
                for charr in plate_to_add:
                    if charr.isalpha():
                        continue
                    elif charr.isnumeric():
                        continue
                    elif charr == ' ' or charr == '-':
                        continue
                    else:
                        no_special = False
                        break

                if no_special:
                    if not self._check_plate_number(plate_to_add):
                        self._plates.append(plate_to_add)
                        return True
                    else:
                        return False
            else:
                if not self._check_plate_number(plate_to_add):
                    self._plates.append(plate_to_add)
                    return True
                else:
                    return False
    
    def delete_plate(self, plate_to_delete):
            if self._check_plate_number(plate_to_delete):
                self._plates.pop(plate_to_delete)
                return True
            else:
                return False

    def print_plates(self):
        print('Local plates:')
        for plate in self._plates:
            print(plate)

    