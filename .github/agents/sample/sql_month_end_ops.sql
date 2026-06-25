INSERT INTO hr_employee (employee_id, full_name, dept_id, salary)
VALUES (hr_employee_seq.NEXTVAL, 'JANE DOE', 30, 75000);

MERGE INTO hr_employee tgt
USING (
  SELECT employee_id, get_bonus(employee_id) AS bonus_amt
    FROM hr_employee_vw
) src
ON (tgt.employee_id = src.employee_id)
WHEN MATCHED THEN
  UPDATE SET tgt.salary = tgt.salary + src.bonus_amt;

SELECT *
  FROM hr_dept_payroll_mv;

