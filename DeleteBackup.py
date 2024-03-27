import os
from datetime import datetime
import random
from InfoStructure.Base import DateTimeClass, PatientClass
from IdentifyPatients import return_patients_with_plans_to_delete
from connect import *


def check_is_approved(rs_treatment_plan):
    if rs_treatment_plan.Review is None:
        return False
    review = rs_treatment_plan.Review
    if review.ApprovalStatus == "Approved":
        return True
    return False


def run():
    print("Running")
    today = DateTimeClass()
    today.from_python_datetime(datetime.now())
    searching_string = ["backup", "notused", "notusing", "dnu"]
    database = "2021"
    patients = return_patients_with_plans_to_delete(database, today, day_since_edit=90, searching_string=searching_string,
                                                    verbose=True)
    print("Found " + str(len(patients)) + " Patients")
    patient_db = get_current("PatientDB")
    plans_deleted = 0
    random.shuffle(patients)
    path = r'\\vscifs1\PhysicsQAdata\BMA\RayStationDataStructure\DataBases'
    db_path = os.path.join(path, database)
    for patient in patients:
        rs_info = patient_db.QueryPatientInfo(Filter={"PatientID": patient.MRN}, UseIndexService=False)
        if len(rs_info) == 1:
            try:
                rs_patient = patient_db.LoadPatient(PatientInfo=rs_info[0], AllowPatientUpgrade=False)
            except:
                continue
            patient_class = PatientClass()
            patient_class.build_info(rs_patient)
            pat_json = os.path.join(db_path, patient_class.return_out_file_name())
            if not os.path.exists(pat_json):
                continue
            for case in rs_patient.Cases:
                for treatment_plan in case.TreatmentPlans:
                    if check_is_approved(treatment_plan):
                        continue
                    delete_tp = False
                    for s in searching_string:
                        if treatment_plan.Name.lower().find(s) != -1:
                            delete_tp = True
                            break
                    if delete_tp:
                        print("Deleting " + treatment_plan.Name.lower())
                        plans_deleted += 1
                        for beam_set in treatment_plan.BeamSets:
                            beams_to_delete = []
                            for beam in beam_set.Beams:
                                beams_to_delete.append(beam.Name)
                            for beam_name in beams_to_delete:
                                beam_set.DeleteBeam(BeamName=beam_name)
            rs_patient.Save()
            if os.path.exists(pat_json):
                os.remove(pat_json)
            header_json = pat_json.replace(".json", "_Header.json")
            if os.path.exists(header_json):
                os.remove(header_json)
    print("Deleted " + str(plans_deleted) + " plans in total")


if __name__ == '__main__':
    pass
