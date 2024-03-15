import os
from datetime import datetime
from InfoStructure.Base import DateTimeClass
from IdentifyPatients import return_patients_with_plans_to_delete
from connect import *


def run():
    print("Running")
    today = DateTimeClass()
    today.from_python_datetime(datetime.now())
    patients = return_patients_with_plans_to_delete(today, 90)
    print("Found " + str(len(patients)) + " Patients")
    patient_db = get_current("PatientDB")
    for patient in patients:
        rs_info = patient_db.QueryPatientInfo(Filter={"PatientID": patient.MRN}, UseIndexService=False)
        if len(rs_info) == 1:
            rs_patient = patient_db.LoadPatient(PatientInfo=rs_info[0], AllowPatientUpgrade=False)
            return


if __name__ == '__main__':
    pass
