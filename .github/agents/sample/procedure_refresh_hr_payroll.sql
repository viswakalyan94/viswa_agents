CREATE OR REPLACE PROCEDURE refresh_hr_payroll AS
  v_bonus NUMBER;
BEGIN
  v_bonus := calc_annual_bonus(1000, 0.05);

  UPDATE hr_employee
     SET salary = salary + v_bonus
   WHERE employee_id = 1000;

  DBMS_MVIEW.REFRESH('HR_DEPT_PAYROLL_MV');
END;
/

