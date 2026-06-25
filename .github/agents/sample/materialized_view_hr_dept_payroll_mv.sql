CREATE MATERIALIZED VIEW hr_dept_payroll_mv
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT e.dept_id,
       COUNT(*) AS employee_count,
       SUM(e.salary) AS total_salary
  FROM hr_employee e
 GROUP BY e.dept_id;
