from ortools.sat.python import cp_model

model = cp_model.CpModel()

# 8個員工
num_employees = 8

# 排3周的班
num_weeks =3 

# 每天的班次分為 : 休息、早、中、晚
shifts = ['O','M','A','N']

# 總排班天數
num_days = num_weeks * 7

# 班次數量 
num_shifts = len(shifts)

work = {}

# 定義排班的控制變數
for e in range(num_employees):
    for s in range(num_shifts):
        for d in range(num_days):
            work[e,s,d] = model.new_bool_var('work%i_%i_%i' % (e,s,d))

# 定義線性目標便亮組和係數組，在對目標最小化時會使用這些目標便亮組和係數組。
obj_int_vars = []
obj_int_coeffs = []
obj_bool_vars = []
obj_bool_coeffs = []

# 約束一、每個員工每天只能做一個班次(硬)
for e in range(num_employees):
    for d in range(num_days):
        model.add(sum(work[e,s,d] for s in range(num_shifts)) ==1)

# 約束二、固定某些員工的班次: 固定某些員工在某些天做某些班次(硬)
fixed_assignments = [
        (0,0,0),
        (1,0,0),
        (2,1,0),
        (3,1,0),
        (4,2,0),
        (5,2,0),
        (6,2,3),
        (7,3,0),
        (0,1,1),
        (1,1,1),
        (2,2,1),
        (3,2,1),
        (4,2,1),
        (5,0,1),
        (6,0,1),
        (7,3,1),
    ]

# 實現固定班次約束
for e,s,d in fixed_assignments:
    model.add(work[e,s,d]==1)

# 約束三、員工需求Request: 某些員工希望某天做(不做)某個班次(軟)
# 負的權重表示某個員工希望上某個班次，正的權重表示某個員工不希望某天上某個班次
requests = [
    # 3號員工希望第一周六休息
    (3,0,5,-2),
    # 5號員工希望第二個週四上晚班
    (5,3,10,-2),
    # 2號員工不希望第一個週五上晚班
    (2,3,4,4)
]

# 實現約束
for e,s,d,w in requests:
    obj_bool_vars.append(work[e,s,d])
    obj_bool_coeffs.append(w)


# 約束四、班次連續天數的約束: 某個員工連續上某個班次的天數(軟)
# (班次, 最小天數(硬), 最小天數(軟), 最小懲罰值, 最大天數(軟), 最大天數(硬), 最大懲罰值)

shift_constraints = [
    # 可以連續休息1天或兩天，不會被懲罰
    (0, 1, 1, 0, 2, 2, 0),
    # 夜班連續上2天或者3天，只上1天或者連續上4天都會被懲罰
    (3, 1, 2,20, 3, 4, 5)
]


# 生成一個連續方班天數的固定模式序列
def negated_bounded_span(works, start, length):
    sequence = []
    # 處理序列的左邊界
    if start > 0:
        sequence.append(works[start-1])
    for i in range(length):
        sequence.append(works[start+i].Not())
    # 處理序列的右邊界
    if start + length < len(works):
        sequence.append(works[start + length])
    return sequence

def add_soft_sequence_constraint(model, works, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost, prefix):

    cost_literals = []
    cost_coefficients = []

    # 禁止連續上小於hard_min天的班
    for length in range(1, hard_min):
        for start in range(len(works) - length -1):
            model.add_bool_or(negated_bounded_span(works, start, length))

    # 懲罰連續上班天數落在區間[hard_min, soft_min) 中的情況
    if min_cost > 0:
        for length in range(hard_min, soft_min):
            for start in range(len(works) - length + 1):
                span = negated_bounded_span(works, start, length)
                name = ': under_span(start=%i, length=%i)' % (start, length)
                lit = model.new_bool_var(prefix + name)
                span.append(lit)
                model.add_bool_or(span)
                cost_literals.append(lit)
                # We filter exactly the sequence with a short length.
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(min_cost * (soft_min - length))

    # 懲罰連續上班天數落在區間(soft_max, hard_max]中的情況
    if max_cost >0 :
        for length in range(soft_max + 1, hard_max + 1):
            for start in range(len(works) - length + 1):
                span = negated_bounded_span(works, start, length)
                name = ': over_span(start=%i, length=%i)' % (start, length)
                lit = model.new_bool_var(prefix + name)
                span.append(lit)
                model.add_bool_or(span)
                cost_literals.append(lit)
                # We filter exactly the sequence with a short length.
                # The penalty is proportional to the delta with soft_min.
                cost_coefficients.append(max_cost * (length - soft_max))

    # 禁止連續上>hard_max天的班
    for start in range(len(works) - hard_max -1):
        model.add_bool_or([works[i].Not() for i in range(start, start + hard_max + 1)])

    return cost_literals, cost_coefficients
# 班次約束
for ct in shift_constraints:
    shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
    for e in range(num_employees):
        works = [work[e, shift, d] for d in range(num_days)]
        variables ,coeffs = add_soft_sequence_constraint(
            model, works, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost, 'shift_constraint(employee %i, shift %i)' % (e, shift))
        obj_bool_vars.extend(variables)
        obj_bool_coeffs.extend(coeffs)

# 約束五、不同班次在每周的合計天數約束(軟)
# (班次, 最小天數(硬), 最小天數(軟), 最小懲罰值, 最大天數(軟), 最大天數(硬), 最大懲罰值)
weekly_sum_constraints = [
    # 每周休息天數的約束
    (0, 1, 2, 7, 2, 3, 4),
    # 最少一個夜班, 最多四個頁班, 不上或者超過四個夜班會懲罰
    (3, 0, 1, 3, 4, 4, 0)
]

def add_soft_sum_constraint(
    model: cp_model.CpModel,
    works: list[cp_model.BoolVarT],
    hard_min: int,
    soft_min: int,
    min_cost: int,
    soft_max: int,
    hard_max: int,
    max_cost: int,
    prefix: str,
) -> tuple[list[cp_model.IntVar], list[int]]:
    """sum constraint with soft and hard bounds.

    This constraint counts the variables assigned to true from works.
    If forbids sum < hard_min or > hard_max.
    Then it creates penalty terms if the sum is < soft_min or > soft_max.

    Args:
      model: the sequence constraint is built on this model.
      works: a list of Boolean variables.
      hard_min: any sequence of true variables must have a sum of at least
        hard_min.
      soft_min: any sequence should have a sum of at least soft_min, or a linear
        penalty on the delta will be added to the objective.
      min_cost: the coefficient of the linear penalty if the sum is less than
        soft_min.
      soft_max: any sequence should have a sum of at most soft_max, or a linear
        penalty on the delta will be added to the objective.
      hard_max: any sequence of true variables must have a sum of at most
        hard_max.
      max_cost: the coefficient of the linear penalty if the sum is more than
        soft_max.
      prefix: a base name for penalty variables.

    Returns:
      a tuple (variables_list, coefficient_list) containing the different
      penalties created by the sequence constraint.
    """
    cost_variables = []
    cost_coefficients = []
    sum_var = model.new_int_var(hard_min, hard_max, "")
    # This adds the hard constraints on the sum.
    model.add(sum_var == sum(works))

    # Penalize sums below the soft_min target.
    if soft_min > hard_min and min_cost > 0:
        delta = model.new_int_var(-len(works), len(works), "")
        model.add(delta == soft_min - sum_var)
        # TODO(user): Compare efficiency with only excess >= soft_min - sum_var.
        excess = model.new_int_var(0, 7, prefix + ": under_sum")
        model.add_max_equality(excess, [delta, 0])
        cost_variables.append(excess)
        cost_coefficients.append(min_cost)

    # Penalize sums above the soft_max target.
    if soft_max < hard_max and max_cost > 0:
        delta = model.new_int_var(-7, 7, "")
        model.add(delta == sum_var - soft_max)
        excess = model.new_int_var(0, 7, prefix + ": over_sum")
        model.add_max_equality(excess, [delta, 0])
        cost_variables.append(excess)
        cost_coefficients.append(max_cost)

    return cost_variables, cost_coefficients

for ct in weekly_sum_constraints:
    shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
    for e in range(num_employees):
        for w in range(num_weeks):
            works = [work[e, shift, d + w * 7] for d in range(7)]
            variables, coeffs = add_soft_sum_constraint(
                model, works, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost, 'weekly_sum_constraint(employee %i, shift %i, week %i)' % (e,shift,w))
            obj_int_vars.extend(variables)
            obj_int_coeffs.extend(coeffs)

# 約束6: 不同班次之間相互連接的約束
#(前一個班次, 後一個班次, 懲罰值 (0 意味被禁止))
penalized_transitions = [
    # 中班連著晚班，懲罰值是4
    (2, 3, 4),
    # 夜班連著早班，被禁止
    (3, 1, 0)
]

# 懲罰和禁止違規的班次連連接
for previous_shift, next_shift, cost in penalized_transitions:
    for e in range(num_employees):
        for d in range(num_days - 1):
            transition = [work[e, previous_shift, d].Not(), work[e, next_shift,d + 1].Not()]

            if cost == 0:
                model.add_bool_or(transition)
            else:
                trans_var = model.new_bool_var ('transition (employee=%i, day=%i)' % (e, d))
                transition.append(trans_var)
                model.add_bool_or(transition)
                obj_bool_vars.append(trans_var)
                obj_bool_coeffs.append(cost)


# 約束七、每周每一天各個班次數量的約束(軟)
weekly_cover_demands = [
        (2,3,1),#周一:2个早班,3个中班,1个晚班
        (2,3,1),#周二:2个早班,3个中班,1个晚班
        (2,2,2),#周三:2个早班,2个中班,2个晚班
        (2,3,1),#周四:2个早班,3个中班,1个晚班
        (2,2,2),#周五:2个早班,2个中班,2个晚班
        (1,2,3),#周六:1个早班,2个中班,2个晚班
        (1,3,1),#周日:1个早班,3个中班,1个晚班
    ]

excess_cover_penalties = (2, 2, 5)
for s in range(1, num_shifts):
    for w in range(num_weeks):
        for d in range(7):
            works = [work[e, s, w * 7 + d] for e in range(num_employees)]
            # Ignore Off shift.
            min_demand = weekly_cover_demands[d] [s - 1]
            worked = model.NewIntVar(min_demand, num_employees, '')
            model.Add(worked == sum(works))
            over_penalty = excess_cover_penalties[s - 1]
            if over_penalty > 0:
                name = 'excess_demand(shift=%i, week=%i, day=%i)' % (s,w,d)
                excess = model.NewIntVar(0, num_employees - min_demand,name)
                model.Add(excess == worked - min_demand)
                obj_int_vars. append(excess)
                obj_int_coeffs.append(over_penalty)

# 


model.Minimize(
sum(obj_bool_vars[i] * obj_bool_coeffs[i]
for i in range(len(obj_bool_vars))) +
sum(obj_int_vars[i] * obj_int_coeffs[i]
for i in range(len(obj_int_vars))))
solver = cp_model.CpSolver()
#设置程序执行时间
solver.parameters.max_time_in_seconds = 10

solution_printer = cp_model.ObjectiveSolutionPrinter()
status = solver.solve(model, solution_printer)

# 答应排班结菜

if status ==cp_model.INFEASIBLE:
    print("The model is infeasible!!")
    

if status == cp_model.OPTIMAL or status == cp_model. FEASIBLE:
    print()
    header = '          '
    for w in range(num_weeks):
     header += 'M T W T F S S '
    print (header)
    for e in range(num_employees):
        schedule = ''
        for d in range(num_days):
            for s in range(num_shifts):
                if solver.BooleanValue(work[e, s, d]):
                  schedule += shifts[s] + ' '
        print('worker %i: %s' % (e, schedule))
    print()
    print('Penalties:')
    for i, var in enumerate(obj_bool_vars):
        if solver.BooleanValue(var):
            penalty = obj_bool_coeffs[i]
        if penalty > 0:
            print(' %s violated, penalty=%i' % (var.Name(), penalty))
        else:
            print(' %s fulfilled, gain=%i' % (var.Name(),-penalty))
    for i, var in enumerate(obj_int_vars):
        if solver.Value(var) > 0:
            print(' %s violated by %i, linear penalty=%i' %
            (var.Name(), solver.Value(var), obj_int_coeffs[i]))

    print()
    print('Statistics')
    print(' - status: %s' % solver.StatusName(status))
    print(' - conflicts: %i' % solver.NumConflicts())
    print(' - branches: %i' % solver.NumBranches())
    print(' - wall time: %f s' % solver.WallTime())