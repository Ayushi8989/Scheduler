import random, copy, math
from operator import itemgetter
from utilities import load_data, show_timetable, set_up, show_statistics, write_solution_to_file
from cost import check_hard_constraints, hard_constraints_cost, empty_space_groups_cost, free_hour


def initial_population(data, schedule, free_slots, filled, groups_empty_space, professors_empty_space, subjects_order):
    classes = data.classes

    for index, current_class in classes.items():
        new_index = 0
        while True:
            start_field = free_slots[new_index]

            # class should not continue beyond working hours
            start_time = start_field[0]
            end_time = start_time + int(current_class.duration) - 1
            if start_time % 8 > end_time % 8:
                new_index += 1
                continue

            found = True
            for i in range(1, int(current_class.duration)):
                field = (i + start_time, start_field[1])
                if field not in free_slots:
                    found = False
                    new_index += 1
                    break

            if start_field[1] not in current_class.classrooms:
                new_index += 1
                continue

            if found:
                for group_index in current_class.groups:
                    insert_order(subjects_order, current_class.subject, group_index, current_class.type, start_time)
                    for i in range(int(current_class.duration)):
                        groups_empty_space[group_index].append(i + start_time)

                for i in range(int(current_class.duration)):
                    filled.setdefault(index, []).append((i + start_time, start_field[1]))       
                    free_slots.remove((i + start_time, start_field[1]))                                
                    professors_empty_space[current_class.professor].append(i + start_time)
                break

    for index, fields_list in filled.items():
        for field in fields_list:
            schedule[field[0]][field[1]] = index


def insert_order(subjects_order, subject, group, type, start_time):
    times = subjects_order[(subject, group)]
    if type == 'L':
        times[0] = start_time
    elif type == 'T':
        times[1] = start_time
    else:
        times[2] = start_time
    subjects_order[(subject, group)] = times


def exchange_two(schedule, filled, index_1, index_2):
    first = filled[index_1]
    filled.pop(index_1, None)
    second = filled[index_2]
    filled.pop(index_2, None)

    for i in range(len(first)):
        t = schedule[first[i][0]][first[i][1]]
        schedule[first[i][0]][first[i][1]] = schedule[second[i][0]][second[i][1]]
        schedule[second[i][0]][second[i][1]] = t

    filled[index_1] = second
    filled[index_2] = first

    return schedule


def valid_professor_group_row(schedule, data, index_class, row):
    c1 = data.classes[index_class]
    for j in range(len(schedule[row])):
        if schedule[row][j] is not None:
            c2 = data.classes[schedule[row][j]]

            if c1.professor == c2.professor:
                return False

            for g in c2.groups:
                if g in c1.groups:
                    return False
    return True


def mutate_ideal_spot(schedule, data, ind_class, free_slots, filled, groups_empty_space, professors_empty_space, subjects_order):
    rows = []
    fields = filled[ind_class]
    for f in fields:
        rows.append(f[0])

    current_class = data.classes[ind_class]
    index = 0
    while True:
        # ideal spot not found
        if index >= len(free_slots):
            return
        start_field = free_slots[index]

        # check if class won't start one day and end on the next
        start_time = start_field[0]
        end_time = start_time + int(current_class.duration) - 1
        if start_time % 8 > end_time % 8:
            index += 1
            continue

        # check whether new classroom is suitable
        if start_field[1] not in current_class.classrooms:
            index += 1
            continue

        # check if whole block can be taken for new class 
        found = True
        for i in range(int(current_class.duration)):
            field = (i + start_time, start_field[1])
            if field not in free_slots or not valid_professor_group_row(schedule, data, ind_class, field[0]):
                found = False
                index += 1
                break

        if found:
            filled.pop(ind_class, None)
            for f in fields:
                free_slots.append((f[0], f[1]))
                schedule[f[0]][f[1]] = None
                # remove empty space of the group from old place of the class
                for group_index in current_class.groups:
                    groups_empty_space[group_index].remove(f[0])
                # remove professor's empty space from old place of the class
                professors_empty_space[current_class.professor].remove(f[0])

            # update order of the subjects and add empty space for each group
            for group_index in current_class.groups:
                insert_order(subjects_order, current_class.subject, group_index, current_class.type, start_time)
                for i in range(int(current_class.duration)):
                    groups_empty_space[group_index].append(i + start_time)

            # add new term of the class to filled, remove those fields from free_slots dict and insert new block in schedule
            for i in range(int(current_class.duration)):
                filled.setdefault(ind_class, []).append((i + start_time, start_field[1]))
                free_slots.remove((i + start_time, start_field[1]))
                schedule[i + start_time][start_field[1]] = ind_class
                # add new empty space for professor
                professors_empty_space[current_class.professor].append(i+start_time)
            break


def evolve(schedule, data, free_slots, filled, groups_empty_space, professors_empty_space, subjects_order):
    n = 3
    sigma = 2
    run_times = 5
    max_stagnation = 200

    for run in range(run_times):
        print('Run {} | sigma = {}'.format(run + 1, sigma))

        t = 0
        stagnation = 0
        cost_stats = 0
        while stagnation < max_stagnation:

            # check if optimal solution is found
            loss_before, cost_classes, cost_professors, cost_classrooms, cost_groups = hard_constraints_cost(schedule, data)
            if loss_before == 0 and check_hard_constraints(schedule, data) == 0:
                print('Found optimal solution: \n')
                show_timetable(schedule)
                break

            # sort classes by their loss
            costs_list = sorted(cost_classes.items(), key=itemgetter(1), reverse=True)

            for i in range(len(costs_list) // 4):
                # mutate one to its ideal spot
                if random.uniform(0, 1) < sigma and costs_list[i][1] != 0:
                    mutate_ideal_spot(schedule, data, costs_list[i][0], free_slots, filled, groups_empty_space,
                                      professors_empty_space, subjects_order)

            loss_after, _, _, _, _ = hard_constraints_cost(schedule, data)
            if loss_after < loss_before:
                stagnation = 0
                cost_stats += 1
            else:
                stagnation += 1

            t += 1
            if t >= 10*n and t % n == 0:
                s = cost_stats
                if s < 2*n:
                    sigma *= 0.85
                else:
                    sigma /= 0.85
                cost_stats = 0

        # print('Number of iterations: {} \nCost: {} \nprofessors cost: {} | Groups cost: {} | Classrooms cost:'
        #       ' {}'.format(t, loss_after, cost_professors, cost_groups, cost_classrooms))


def simulated_annealing(schedule, data, free_slots, filled, groups_empty_space, professors_empty_space, subjects_order, file):
    iter_count = 2500
    temperature = 0.5
    _, _, curr_cost_group = empty_space_groups_cost(groups_empty_space)
    curr_cost = curr_cost_group  
    if free_hour(schedule) == -1:
        curr_cost += 1

    for i in range(iter_count):
        rt = random.uniform(0, 1)
        temperature *= 0.99                  

        # save current results
        old_matrix = copy.deepcopy(schedule)
        old_free = copy.deepcopy(free_slots)
        old_filled = copy.deepcopy(filled)
        old_groups_empty_space = copy.deepcopy(groups_empty_space)
        old_professors_empty_space = copy.deepcopy(professors_empty_space)
        old_subjects_order = copy.deepcopy(subjects_order)

        # attempt to mutate a quarter of all classes
        for j in range(len(data.classes) // 4):
            index_class = random.randrange(len(data.classes))
            mutate_ideal_spot(schedule, data, index_class, free_slots, filled, groups_empty_space, professors_empty_space,
                              subjects_order)
        _, _, new_cost_groups = empty_space_groups_cost(groups_empty_space)
        new_cost = new_cost_groups  
        if free_hour(schedule) == -1:
            new_cost += 1

        if new_cost < curr_cost or rt <= math.exp((curr_cost - new_cost) / temperature):
            curr_cost = new_cost
        else:
            # return to previously saved data
            schedule = copy.deepcopy(old_matrix)
            free_slots = copy.deepcopy(old_free)
            filled = copy.deepcopy(old_filled)
            groups_empty_space = copy.deepcopy(old_groups_empty_space)
            professors_empty_space = copy.deepcopy(old_professors_empty_space)
            subjects_order = copy.deepcopy(old_subjects_order)
        if i % 100 == 0:
            print('Iteration: {:4d} | Average cost: {:0.8f}'.format(i, curr_cost))

    print('\n\nTimetable after annealing:\n')
    show_timetable(schedule)
    print('Statistics after annealing')
    show_statistics(schedule, data, subjects_order, groups_empty_space, professors_empty_space)
    write_solution_to_file(schedule, data, filled, file, groups_empty_space, professors_empty_space, subjects_order)


def main():
    filled = {}
    subjects_order = {}
    groups_empty_space = {}
    professors_empty_space = {}
    file = 'input.json'

    data = load_data(file, professors_empty_space, groups_empty_space, subjects_order)
    schedule, free_slots = set_up(len(data.classrooms))
    initial_population(data, schedule, free_slots, filled, groups_empty_space, professors_empty_space, subjects_order)

    total, _, _, _, _ = hard_constraints_cost(schedule, data)
    print('Initial cost of hard constraints: {}'.format(total))

    evolve(schedule, data, free_slots, filled, groups_empty_space, professors_empty_space, subjects_order)
    print('Statistics')
    show_statistics(schedule, data, subjects_order, groups_empty_space, professors_empty_space)
    simulated_annealing(schedule, data, free_slots, filled, groups_empty_space, professors_empty_space, subjects_order, file)


if __name__ == '__main__':
    main()