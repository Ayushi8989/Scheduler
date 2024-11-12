def subjects_order_cost(subjects_order):
    cost = 0
    total = 0

    for (subject, group_index), times in subjects_order.items():
        if times[0] != -1 and times[1] != -1:
            total += 1
            # P after T
            if times[0] > times[1]:
                cost += 1

        if times[0] != -1 and times[2] != -1:
            total += 1
            # P after L
            if times[0] > times[2]:
                cost += 1

        if times[1] != -1 and times[2] != -1:
            total += 1
            # T after L
            if times[1] > times[2]:
                cost += 1

    return 100 * (total - cost) / total


def empty_space_groups_cost(groups_empty_space):
    cost = 0
    max_empty = 0

    for group_index, times in groups_empty_space.items():
        times.sort()
        empty_per_day = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for i in range(1, len(times) - 1):
            a = times[i-1]
            b = times[i]
            diff = b - a
            if a // 8 == b // 8 and diff > 1:
                empty_per_day[a // 8] += diff - 1
                cost += diff - 1

        for key, value in empty_per_day.items():
            if max_empty < value:
                max_empty = value

    return cost, max_empty, cost / len(groups_empty_space)


def empty_space_professors_cost(professors_empty_space):
    cost = 0
    max_empty = 0

    for professor_name, times in professors_empty_space.items():
        times.sort()
        empty_per_day = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for i in range(1, len(times) - 1):
            a = times[i - 1]
            b = times[i]
            diff = b - a
            if a // 8 == b // 8 and diff > 1:
                empty_per_day[a // 8] += diff - 1
                cost += diff - 1

        # compare current max with empty spaces per day for current professor
        for key, value in empty_per_day.items():
            if max_empty < value:
                max_empty = value

    return cost, max_empty, cost / len(professors_empty_space)


def free_hour(schedule):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = [9, 10, 11, 12, 13, 14, 15, 16, 17]

    for i in range(len(schedule)):
        exists = True
        for j in range(len(schedule[i])):
            field = schedule[i][j]
            if field is not None:
                exists = False

        if exists:
            return '{}: {}'.format(days[i // 8], hours[i % 8])

    return -1


def hard_constraints_cost(schedule, data):
    cost_class = {}
    for c in data.classes:
        cost_class[c] = 0

    cost_classrooms = 0
    cost_professor = 0
    cost_group = 0
    for i in range(len(schedule)):
        for j in range(len(schedule[i])):
            field = schedule[i][j]                                        
            if field is not None:
                c1 = data.classes[field]                                

                # calculate loss for classroom
                if j not in c1.classrooms:
                    cost_classrooms += 1
                    cost_class[field] += 1

                for k in range(j + 1, len(schedule[i])):                  
                    next_field = schedule[i][k]
                    if next_field is not None:
                        c2 = data.classes[next_field]                  

                        # calculate loss for professors
                        if c1.professor == c2.professor:
                            cost_professor += 1
                            cost_class[field] += 1

                        # calculate loss for groups
                        g1 = c1.groups
                        g2 = c2.groups
                        for g in g1:
                            if g in g2:
                                cost_group += 1
                                cost_class[field] += 1

    total_cost = cost_professor + cost_classrooms + cost_group
    return total_cost, cost_class, cost_professor, cost_classrooms, cost_group


def check_hard_constraints(schedule, data):
    overlaps = 0
    for i in range(len(schedule)):
        for j in range(len(schedule[i])):
            field = schedule[i][j]                                    
            if field is not None:
                c1 = data.classes[field]                            

                # calculate loss for classroom
                if j not in c1.classrooms:
                    overlaps += 1

                for k in range(len(schedule[i])):                     
                    if k != j:
                        next_field = schedule[i][k]
                        if next_field is not None:
                            c2 = data.classes[next_field]           

                            # calculate loss for professors
                            if c1.professor == c2.professor:
                                overlaps += 1

                            # calculate loss for groups
                            g1 = c1.groups
                            g2 = c2.groups

                            for g in g1:
                                if g in g2:
                                    overlaps += 1

    return overlaps
