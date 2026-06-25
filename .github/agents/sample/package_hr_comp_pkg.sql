CREATE OR REPLACE PACKAGE hr_comp_pkg AS
  FUNCTION get_bonus(p_employee_id NUMBER) RETURN NUMBER;
  PROCEDURE apply_bonus(p_employee_id NUMBER, p_rate NUMBER);
END hr_comp_pkg;
/

CREATE OR REPLACE PACKAGE BODY hr_comp_pkg AS
  FUNCTION get_bonus(p_employee_id NUMBER) RETURN NUMBER IS
  BEGIN
    RETURN calc_annual_bonus(p_employee_id, 0.10);
  END get_bonus;

  PROCEDURE apply_bonus(p_employee_id NUMBER, p_rate NUMBER) IS
  BEGIN
    UPDATE hr_employee
       SET salary = salary + calc_annual_bonus(p_employee_id, p_rate)
     WHERE employee_id = p_employee_id;
  END apply_bonus;
END hr_comp_pkg;
/
