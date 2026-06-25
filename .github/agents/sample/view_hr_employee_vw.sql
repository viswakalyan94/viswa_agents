CREATE OR REPLACE VIEW hr_employee_vw AS
SELECT e.employee_id,
       e.full_name,
       e.dept_id,
       e.salary
  FROM hr_employee e;
