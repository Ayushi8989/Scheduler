import json, random
from cost import check_hard_constraints, subjects_order_cost, empty_space_groups_cost, empty_space_professors_cost, \
    free_hour
from base import Class, Classroom, Data


def load_data(file_path, professors_empty_space, groups_empty_space, subjects_order):
    with open(file_path) as file:
        data = json.load(file)

    classes = {}
    classrooms = {}
    professors = {}
    groups = {}
    class_list = []

    for cl in data['Classes']:
        new_group = cl['Groups']
        new_professor = cl['Professor']

        if new_professor not in professors_empty_space:
            professors_empty_space[new_professor] = []

        new = Class(new_group, new_professor, cl['Subject'], cl['Type'], cl['Length'], cl['Allowed_Classrooms'])

        for group in new_group:
            if group not in groups:
                groups[group] = len(groups)
                groups_empty_space[groups[group]] = []


        if new_professor not in professors:
            professors[new_professor] = len(professors)
        class_list.append(new)

    random.shuffle(class_list)
    
    for cl in class_list:
        classes[len(classes)] = cl

    for type in data['Classrooms']:
        for name in data['Classrooms'][type]:
            new = Classroom(name, type)
            classrooms[len(classrooms)] = new

    for i in classes:
        cl = classes[i]

        classroom = cl.classrooms
        index_classrooms = []

        for index, c in classrooms.items():
            if c.type == classroom:
                index_classrooms.append(index)
        cl.classrooms = index_classrooms

        class_groups = cl.groups
        index_groups = []
        for name, index in groups.items():
            if name in class_groups:
                # order of subjects
                if (cl.subject, index) not in subjects_order:
                    subjects_order[(cl.subject, index)] = [-1, -1, -1]
                index_groups.append(index)
        cl.groups = index_groups

    return Data(groups, professors, classes, classrooms)


def set_up(num_of_columns):
    w, h = num_of_columns, 40                                       
    schedule = [[None for x in range(w)] for y in range(h)]
    free_slots = []

    for i in range(len(schedule)):
        for j in range(len(schedule[i])):
            free_slots.append((i, j))
    return schedule, free_slots


def show_timetable(schedule):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = [9, 10, 11, 12, 13, 14, 15, 16, 17]

    for i in range(len(schedule[0])):
        if i == 0:
            print('{:17s} C{:6s}'.format('', '0'), end='')
        else:
            print('C{:6s}'.format(str(i)), end='')
    print()

    d_cnt = 0
    h_cnt = 0
    for i in range(len(schedule)):
        day = days[d_cnt]
        hour = hours[h_cnt]
        print('{:10s} {:2d} ->  '.format(day, hour), end='')
        for j in range(len(schedule[i])):
            print('{:6s} '.format(str(schedule[i][j])), end='')
        print()
        h_cnt += 1
        if h_cnt == 8:
            h_cnt = 0
            d_cnt += 1
            print()


def write_solution_to_file(schedule, data, filled, filepath, groups_empty_space, professors_empty_space, subjects_order):
    f = open('output-of-' + filepath, 'w')

    f.write('-------------------------- STATISTICS --------------------------\n')
    cost_hard = check_hard_constraints(schedule, data)
    if cost_hard == 0:
        f.write('\nHard constraints satisfied: 100.00 %\n')
    else:
        f.write('Hard constraints NOT satisfied, cost: {}\n'.format(cost_hard))
    f.write('Soft constraints satisfied: {:.02f} %\n\n'.format(subjects_order_cost(subjects_order)))

    empty_groups, max_empty_group, average_empty_groups = empty_space_groups_cost(groups_empty_space)
    f.write('Total empty space for all groups and all days: {}\n'.format(empty_groups))
    f.write('Max empty space for group in day: {}\n'.format(max_empty_group))
    f.write('Average empty space for groups per week: {:.02f}\n\n'.format(average_empty_groups))

    empty_professors, max_empty_professor, average_empty_professors = empty_space_professors_cost(professors_empty_space)
    f.write('Total empty space for all professor and all days: {}\n'.format(empty_professors))
    f.write('Max empty space for professor in day: {}\n'.format(max_empty_professor))
    f.write('Average empty space for professor per week: {:.02f}\n\n'.format(average_empty_professors))

    f_hour = free_hour(schedule)
    if f_hour != -1:
        f.write('Free hour -> {}\n'.format(f_hour))
    else:
        f.write('No hours without classes.\n')

    groups_dict = {}
    for group_name, group_index in data.groups.items():
        if group_index not in groups_dict:
            groups_dict[group_index] = group_name
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = [9, 10, 11, 12, 13, 14, 15, 16, 17]

    f.write('\n--------------------------- SCHEDULE ---------------------------')
    for class_index, times in filled.items():
        c = data.classes[class_index]
        groups = ' '
        for g in c.groups:
            groups += groups_dict[g] + ', '
        f.write('\n\nClass {}\n'.format(class_index))
        f.write('professor: {} \nSubject: {} \nGroups:{} \nType: {} \nDuration: {} hour(s)'
                .format(c.professor, c.subject, groups[:len(groups) - 2], c.type, c.duration))
        room = str(data.classrooms[times[0][1]])
        f.write('\nClassroom: {:2s}\nTime: {}'.format(room[:room.rfind('-')], days[times[0][0] // 12]))
        for time in times:
            f.write(' {}'.format(hours[time[0] % 8]))
    f.close()


def show_statistics(schedule, data, subjects_order, groups_empty_space, professors_empty_space):
    cost_hard = check_hard_constraints(schedule, data)
    if cost_hard == 0:
        print('Hard constraints satisfied: 100.00 %')
    else:
        print('Hard constraints NOT satisfied, cost: {}'.format(cost_hard))
    print('Soft constraints satisfied: {:.02f} %\n'.format(subjects_order_cost(subjects_order)))