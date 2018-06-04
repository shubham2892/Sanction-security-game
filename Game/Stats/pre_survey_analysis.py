import csv


def get_range_ipip(score):
    if 16 <= score <= 20:
        return "High"
    elif 15 <= score <= 11:
        return "medium"
    else:
        return "low"


def get_range_dospert(score):
    if score <= 18:
        return "low"
    elif score >= 30:
        return "High"
    else:
        return "medium"


def dospert_scale_analysis(file_name):
    dospert_scale_dict = {}

    with open(file_name) as csvfile:
        file_reader = csv.reader(csvfile)
        file_reader.next()
        for row in file_reader:
            for i in range(1, 31):
                row[i] = int(row[i])

            mturk_id = row[31]
            # IPIP 37 -- 56
            base_start = 0
            ethical = row[base_start + 6] + (row[base_start + 9]) + (row[base_start + 10]) + (
                row[base_start + 16]) + row[base_start + 29] + row[base_start + 30]
            Financial = row[base_start + 3] + (row[base_start + 4]) + (row[base_start + 8]) + (
                row[base_start + 12]) + row[base_start + 14] + row[base_start + 18]
            heath_safety = row[base_start + 5] + (row[base_start + 15]) + (row[base_start + 17]) + (
                row[base_start + 20]) + row[base_start + 23] + row[base_start + 26]
            recreational = row[base_start + 2] + (row[base_start + 11]) + (row[base_start + 13]) + (
                row[base_start + 19]) + row[base_start + 24] + row[base_start + 25]
            social = row[base_start + 1] + (row[base_start + 7]) + (row[base_start + 21]) + (
                row[base_start + 22]) + row[base_start + 27] + row[base_start + 28]

            dospert_scale_dict[mturk_id] = {"ethical": get_range_dospert(ethical),
                                            "Financial": get_range_dospert(Financial),
                                            "heath_safety": get_range_dospert(heath_safety),
                                            "recreational": get_range_dospert(recreational),
                                            "social": get_range_dospert(social),
                                            "total": (ethical + Financial + heath_safety + recreational + social)}
        print(dospert_scale_dict)
    return dospert_scale_dict


def ipip_mini_test_analysis(file_name):
    ipip_test_score = {}
    with open(file_name) as csvfile:
        file_reader = csv.reader(csvfile)
        file_reader.next()
        for row in file_reader:
            for i in range(37, 57):
                row[i] = int(row[i])

            mturk_id = row[31]
            # IPIP 37 -- 56
            base_start = 36
            openess = row[base_start + 5] + (6 - row[base_start + 10]) + (6 - row[base_start + 15]) + (
                    6 - row[base_start + 20])
            conscientiousness = row[base_start + 3] + (6 - row[base_start + 8]) + (row[base_start + 13]) + (
                    6 - row[base_start + 18])
            extraversion = row[base_start + 1] + (6 - row[base_start + 6]) + (row[base_start + 11]) + (
                    6 - row[base_start + 16])
            agreeableness = row[base_start + 2] + (6 - row[base_start + 7]) + (row[base_start + 12]) + (
                    6 - row[base_start + 17])
            neuroticism = row[base_start + 4] + (6 - row[base_start + 9]) + (row[base_start + 14]) + (
                    6 - row[base_start + 19])

            ipip_test_score[mturk_id] = {"openess": get_range_ipip(openess),
                                         "conscientiousness": get_range_ipip(conscientiousness),
                                         "extraversion": get_range_ipip(extraversion),
                                         "agreeableness": get_range_ipip(agreeableness),
                                         "euroticism": get_range_ipip(neuroticism)}

    print(ipip_test_score)

    if __name__ == "__main__":
        # ipip_mini_test_analysis("Presurvey-mturk.csv")
        dospert_scale_analysis("Presurvey-mturk.csv")
