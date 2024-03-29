import os
from datetime import datetime
from typing import List
from InfoStructure.Base import PatientHeader, DateTimeClass, StrippedDownPlan, ReviewClass
from InfoStructure.Base import update_local_database


def check_is_approved(tp: StrippedDownPlan):
    if tp.Review is None:
        return False
    review: ReviewClass
    review = tp.Review
    if review.ApprovalStatus == "Approved":
        return True
    return False


def return_plan_names_by_contains(patients: List[PatientHeader], find_str: str):
    plan_names: List[str]
    plan_names = []
    for patient in patients:
        for case in patient.Cases:
            for plan in case.TreatmentPlans:
                is_approved = check_is_approved(plan)
                if not is_approved:
                    if plan.PlanName.lower().find(find_str) != -1:
                        if plan.PlanName not in plan_names:
                            plan_names.append(plan.PlanName)
    return plan_names


def filter_patients_by_plan_startswith(patients: List[PatientHeader], find_str: str):
    patient_list: List[PatientHeader]
    patient_list = []
    for patient in patients:
        added_patient = False
        for case in patient.Cases:
            if added_patient:
                break
            for plan in case.TreatmentPlans:
                is_approved = check_is_approved(plan)
                if not is_approved:
                    if plan.PlanName.lower().startswith(find_str):
                        patient_list.append(patient)
                        added_patient = True
                        break
    return patient_list


def load_patient_headers(header_files: List[str]):
    patients: List[PatientHeader]
    patients = []
    for header_file in header_files:
        if os.path.exists(header_file):
            patient_header = PatientHeader.from_json_file(header_file)
            patients.append(patient_header)
    return patients


def identify_plan_names(database_path):
    all_files = os.listdir(database_path)
    json_files = [os.path.join(database_path, i) for i in all_files if i.endswith(".json")]
    header_files = [i for i in json_files if i.endswith("_Header.json")]
    patients = load_patient_headers(header_files)
    plan_names = return_plan_names_by_contains(patients, 'backup')
    fid = open(os.path.join("Data", 'PlanNames.txt'), 'w+')
    for line in plan_names:
        fid.write(line + '\n')
    fid.close()
    return plan_names


def separate_by_min_date(start_date: DateTimeClass, days_since_last_edit: int, header_files: List[str]):
    loading_headers = []

    for file in header_files:
        _, header_file = os.path.split(file)
        date = header_file.split('_')[-2]
        year, month, day, hour, minute = date.split('.')
        date_object = DateTimeClass()
        date_object.year = int(year)
        date_object.month = int(month)
        date_object.day = int(day)
        if (start_date - date_object).days > days_since_last_edit:
            loading_headers.append(file)
    return loading_headers


def return_patients_with_plans_to_delete(database: str, today: DateTimeClass, day_since_edit: int,
                                         searching_string: List[str], verbose=False):
    # searching_string = ["backup", "notused", "notusing", "dnu"]
    if today is None:
        today = DateTimeClass()
        today.from_python_datetime(datetime.today())
    path = r'\\vscifs1\PhysicsQAdata\BMA\RayStationDataStructure\DataBases'
    # path = r'C:\Users\Markb\Modular_Projects\Local_Databases'
    # update_local_database(local_database_path=r'C:\Users\Markb\Modular_Projects\Local_Databases',
    #                       network_database_path=path)
    database_path = os.path.join(path, database)
    all_files = os.listdir(database_path)
    json_files = [os.path.join(database_path, i) for i in all_files if i.endswith(".json")]
    header_files = [i for i in json_files if i.endswith("_Header.json")]
    header_files = separate_by_min_date(start_date=today, days_since_last_edit=day_since_edit, header_files=header_files)
    patients = load_patient_headers(header_files)
    patients_with_plans_to_delete: List[PatientHeader]
    patients_with_plans_to_delete = []
    for find_str in searching_string:
        patients_with_plans_to_delete += filter_patients_by_plan_startswith(patients, find_str)
    if verbose:
        plans_to_delete = 0
        for pat in patients_with_plans_to_delete:
            for case in pat.Cases:
                for tp in case.TreatmentPlans:
                    for s in searching_string:
                        if tp.PlanName.lower().find(s) != -1:
                            print(pat.MRN + " " + tp.PlanName)
                            plans_to_delete += 1
        print("Aiming to delete " + str(plans_to_delete) + " plans")
    return patients_with_plans_to_delete


if __name__ == '__main__':
    # x = return_patients_with_plans_to_delete("2020", None, 90, verbose=True,
    #                                          searching_string=["backup", "notused", "notusing", "dnu"])
    pass
