import os
from IdentifyPatients import return_patients_with_plans_to_delete
from connect import *


def run():
    patients = return_patients_with_plans_to_delete()
    patient_db = get_current("PatientDB")
    for patient in patients:
        rs_info = patient_db.QueryPatientInfo(Filter={"Id": patient.RS_UID}, UseIndexService=False)
        if len(rs_info) == 1:
            rs_patient = patient_db.LoadPatient(PatientInfo=rs_info[0], AllowPatientUpgrade=False)
            return


if __name__ == '__main__':
    pass
