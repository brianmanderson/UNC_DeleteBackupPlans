import os
from datetime import datetime
from InfoStructure.Base import DateTimeClass
from IdentifyPatients import return_patients_with_plans_to_delete
from connect import *


def check_is_approved(rs_treatment_plan):
    if rs_treatment_plan.Review is None:
        return False
    review: ReviewClass
    review = tp.Review
    if review.ApprovalStatus == "Approved":
        return True
    return False


def run():
    print("Running")
    today = DateTimeClass()
    today.from_python_datetime(datetime.now())
    patients = return_patients_with_plans_to_delete(today, 60)
    searching_strings = ["backup", "notused", "notusing", "dnu"]
    print("Found " + str(len(patients)) + " Patients")
    patient_db = get_current("PatientDB")
    for patient in patients:
        rs_info = patient_db.QueryPatientInfo(Filter={"PatientID": patient.MRN}, UseIndexService=False)
        if len(rs_info) == 1:
            rs_patient = patient_db.LoadPatient(PatientInfo=rs_info[0], AllowPatientUpgrade=False)
            for case in rs_patient.Cases:
                for treatment_plan in case.TreatmentPlans:
                    delete_tp = False
                    for s in searching_strings:
                        if treatment_plan.Name.lower().find(s) != -1:
                            delete_tp = True
                            break
                    if delete_tp:
                        for beam_set in treatment_plan.BeamSets:
                            for beam in beam_set.Beams:

            return


if __name__ == '__main__':
    pass
