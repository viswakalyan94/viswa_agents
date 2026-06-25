CREATE OR REPLACE FUNCTION calc_annual_bonus (
  p_employee_id NUMBER,
  p_rate NUMBER
) RETURN NUMBER AS
  v_salary NUMBER;
BEGIN
  SELECT salary
    INTO v_salary
    FROM hr_employee
   WHERE employee_id = p_employee_id;

  RETURN v_salary * p_rate;
END;
/
