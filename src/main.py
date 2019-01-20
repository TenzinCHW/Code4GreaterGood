import datetime
import csv
from collections import namedtuple, defaultdict

class ClassParticipant:
    def __init__(self, id_no, subjects):
        self.id_no = id_no
        self.mod_ids = tuple(sorted(i for i in subjects if i != None))
        self.sessions = set() # set of Session namedtuples
        self.modules = None # Assign tuple of Module objects

    def __repr__(self):
        return self.id_no

    def assign_module(self, mod):
        assert(mod in self.modules)
        for session in mod.get_sessions():
            self.sessions.add(session)

class Student(ClassParticipant):
    pass

class Professor(ClassParticipant):
    pass

class Module:
    def __init__(self, mod_id, lessons):
        self.mod_id = mod_id
        self.lessons = {Lesson(*l.values()) : 0 for l in lessons} # Counts number of students in each lesson

    def __repr__(self):
        return self.mod_id

    def __lt__(self, other):
        self.mod_id < other.mod_id

    def get_sessions(self):
        return [lesson.get_session() for lesson in self.lessons]

class Lesson:
    def __init__(self, mod_id, lesson_name, duration_hours, capacity):
        self.mod_id = mod_id
        self.lesson_name = lesson_name
        self.num_timeslots = int(2*float(duration_hours))
        self.capacity = int(capacity)
        self.session_count = 0
        self.count = 0

    def get_session(self):
        if self.count < self.capacity:
            self.count += 1
        else:
            self.session_count += 1
            self.count = 0
        return Session(self.mod_id, self.lesson_name, self.session_count)

Session = namedtuple('Session', ['mod_id', 'lesson_name', 'session_num'])

class Schedule:
    def __init__(self):
        pass

if __name__ == '__main__':
    # Read in data
    with open('../data/students.csv') as f:
        s = list(csv.DictReader(f))
    with open('../data/professors.csv') as f:
        p = list(csv.DictReader(f))
    with open('../data/modules.csv') as f:
        m = list(csv.DictReader(f))

    # Create collection of students, professors, and student count of modules and module combinations
    s = [Student(i['ID'], [k for j, k in i.items() if j != 'ID']) for i in s]
    print(s)
    p = [Professor(i['ID'], [k for j, k in i.items() if j!= 'ID']) for i in p]
    print(p)
    uni_mods = set(i['ID'] for i in m)
    m = {Module(m_id, [l for l in m if l['ID'] == m_id]) :
            len([i for i in s if m_id in i.mod_ids])
            for m_id in uni_mods}
    print(m)

    for i in s: # Assign actual module objects to the modules attr for each student
        i.modules = tuple(sorted(j for j in m if j.mod_id in i.mod_ids))

    # Get number of students taking each combination
    combinations = defaultdict(lambda: 0)
    for i in s:
        combinations[i.modules] += 1
    print(combinations)

    # Raise exception (and fail) if there can be no possible timetable schedule
    for i in s:
        total_timeslots = 0
        for j in i.modules:
            total_timeslots = sum(k.num_timeslots for k in j.lessons)
        if total_timeslots > 69:
            raise Exception('No feasible timetable can exist')

    # Sort module combinations by descending number of students
    sorted_combos = sorted(((v, k) for k, v in combinations.items()), reverse=True)
    print(sorted_combos)

    # Assign sessions of each lesson based on number of students for each module combo
    for count, combo in sorted_combos:
        for i in s:
            if i.modules == combo:
                for mod in i.modules:
                    i.assign_module(mod)

    # Get number of unique session combinations
    uni_sess_combo = set(tuple(i.sessions) for i in s)

