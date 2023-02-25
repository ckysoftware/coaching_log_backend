def convert_db_list_to_py_list(db_list):
    result = []
    for item in db_list:
        result.append(item.__dict__)
    return result
